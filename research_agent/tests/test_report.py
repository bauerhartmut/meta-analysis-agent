"""Tests for the closing report as a reviewable manuscript.

The claim under test is not "the file contains some text": it is that a reader
can check every statement. So each test asks for the thing a reviewer needs -
the question, the method with its numbers, the evidence chain per claim (quote,
section, page), the limitations counted from the database, the conditions that
would overturn a claim, and BibTeX entries with deterministic keys.
"""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.database import Database
from research_agent.report import _Bibliography, build_report


def _source(db, sid="s1", author="Doe, Jane; Roe, Richard", year="2024-03-01",
            title="Polygenic scores & variance", url="https://example.org/a_b",
            source_type="paper"):
    db.save_source({
        "id": sid, "title": title, "author": author, "publication_date": year,
        "url": url, "source_type": source_type,
        "date_added": "2026-01-01T00:00:00Z",
    })


def _quoted_fact(db, sid="s1"):
    db.save_fact({
        "id": "f1",
        "content": "Polygenic scores explain about 4 percent of the variance.",
        "confidence": 0.72, "source_ids": json.dumps([sid]),
        "quote": "PGS explain roughly 4% of the variance in EA.",
        "quote_start": 10, "quote_end": 48, "quote_exact": 1,
        "section": "Results", "page": 4,
        "date_added": "2026-01-01T00:00:00Z",
    })


class ReportTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="report_doc_")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.db = Database(":memory:")

    def build(self, topic="embryo selection"):
        path = build_report(self.db, topic, reason="budget reached", out_dir=self.tmp)
        text = Path(path).read_text(encoding="utf-8")
        bib = Path(str(path)[:-3] + ".bib").read_text(encoding="utf-8")
        return text, bib


class TestManuscriptForm(ReportTest):
    def test_has_the_sections_a_reviewer_reads_in_order(self):
        _source(self.db)
        _quoted_fact(self.db)
        text, _ = self.build()

        positions = [
            text.index("## Kurzfassung"),
            text.index("## Fragestellung"),
            text.index("## Methode"),
            text.index("## Ergebnis"),
            text.index("## Limitationen"),
            text.index("## Was würde mich umstimmen"),
            text.index("## Literatur (BibTeX)"),
        ]
        self.assertEqual(positions, sorted(positions))

    def test_method_states_what_was_done_with_which_numbers(self):
        _source(self.db)
        _quoted_fact(self.db)
        text, _ = self.build()

        self.assertIn("**Suche und Relevanzfilter:** 1 Quelle gespeichert", text)
        self.assertIn("**Extraktion:** 1 Fakt, davon 1 mit einer im Quellentext", text)
        self.assertIn("deterministisch aus der Datenbank", text)

    def test_question_section_names_the_sub_questions(self):
        self.db.save_program_item({
            "id": "p1", "topic": "embryo selection",
            "question": "How large is the polygenic score effect?",
            "kind": "measurement", "status": "open", "cycles_spent": 2,
            "opened_at": "2026-01-01T00:00:00Z",
        })
        text, _ = self.build()

        question_section = text.split("## Fragestellung")[1].split("## Methode")[0]
        self.assertIn("How large is the polygenic score effect?", question_section)


class TestEvidenceChain(ReportTest):
    def test_fact_carries_quote_section_and_page(self):
        _source(self.db)
        _quoted_fact(self.db)
        text, _ = self.build()

        self.assertIn("[doe2024]", text)
        self.assertIn("PGS explain roughly 4% of the variance in EA.", text)
        self.assertIn("Abschnitt „Results“, S. 4", text)
        self.assertIn("wörtlich im Text gefunden", text)

    def test_fact_without_passage_is_marked_not_checkable(self):
        _source(self.db)
        self.db.save_fact({
            "id": "f2", "content": "Gains are small.", "confidence": 0.5,
            "source_ids": json.dumps(["s1"]),
            "date_added": "2026-01-01T00:00:00Z",
        })
        text, _ = self.build()

        self.assertIn("keine Textstelle gespeichert", text)
        self.assertIn("nicht nachprüfbar", text)

    def test_claim_without_any_source_says_so(self):
        self.db.save_fact({
            "id": "f3", "content": "Unattributed claim.", "confidence": 0.4,
            "source_ids": "[]", "date_added": "2026-01-01T00:00:00Z",
        })
        text, _ = self.build()

        self.assertIn("keine Quelle zugeordnet", text)

    def test_hypothesis_chain_is_signed_and_counted(self):
        _source(self.db)
        self.db.save_hypothesis({
            "id": "h1", "claim": "Within-family effects are smaller.",
            "status": "supported", "confidence": 0.6,
            "date_added": "2026-01-01T00:00:00Z",
        })
        self.db.save_evidence({
            "id": "e1", "hypothesis_id": "h1", "source_id": "s1",
            "evidence_type": "supports", "content": "Sibling estimates are half",
            "strength": 0.7, "date_added": "2026-01-01T00:00:00Z",
        })
        self.db.save_evidence({
            "id": "e2", "hypothesis_id": "h1", "source_id": "s1",
            "evidence_type": "contradicts", "content": "One cohort disagrees",
            "strength": 0.3, "date_added": "2026-01-01T00:00:00Z",
        })
        text, _ = self.build()

        self.assertIn("Evidenzkette: [doe2024] +0.70 - Sibling estimates are half", text)
        self.assertIn("−0.30 - One cohort disagrees", text)

    def test_simulation_evidence_points_at_the_experiment(self):
        self.db.save_hypothesis({
            "id": "h1", "claim": "Power claim", "status": "proposed",
            "confidence": 0.4, "date_added": "2026-01-01T00:00:00Z",
        })
        self.db.save_evidence({
            "id": "e1", "hypothesis_id": "h1", "source_id": "",
            "evidence_type": "supports", "content": "simulated power 0.83",
            "strength": 0.5, "experiment_id": "exp123456",
            "date_added": "2026-01-01T00:00:00Z",
        })
        text, _ = self.build()

        self.assertIn("[exp:exp12345]", text)

    def test_verdict_carries_the_chain_of_its_material(self):
        _source(self.db)
        _quoted_fact(self.db)
        self.db.save_program_item({
            "id": "p1", "topic": "embryo selection",
            "question": "How large is the effect?", "kind": "measurement",
            "status": "done", "cycles_spent": 4,
            "verdict": json.dumps({
                "favored": "The effect is small", "confidence": 0.6,
                "material_fact_ids": ["f1", "f-gone"], "evidence_items": 1,
                "answered": True,
            }),
            "opened_at": "2026-01-01T00:00:00Z",
        })
        text, _ = self.build()

        section = text.split("### Verdikte je Teilfrage")[1]
        self.assertIn("Belege (1 Fakt des Materials)", section)
        self.assertIn("PGS explain roughly 4% of the variance in EA.", section)
        self.assertIn("Abschnitt „Results“, S. 4", section)
        self.assertIn("[doe2024]", section)
        self.assertIn("1 weiterer Material-Fakt ist nicht mehr im Bestand", section)

    def test_every_cited_fact_appears_in_the_chain(self):
        """A chain of 6 facts must not be reported as 4 facts plus 2 missing.

        The section used to show the first four and then claim the rest were no
        longer in the database - a statement about the evidence that is simply
        false, in the one place a reader goes to check the conclusion.
        """
        _source(self.db)
        ids = []
        for index in range(6):
            fact_id = f"f{index}"
            ids.append(fact_id)
            self.db.save_fact({
                "id": fact_id,
                "content": f"Finding number {index} about the effect size.",
                "confidence": 0.7, "source_ids": json.dumps(["s1"]),
                "quote": f"Quote number {index} from the paper.",
                "quote_start": index, "quote_end": index + 10, "quote_exact": 1,
                "section": "Results", "page": 4,
                "date_added": "2026-01-01T00:00:00Z",
            })
        self.db.save_program_item({
            "id": "p1", "topic": "embryo selection",
            "question": "How large is the effect?", "kind": "measurement",
            "status": "done", "cycles_spent": 4,
            "verdict": json.dumps({
                "favored": "The effect is small", "confidence": 0.6,
                "material_fact_ids": ids, "evidence_items": 6, "answered": True,
            }),
            "opened_at": "2026-01-01T00:00:00Z",
        })
        text, _ = self.build()

        section = text.split("### Verdikte je Teilfrage")[1]
        self.assertIn("Belege (6 Fakten des Materials)", section)
        for index in range(6):
            self.assertIn(f"Quote number {index} from the paper.", section)
        self.assertNotIn("nicht mehr im Bestand", section)

    def test_verdict_from_an_older_run_says_its_evidence_is_missing(self):
        self.db.save_program_item({
            "id": "p1", "topic": "embryo selection", "question": "Q",
            "kind": "empirical", "status": "done",
            "verdict": json.dumps({"favored": "X", "confidence": 0.5,
                                   "evidence_items": 3}),
            "opened_at": "2026-01-01T00:00:00Z",
        })
        text, _ = self.build()

        self.assertIn("Belege: nicht gespeichert", text)


class TestLimitationsAndDeciders(ReportTest):
    def test_limitations_are_counted_from_the_database(self):
        _source(self.db)
        _quoted_fact(self.db)
        self.db.save_fact({
            "id": "f2", "content": "Unquoted claim.", "confidence": 0.5,
            "source_ids": json.dumps(["s1"]),
            "date_added": "2026-01-01T00:00:00Z",
        })
        text, _ = self.build()

        self.assertIn("**Belegdichte:** 1 von 2 Fakten mit belegter Textstelle", text)
        self.assertIn("Eine Aussage hat keine Textstelle", text)
        self.assertIn("**Volltextabdeckung:** 0 von 1 Quellen", text)

    def test_limitations_name_budget_closes_as_effort_not_answers(self):
        self.db.save_program_item({
            "id": "p1", "topic": "embryo selection", "question": "Q1",
            "kind": "empirical", "status": "done", "cycles_spent": 8,
            "close_reason": "Zyklenbudget ausgeschöpft (8/8)",
            "opened_at": "2026-01-01T00:00:00Z",
        })
        text, _ = self.build()

        self.assertIn("**Abschluss aus Aufwandsgründen:** 1 Teilfrage wurde", text)
        self.assertIn("**Ohne Verdikt:** 1 abgeschlossene Teilfrage hat", text)

    def test_what_would_change_my_mind_uses_stored_conditions(self):
        self.db.save_hypothesis({
            "id": "h1", "claim": "Effects are small", "status": "supported",
            "confidence": 0.6,
            "falsification_conditions": json.dumps(["A sibling design shows equal effects."]),
            "date_added": "2026-01-01T00:00:00Z",
        })
        self.db.save_program_item({
            "id": "p1", "topic": "embryo selection",
            "question": "How large is the effect?", "kind": "measurement",
            "status": "done", "verdict": json.dumps({
                "favored": "The effect is small", "confidence": 0.6,
                "discriminating_test": "sibling design", "answered": True,
            }),
            "opened_at": "2026-01-01T00:00:00Z",
        })
        text, _ = self.build()

        section = text.split("## Was würde mich umstimmen")[1].split("## Offene Fragen")[0]
        self.assertIn("A sibling design shows equal effects.", section)
        self.assertIn("würde gegen „The effect is small“ entscheiden", section)

    def test_without_conditions_the_gap_is_stated(self):
        _source(self.db)
        self.db.save_hypothesis({
            "id": "h1", "claim": "Bare claim", "status": "proposed",
            "confidence": 0.3, "date_added": "2026-01-01T00:00:00Z",
        })
        text, _ = self.build()

        self.assertIn("Keine Falsifikationsbedingung gespeichert", text)


class TestBibliography(ReportTest):
    def test_report_contains_bibtex_and_writes_the_bib_file(self):
        _source(self.db)
        _quoted_fact(self.db)
        text, bib = self.build()

        self.assertIn("```bibtex", text)
        self.assertIn("@misc{doe2024", text)
        self.assertIn("@misc{doe2024", bib)
        self.assertIn("author = {Doe, Jane; Roe, Richard}", bib)
        self.assertIn("year = {2024}", bib)
        # The file is written next to the report, not somewhere else.
        self.assertTrue(bib.startswith("@misc"))

    def test_special_characters_are_escaped(self):
        _source(self.db)
        _quoted_fact(self.db)
        _, bib = self.build()

        self.assertIn("Polygenic scores \\& variance", bib)
        self.assertIn("example.org/a\\_b", bib)
        # A raw ampersand would end the field's brace group in BibTeX.
        title_line = [line for line in bib.splitlines() if "title =" in line][0]
        self.assertNotIn(" & ", title_line)

    def test_keys_are_surname_year_and_disambiguated(self):
        for sid, author in (("s1", "Doe, Jane"), ("s2", "Doe, John")):
            _source(self.db, sid=sid, author=author, title=f"Paper {sid}")
            self.db.save_fact({
                "id": f"f-{sid}", "content": f"Claim {sid}", "confidence": 0.5,
                "source_ids": json.dumps([sid]),
                "date_added": "2026-01-01T00:00:00Z",
            })
        text, _ = self.build()

        self.assertIn("[doe2024]", text)
        self.assertIn("[doe2024a]", text)

    def test_missing_source_stays_visible(self):
        self.db.save_fact({
            "id": "f1", "content": "Orphan claim", "confidence": 0.5,
            "source_ids": json.dumps(["ghost-id"]),
            "date_added": "2026-01-01T00:00:00Z",
        })
        text, bib = self.build()

        self.assertIn("[fehltghostid]", text)
        self.assertIn("Quelle nicht im Bestand", bib)

    def test_uncited_report_has_no_bibliography_entries(self):
        text, bib = self.build()

        self.assertIn("_Keine Quelle zitiert._", text)
        self.assertEqual(bib, "")

    def test_bibliography_class_is_deterministic(self):
        _source(self.db)
        first = _Bibliography(self.db)
        second = _Bibliography(self.db)
        self.assertEqual(first.key("s1"), second.key("s1"))
        self.assertEqual(first.cite("s1"), "[doe2024]")
        self.assertEqual(first.entry("doe2024"), second.entry("doe2024"))


if __name__ == "__main__":
    unittest.main()
