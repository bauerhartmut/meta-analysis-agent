"""Passt die gespeicherte SE zum KI - und wo zaehlt sie ueberhaupt?

Der Anlass war eine Zeile, deren SE 16 % kleiner schien als die aus dem KI
ableitbare. Die Pruefung des Codes zeigt: `standardize` rechnet bei
Ratio-Typen (or, rr, hr) mit vorhandenem KI die log-SE **aus dem KI** und
ignoriert die gespeicherte `se`. Nur ohne brauchbares KI liest es `se` als
Standardfehler des log-Ratio. Fuer lineare Typen (beta, mean_diff, g, smd, z,
heritability) nutzt es `se` direkt.

Deshalb misst dieses Skript zwei Dinge getrennt:

A. Auf welcher Skala ist die gespeicherte SE bei Ratio-Typen? Vergleich mit
   (hi-lo)/(2z) [Ratio-Skala] und (ln hi - ln lo)/(2z) [log-Skala].
B. Wo geht die SE tatsaechlich in den Pool ein - mit KI (dort gewinnt das KI),
   ohne KI (dort wird `se` als log-SE gelesen) oder linear.

Read-only auf Kopien, 0 Modellaufrufe.

Aufruf:
    export PYTHONIOENCODING=utf-8
    .venv/bin/python.exe scripts/messe_se_ki_konsistenz_20261110.py
"""

import json
import math
import sqlite3
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from messe_quote_luecken_bestand import kopiere, aufraeumen            # noqa: E402
from messe_effekt_duplikate import gruppe                            # noqa: E402
from research_agent.meta.designs import aggregate_design, classify_design  # noqa: E402
from research_agent.meta.pooling import _lesepass                     # noqa: E402

VALIDIERUNG = ROOT / "data" / "bench" / "validierung"
OUT_JSON = VALIDIERUNG / "se_ki_konsistenz_20261110.json"
OUT_MD = VALIDIERUNG / "se_ki_konsistenz_20261110.md"

RATIO = {"or", "rr", "hr", "odds ratio", "risk ratio", "hazard ratio",
         "relative risk", "rate ratio"}
LINEAR = {"beta", "mean_diff", "g", "smd", "z", "heritability", "md",
          "mean difference", "std mean difference"}
SKIP = {"r", "other", ""}


def z_wert(level):
    try:
        lvl = float(level)
    except (TypeError, ValueError):
        lvl = 0.95
    if not 0.5 < lvl < 0.999:
        lvl = 0.95
    return statistics.NormalDist().inv_cdf(1 - (1 - lvl) / 2)


def varianten(typ, lo, hi, level):
    """SE auf beiden Skalen; fuer lineare Typen sind beide identisch."""
    z = z_wert(level)
    if typ in RATIO:
        if lo <= 0 or hi <= 0:
            return None, None
        return ((hi - lo) / (2 * z),
                (math.log(hi) - math.log(lo)) / (2 * z))
    se = (hi - lo) / (2 * z)
    return se, se


def stats(rels):
    if not rels:
        return {}
    absrel = sorted(abs(r) for r in rels)
    n = len(absrel)
    return {
        "n": n,
        "passt_5": sum(1 for r in absrel if r <= 0.05),
        "ueber_10": sum(1 for r in absrel if r > 0.10),
        "ueber_20": sum(1 for r in absrel if r > 0.20),
        "anteil_ueber_10": round(sum(1 for r in absrel if r > 0.10) / n, 4),
        "median_abs_rel": round(statistics.median(absrel), 4),
        "p90_abs_rel": round(absrel[int(0.9 * (n - 1))], 4),
    }


def lies(path: Path, index: int):
    dest = kopiere(path, index)
    conn = None
    try:
        conn = sqlite3.connect(dest, timeout=10)
        conn.row_factory = sqlite3.Row
        return [dict(r) for r in conn.execute("SELECT * FROM study_effects")]
    finally:
        if conn is not None:
            conn.close()
        aufraeumen(dest)


def main() -> int:
    db_pfade = [p for p in sorted((ROOT / "data").rglob("*.db"))
                if "-usage" not in p.name]
    skala = Counter()                      # Ratio: linear / log / unklar
    rels = defaultdict(list)               # Gruppe -> Abweichungen der genutzten SE
    alle_rel = defaultdict(list)           # Gruppe -> Abweichung gegen die naechste Skala
    nicht_pruefbar = Counter()
    nutzung = Counter()
    ratio_ohne_ki = []
    beispiele = []
    dbs = 0
    fehler = []

    for index, path in enumerate(db_pfade):
        try:
            rows = lies(path, index)
        except Exception as exc:                          # noqa: BLE001
            fehler.append({"datei": path.relative_to(ROOT).as_posix(),
                           "fehler": str(exc)})
            continue
        if not rows:
            continue
        dbs += 1
        bestand = "themen" if gruppe(path) == "themen" else "andere"

        for row in rows:
            typ = str(row.get("effect_type") or "").strip().lower()
            design = str(row.get("design") or "")
            kat = classify_design(design) or "(unklassifiziert)"
            agg = "uebersicht" if aggregate_design(design) else "primaer"
            eff, se = row.get("effect"), row.get("se")
            lo, hi = row.get("ci_low"), row.get("ci_high")
            ki_da = (lo is not None and hi is not None
                     and float(lo) < float(hi))

            if typ in SKIP or (typ not in RATIO and typ not in LINEAR):
                nicht_pruefbar["typ_unbekannt"] += 1
                continue
            if eff is None:
                nicht_pruefbar["kein_effekt"] += 1
                continue

            if typ in RATIO and ki_da:
                se_lin, se_log = varianten(typ, float(lo), float(hi),
                                           row.get("ci_level"))
                if se is None or se_lin is None:
                    nicht_pruefbar["keine_se_oder_ki"] += 1
                    continue
                r_lin = float(se) / se_lin - 1
                r_log = float(se) / se_log - 1
                naeher = "linear" if abs(r_lin) <= abs(r_log) else "log"
                passt_lin = abs(r_lin) <= 0.05
                passt_log = abs(r_log) <= 0.05
                skala[(typ, "linear" if passt_lin else "-")] += 1
                skala[(typ, "log" if passt_log else "-")] += 1
                skala[(typ, "naeher_" + naeher)] += 1
                # Mit KI gewinnt das KI; die SE geht nicht in den Pool ein.
                nutzung["ratio_mit_ki_se_unbenutzt"] += 1
                alle_rel[("typ", typ)].append(r_log if naeher == "log" else r_lin)
                continue

            if typ in RATIO:
                # Ohne KI liest standardize `se` als log-SE. Wenn die
                # Extraktion linear speichert, ist die Zeile um Faktor effect
                # zu unpraezise.
                if se is None:
                    nicht_pruefbar["kein_se"] += 1
                    continue
                nutzung["ratio_ohne_ki_se_als_log"] += 1
                ratio_ohne_ki.append({
                    "datei": path.relative_to(ROOT).as_posix(),
                    "id": row.get("id"), "typ": typ, "effect": float(eff),
                    "se": float(se),
                    "se_je_effect": round(float(se) / float(eff), 6)
                    if float(eff) else None,
                    "design_kat": kat,
                })
                continue

            # lineare Typen: standardize nutzt se direkt
            if se is None:
                nicht_pruefbar["kein_se"] += 1
                continue
            if not ki_da:
                nicht_pruefbar["linear_ohne_ki"] += 1
                continue
            se_lin, _ = varianten(typ, float(lo), float(hi), row.get("ci_level"))
            if not se_lin:
                nicht_pruefbar["ki_ungueltig"] += 1
                continue
            rel = float(se) / se_lin - 1
            if not math.isfinite(rel):
                nicht_pruefbar["se_ungueltig"] += 1
                continue
            nutzung["linear_se_genutzt"] += 1
            for key in (("typ", typ), ("design", kat), ("aggregat", agg),
                        ("bestand", bestand), ("pass", f"pass {_lesepass(row)}"),
                        ("typ_design", f"{typ} | {kat}")):
                rels[key].append(rel)
            if abs(rel) > 0.10 and len(beispiele) < 200:
                beispiele.append({
                    "datei": path.relative_to(ROOT).as_posix(),
                    "id": row.get("id"), "typ": typ, "design_kat": kat,
                    "effect": float(eff), "ci": [float(lo), float(hi)],
                    "se_ges": float(se), "se_ki": round(se_lin, 6),
                    "rel": round(rel, 4),
                })

    def tabelle(praefix, quelle):
        return dict(sorted(
            ((k[1], stats(v)) for k, v in quelle.items() if k[0] == praefix),
            key=lambda kv: -kv[1]["n"]))

    se_je_effect = [e["se_je_effect"] for e in ratio_ohne_ki
                    if e.get("se_je_effect")]
    ergebnis = {
        "definition": "A: Skala der gespeicherten SE bei Ratio-Typen gegen "
                      "(hi-lo)/(2z) und (ln hi - ln lo)/(2z). B: Abweichung nur "
                      "dort, wo standardize die SE wirklich liest.",
        "code_befund": "Ratio + KI: standardize rechnet die log-SE aus dem KI, "
                       "se bleibt unbenutzt. Ratio ohne KI: se wird als log-SE "
                       "gelesen. Linear: se wird direkt gelesen.",
        "dbs": dbs,
        "dbs_fehler": fehler,
        "nicht_pruefbar": dict(nicht_pruefbar),
        "nutzung": dict(nutzung),
        "skala_ratio": {f"{typ}|{marke}": n for (typ, marke), n
                        in sorted(skala.items())},
        "ratio_ohne_ki": {
            "n": len(ratio_ohne_ki),
            "median_se_je_effect": round(statistics.median(se_je_effect), 4)
            if se_je_effect else None,
            "beispiele": ratio_ohne_ki[:40],
        },
        "genutzte_se_nach_typ": tabelle("typ", rels),
        "genutzte_se_nach_design": tabelle("design", rels),
        "genutzte_se_nach_aggregat": tabelle("aggregat", rels),
        "genutzte_se_nach_bestand": tabelle("bestand", rels),
        "genutzte_se_nach_pass": tabelle("pass", rels),
        "beispiele_ueber_10": sorted(beispiele, key=lambda b: -abs(b["rel"]))[:30],
    }
    VALIDIERUNG.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(ergebnis, ensure_ascii=False, indent=2),
                        encoding="utf-8")

    def md_tabelle(titel, daten, hinweis=""):
        zeilen = [f"### {titel}", ""]
        if hinweis:
            zeilen += [hinweis, ""]
        zeilen += ["| Gruppe | n | passt (±5 %) | >10 % | >20 % | Median |r| "
                   "| P90 |r| |", "|---|---:|---:|---:|---:|---:|---:|"]
        for name, s in daten.items():
            zeilen.append(
                f"| `{name}` | {s['n']} | {s['passt_5']} | {s['ueber_10']} | "
                f"{s['ueber_20']} | {s['median_abs_rel']:.1%} | "
                f"{s['p90_abs_rel']:.1%} |"
            )
        zeilen.append("")
        return zeilen

    md = [
        "# Passt die gespeicherte SE zum KI - und wo zählt sie? (2026-11-10)",
        "",
        f"{dbs} Datenbanken, read-only auf Kopien, 0 Modellaufrufe. "
        f"{len(fehler)} DBs ohne Tabelle (siehe JSON).",
        "",
        "## Der Code entscheidet, welche Abweichung zählt",
        "",
        "- **Ratio-Typ (`or`, `rr`, `hr`) mit KI:** `standardize` rechnet die "
        "log-SE aus dem KI. Die gespeicherte `se` wird **nicht** benutzt.",
        "- **Ratio-Typ ohne KI:** `se` wird als Standardfehler des log-Ratio "
        "gelesen. Steht sie auf der Ratio-Skala, ist die Zeile um den Faktor "
        "`effect` zu unpräzise.",
        "- **Linear (`beta`, `mean_diff`, `g`, `smd`, `z`, `heritability`):** "
        "`se` wird direkt gelesen.",
        "",
        "## A. Auf welcher Skala liegt die SE bei Ratio-Typen?",
        "",
        "| Typ | Zeilen mit KI | passt linear (±5 %) | passt log (±5 %) | "
        "näher an linear |",
        "|---|---:|---:|---:|---:|",
    ]
    for typ in sorted(RATIO):
        n = ergebnis["skala_ratio"].get(f"{typ}|naeher_linear", 0) + \
            ergebnis["skala_ratio"].get(f"{typ}|naeher_log", 0)
        if not n:
            continue
        md.append(
            f"| `{typ}` | {n} | {ergebnis['skala_ratio'].get(f'{typ}|linear', 0)} "
            f"| {ergebnis['skala_ratio'].get(f'{typ}|log', 0)} "
            f"| {ergebnis['skala_ratio'].get(f'{typ}|naeher_linear', 0)} |"
        )
    md += [
        "",
        "## B. Wo die SE in den Pool eingeht",
        "",
        "| Pfad | Zeilen |",
        "|---|---:|",
    ]
    for k, v in ergebnis["nutzung"].items():
        md.append(f"| `{k}` | {v} |")
    rk = ergebnis["ratio_ohne_ki"]
    md += [
        "",
        f"**Kritisch:** {rk['n']} Ratio-Zeilen haben eine SE, aber kein "
        f"brauchbares KI. Dort liest `standardize` die SE als log-SE. Median "
        f"`se/effect` = {rk['median_se_je_effect']} — liegt der Wert nahe 0,1 "
        "bis 0,3, ist die SE auf der log-Skala gespeichert und alles ist in "
        "Ordnung; liegt er nahe 1, wurde linear gespeichert und die Zeile ist "
        "zu unpräzise.",
        "",
    ]
    md += md_tabelle("Linear: Abweichung der genutzten SE nach Typ",
                     ergebnis["genutzte_se_nach_typ"])
    md += md_tabelle("Linear: nach Design", ergebnis["genutzte_se_nach_design"])
    md += md_tabelle("Linear: nach Bestand", ergebnis["genutzte_se_nach_bestand"])
    md += md_tabelle("Linear: nach Lesepass", ergebnis["genutzte_se_nach_pass"])
    md += ["## Beispiele mit mehr als 10 % Abweichung (linear, SE genutzt)", ""]
    for b in ergebnis["beispiele_ueber_10"][:15]:
        md.append(
            f"- {Path(b['datei']).name} `{b['id']}` ({b['typ']}, {b['design_kat']}): "
            f"Effekt {b['effect']}, KI {b['ci'][0]}–{b['ci'][1]}, "
            f"SE gespeichert {b['se_ges']:.4f} vs. aus KI {b['se_ki']:.4f} "
            f"({b['rel']:+.1%})"
        )
    md.append("")
    OUT_MD.write_text("\n".join(md), encoding="utf-8")

    print(f"DBs: {dbs}, Fehler: {len(fehler)}")
    print("Nutzung:", dict(nutzung))
    print("Nicht pruefbar:", dict(nicht_pruefbar))
    print("Skala Ratio:", {k: v for k, v in ergebnis["skala_ratio"].items()
                           if "naeher" in k or k.endswith("|linear")})
    print("Ratio ohne KI:", rk["n"], "Median se/effect:", rk["median_se_je_effect"])
    for name in ("genutzte_se_nach_typ", "genutzte_se_nach_design"):
        print(f"-- {name}")
        for key, st in ergebnis[name].items():
            print(f"   {key}: n={st['n']} median|r|={st['median_abs_rel']:.1%} "
                  f">10%={st['ueber_10']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
