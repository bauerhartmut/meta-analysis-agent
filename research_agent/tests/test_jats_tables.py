"""Tests für den JATS-Tabellenleser (Implementierungsplan T4, Stufe 1)."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.research.jats_tables import parse_jats, stat_rich_candidates

JATS = """<?xml version="1.0" encoding="utf-8"?>
<article xmlns:xlink="http://www.w3.org/1999/xlink">
<front><article-meta>
<article-id pub-id-type="doi">10.9999/jats-test</article-id>
<article-id pub-id-type="pmid">12345678</article-id>
<title-markup/>
</article-meta></front>
<body>
<sec><title>Results</title><p>Overall effect (95% CI 0.20-0.40) across groups.</p></sec>
<table-wrap id="t1"><label>Table 1</label><caption>Sleep onset latency by arm
(PE, SE, and 95% CI; taxonomy; supplementary Table S1 lists items).</caption>
<table>
<thead><tr><th>Outcome</th><th>Melatonin</th><th>Placebo</th>
<th>WMD (95% CI)</th><th>SE</th><th>N</th></tr></thead>
<tbody>
<tr><td>Sleep onset latency (min)</td><td>38.2</td><td>45.1</td>
<td>-6.90 (9.1 to -4.7)</td><td>1.11</td><td>N = 120</td></tr>
<tr><td>Sleep quality (score)</td><td>7.4 (SD 1.2)</td><td>7.1 (SD 1.3)</td>
<td>0.30</td><td>0.11</td><td>N = 98</td></tr>
<tr><td>Author note</td></tr>
<tr><td>Adverse events (%)</td><td>12.4</td><td>11.0</td><td>1.4</td><td>1.0</td><td>N = 218</td></tr>
</tbody>
</table></table-wrap>
<table-wrap id="t2"><label>Table 2</label><caption>No data table; see figure.</caption>
<fig id="f1"><label>Fig 1</label></fig>
</table-wrap>
</body></article>
"""


class JatsTablesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="jats_")
        self.path = Path(self.tmp) / "in.xml"
        self.path.write_text(JATS, encoding="utf-8")
        self.tables = parse_jats(self.path)

    def test_finds_one_structured_table(self):
        self.assertEqual(len(self.tables), 1)
        self.assertEqual(self.tables[0].label, "Table 1")
        self.assertIn("Sleep onset latency", self.tables[0].caption)

    def test_header_and_rows_split(self):
        t = self.tables[0]
        self.assertEqual(t.header[0], "Outcome")
        self.assertEqual(len(t.rows), 4)
        self.assertEqual(t.rows[0].cells[0], "Sleep onset latency (min)")

    def test_stat_rich_rows_keep_origin(self):
        rich = self.tables[0].stat_rich_rows
        self.assertEqual(len(rich), 3)
        # Zeile 1: CI-Zelle + SE-Spalte im Header.
        self.assertTrue(rich[0].has_ci)
        self.assertTrue(rich[0].has_se)
        self.assertTrue(rich[0].has_n)
        self.assertFalse(rich[0].cells[0].isdigit())
        # 'Adverse events' erbt die Header-Rollen der Zellspalten.
        self.assertTrue(rich[2].has_se)
        self.assertTrue(rich[2].has_ci)

    def test_sd_plus_n_row_is_candidate_without_ci(self):
        # Zeile 2 qualifiziert über SD+N+Zahlen, nicht über eine CI-Zelle;
        # die Header-Semantik (CI/SE-Spalte) überträgt die Rollen auf die
        # numerischen Zellen, deshalb ist has_ci hier nicht der Auslöser.
        rich = self.tables[0].stat_rich_rows
        row2 = rich[1]
        self.assertTrue(row2.has_sd)
        self.assertTrue(row2.has_n)

    def test_candidates_expose_table_label_and_cells(self):
        cands = stat_rich_candidates(self.path)
        self.assertTrue(all(c["table_label"] == "Table 1" for c in cands))
        self.assertEqual(len(cands), 3)

    def test_rows_without_stats_stay_outside_the_candidates(self):
        # 'Author note' (1 Zelle, keine Statistik) ist nie Kandidat.
        cands = stat_rich_candidates(self.path)
        self.assertTrue(all("Author note" not in c["cells"] for c in cands))


TWO_HEADER_ROWS = """<?xml version="1.0" encoding="utf-8"?>
<article><body><table-wrap id="t9"><label>Table 2</label>
<caption>Sleep outcomes by arm.</caption><table>
<thead>
<tr><th>Table 2 Sleep outcomes</th></tr>
<tr><th rowspan="2">Outcome</th><th colspan="2">Treatment</th>
<th colspan="2">Placebo</th><th rowspan="2">Hedges g (95% CI)</th></tr>
<tr><th>Mean</th><th>SD</th><th>Mean</th><th>SD</th></tr>
</thead>
<tbody>
<tr><td>Sleep onset latency</td><td>38.2</td><td>4.1</td><td>45.1</td><td>4.7</td>
<td>-0.22 (-0.32 to -0.17)</td></tr>
<tr><td>Sleep efficiency</td><td colspan="2">88.0 (4.2)</td><td>85.1</td><td>3.9</td>
<td>0.11 (-0.02 to 0.24)</td></tr>
</tbody></table></table-wrap></body></article>
"""


class TwoHeaderRowsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="jats_two_")
        self.path = Path(self.tmp) / "in.xml"
        self.path.write_text(TWO_HEADER_ROWS, encoding="utf-8")
        self.table = parse_jats(self.path)[0]

    def test_both_header_rows_are_composed_per_column(self):
        self.assertEqual(self.table.header, [
            "Outcome", "Treatment Mean", "Treatment SD",
            "Placebo Mean", "Placebo SD", "Hedges g (95% CI)",
        ])

    def test_title_row_does_not_become_a_column_name(self):
        self.assertNotIn("Table 2 Sleep outcomes", " | ".join(self.table.header))

    def test_data_rows_are_not_part_of_the_header(self):
        self.assertEqual(len(self.table.rows), 2)
        self.assertEqual(self.table.rows[0].cells[0], "Sleep onset latency")

    def test_first_row_has_as_many_cells_as_the_header(self):
        self.assertEqual(len(self.table.rows[0].cells), len(self.table.header))

    def test_merged_data_cell_stays_one_cell(self):
        # Eine zusammengefasste Datenzelle darf nicht verdoppelt werden.
        self.assertEqual(len(self.table.rows[1].cells), 5)
        self.assertEqual(self.table.rows[1].cells[1], "88.0 (4.2)")


ROWSPAN_GROUP = """<?xml version="1.0" encoding="utf-8"?>
<article><body><table-wrap id="t7"><label>Table 3</label>
<caption>Sleep by tertile.</caption><table>
<thead><tr><th>Diseases</th><th>Tertile</th><th>OR (95% CI)</th></tr></thead>
<tbody>
<tr><td rowspan="2">Sleep disorders</td><td>T2</td><td>0.574 (0.390-0.843)</td></tr>
<tr><td>T3</td><td>0.349 (0.242-0.502)</td></tr>
<tr><td>Depression</td><td>T2</td><td>1.100 (0.900-1.340)</td></tr>
</tbody></table></table-wrap></body></article>
"""


class RowspanGroupTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="jats_group_")
        self.path = Path(self.tmp) / "in.xml"
        self.path.write_text(ROWSPAN_GROUP, encoding="utf-8")
        self.table = parse_jats(self.path)[0]

    def test_second_row_inherits_the_group_label(self):
        self.assertEqual(self.table.rows[1].row_group, "Sleep disorders")

    def test_cells_stay_verbatim_for_the_quote(self):
        # Das geerbte Label darf die Zeile nicht aendern; sie ist ein Zitat.
        self.assertEqual(self.table.rows[1].cells, ["T3", "0.349 (0.242-0.502)"])

    def test_own_label_rows_carry_no_group(self):
        self.assertEqual(self.table.rows[0].row_group, "")
        self.assertEqual(self.table.rows[2].row_group, "")
        self.assertEqual(self.table.rows[2].cells[0], "Depression")


SECTION_ROW = """<?xml version="1.0" encoding="utf-8"?>
<article><body><table-wrap id="t8"><label>Table 4</label>
<caption>Odds ratios for daytime sleepiness by nutrient.</caption><table>
<thead><tr><th>Model</th><th>Q1 OR (95% CI)</th><th>Q2 OR (95% CI)</th></tr></thead>
<tbody>
<tr><td>Total fat</td><td></td><td></td></tr>
<tr><td>Model 1</td><td>1.00</td><td>1.32 (0.78-2.25)</td></tr>
<tr><td>Model 2</td><td>1.00</td><td>1.21 (0.69-2.12)</td></tr>
<tr><td>Saturated fat</td><td></td><td></td></tr>
<tr><td>Model 1</td><td>1.40 (1.08-1.81)</td><td>1.11 (0.94-1.31)</td></tr>
</tbody></table></table-wrap></body></article>
"""


class SectionRowTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="jats_section_")
        self.path = Path(self.tmp) / "in.xml"
        self.path.write_text(SECTION_ROW, encoding="utf-8")
        self.table = parse_jats(self.path)[0]

    def test_model_rows_inherit_the_section_label(self):
        self.assertEqual(self.table.rows[1].row_group, "Total fat")
        self.assertEqual(self.table.rows[2].row_group, "Total fat")

    def test_a_new_section_resets_the_label(self):
        self.assertEqual(self.table.rows[4].row_group, "Saturated fat")

    def test_section_row_itself_has_no_group(self):
        self.assertEqual(self.table.rows[0].row_group, "")


if __name__ == "__main__":
    unittest.main()
