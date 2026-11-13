#!/usr/bin/env python3
"""Build a fulltext review and arm-value template for the 36 P0 includes.

Only reads existing screening/sign-off artifacts. No model, no network, no
fulltext retrieval. Empty values mean "not reported"; nothing is estimated.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "evaluation" / "c1_pilot"
OUT = PILOT / "holdout_p0_20261112"
SIGNOFF = OUT / "manual_review_signoff_v1.json"
MANUAL = OUT / "manual_review_decisions_v1.jsonl"
JSON_PATH = OUT / "fulltext_extraction_template_v1.json"
CSV_PATH = OUT / "fulltext_extraction_template_v1.csv"
MD_PATH = OUT / "fulltext_extraction_template_v1.md"
MANIFEST = OUT / "fulltext_retrieval_manifest_v1.json"
OUTCOME_SLOTS = 4


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def blank_arm() -> dict:
    return {
        "n_analyzed": None,
        "mean": None,
        "sd": None,
        "mean_change": None,
        "sd_change": None,
        "se": None,
        "ci_low": None,
        "ci_high": None,
        "events": None,
        "total": None,
    }


def blank_outcome(slot: int) -> dict:
    return {
        "slot": slot,
        "outcome_verbatim": "",
        "outcome_normalized": "",
        "outcome_type": "",
        "unit": "",
        "time_point": "",
        "planned_effect_type": "",
        "intervention": blank_arm(),
        "control": blank_arm(),
        "source_locator": "",
        "source_quote": "",
        "notes": "",
    }


def blank_study() -> dict:
    return {
        "design_verbatim": "",
        "design_category": "",
        "trial_name": "",
        "randomization_ratio": "",
        "intervention_label": "",
        "control_label": "",
        "n_randomized_intervention": None,
        "n_randomized_control": None,
        "n_analyzed_intervention": None,
        "n_analyzed_control": None,
        "analysis_population": "",
        "follow_up": "",
        "source_locator": "",
        "source_quote": "",
    }


def main() -> None:
    signoff = json.loads(SIGNOFF.read_text(encoding="utf-8"))
    manual = {row["pmcid"]: row for row in read_jsonl(MANUAL)}
    includes = [row for row in signoff["rows"] if row["decision"] == "include_for_fulltext"]
    if len(includes) != 36:
        raise SystemExit(f"expected 36 includes, got {len(includes)}")
    if set(manual) != {row["pmcid"] for row in signoff["rows"]}:
        raise SystemExit("manual decisions and sign-off list do not contain the same PMCIDs")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {"records": []}
    retrieved = {row["pmcid"]: row for row in manifest.get("records", []) if row.get("saved")}

    articles = []
    for number, row in enumerate(includes, 1):
        local = retrieved.get(row["pmcid"])
        articles.append(
            {
                "article_number": number,
                "pmcid": row["pmcid"],
                "pmid": manual[row["pmcid"]].get("pmid", ""),
                "doi": row["doi"],
                "source_url": row["source_url"],
                "title": row["title"],
                "journal": row["journal"],
                "pub_year": row["pub_year"],
                "priority": row["priority"],
                "open_question": row["open_question"],
                "reason_code": row["reason_code"],
                "screening_decision": "include_for_fulltext",
                "fulltext_available": bool(local),
                "fulltext_local_path": local["local_path"] if local else "",
                "fulltext_sha256": local["sha256"] if local else "",
                "fulltext_bytes": local["bytes"] if local else None,
                "fulltext_retrieved_at": manifest.get("started_at", "") if local else "",
                "reviewer": "offen",
                "review_date": "offen",
                "final_decision": "offen",
                "eligibility": {
                    "parallel_two_arm_rct_confirmed": None,
                    "randomization_confirmed": None,
                    "no_arm_collapse": None,
                    "arm_sizes_reported": None,
                    "outcome_data_extractable": None,
                    "notes": "",
                },
                "study": blank_study(),
                "outcomes": [blank_outcome(slot) for slot in range(1, OUTCOME_SLOTS + 1)],
                "notes": "",
            }
        )

    payload = {
        "template_id": "p0_fulltext_extraction_v1",
        "created_at": "2026-11-12",
        "status": "pending_fulltext_review",
        "records": len(articles),
        "model_used": False,
        "fulltext_retrieved": len(retrieved) == len(articles),
        "fulltext_retrieved_scope": "all_36",
        "fulltext_available_count": len(retrieved),
        "fulltext_retrieval_status": "partial_shortlist_30_of_36" if retrieved else "not_started",
        "fulltext_retrieval_manifest": str(MANIFEST.relative_to(ROOT)).replace("\\", "/") if MANIFEST.exists() else "",
        "instructions": {
            "scope": "36 vorlaeufige Einschluesse aus dem konsolidierten Abstract-Screening v2.",
            "no_estimation": "Nur berichtete Werte eintragen; keine Schaetzung, Imputation oder Umrechnung.",
            "no_arm_collapse": "Keine getrennten Arme zusammenfassen; genau zwei parallele Arme bestaetigen.",
            "continuous_fields": "N, Mean, SD; bei Veraenderungswerten Mean change und SD change. SE/CI nur woertlich, nicht in SD umrechnen.",
            "binary_fields": "Events und Total pro Arm; keine Ereigniszahlen aus Prozentwerten rekonstruieren.",
            "quote": "Exakte Belegstelle mit Tabelle/Seite und woertlichem Zitat; keine Paraphrase.",
            "final_decision": "einschluss, ausschluss oder offen; erst nach Reviewer-Eintrag gueltig.",
        },
        "articles": articles,
    }
    JSON_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    fieldnames = [
        "article_number",
        "pmcid",
        "pmid",
        "doi",
        "source_url",
        "title",
        "journal",
        "pub_year",
        "priority",
        "open_question",
        "fulltext_available",
        "fulltext_local_path",
        "fulltext_sha256",
        "fulltext_bytes",
        "fulltext_retrieved_at",
        "reviewer",
        "review_date",
        "final_decision",
        "design_verbatim",
        "design_category",
        "trial_name",
        "randomization_ratio",
        "intervention_label",
        "control_label",
        "n_randomized_intervention",
        "n_randomized_control",
        "n_analyzed_intervention",
        "n_analyzed_control",
        "analysis_population",
        "follow_up",
        "outcome_slot",
        "arm_role",
        "arm_label",
        "outcome_verbatim",
        "outcome_normalized",
        "outcome_type",
        "unit",
        "time_point",
        "planned_effect_type",
        "n_analyzed",
        "mean",
        "sd",
        "mean_change",
        "sd_change",
        "se",
        "ci_low",
        "ci_high",
        "events",
        "total",
        "source_locator",
        "source_quote",
        "notes",
    ]
    with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for article in articles:
            study = article["study"]
            for outcome in article["outcomes"]:
                for role, label, values in (
                    ("intervention", "Intervention", outcome["intervention"]),
                    ("control", "Kontrolle", outcome["control"]),
                ):
                    writer.writerow(
                        {
                            "article_number": article["article_number"],
                            "pmcid": article["pmcid"],
                            "pmid": article["pmid"],
                            "doi": article["doi"],
                            "source_url": article["source_url"],
                            "title": article["title"],
                            "journal": article["journal"],
                            "pub_year": article["pub_year"],
                            "priority": article["priority"],
                            "open_question": article["open_question"],
                            "fulltext_available": article["fulltext_available"],
                            "fulltext_local_path": article["fulltext_local_path"],
                            "fulltext_sha256": article["fulltext_sha256"],
                            "fulltext_bytes": article["fulltext_bytes"],
                            "fulltext_retrieved_at": article["fulltext_retrieved_at"],
                            "reviewer": article["reviewer"],
                            "review_date": article["review_date"],
                            "final_decision": article["final_decision"],
                            "design_verbatim": study["design_verbatim"],
                            "design_category": study["design_category"],
                            "trial_name": study["trial_name"],
                            "randomization_ratio": study["randomization_ratio"],
                            "intervention_label": study["intervention_label"],
                            "control_label": study["control_label"],
                            "n_randomized_intervention": study["n_randomized_intervention"],
                            "n_randomized_control": study["n_randomized_control"],
                            "n_analyzed_intervention": study["n_analyzed_intervention"],
                            "n_analyzed_control": study["n_analyzed_control"],
                            "analysis_population": study["analysis_population"],
                            "follow_up": study["follow_up"],
                            "outcome_slot": outcome["slot"],
                            "arm_role": role,
                            "arm_label": label,
                            "outcome_verbatim": outcome["outcome_verbatim"],
                            "outcome_normalized": outcome["outcome_normalized"],
                            "outcome_type": outcome["outcome_type"],
                            "unit": outcome["unit"],
                            "time_point": outcome["time_point"],
                            "planned_effect_type": outcome["planned_effect_type"],
                            "n_analyzed": values["n_analyzed"],
                            "mean": values["mean"],
                            "sd": values["sd"],
                            "mean_change": values["mean_change"],
                            "sd_change": values["sd_change"],
                            "se": values["se"],
                            "ci_low": values["ci_low"],
                            "ci_high": values["ci_high"],
                            "events": values["events"],
                            "total": values["total"],
                            "source_locator": outcome["source_locator"],
                            "source_quote": outcome["source_quote"],
                            "notes": outcome["notes"],
                        }
                    )

    lines = [
        "# Volltext-Prüfvorlage: 36 vorläufige P0-Einschlüsse",
        "",
        "Stand: 2026-11-13",
        f"Status: **VOLLTEXT-PRÜFUNG OFFEN**; {len(retrieved)}/{len(articles)} XML lokal verfügbar; "
        "sechs Reservefälle nicht abgerufen; kein Gate-Pass, keine endgültige Holdout-Auswahl.",
        "",
        "## Regeln",
        "",
        "- Genau zwei parallele Arme bestätigen; keine Armzusammenführung.",
        "- Nur berichtete Werte eintragen. Fehlende Werte bleiben leer.",
        "- Keine Schätzung, keine Imputation, keine Umrechnung von SE/CI in SD.",
        "- Kontinuierlich: N, Mean, SD; bei Veränderung zusätzlich Mean change und SD change.",
        "- Binär: Events und Total pro Arm; keine Rekonstruktion aus Prozentwerten.",
        "- Beleg mit Tabelle/Seite und wörtlichem Zitat; keine Paraphrase.",
        "- Reviewer, Datum und finale Entscheidung setzen: `einschluss`, `ausschluss` oder `offen`.",
        "",
        f"Die maschinenlesbare Langform steht in `{CSV_PATH.name}`: pro Artikel",
        f"{OUTCOME_SLOTS} Outcome-Slots mit je einer Interventions- und Kontrollzeile.",
        "",
    ]

    for article in articles:
        lines.extend(
            [
                f"## {article['article_number']}. {article['pmcid']} — {article['title']}",
                "",
                f"- Quelle: [{article['pmcid']}]({article['source_url']}) · DOI `{article['doi']}`",
                f"- Lokal: `{article['fulltext_local_path']}` · SHA-256 `{article['fulltext_sha256']}` · "
                f"{article['fulltext_bytes']} Bytes"
                if article["fulltext_available"]
                else "- Lokal: nicht abgerufen (Reservefall)",
                f"- Journal/Jahr: {article['journal']} ({article['pub_year']})",
                f"- Screening: vorläufiger Einschluss ({article['reason_code']}); Priorität **{article['priority']}**",
                f"- Offener Zweifel: {article['open_question']}",
                f"- Reviewer: **{article['reviewer']}** · Datum: **{article['review_date']}** · "
                f"Finale Entscheidung: **{article['final_decision']}**",
                "",
                "### Eignung am Volltext",
                "",
                "- [ ] randomisierter Parallelvergleich",
                "- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme",
                "- [ ] Arm-N bzw. analysierte N pro Arm berichtet",
                "- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total",
                "- [ ] Outcome, Einheit und Zeitpunkt eindeutig",
                "",
                "### Studien- und Armdefinition",
                "",
                "| Feld | Eintrag |",
                "|---|---|",
                "| Design (wörtlich) | |",
                "| Design-Kategorie | |",
                "| Trial-/Studienname | |",
                "| Randomisierungsverhältnis | |",
                "| Interventionsarm (Label) | |",
                "| Kontrollarm (Label) | |",
                "| N randomisiert (Intervention / Kontrolle) | / |",
                "| N analysiert (Intervention / Kontrolle) | / |",
                "| Analysepopulation | |",
                "| Follow-up / Zeitpunkte | |",
                "| Beleg (Tabelle/Seite) | |",
                "| Zitat | |",
                "",
                "### Outcome-Definitionen",
                "",
                "| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |",
                "|---:|---|---|---|---|---|",
            ]
        )
        for outcome in article["outcomes"]:
            lines.append(
                f"| {outcome['slot']} | | cont/bin | | | md/smd/or/rr |"
            )
        lines.extend(
            [
                "",
                "### Armwerte",
                "",
                "| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |",
                "|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|",
            ]
        )
        for outcome in article["outcomes"]:
            lines.append(
                f"| {outcome['slot']} | Intervention | | | | | | | | | | |"
            )
            lines.append(
                f"| {outcome['slot']} | Kontrolle | | | | | | | | | | |"
            )
        lines.extend(
            [
                "",
                "Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):",
                "",
                "- Slot 1:",
                "- Slot 2:",
                "- Slot 3:",
                "- Slot 4:",
                "",
                "### Abschluss",
                "",
                "- [ ] alle berichteten Armwerte eingetragen",
                "- [ ] keine Schätzung/Umrechnung/Armzusammenführung",
                "- [ ] finale Entscheidung gesetzt und begründet",
                "",
                "---",
                "",
            ]
        )

    lines.extend(
        [
            "## Legende",
            "",
            "- **cont**: kontinuierliches Outcome; **bin**: binäres Outcome.",
            "- **md**: Mittelwertsdifferenz; **smd**: standardisierte Differenz; **or/rr**: Odds-/Risk Ratio.",
            "- **Mean change/SD change**: nur wenn als Veränderung berichtet; nicht aus Baseline und Follow-up schätzen.",
            "- **SE/95%-CI**: nur wörtlich übernehmen; keine Umrechnung in SD.",
            "- **Beleg**: Tabelle/Abbildung/Seite plus wörtliches Zitat; keine Paraphrase.",
            "",
            "Kein Modelllauf; 30 Shortlist-XML abgerufen, keine PDFs, keine Testwiederverwendung.",
            "",
        ]
    )
    MD_PATH.write_text("\n".join(lines), encoding="utf-8")

    print(
        json.dumps(
            {
                "articles": len(articles),
                "csv_rows": len(articles) * OUTCOME_SLOTS * 2,
                "outcome_slots": OUTCOME_SLOTS,
                "status": "pending_fulltext_review",
                "fulltext_available_count": len(retrieved),
                "model_used": False,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
