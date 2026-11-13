#!/usr/bin/env python3
"""Power-Abschaetzung fuer gepaarte Genauigkeitsvergleiche.

Modell: gepaarter McNemar-Test auf Feldebene, mit Design-Effekt aus dem
Artikel-Clustering. Die Rechnung ist asymptotisch (Normalapproximation) und
damit eine Abschaetzung, keine Zusicherung.

Annahmen, die im Bericht offengelegt werden:
- Felder je Record: 4 (binaer), 6 (kontinuierlich), 8 (kontinuierlich mit
  beiden Armen und Zeitpunkt).
- Records je Artikel: 60/25 bis 100/25.
- ICC der Fehler innerhalb eines Artikels: 0.1, 0.2, 0.3.
- Diskordanzrate (Anteil Felder, in denen sich zwei Varianten unterscheiden):
  0.15 und 0.25.
- Alpha 0.05 zweiseitig, Power 0.80.

Ausgabe:
- ``power_estimation_v1.json``
- ``power_estimation_v1.md``
"""

from __future__ import annotations

import json
import math
from datetime import date
from pathlib import Path

BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "evaluation" / "multi_model_cross_validation"
OUT_JSON = OUT_DIR / "power_estimation_v1.json"
OUT_MD = OUT_DIR / "power_estimation_v1.md"

ALPHA = 0.05
POWER = 0.80
ARTICLES = 25
RECORD_OPTIONS = (60, 80, 100, 120)
FIELD_OPTIONS = (4, 6, 8)
ICC_OPTIONS = (0.1, 0.2, 0.3)
DISCORDANCE_OPTIONS = (0.15, 0.25)


def z_value(probability: float) -> float:
    """Inverse Normalverteilung ueber die Fehlerfunktion (ohne scipy)."""
    low, high = -10.0, 10.0
    for _ in range(200):
        mid = (low + high) / 2
        if 0.5 * (1 + math.erf(mid / math.sqrt(2))) < probability:
            low = mid
        else:
            high = mid
    return (low + high) / 2


Z_ALPHA = z_value(1 - ALPHA / 2)
Z_POWER = z_value(POWER)


def design_effect(records: int, icc: float) -> float:
    per_article = records / ARTICLES
    return 1 + (per_article - 1) * icc


def power_for(delta: float, n_eff: float, discordance: float) -> float:
    """Power des gepaarten Tests fuer eine Differenz delta (Anteilsdifferenz)."""
    if delta <= 0 or delta >= discordance:
        return 0.0
    numerator = delta * math.sqrt(n_eff) - Z_ALPHA * math.sqrt(discordance)
    denominator = math.sqrt(max(discordance - delta * delta, 1e-9))
    z = numerator / denominator
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def minimal_detectable_difference(n_eff: float, discordance: float) -> float:
    """Kleinste Differenz, die bei 80 % Power nachweisbar ist."""
    low, high = 1e-4, discordance - 1e-4
    for _ in range(200):
        mid = (low + high) / 2
        if power_for(mid, n_eff, discordance) < POWER:
            low = mid
        else:
            high = mid
    return (low + high) / 2


def fields_needed(delta: float, discordance: float, icc: float, records: int) -> int:
    """Felder, die fuer delta bei gegebener Power noetig waeren."""
    low, high = 1, 2_000_000
    for _ in range(200):
        mid = (low + high) // 2
        n_eff = mid / design_effect(records, icc)
        if power_for(delta, n_eff, discordance) < POWER:
            low = mid
        else:
            high = mid
    return high


def main() -> int:
    rows = []
    for records in RECORD_OPTIONS:
        for fields in FIELD_OPTIONS:
            n_fields = records * fields
            for icc in ICC_OPTIONS:
                deff = design_effect(records, icc)
                n_eff = n_fields / deff
                for discordance in DISCORDANCE_OPTIONS:
                    mdd = minimal_detectable_difference(n_eff, discordance)
                    rows.append(
                        {
                            "records": records,
                            "fields_per_record": fields,
                            "fields_total": n_fields,
                            "records_per_article": round(records / ARTICLES, 2),
                            "icc": icc,
                            "design_effect": round(deff, 3),
                            "effective_fields": round(n_eff, 1),
                            "discordance": discordance,
                            "mdd_pp": round(mdd * 100, 2),
                        }
                    )

    required = []
    for records in (60, 80, 100):
        for fields in FIELD_OPTIONS:
            for icc in ICC_OPTIONS:
                need = fields_needed(0.05, 0.25, icc, records)
                required.append(
                    {
                        "records": records,
                        "fields_per_record": fields,
                        "fields_total": records * fields,
                        "icc": icc,
                        "fields_needed_for_5pp": need,
                        "enough": records * fields >= need,
                    }
                )

    base = [
        row
        for row in rows
        if row["records"] == 60
        and row["fields_per_record"] == 6
        and row["discordance"] == 0.25
    ]
    verdict = {
        "mdd_range_pp_at_60_records_6_fields": [
            min(row["mdd_pp"] for row in base),
            max(row["mdd_pp"] for row in base),
        ],
        "note": (
            "Die Spanne zeigt die Abhaengigkeit von ICC und Diskordanz. "
            "Eine Differenz unterhalb der MDD ist mit dieser Stichprobe nicht "
            "entscheidbar; ein nicht signifikantes Ergebnis ist kein "
            "Gleichstandsbeweis."
        ),
        "fields_for_5pp_at_60_records": [
            row["fields_needed_for_5pp"]
            for row in required
            if row["records"] == 60 and row["fields_per_record"] == 6
        ],
    }

    payload = {
        "estimation_id": "crossval_power_v1",
        "created": date.today().isoformat(),
        "method": "gepaarter McNemar-Test, Normalapproximation, Design-Effekt aus Artikel-Clustering",
        "assumptions": {
            "alpha": ALPHA,
            "power": POWER,
            "articles": ARTICLES,
            "records_options": list(RECORD_OPTIONS),
            "fields_per_record_options": list(FIELD_OPTIONS),
            "icc_options": list(ICC_OPTIONS),
            "discordance_options": list(DISCORDANCE_OPTIONS),
        },
        "rows": rows,
        "required_fields": required,
        "verdict": verdict,
    }
    OUT_JSON.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# Power-Abschaetzung",
        "",
        f"Stand: {payload['created']}",
        "Gepaarter McNemar-Test auf Feldebene, Design-Effekt aus Artikel-Clustering.",
        "Asymptotische Naeherung, keine Zusicherung.",
        "",
        "## Kleinste nachweisbare Differenz (Prozentpunkte)",
        "",
        "| Records | Felder/Record | ICC 0.1 | ICC 0.2 | ICC 0.3 |",
        "|---:|---:|---:|---:|---:|",
    ]
    for records in (60, 80, 100):
        for fields in (6,):
            cells = []
            for icc in ICC_OPTIONS:
                match = [
                    row
                    for row in rows
                    if row["records"] == records
                    and row["fields_per_record"] == fields
                    and row["icc"] == icc
                    and row["discordance"] == 0.25
                ][0]
                cells.append(f"{match['mdd_pp']} pp")
            lines.append(f"| {records} | {fields} | " + " | ".join(cells) + " |")
    lines += [
        "",
        "Diskordanz 0.25, Power 0.80, Alpha 0.05 zweiseitig.",
        "",
        "## Reicht die Stichprobe fuer 5 Prozentpunkte?",
        "",
        "| Records | Felder/Record | ICC | benoetigte Felder | reicht |",
        "|---:|---:|---:|---:|---|",
    ]
    for row in required:
        if row["fields_per_record"] != 6:
            continue
        lines.append(
            f"| {row['records']} | {row['fields_per_record']} | {row['icc']} | "
            f"{row['fields_needed_for_5pp']} | {'ja' if row['enough'] else 'nein'} |"
        )
    lines += [
        "",
        "## Einordnung",
        "",
        f"Bei 60 Records und 6 Feldern liegt die kleinste nachweisbare Differenz "
        f"zwischen {verdict['mdd_range_pp_at_60_records_6_fields'][0]} und "
        f"{verdict['mdd_range_pp_at_60_records_6_fields'][1]} Prozentpunkten.",
        "",
        "Fuer 5 Prozentpunkte waeren bei 60 Records "
        f"{min(verdict['fields_for_5pp_at_60_records'])} bis "
        f"{max(verdict['fields_for_5pp_at_60_records'])} Felder noetig - mehr, als "
        "60 Records mit 6 bis 8 Feldern liefern.",
        "",
        verdict["note"],
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("MDD 60 Records / 6 Felder:",
          verdict["mdd_range_pp_at_60_records_6_fields"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
