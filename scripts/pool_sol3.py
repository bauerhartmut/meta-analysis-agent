"""Drei SOL-Studien mit der vorhandenen Pooling-Engine zusammenfassen.

Nutzt ``research_agent.meta.pooling.pool`` (Random Effects, Hartung-Knapp-
Sidak) - keine eigene Statistik. Die Eingabewerte stehen mit Quelle und
Ableitung in ``data/bench/sol2/auswahlregel_pooling_20261108.md`` und
``pruefung_kandidaten_20261108.md``.

Hauptanalyse (Regel 4-6):
  PMC3489506  Tagebuch     -37.5  SE 9.0818   (CI -55.3 bis -19.7)
  PMC2933606  65-80 Jahre  -15.6  SE 4.9236   (CI -25.3 bis -6.0)
  PMC2952772  0.05 mg/kg   -31.0  SE 10.0     (berichtet)

Sensitivitaeten S1-S7 wie in der Auswahlregel festgelegt.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_agent.meta.pooling import pool  # noqa: E402

Z = 1.959964


def se_from_ci(low: float, high: float) -> float:
    return (high - low) / (2.0 * Z)


# Hauptzeilen: (label, effekt, se, herkunft)
MAIN = [
    ("PMC3489506", -37.5, se_from_ci(-55.3, -19.7), "Tagebuch, adjustiert, Studienangabe"),
    ("PMC2933606", -15.6, se_from_ci(-25.3, -6.0), "65-80 Jahre, adjustiert, Studienangabe"),
    ("PMC2952772", -31.0, 10.0, "0.05 mg/kg, SE berichtet"),
]

ALT = {
    "PMC3489506": ("PMC3489506", -45.3, se_from_ci(-68.8, -21.9), "Aktigraphie, adjustiert"),
    "PMC2933606": ("PMC2933606", -0.6, se_from_ci(-14.0, 12.7), "Low excretors, adjustiert"),
    "PMC2952772_010": ("PMC2952772", -36.0, 10.0, "0.1 mg/kg, SE berichtet"),
    "PMC2952772_015": ("PMC2952772", -42.0, 9.0, "0.15 mg/kg, SE berichtet"),
    "PMC3489506_unadj": ("PMC3489506", -37.44, se_from_ci(-58.77, -16.11),
                         "Tagebuch, unadjustiert (HTA Tab. 7)"),
    "PMC3489506_act_unadj": ("PMC3489506", -54.61, se_from_ci(-83.67, -25.56),
                             "Aktigraphie, unadjustiert (HTA Tab. 7)"),
}


def rows_of(spec):
    return [{"label": label, "est": est, "se": se} for label, est, se, _ in spec]


def summarise(spec, note: str = ""):
    result = pool(rows_of(spec), method="hksj")
    out = {
        "analyse": note,
        "k": result.get("k"),
        "studien": [label for label, *_ in spec],
        "pooled": result.get("pooled"),
        "ci_low": result.get("ci_low"),
        "ci_high": result.get("ci_high"),
        "se_hksj": result.get("se_hksj"),
        "tau2": result.get("tau2"),
        "q": result.get("q"),
        "i2": result.get("i2"),
        "pi_low": result.get("pi_low"),
        "pi_high": result.get("pi_high"),
        "fixed": result.get("fixed"),
        "fixed_ci_low": result.get("fixed_ci_low"),
        "fixed_ci_high": result.get("fixed_ci_high"),
        "small_k_note": result.get("small_k_note") or "",
        "inputs": [{"label": l, "est": e, "se": round(s, 4), "herkunft": h}
                   for l, e, s, h in spec],
    }
    return out


def fmt(value, digits=2):
    return "-" if value is None else f"{value:.{digits}f}"


def main() -> int:
    analyses = [summarise(MAIN, "Hauptanalyse")]

    alt1 = [ALT["PMC3489506"]] + MAIN[1:]
    alt2 = [MAIN[0], ALT["PMC2933606"]] + MAIN[2:]
    alt3 = MAIN[:2] + [ALT["PMC2952772_015"]]
    alt4 = [ALT["PMC3489506"], ALT["PMC2933606"], ALT["PMC2952772_015"]]
    analyses += [
        summarise(alt1, "S1 PMC3489506 Aktigraphie"),
        summarise(alt2, "S2 PMC2933606 Low excretors"),
        summarise(alt3, "S3 PMC2952772 0.15 mg/kg"),
        summarise(alt4, "S4 alle Alternativen (S1+S2+S3)"),
    ]

    for drop in range(3):
        subset = [row for index, row in enumerate(MAIN) if index != drop]
        analyses.append(summarise(subset, f"S5 ohne {MAIN[drop][0]} (Leave-one-out)"))

    for key in ("PMC2952772_010",):
        analyses.append(summarise(MAIN[:2] + [ALT[key]],
                                  "S3b PMC2952772 0.1 mg/kg"))

    analyses.append(summarise([ALT["PMC3489506_unadj"]] + MAIN[1:],
                              "S8 S1 Tagebuch unadjustiert (HTA)"))
    analyses.append(summarise(MAIN[:2] + [("PMC2952772", -31.0, 11.0,
                                           "0.05 mg/kg, SE aus CI (11.0)")],
                              "S10 PMC2952772 SE 11.0 aus CI"))
    analyses.append(summarise([ALT["PMC3489506_act_unadj"]] + MAIN[1:],
                              "S9 S1 Aktigraphie unadjustiert (HTA)"))

    payload = {
        "frage": "Melatonin vs Placebo, SOL in Minuten, negativ = Reduktion",
        "modell": "Random Effects, tau2 DerSimonian-Laird, HKSJ (t, df=k-1)",
        "engine": "research_agent.meta.pooling.pool",
        "se_regel": "(obere - untere CI-Grenze) / 3.919928",
        "analysen": analyses,
    }

    data_dir = Path("data/bench/sol2")
    json_path = data_dir / "pooling_sol3_20261108.json"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2),
                         encoding="utf-8")

    lines = [
        "# Pooling der drei SOL-Studien (k = 3)",
        "",
        "Modell: Random Effects, tau2 nach DerSimonian-Laird, "
        "Hartung-Knapp-Sidak-Intervall (t, df = k-1).",
        "Vorzeichen: negativ = Melatonin senkt die Einschaflatenz.",
        "",
        "## Eingabewerte der Hauptanalyse",
        "",
        "| Studie | Effekt (min) | SE | Herkunft |",
        "|---|---:|---:|---|",
    ]
    for label, est, se, origin in MAIN:
        lines.append(f"| {label} | {est:.1f} | {se:.2f} | {origin} |")

    lines += [
        "",
        "## Ergebnisse",
        "",
        "| Analyse | k | gepoolt (min) | 95 %-CI (HKSJ) | tau2 | Q | I2 (%) | PI |",
        "|---|---:|---:|---|---:|---:|---:|---|",
    ]
    for item in analyses:
        ci = f"{fmt(item['ci_low'])} bis {fmt(item['ci_high'])}"
        pi = "-" if item["pi_low"] is None else f"{fmt(item['pi_low'])} bis {fmt(item['pi_high'])}"
        lines.append(
            f"| {item['analyse']} | {item['k']} | {fmt(item['pooled'])} | {ci} | "
            f"{fmt(item['tau2'], 3)} | {fmt(item['q'], 2)} | {fmt(item['i2'], 1)} | {pi} |"
        )

    main_row = analyses[0]
    lines += [
        "",
        "## Lesart",
        "",
        f"Die Hauptanalyse schaetzt eine mittlere Reduktion von "
        f"**{fmt(main_row['pooled'])} min** (95 %-CI {fmt(main_row['ci_low'])} bis "
        f"{fmt(main_row['ci_high'])}) aus k = {main_row['k']} Studien. "
        f"tau2 = {fmt(main_row['tau2'], 3)}, Q = {fmt(main_row['q'], 2)}, "
        f"I2 = {fmt(main_row['i2'], 1)} %.",
        "",
        "Das HKSJ-Intervall ist bei k = 3 breit und asymmetrisch um die "
        "gepoolte Zahl - das ist die korrekte Unsicherheit, keine Schwaeche "
        "der Rechnung. Das Prediction Interval hat df = k-2 = 1 und ist "
        "deshalb praktisch unbrauchbar; es steht nur da, weil es berechnet "
        "werden kann, nicht weil es etwas aussagt.",
        "",
        "I2 bei k = 3 ist nicht als Heterogenitaetsmass interpretierbar: "
        "Q hat zwei Freiheitsgrade, die Schaetzung ist extrem unsicher.",
        "",
    ]
    md_path = data_dir / "pooling_sol3_20261108.md"
    # Die Markdown-Fassung ist handgepflegt (Lesart, Nachrechnung, Grenzen).
    # Das Skript schreibt nur das JSON, damit ein Lauf die Kommentare nicht
    # ueberschreibt.

    for item in analyses:
        print(f"{item['analyse']:<38} k={item['k']} "
              f"pooled={fmt(item['pooled'])} "
              f"[{fmt(item['ci_low'])}; {fmt(item['ci_high'])}] "
              f"tau2={fmt(item['tau2'], 3)} I2={fmt(item['i2'], 1)}")
    print(f"JSON: {json_path}")
    print(f"MD:   {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
