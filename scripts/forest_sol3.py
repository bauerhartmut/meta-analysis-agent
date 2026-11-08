"""Forest-Darstellung der SOL-Analysen (k = 3).

Liest data/bench/sol2/pooling_sol3_20261108.json und erzeugt eine
Markdown-Tabelle mit Effekt, 95%-CI, Random-Effects-Gewicht und ASCII-Balken.

Gewicht: w_i = 1 / (se_i^2 + tau^2), normiert auf 100 % innerhalb der Analyse.
Kein neues Pooling, keine neuen Zahlen: alle Werte stammen aus dem JSON.
"""
from pathlib import Path
import json

DATA = Path(__file__).resolve().parent.parent / "data" / "bench" / "sol2"
SRC = DATA / "pooling_sol3_20261108.json"
OUT = DATA / "forest_sol3_20261108.md"

XMIN, XMAX, WIDTH = -180.0, 130.0, 80
PAD_MAIN = " " * 53
PAD_SENS = " " * 47


def pos(v):
    p = (v - XMIN) / (XMAX - XMIN) * WIDTH
    return max(0, min(WIDTH - 1, int(round(p))))


def bar(lo, hi, est, point="*", fill="-", edge="|"):
    cells = [" "] * WIDTH
    a, b, c = pos(lo), pos(hi), pos(est)
    for i in range(a, b + 1):
        cells[i] = fill
    cells[a] = edge
    cells[b] = edge
    cells[c] = point
    return "".join(cells)


def axis():
    cells = [" "] * WIDTH
    cells[pos(0)] = "+"
    return "".join(cells)


def axis_labels():
    cells = [" "] * WIDTH
    for text, p in (("-180", 0), ("0", pos(0) - 1), ("+130", WIDTH - 4)):
        for k, ch in enumerate(text):
            if 0 <= p + k < WIDTH:
                cells[p + k] = ch
    return "".join(cells)


def weights(inputs, tau2):
    w = [1.0 / (i["se"] ** 2 + tau2) for i in inputs]
    total = sum(w)
    return [100.0 * x / total for x in w]


KURZ = (
    ("Hauptanalyse", "Hauptanalyse"),
    ("S1 PMC3489506", "S1 Aktigraphie"),
    ("S2 PMC2933606", "S2 Low excretors"),
    ("S3 PMC2952772 0.15", "S3 0,15 mg/kg"),
    ("S3b ", "S3b 0,1 mg/kg"),
    ("S4 ", "S4 alle Alternativen"),
    ("S5 ohne PMC3489506", "S5a ohne S1"),
    ("S5 ohne PMC2933606", "S5b ohne S2"),
    ("S5 ohne PMC2952772", "S5c ohne S3"),
    ("S8 ", "S8 S1 Tageb. unadj."),
    ("S9 ", "S9 S1 Aktigr. unadj."),
)


def kurz(name):
    for pre, lab in KURZ:
        if name.startswith(pre):
            return lab
    return name[:28]


def fmt(v):
    return f"{v:+.2f}"


def main():
    data = json.loads(SRC.read_text(encoding="utf-8"))
    analyses = data["analysen"]
    if not analyses:
        raise SystemExit("keine Analysen im JSON")

    lines = [
        "# Forest-Darstellung: Melatonin und Einschaflatenz (k = 3)",
        "",
        "Stand: 2026-11-08. Alle Werte aus `pooling_sol3_20261108.json`,",
        "erzeugt von `scripts/forest_sol3.py`. Vorzeichen: negativ = Melatonin",
        "senkt die Einschaflatenz. Skala der Balken: -180 bis +130 Minuten,",
        "80 Zeichen; `|` = Rand des 95 %-CI, `*` = Punktschaetzer,",
        "`+` = Nullinie. Bei Werten ausserhalb der Skala wird der Balken am",
        "Rand abgeschnitten (betrifft nur S5a/S5c am unteren Ende).",
        "",
        "Kein neues Pooling. Das CI der gepoolten Zeile ist das",
        "Hartung-Knapp-Sidak-Intervall, das CI der Studienzeile ist",
        "Est +/- 1,96 * SE (Normalapproximation aus dem hinterlegten SE).",
        "",
    ]

    main_a = analyses[0]
    lines += [
        "## Hauptanalyse",
        "",
        f"Modell: Random Effects, tau^2 = {main_a['tau2']:.2f}, "
        f"I^2 = {main_a['i2']:.1f} %, k = {main_a['k']}.",
        "",
        "```text",
        f"{'Studie':<12}{'Effekt':>9}{'95%-CI':>22}{'Gew.':>8}  Balken",
    ]
    w_main = weights(main_a["inputs"], main_a["tau2"])
    for inp, wt in zip(main_a["inputs"], w_main):
        lo = inp["est"] - 1.96 * inp["se"]
        hi = inp["est"] + 1.96 * inp["se"]
        lines.append(
            f"{inp['label']:<12}{fmt(inp['est']):>9}"
            f"{fmt(lo) + ' bis ' + fmt(hi):>22}{wt:>7.1f}%  "
            f"{bar(lo, hi, inp['est'])}"
        )
    lines.append(PAD_MAIN + axis())
    lines.append(PAD_MAIN + axis_labels())
    lines.append(
        f"{'Gepoolt':<12}{fmt(main_a['pooled']):>9}"
        f"{fmt(main_a['ci_low']) + ' bis ' + fmt(main_a['ci_high']):>22}"
        f"{100.0:>7.1f}%  "
        f"{bar(main_a['ci_low'], main_a['ci_high'], main_a['pooled'], '*', '=', '#')}"
    )
    lines += ["```", ""]
    if "pi_low" in main_a:
        lines += [
            f"Prediction Interval (df = 1, unbrauchbar): "
            f"{main_a['pi_low']:.1f} bis {main_a['pi_high']:.1f} min.",
            "",
        ]

    lines += [
        "## Alle Sensitivitaeten",
        "",
        "Gewichte in Klammern in der Reihenfolge der Studienzeilen:",
        "S1 / S2 / S3. Die Gewichte verschieben sich mit tau^2, weil",
        "groessere Zwischenstudienvarianz die Studien angleicht.",
        "",
        "```text",
        f"{'Analyse':<26}{'gepoolt':>9}{'95%-CI':>22}{'tau^2':>9}{'I2':>7}"
        f"  Gewichte S1/S2/S3",
    ]
    for a in analyses[1:]:
        w = weights(a["inputs"], a["tau2"])
        wtxt = " / ".join(f"{x:.0f}" for x in w)
        lines.append(
            f"{kurz(a['analyse']):<26}{fmt(a['pooled']):>9}"
            f"{fmt(a['ci_low']) + ' bis ' + fmt(a['ci_high']):>22}"
            f"{a['tau2']:>9.1f}{a['i2']:>6.1f}%  {wtxt}"
        )
    lines += ["```", ""]

    lines += [
        "## Balken je Analyse",
        "",
        "```text",
        "(je Analyse: Studienzeilen, Nullinie, gepoolte Zeile)",
    ]
    for a in analyses:
        lines.append(f"-- {a['analyse']}  (tau^2 = {a['tau2']:.1f})")
        for inp in a["inputs"]:
            lo = inp["est"] - 1.96 * inp["se"]
            hi = inp["est"] + 1.96 * inp["se"]
            lines.append(
                f"   {inp['label']:<11}{fmt(inp['est']):>9}"
                f"{fmt(lo) + ' bis ' + fmt(hi):>22}  {bar(lo, hi, inp['est'])}"
            )
        lines.append(PAD_SENS + axis())
        lines.append(PAD_SENS + axis_labels())
        lines.append(
            f"   {'Pool':<11}{fmt(a['pooled']):>9}"
            f"{fmt(a['ci_low']) + ' bis ' + fmt(a['ci_high']):>22}  "
            f"{bar(a['ci_low'], a['ci_high'], a['pooled'], '*', '=', '#')}"
        )
        lines.append("")
    lines += ["```", ""]

    lines += [
        "## Hinweise zur Lesart",
        "",
        "- Die Studienzeilen der Hauptanalyse sind die drei Effekte, die ins",
        "  Pooling eingehen; die Gewichte summieren sich auf 100 %.",
        "- S8/S9 nutzen die unadjustierte Differenz aus dem HTA-Bericht",
        "  (SE 10,88 bzw. 14,82 statt 9,08 bzw. 11,96).",
        "- Bei k = 2 (S5a-c) sind die Gewichte wenig aussagekraeftig: mit zwei",
        "  Beobachtungen und grossem tau^2 naehern sie sich 50/50.",
        "- Die Balken zeigen Unsicherheit, nicht Studiengroesse. Ein breiter",
        "  Balken heisst nicht automatisch kleine Studie.",
        "",
        "## Quelle",
        "",
        "`pooling_sol3_20261108.json`, `pooling_sol3_20261108.md`,",
        "`mends_hta_zusatz_20261108.md`.",
        "",
    ]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"geschrieben: {OUT} ({len(lines)} Zeilen)")
    for a in analyses:
        w = weights(a["inputs"], a["tau2"])
        print(f"  {a['analyse'][:34]:<34} Summe Gewichte = {sum(w):.6f} %")


if __name__ == "__main__":
    main()
