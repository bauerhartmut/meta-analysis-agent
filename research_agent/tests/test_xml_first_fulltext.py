"""XML-first-Volltextpfad: JATS-XML vor PDF, Tabellen bis in die Extraktion.

Hintergrund: Beide Melatonin-Netzlaeufe holten SE/CI fast nur aus Textpfaden
(Run 1: 0/19 Effekte mit CI, Run 2: 2/8), obwohl Europe PMC fuer OA-Artikel
strukturierte JATS-XML liefert. ``fetch_open_access_text`` kannte PMC-IDs nur,
wenn sie in der URL standen; DOI-Quellen gingen direkt an Unpaywall (PDF).
Diese Tests halten den neuen Vorrang und die Tabellenerhaltung fest.
"""

from __future__ import annotations

import asyncio
import unittest

from research_agent.research.extractor import ContentExtractor
from research_agent.research.jats_tables import blocks_from_jats

LONG_TEXT = (
    "Melatonin reduced sleep onset latency in adults; the pooled effect was "
    "computed from the per-trial estimates reported in the tables. " * 20
)

XML = f"""<?xml version="1.0"?>
<article>
  <front><article-meta><title-group><article-title>Melatonin trial</article-title>
  </title-group></article-meta></front>
  <body>
    <sec><title>Results</title><p>{LONG_TEXT}</p></sec>
    <table-wrap id="t1">
      <label>Table 1</label>
      <caption><p>Effect of melatonin on sleep onset latency.</p></caption>
      <table>
        <thead><tr>
          <th>Outcome</th><th>Intervention</th><th>Control</th>
          <th>MD (95% CI)</th><th>SE</th><th>N</th>
        </tr></thead>
        <tbody>
          <tr><td>Sleep onset latency (min)</td><td>38.2</td><td>45.1</td>
              <td>-6.90 (9.1 to -4.7)</td><td>1.11</td><td>N = 120</td></tr>
          <tr><td>Sleep quality (score)</td><td>7.4 (SD 1.2)</td><td>7.1 (SD 1.3)</td>
              <td>0.30</td><td>0.11</td><td>N = 98</td></tr>
        </tbody>
      </table>
    </table-wrap>
  </body>
</article>
"""


class _Response:
    def __init__(self, status=200, json_payload=None, text=""):
        self.status = status
        self._json = json_payload
        self._text = text

    async def json(self):
        return self._json

    async def text(self, *args, **kwargs):
        return self._text

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class _Session:
    def __init__(self, routes):
        self.routes = routes
        self.calls = []

    def get(self, url=None, **kwargs):
        self.calls.append(url or "")
        for needle, response in self.routes:
            if needle in (url or ""):
                return _Response(**response)
        return _Response(status=404, json_payload={})


def _extractor(routes):
    extractor = ContentExtractor()
    session = _Session(routes)

    async def _ensure():
        return session

    extractor._get_session = _ensure
    return extractor, session


SEARCH_HIT = {"resultList": {"result": [{"pmcid": "PMC13669090"}]}}


class XmlFirstRetrievalTest(unittest.TestCase):
    def test_doi_source_uses_fulltext_xml_before_any_pdf(self):
        extractor, session = _extractor([
            ("europepmc/webservices/rest/search", {"json_payload": SEARCH_HIT}),
            ("fullTextXML", {"text": XML}),
            ("api.unpaywall.org", {"json_payload": {"is_oa": True, "oa_locations": []}}),
        ])

        result = asyncio.run(extractor.fetch_open_access_text(
            doi="10.1234/melatonin", title="Melatonin trial"
        ))

        self.assertIsNotNone(result)
        self.assertTrue(result["fulltext_source"].startswith("europepmc-fulltext"))
        self.assertFalse(
            any("unpaywall" in url for url in session.calls),
            "the XML route must win before PDF discovery",
        )

    def test_pmcid_in_url_skips_the_doi_lookup(self):
        extractor, session = _extractor([
            ("fullTextXML", {"text": XML}),
        ])

        result = asyncio.run(extractor.fetch_open_access_text(
            url="https://europepmc.org/article/PMC/PMC13669090", title="Melatonin trial"
        ))

        self.assertIsNotNone(result)
        self.assertFalse(any("/search" in url for url in session.calls))


class TablePreservationTest(unittest.TestCase):
    def test_table_rows_survive_in_the_document_text(self):
        extractor, _ = _extractor([("fullTextXML", {"text": XML})])

        result = asyncio.run(extractor.fetch_open_access_text(
            url="https://europepmc.org/article/PMC/PMC13669090", title="Melatonin trial"
        ))

        content = result["content"]
        self.assertIn("|Sleep onset latency (min)|38.2|45.1|", content)
        self.assertIn("|1.11|N = 120", content)
        # Kein Tag-Rest aus dem XML.
        self.assertNotIn("<td>", content)

    def test_structured_tables_travel_with_the_result(self):
        extractor, _ = _extractor([("fullTextXML", {"text": XML})])

        result = asyncio.run(extractor.fetch_open_access_text(
            url="https://europepmc.org/article/PMC/PMC13669090", title="Melatonin trial"
        ))

        blocks = result.get("jats_tables") or []
        self.assertEqual(len(blocks), 1)
        block = blocks[0]
        self.assertEqual(block["table_label"], "Table 1")
        self.assertEqual(block["parser"], "jats-table/1")
        self.assertEqual(block["n_lines"], 2)
        self.assertEqual(len(block["effect_cells"]), 2)
        self.assertTrue(block["effect_cells"][0]["has_ci"])
        self.assertIn("1.11", block["effect_cells"][0]["line"])


class TableRendererFidelityTest(unittest.TestCase):
    """Zwei Fehler, die die Spaltenzuordnung still zerstoeren koennen."""

    def test_empty_cells_keep_their_column(self):
        from research_agent.coverage.manager import _xml_to_text

        xml = ("<table-wrap><caption>t</caption>"
               "<tr><td>Arm</td><td/><td>7.5</td></tr></table-wrap>")
        self.assertIn("|Arm| |7.5", _xml_to_text(xml))

    def test_less_than_cell_text_is_not_stripped_as_markup(self):
        from research_agent.coverage.manager import _xml_to_text

        xml = ("<table-wrap><caption>t</caption>"
               "<tr><td>Arm</td><td>&lt;.001</td><td>9.9</td></tr></table-wrap>")
        self.assertIn("|Arm|<.001|9.9", _xml_to_text(xml))


class BlocksFromJatsTest(unittest.TestCase):
    def test_body_rows_are_literal_parts_of_the_rendered_text(self):
        from research_agent.coverage.manager import _xml_to_text

        text = _xml_to_text(XML)
        blocks = blocks_from_jats(XML)

        self.assertTrue(blocks)
        for block in blocks:
            for line in block["body"].splitlines():
                self.assertIn(line, text)
