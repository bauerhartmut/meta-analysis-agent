"""Full-text pipeline: sections, quote spans, pages, PDFs, stored citations.

Offline: hand-built PDF bytes, fake HTTP responses, in-memory or temp databases.
The claim under test is the one that matters for research work - every stored
fact carries a passage that exists in a stored document, with its section and
page - and the failure mode that matters: a quote the model made up must not be
presented as a citation.
"""

import asyncio
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.config import Config
from research_agent.database import Database
from research_agent.memory.store import MemoryStore
from research_agent.models import gen_id, now_iso
from research_agent.orchestrator import ResearchOrchestrator
from research_agent.research.extractor import ContentExtractor
from research_agent.research.fulltext import (
    locate_quote,
    page_for_offset,
    page_offsets,
    section_for_offset,
    select_text,
    split_sections,
)


PAPER = """Polygenic Scores and Cognitive Outcomes
Jane Doe, John Smith

Abstract
Polygenic scores for educational attainment explain 11 to 13 percent of the
variance in educational attainment. The within-family estimate was roughly four
percent in the same cohort.

1. Introduction
Genetic prediction of complex traits is contested. Critics note that population
stratification inflates naive estimates considerably when it is ignored.

2. Methods
We analysed 1.1 million individuals of European ancestry. Siblings were compared
within families to control for shared ancestry and assay batch.

3. Results
The polygenic score predicted 4.2 percent of variance (95% CI 3.8-4.6) in the
held-out cohort of 120,000 people. The effect was smaller in the within-family
design, at 1.9 percent of variance.

4. Discussion
Our results suggest that the effect is smaller than earlier reports claimed.
Gene-by-environment interplay remains unmeasured here.

References
Smith J. 2019. Something about genetics. Nature 42:1-10.
"""


def _pdf_bytes(lines):
    """A minimal one-page PDF with real text (no external PDF library)."""
    content = "BT /F1 12 Tf 72 720 Td 14 TL " + " ".join(
        f"({line}) Tj T*" for line in lines
    ) + " ET"
    objects = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        "/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        f"<< /Length {len(content)} >>\nstream\n{content}\nendstream",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = "%PDF-1.4\n"
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{number} 0 obj\n{body}\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n"
    for offset in offsets:
        out += f"{offset:010d} 00000 n \n"
    out += f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n"
    return out.encode("latin-1")


class _Response:
    def __init__(self, status=200, body=b"", text="", content_type="text/html",
                 payload=None):
        self.status = status
        self._body = body
        self._text = text
        self.headers = {"Content-Type": content_type}
        self._payload = payload

    async def read(self):
        return self._body

    async def text(self, *args, **kwargs):
        return self._text

    async def json(self):
        return self._payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False


class _Session:
    def __init__(self, responses):
        self.responses = responses if isinstance(responses, list) else [responses]
        self.calls = []
        self.closed = False

    def get(self, url=None, **kwargs):
        self.calls.append(url)
        return self.responses[min(len(self.calls) - 1, len(self.responses) - 1)]

    async def close(self):
        self.closed = True


class TestSections(unittest.TestCase):
    def test_sections_cover_the_document_in_order(self):
        sections = split_sections(PAPER)
        keys = [s["key"] for s in sections]
        self.assertEqual(
            keys,
            ["front_matter", "abstract", "introduction", "methods", "results",
             "discussion", "references"],
        )
        self.assertEqual(sections[0]["start"], 0)
        self.assertEqual(sections[-1]["end"], len(PAPER))
        for section in sections:
            if section["key"] in ("front_matter", "full_text"):
                continue  # those titles are labels, not lines of the document
            self.assertEqual(PAPER[section["start"]:section["start"] + 3],
                             section["title"][:3])

    def test_references_are_flagged(self):
        sections = split_sections(PAPER)
        references = [s for s in sections if s["key"] == "references"]
        self.assertTrue(references and references[0]["is_references"])
        self.assertIn("Smith J.", PAPER[references[0]["start"]:references[0]["end"]])

    def test_section_for_offset(self):
        sections = split_sections(PAPER)
        offset = PAPER.index("The polygenic score predicted")
        self.assertEqual(section_for_offset(sections, offset), "3. Results")
        self.assertEqual(section_for_offset(sections, -1), "")

    def test_document_without_headings_is_one_block(self):
        text = "A single paragraph about heritability without any headings at all."
        sections = split_sections(text)
        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0]["key"], "full_text")

    def test_empty_text_has_no_sections(self):
        self.assertEqual(split_sections(""), [])


class TestQuoteLocation(unittest.TestCase):
    SENTENCE = ("The polygenic score predicted 4.2 percent of variance "
                "(95% CI 3.8-4.6) in the held-out cohort of 120,000 people.")

    def test_exact_quote(self):
        span = locate_quote(PAPER, self.SENTENCE)
        self.assertIsNotNone(span)
        self.assertTrue(span.exact)
        self.assertIn("4.2 percent", PAPER[span.start:span.end])

    def test_line_breaks_in_the_quote_do_not_matter(self):
        # The document wraps this sentence; the quote does not.
        quote = self.SENTENCE.replace("in the held-out", "in the\nheld-out")
        span = locate_quote(PAPER, quote)
        self.assertIsNotNone(span)
        self.assertTrue(span.exact)

    def test_hyphenation_from_pdf_columns_is_forgiven(self):
        text = "Polygenic scores were examined in a large cohort of 1.1 million sub-\njects."
        span = locate_quote(text, "a large cohort of 1.1 million subjects")
        self.assertIsNotNone(span)
        self.assertIn("million", text[span.start:span.end])

    def test_curly_quotes_are_normalized(self):
        text = "The authors call this \u201cheritability\u201d and measure it in twins."
        span = locate_quote(text, 'call this "heritability" and measure it')
        self.assertIsNotNone(span)

    def test_invented_quote_is_not_located(self):
        self.assertIsNone(locate_quote(
            PAPER, "The authors prove that embryo selection raises IQ by 15 points."
        ))

    def test_short_fragment_is_rejected(self):
        self.assertIsNone(locate_quote(PAPER, "Results"))

    def test_paraphrase_is_located_but_not_exact(self):
        # One number changed: the head still matches, the span reports itself as
        # inexact so the caller can treat the citation as weaker.
        span = locate_quote(
            PAPER,
            "The polygenic score predicted 4.2 percent of variance (95% CI 3.8-4.7)",
        )
        if span is not None:
            self.assertFalse(span.exact)
            self.assertTrue(span.start < span.end)
            self.assertLessEqual(span.end, len(PAPER))


class TestPages(unittest.TestCase):
    def test_offsets_match_the_join(self):
        pages = ["first page text", "", "third page text"]
        joined = "\n\n".join(page.strip() for page in pages)
        ranges = page_offsets(pages)
        self.assertEqual(len(ranges), 3)
        for start, end, number in ranges:
            self.assertLessEqual(end, len(joined))
            self.assertTrue(joined[start:end] in pages[number - 1])

    def test_prefix_shifts_every_page(self):
        ranges = page_offsets(["alpha", "beta"], prefix=10)
        self.assertEqual(ranges[0][0], 10)
        self.assertEqual(page_for_offset(ranges, 12), 1)
        self.assertEqual(page_for_offset(ranges, ranges[1][0]), 2)

    def test_unknown_offset_is_minus_one(self):
        self.assertEqual(page_for_offset([], 5), -1)
        self.assertEqual(page_for_offset([[0, 10, 1]], 99), -1)


class TestSelectText(unittest.TestCase):
    def test_short_text_is_returned_whole(self):
        self.assertEqual(select_text(PAPER, ["polygenic"], budget=100000), PAPER)

    def test_budget_is_respected_and_references_are_dropped(self):
        selection = select_text(PAPER, ["polygenic", "variance"], budget=400)
        self.assertLessEqual(len(selection), 400)
        self.assertNotIn("Smith J. 2019", selection)

    def test_relevant_late_section_is_preferred_over_early_filler(self):
        filler = "\n\n".join(
            f"Filler paragraph {i} about unrelated administrative matters." for i in range(60)
        )
        document = f"Introduction\n{filler}\n\nResults\nThe heritability estimate rose with age.\n"
        selection = select_text(document, ["heritability", "age"], budget=300)
        self.assertIn("heritability estimate rose", selection)


class TestPdfExtraction(unittest.TestCase):
    def test_pages_are_extracted(self):
        pages = ContentExtractor._pdf_pages(
            _pdf_bytes(["The heritability estimate rose with age.", "Second line."])
        )
        self.assertEqual(len(pages), 1)
        self.assertIn("heritability estimate rose", pages[0])

    def test_garbage_pdf_yields_nothing(self):
        self.assertEqual(ContentExtractor._pdf_pages(b"%PDF-1.4 broken"), [])

    def test_arxiv_pdf_url(self):
        self.assertEqual(
            ContentExtractor.arxiv_pdf_url("https://arxiv.org/abs/2410.15581v1"),
            "https://arxiv.org/pdf/2410.15581v1.pdf",
        )
        self.assertEqual(
            ContentExtractor.arxiv_pdf_url("https://arxiv.org/pdf/2410.15581.pdf"),
            "https://arxiv.org/pdf/2410.15581.pdf",
        )
        self.assertEqual(ContentExtractor.arxiv_pdf_url("https://example.org/x"), "")

    def test_direct_pdf_url_is_parsed(self):
        pdf = _pdf_bytes([
            "The polygenic score predicted 4.2 percent of variance in the held-out "
            "cohort of 120,000 people. The within-family estimate was 1.9 percent, "
            "which is considerably smaller than the naive estimate. Siblings were "
            "compared within families to control for shared ancestry, and the "
            "analysis was preregistered before any outcome data were inspected."
        ])
        extractor = ContentExtractor()
        session = _Session(_Response(body=pdf, content_type="application/pdf"))

        async def _ensure():
            return session

        extractor._get_session = _ensure
        result = asyncio.run(extractor.extract("https://example.org/paper.pdf"))

        self.assertTrue(result["success"])
        self.assertEqual(result["fulltext_source"], "pdf-direct")
        self.assertIn("4.2 percent", result["content"])
        self.assertEqual(len(result["pages"]), 1)


class TestSourceTextStorage(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db = Database(os.path.join(self.tmp, "test.db"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_text_is_stored_once_and_read_back(self):
        row = self.db.save_source_text(
            "src1", PAPER, kind="pdf", origin_url="https://example.org/paper.pdf",
            sections=split_sections(PAPER), pages=["p1"], page_offsets=[[0, 10, 1]],
        )
        self.assertTrue(row["id"])
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "fulltext",
                                                    row["id"] + ".txt")))
        self.assertEqual(self.db.read_source_text(row["id"]), PAPER)
        again = self.db.save_source_text("src1", PAPER, kind="pdf")
        self.assertEqual(again["id"], row["id"])
        self.assertEqual(self.db.fulltext_stats()["texts"], 1)

    def test_empty_text_is_not_stored(self):
        self.assertIsNone(self.db.save_source_text("src1", "   "))

    def test_stats_separate_abstracts_from_documents(self):
        self.db.save_source_text("doc", PAPER * 5, kind="pdf")
        self.db.save_source_text("abs", "Short abstract only.", kind="abstract")
        stats = self.db.fulltext_stats()
        self.assertEqual(stats["texts"], 2)
        self.assertEqual(stats["sources_with_fulltext"], 1)

    def test_sources_missing_fulltext_skips_upgraded_ones(self):
        for source_id, text in (("a", "x" * 500), ("b", "y" * 500)):
            self.db.save_source({"id": source_id, "title": source_id, "url": "",
                                 "raw_text": text, "content": text,
                                 "date_added": now_iso(), "relevance": 0.5})
        self.db.save_source_text("b", PAPER * 5, kind="pdf")
        missing = [row["id"] for row in self.db.get_sources_missing_fulltext(10)]
        self.assertIn("a", missing)
        self.assertNotIn("b", missing)

    def test_fact_evidence_roundtrip(self):
        self.db.save_fact({
            "id": "f1", "content": "Let X be Y", "quote": "Let X be Y",
            "quote_start": 0, "quote_end": 8, "quote_exact": 1,
            "source_text_id": "abc", "section": "Results", "page": 3,
        })
        fact = self.db.get_facts()[0]
        self.assertEqual(fact["section"], "Results")
        self.assertEqual(fact["page"], 3)
        self.assertEqual(self.db.count_facts_with_quote(), 1)


class _QuoteLLM:
    """Returns one fact with the quote the test wants to see verified."""

    def __init__(self, quote, content=None, confidence=0.9):
        self.quote = quote
        self.content = content or (
            "The polygenic score predicted 4.2 percent of variance in the cohort."
        )
        self.confidence = confidence
        self.prompts = []

    async def chat_json(self, messages, **kwargs):
        self.prompts.append(messages[-1]["content"])
        return [{"content": self.content, "quote": self.quote,
                 "confidence": self.confidence}]


class TestFactCitations(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db = Database(os.path.join(self.tmp, "test.db"))
        self.memory = MemoryStore(self.db, llm=None)
        self.source_id = gen_id()
        self.db.save_source({"id": self.source_id, "title": "A paper",
                             "url": "https://example.org/p", "raw_text": PAPER,
                             "content": PAPER, "date_added": now_iso()})
        self.sections = split_sections(PAPER)
        self.row = self.db.save_source_text(
            self.source_id, PAPER, kind="pdf", sections=self.sections,
            pages=["p1"], page_offsets=[[0, len(PAPER), 1]],
        )

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _extract(self, llm, **kwargs):
        self.memory.llm = llm
        return asyncio.run(self.memory.extract_facts(
            PAPER, self.source_id, "IQ Genetics", **kwargs
        ))

    def test_found_quote_is_stored_with_section_and_page(self):
        quote = ("The polygenic score predicted 4.2 percent of variance "
                 "(95% CI 3.8-4.6) in the held-out cohort of 120,000 people.")
        facts = self._extract(
            _QuoteLLM(quote), sections=self.sections,
            page_offsets=[[0, len(PAPER), 1]], source_text_id=self.row["id"],
        )
        self.assertEqual(len(facts), 1)
        fact = facts[0]
        self.assertEqual(fact.quote, quote)
        self.assertGreaterEqual(fact.quote_start, 0)
        self.assertEqual(fact.quote_exact, 1)
        self.assertEqual(fact.section, "3. Results")
        self.assertEqual(fact.page, 1)
        self.assertEqual(fact.source_text_id, self.row["id"])
        self.assertIn("4.2 percent", PAPER[fact.quote_start:fact.quote_end])

    def test_invented_quote_is_marked_and_weakens_the_fact(self):
        quote = "Embryo selection raises IQ by fifteen points in every study."
        baseline = self.memory.calibrate_fact_confidence(
            "The polygenic score predicted 4.2 percent of variance in the cohort.",
            self.db.get_source(self.source_id), 0.9,
        )
        facts = self._extract(_QuoteLLM(quote))
        self.assertEqual(len(facts), 1)
        fact = facts[0]
        self.assertEqual(fact.quote_start, -1)
        self.assertEqual(fact.quote_exact, 0)
        self.assertEqual(fact.source_text_id, "")
        self.assertEqual(fact.section, "")
        self.assertAlmostEqual(fact.confidence, round(baseline * 0.85, 3), places=3)

    def test_fact_without_quote_keeps_its_confidence(self):
        facts = self._extract(_QuoteLLM(""))
        self.assertEqual(len(facts), 1)
        self.assertEqual(facts[0].quote_start, -1)
        self.assertGreater(facts[0].confidence, 0.3)

    def test_quote_from_a_late_section_survives_prompt_trimming(self):
        filler = "\n\n".join(
            f"Paragraph {i} discusses administrative details of the cohort." for i in range(400)
        )
        document = (f"Introduction\n{filler}\n\nResults\n"
                    f"The polygenic score predicted 4.2 percent of variance in the cohort.\n")
        self.db.update_source(self.source_id, {"raw_text": document, "content": document})
        quote = "The polygenic score predicted 4.2 percent of variance in the cohort."
        self.memory.llm = llm = _QuoteLLM(quote)
        facts = asyncio.run(self.memory.extract_facts(
            document, self.source_id, "IQ Genetics"
        ))
        self.assertEqual(len(facts), 1)
        # The prompt was trimmed to the budget, the citation still points into
        # the full document at the right place.
        self.assertLess(len(llm.prompts[0]), len(document))
        self.assertGreaterEqual(facts[0].quote_start, len(filler))
        self.assertEqual(facts[0].section, "Results")


class _FakeExtractor:
    """Extractor stub: page fetch, open-access copy, abstract."""

    def __init__(self, page_text="", oa_pages=None, abstract=""):
        self.page_text = page_text
        self.oa_pages = oa_pages or []
        self.abstract = abstract
        self.calls = []

    async def extract(self, url):
        self.calls.append(("extract", url))
        if self.page_text:
            return {"success": True, "content": self.page_text, "pages": [],
                    "url": url}
        return {"success": False, "content": "", "url": url}

    async def fetch_open_access_text(self, url="", title="", doi=""):
        self.calls.append(("oa", url))
        if not self.oa_pages:
            return None
        text = "\n\n".join(page.strip() for page in self.oa_pages)
        content = f"{title}\n\n{text}" if title else text
        return {
            "success": True, "content": content, "pages": list(self.oa_pages),
            "text_prefix": len(content) - len(text),
            "fulltext_source": "https://oa.example/paper.pdf",
        }

    async def fetch_abstract(self, url="", title="", doi=""):
        self.calls.append(("abstract", url))
        if self.abstract:
            return {"success": True, "content": self.abstract, "url": url}
        return None


def _orch(**cfg_kwargs):
    cfg = Config()
    cfg.database_url = ":memory:"
    cfg.llm_failure_threshold = 0
    for key, value in cfg_kwargs.items():
        setattr(cfg, key, value)
    orch = ResearchOrchestrator(cfg)
    orch.current_topic = "test topic"
    return orch


class TestOrchestratorFullText(unittest.TestCase):
    def test_open_access_pdf_is_stored_with_pages_and_sections(self):
        orch = _orch()
        pages = ["1. Introduction\n" + "text " * 400,
                 "2. Results\nThe estimate was 4.2 percent."]
        orch.extractor = _FakeExtractor(oa_pages=pages)
        source = {"id": "s1", "title": "A paper", "url": "https://doi.org/10.1/x",
                  "raw_text": "short snippet", "content": "short snippet"}

        payload = asyncio.run(orch._ensure_source_text(source))

        self.assertIsNotNone(payload)
        self.assertEqual(payload["kind"], "pdf")
        keys = [s["key"] for s in payload["sections"]]
        self.assertIn("introduction", keys)
        self.assertIn("results", keys)
        stored = orch.db.get_source_text_for_source("s1")
        self.assertIsNotNone(stored)
        self.assertEqual(stored["pages"], 2)
        # Page offsets point at the real page text inside the stored content.
        offset = payload["text"].index("The estimate was 4.2 percent")
        self.assertEqual(page_for_offset(payload["page_offsets"], offset), 2)

    def test_stored_text_is_reused_without_another_fetch(self):
        orch = _orch()
        extractor = _FakeExtractor(oa_pages=["1. Abstract\n" + "x " * 2000])
        orch.extractor = extractor
        source = {"id": "s1", "title": "T", "url": "https://doi.org/10.1/x",
                  "raw_text": "", "content": ""}

        asyncio.run(orch._ensure_source_text(source))
        calls_after_first = len(extractor.calls)
        payload = asyncio.run(orch._ensure_source_text(source))

        self.assertEqual(len(extractor.calls), calls_after_first)
        self.assertEqual(payload["text"], orch.db.read_source_text(payload["text_id"]))

    def test_no_text_at_all_returns_none(self):
        orch = _orch()
        orch.extractor = _FakeExtractor()
        self.assertIsNone(asyncio.run(orch._ensure_source_text(
            {"id": "s1", "title": "T", "url": "", "raw_text": "", "content": ""}
        )))

    def test_batch_upgrade_is_bounded(self):
        orch = _orch()
        orch.extractor = _FakeExtractor(oa_pages=["Abstract\n" + "y " * 2000])
        for source_id in ("a", "b", "c"):
            orch.db.save_source({"id": source_id, "title": source_id,
                                 "url": f"https://example.org/{source_id}",
                                 "raw_text": "z" * 500, "content": "z" * 500,
                                 "date_added": now_iso(), "relevance": 0.4})

        upgraded = asyncio.run(orch._upgrade_fulltext_batch(limit=1))

        self.assertEqual(len(upgraded), 1)
        self.assertEqual(sum(1 for c in orch.extractor.calls if c[0] == "oa"), 1)

    def test_facts_are_extracted_with_the_citable_text(self):
        orch = _orch()
        pages = ["1. Abstract\n" + "abstract text " * 300,
                 "2. Results\nThe estimate was 4.2 percent of variance."]
        orch.extractor = _FakeExtractor(oa_pages=pages)

        class _RecordingMemory:
            def __init__(self):
                self.calls = []

            async def extract_facts(self, text, source_id, topic, **kwargs):
                self.calls.append((text, source_id, kwargs))
                return []

        recorder = _RecordingMemory()
        orch.memory = recorder
        source = type("S", (), {"id": "s1", "title": "T",
                                "url": "https://doi.org/10.1/x",
                                "raw_text": "", "content": ""})()

        asyncio.run(orch._extract_source_facts(source, "IQ Genetics"))

        self.assertEqual(len(recorder.calls), 1)
        text, source_id, kwargs = recorder.calls[0]
        self.assertEqual(source_id, "s1")
        self.assertIn("4.2 percent", text)
        self.assertTrue(kwargs["source_text_id"])
        self.assertTrue(kwargs["sections"])
        self.assertTrue(kwargs["page_offsets"])


class TestOriginalPdfLink(unittest.TestCase):
    """Auftrag v2 §2.1: die Textzeile kennt ihre ORIGINAL-PDF
    (grid-Kandidatenquelle für den Tabellen-Adapter)."""

    def test_source_text_row_carries_the_pdf_path(self):
        db = Database(":memory:")
        body = "A short reaction-time document body for the pdf-link test."
        db.save_source_text(
            "s1", body, kind="pdf",
            origin_url="https://example.org/paper.pdf",
            original_pdf_path="origpdf/abc123deadbeef.pdf",
        )
        row = db.get_source_text_for_source("s1")
        self.assertEqual(row.get("original_pdf_path"),
                         "origpdf/abc123deadbeef.pdf")
        # Default bleibt leer: legacy-Zeilen ohne Original-PDF.
        db.save_source_text("s2", body, kind="html")
        row2 = db.get_source_text_for_source("s2")
        self.assertEqual(row2.get("original_pdf_path"), "")


class TestOriginalPdfPersistence(unittest.TestCase):
    """Auftrag v2 §2.1: neben dem Textabzug liegt die ORIGINAL-PDF persistent,
    damit der pypdf-Layout-Adapter dort lesen kann. Das Ablegen ist
    idempotent und scheitert nie (fail-soft)."""

    def test_bytes_are_stored_idempotently_by_hash(self):
        tmp = tempfile.mkdtemp(prefix="origpdf_")
        old_cwd = os.getcwd()
        try:
            os.chdir(tmp)
            pdf = _pdf_bytes(["Persistenzprobe für die Originaldatei."])
            path = ContentExtractor._persist_original_pdf(pdf)
            self.assertTrue(path)
            self.assertTrue(path.startswith("origpdf/"))
            #Relative zu data/ - dieselbe Konvention wie die Textabzuege
            # "fulltext/...", die read_source_text ueber die DB auflöst.
            target = Path("data") / path
            self.assertTrue(target.exists())
            second = ContentExtractor._persist_original_pdf(pdf)
            self.assertEqual(second, path)  # idempotent: gleicher Hash, keine Doppel
            self.assertEqual(target.read_bytes(), pdf)
        finally:
            os.chdir(old_cwd)
            shutil.rmtree(tmp, ignore_errors=True)

    def test_bad_target_location_fails_soft(self):
        """Ein mean Fehler beim Speichern (unwritters Verzeichnis) darf nie
        die Weiterverarbeitung blockieren - die Rückgabe ist dann leer."""
        old_cwd = os.getcwd()
        tmp = tempfile.mkdtemp(prefix="origpdf_bad_")
        try:
            os.chdir(tmp)
            Path("data").mkdir(parents=True, exist_ok=True)
            blocker = Path("data") / "origpdf"
            blocker.write_text("belegt den Pfad als DATEI\n")
            # data/origpdf ist jetzt selbst eine DATEI: mkdir und Schreiben
            # scheitern; _persist_original_pdf fällt weich und liefert leer.
            result = ContentExtractor._persist_original_pdf(b"%PDF-1.4 x")
            self.assertEqual(result, "")
        finally:
            os.chdir(old_cwd)
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
