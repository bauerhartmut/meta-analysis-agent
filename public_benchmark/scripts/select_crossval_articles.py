#!/usr/bin/env python3
"""Waehlt die Artikel fuer das Cross-Validation-Experiment (Schritt 1).

Deterministisch, ohne Modell, ohne Netz. Grundlage sind die vorhandenen
Screening-Entscheidungen des P0-Laufs und die G5-Reservierung.

Regeln:
- Nur Kandidaten mit ``decision == "include_for_fulltext"``.
- Kein Artikel aus G5: weder die 30 Shortlist-Artikel noch die 36 menschlich
  bestaetigten Einschluesse. G5 bleibt unberuehrt.
- Kein Artikel aus Yun (Freeze, Dev, Test); die Disjunktheit wird gegen die
  drei Dateien geprueft, nicht nur uebernommen.
- Rangfolge ueber SHA-256 aus festem Salt und PMCID: reproduzierbar und
  unabhaengig von Eingabereihenfolge.
- 25 Primaerartikel, 10 vorab bestimmte Reserveartikel.

Ausgabe:
- ``candidate_shortlist_v1.json``
- ``candidate_shortlist_v1.md``
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

BENCH_ROOT = Path(__file__).resolve().parents[1]
P0_DIR = BENCH_ROOT / "evaluation" / "c1_pilot" / "holdout_p0_20261112"
OUT_DIR = BENCH_ROOT / "evaluation" / "multi_model_cross_validation"
DATA_DIR = BENCH_ROOT / "processed_data"

DECISIONS_PATH = P0_DIR / "screening_decisions_v2.jsonl"
CANDIDATES_PATH = P0_DIR / "candidates.jsonl"
SHORTLIST_PATH = P0_DIR / "fulltext_retrieval_manifest_v1.json"
OUT_JSON = OUT_DIR / "candidate_shortlist_v1.json"
OUT_MD = OUT_DIR / "candidate_shortlist_v1.md"

SALT = "crossval-20261113-v1"
REQUIRED_PUB_TYPE = "Randomized Controlled Trial"
# Keine Zusammenfassungen, Korrekturen oder Protokolle: sie enthalten keine
# eigenen Armwerte und wuerden Annotationszeit ohne Ertrag binden.
TITLE_EXCLUDE = re.compile(
    r"^(summary of research|correction|erratum|retraction|comment|reply|response to)"
    r"|study protocol|protocol for a|protocol of a",
    re.IGNORECASE,
)
PRIMARY_COUNT = 25
RESERVE_COUNT = 10
TARGET_RECORDS = (60, 80)

YUN_FILES = {
    "yun_freeze_275": DATA_DIR / "yun_c1_frozen_275.jsonl",
    "yun_dev_26": DATA_DIR / "yun_c1_dev_26.jsonl",
    "yun_test_249": DATA_DIR / "yun_c1_test_249.jsonl",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def rank_key(pmcid: str) -> str:
    return hashlib.sha256(f"{SALT}:{pmcid}".encode("utf-8")).hexdigest()


def g5_articles() -> tuple[set[str], set[str]]:
    """G5-Mengen: Shortlist (abgerufen) und menschlich bestaetigte Einschluesse."""
    shortlist = {
        row["pmcid"]
        for row in json.loads(SHORTLIST_PATH.read_text(encoding="utf-8"))["records"]
    }
    confirmed = {
        row["pmcid"]
        for row in load_jsonl(DECISIONS_PATH)
        if row.get("screening_method") == "manual_assisted_review_v1"
        and row.get("decision") == "include_for_fulltext"
    }
    return shortlist, confirmed


def yun_articles() -> dict[str, set[str]]:
    return {
        name: {row["pmcid"] for row in load_jsonl(path)}
        for name, path in YUN_FILES.items()
    }


def select(
    decisions: list[dict[str, Any]],
    candidates: dict[str, dict[str, Any]],
    excluded: set[str],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Filtert den Kandidatenpool und sortiert ihn deterministisch.

    Die Zahlenschritte werden mitgezaehlt, damit der Ausschluss nachvollziehbar
    bleibt und nicht als stille Vorauswahl verschwindet.
    """
    screened = [
        row
        for row in decisions
        if row.get("decision") == "include_for_fulltext"
        and row["pmcid"] not in excluded
    ]
    rct = [
        row
        for row in screened
        if REQUIRED_PUB_TYPE in (candidates.get(row["pmcid"], {}).get("pub_types") or [])
    ]
    filtered = [row for row in rct if not TITLE_EXCLUDE.search(row.get("title") or "")]
    funnel = {
        "include_for_fulltext_not_g5_not_yun": len(screened),
        "with_rct_pub_type": len(rct),
        "after_title_exclusion": len(filtered),
        "title_excluded": len(rct) - len(filtered),
    }
    return sorted(filtered, key=lambda row: rank_key(row["pmcid"])), funnel


def build() -> dict[str, Any]:
    decisions = load_jsonl(DECISIONS_PATH)
    candidates = {row["pmcid"]: row for row in load_jsonl(CANDIDATES_PATH)}
    shortlist, confirmed = g5_articles()
    g5 = shortlist | confirmed
    yun = yun_articles()
    yun_all = set().union(*yun.values())

    pool, funnel = select(decisions, candidates, g5 | yun_all)
    chosen = pool[: PRIMARY_COUNT + RESERVE_COUNT]

    rows = []
    for index, row in enumerate(chosen, start=1):
        rows.append(
            {
                "position": index,
                "role": "primary" if index <= PRIMARY_COUNT else "reserve",
                "pmcid": row["pmcid"],
                "doi": row.get("doi") or "",
                "title": row.get("title") or "",
                "journal": row.get("journal") or "",
                "pub_year": row.get("pub_year") or "",
                "rank_sha256": rank_key(row["pmcid"]),
                "pub_types": candidates.get(row["pmcid"], {}).get("pub_types") or [],
                "screening_reason_codes": row.get("reason_codes") or [],
                "needs_fulltext_check": True,
                "reserved_for": "crossval_exploration",
            }
        )

    primary = [row for row in rows if row["role"] == "primary"]
    reserve = [row for row in rows if row["role"] == "reserve"]

    checks = {
        "primary_count_ok": len(primary) == PRIMARY_COUNT,
        "reserve_count_ok": len(reserve) == RESERVE_COUNT,
        "unique_pmcids": len({row["pmcid"] for row in rows}) == len(rows),
        "g5_overlap": sorted({row["pmcid"] for row in rows} & g5),
        "yun_overlap": sorted({row["pmcid"] for row in rows} & yun_all),
        "g5_excluded_count": len(g5),
        "g5_shortlist_count": len(shortlist),
        "g5_confirmed_count": len(confirmed),
        "yun_by_split": {name: len(ids) for name, ids in yun.items()},
        "eligible_pool": len(pool),
        "funnel": funnel,
    }
    checks["ok"] = (
        checks["primary_count_ok"]
        and checks["reserve_count_ok"]
        and checks["unique_pmcids"]
        and not checks["g5_overlap"]
        and not checks["yun_overlap"]
    )

    return {
        "dataset": "crossval_exploration",
        "version": "1.0",
        "created": date.today().isoformat(),
        "status": "selected_pending_fulltext_check"
        if checks["ok"]
        else "selection_failed",
        "model_used": False,
        "network_used": False,
        "salt": SALT,
        "primary_count": len(primary),
        "reserve_count": len(reserve),
        "target_records": list(TARGET_RECORDS),
        "inclusion_criteria": [
            "decision == include_for_fulltext aus dem Abstract-Screening",
            f"pub_types enthaelt {REQUIRED_PUB_TYPE}",
            "Titel ist keine Zusammenfassung, Korrektur, Ruecknahme, Kommentar oder Protokoll",
            "artikeldisjunkt zu G5 und zu Yun (Freeze, Dev, Test)",
            "Volltextpruefung bestaetigt mindestens einen Vergleich mit Armwerten",
        ],
        "target_records_note": (
            "60-80 Armwert-Records aus 25 Artikeln; die tatsaechliche Recordzahl "
            "wird nach der Volltextpruefung festgestellt, nicht geschaetzt."
        ),
        "source": {
            "decisions": str(DECISIONS_PATH.relative_to(BENCH_ROOT)).replace("\\", "/"),
            "g5_shortlist": str(SHORTLIST_PATH.relative_to(BENCH_ROOT)).replace("\\", "/"),
            "g5_policy": (
                "G5 = 30 abgerufene Shortlist-Artikel plus 36 menschlich "
                "bestaetigte Einschluesse; Reserve der G5-Auswahl bleibt "
                "ausserhalb dieses Experiments, damit G5 nie auf einen hier "
                "vergebenen Artikel zurueckgreifen muss."
            ),
        },
        "checks": checks,
        "articles": rows,
    }


def render_md(payload: dict[str, Any]) -> str:
    checks = payload["checks"]
    lines = [
        "# Cross-Validation: Artikelauswahl v1",
        "",
        f"Stand: {payload['created']}",
        f"Status: **{payload['status']}**",
        "Kein Modellaufruf, kein Netzzugriff.",
        "",
        "## Auswahlregel",
        "",
        "1. Nur Kandidaten mit `decision == include_for_fulltext`.",
        "2. Ausschluss aller G5-Artikel (30 Shortlist + 36 bestaetigte Einschluesse).",
        "3. Ausschluss aller Yun-Artikel (Freeze 275, Dev 26, Test 249).",
        f"4. Rangfolge: `sha256(\"{payload['salt']}:<PMCID>\")` aufsteigend.",
        f"5. {payload['primary_count']} Primaerartikel, {payload['reserve_count']} Reserve.",
        "",
        "## Pruefungen",
        "",
        "| Pruefung | Ergebnis |",
        "|---|---|",
        f"| Primerzahl = {PRIMARY_COUNT} | {checks['primary_count_ok']} |",
        f"| Reservezahl = {RESERVE_COUNT} | {checks['reserve_count_ok']} |",
        f"| PMCIDs eindeutig | {checks['unique_pmcids']} |",
        f"| Schnittmenge mit G5 ({checks['g5_excluded_count']} Artikel) | {checks['g5_overlap'] or 'leer'} |",
        f"| Schnittmenge mit Yun (70 Artikel) | {checks['yun_overlap'] or 'leer'} |",
        f"| Kandidatenpool nach Ausschluss | {checks['eligible_pool']} |",
        "",
        "## Auswahltrichter",
        "",
        "| Schritt | Artikel |",
        "|---|---:|",
        f"| Abstract-Freigabe, ohne G5 und ohne Yun | {checks['funnel']['include_for_fulltext_not_g5_not_yun']} |",
        f"| davon mit RCT-Publikationstyp | {checks['funnel']['with_rct_pub_type']} |",
        f"| davon ohne Zusammenfassung/Korrektur/Protokoll | {checks['funnel']['after_title_exclusion']} |",
        "",
        "## Primaerartikel",
        "",
        "| # | PMCID | Jahr | Journal | Titel |",
        "|---:|---|---|---|---|",
    ]
    for row in payload["articles"]:
        if row["role"] != "primary":
            continue
        title = row["title"].replace("|", "/")[:90]
        lines.append(
            f"| {row['position']} | {row['pmcid']} | {row['pub_year']} | "
            f"{row['journal'][:30]} | {title} |"
        )
    lines += [
        "",
        "## Reserve (vorab bestimmt)",
        "",
        "| # | PMCID | Jahr | Journal | Titel |",
        "|---:|---|---|---|---|",
    ]
    for row in payload["articles"]:
        if row["role"] != "reserve":
            continue
        title = row["title"].replace("|", "/")[:90]
        lines.append(
            f"| {row['position']} | {row['pmcid']} | {row['pub_year']} | "
            f"{row['journal'][:30]} | {title} |"
        )
    lines += [
        "",
        "## Offen nach diesem Schritt",
        "",
        "- Volltextpruefung: liefert jeder Artikel tatsaechlich Armwerte fuer",
        "  mindestens einen Vergleich? Die Auswahl ist eine Kandidatenliste,",
        "  keine Einschlussentscheidung.",
        "- Recordzahl feststellen; bei unter 60 Records Reserve nachziehen,",
        "  bei weiterhin zu wenig ein zweites Artikelkontingent ziehen.",
        "- Annotation durch unabhaengige Personen (F2), danach Einfrieren.",
        "- Kein Modellaufruf vor `freeze.json`.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    if not DECISIONS_PATH.exists() or not SHORTLIST_PATH.exists():
        print(f"ABBRUCH: Grundlage fehlt: {DECISIONS_PATH} / {SHORTLIST_PATH}")
        return 2
    payload = build()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    OUT_MD.write_text(render_md(payload), encoding="utf-8")

    checks = payload["checks"]
    print(f"Primaer: {payload['primary_count']}, Reserve: {payload['reserve_count']}")
    print(f"Pool nach Ausschluss: {checks['eligible_pool']}")
    print(f"G5-Schnittmenge: {checks['g5_overlap'] or 'leer'}")
    print(f"Yun-Schnittmenge: {checks['yun_overlap'] or 'leer'}")
    print(f"Status: {payload['status']}")
    return 0 if checks["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
