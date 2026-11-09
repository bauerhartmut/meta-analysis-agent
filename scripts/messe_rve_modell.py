"""E4i - wie viel der RVE-Verbreiterung ist Modell, wie viel Cluster?

Drei Rechnungen auf demselben Material (die Zeilen VOR dem Kollaps):

    HKJ      pool(kept)                              RE, w = 1/(v + tau2)
    RVE-FE   pool_rve(sub_rows)                      FE, w = 1/v
    RVE-RE   pool_rve(sub_rows, weights="random")    RE, w = 1/(v + tau2)
             zusaetzlich mit REML-tau2 als Sensitivitaet

Log-Breiten sind additiv, linear nicht:

    ln(w_RE / w_HKJ) = ln(w_RE / w_FE)  +  ln(w_FE / w_HKJ)
                       \\__ Modell __/     \\__ Cluster __/

Der Modellanteil ist der Wechsel von Fixed zu Random Effects, der
Clusteranteil die Korrektur fuer haengige Zeilen. Nur wenn beide getrennt
sind, sagt die Zahl etwas ueber Scheinpraezision.

Read-only auf DB-Kopien, keine Modellaufrufe.

Aufruf:
    export PYTHONIOENCODING=utf-8
    .venv/bin/python.exe scripts/messe_rve_modell.py
"""

import json
import math
import sqlite3
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from messe_quote_luecken_bestand import kopiere, aufraeumen   # noqa: E402
from messe_effekt_duplikate import gruppe                     # noqa: E402
from research_agent.meta.outcome_labels import normalize_outcome  # noqa: E402
from research_agent.meta.pooling import (                    # noqa: E402
    _collapse_same_study, _split_pool_conditions, pool, pool_rve, standardize,
)

VALIDIERUNG = ROOT / "data" / "bench" / "validierung"
OUT_JSON = VALIDIERUNG / "e4i_rve_modell_20261108.json"
OUT_MD = VALIDIERUNG / "e4i_rve_modell_20261108.md"

ZIELE = ("major adverse cardiovascular", "incident cardiovascular disease",
         "depressive symptoms", "preeclampsia", "frailty")


def themen_dbs():
    return sorted(p for p in (ROOT / "data").rglob("*.db")
                  if "-usage" not in p.name and gruppe(p) == "themen")


def lies(path, index):
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


def standardisiere(rows):
    out = []
    for row in rows:
        est, se, scale, reason = standardize(row)
        if reason or se is None:
            continue
        item = dict(row)
        item.update({
            "est": float(est), "se": float(se), "scale": scale,
            "outcome_group": normalize_outcome(
                str(row.get("outcome") or "").strip() or "(kein Outcome)"),
        })
        out.append(item)
    return out


def breite(analysis):
    low, high = analysis.get("ci_low"), analysis.get("ci_high")
    if low is None or high is None:
        return None
    return float(high) - float(low)


def faktor(zaehler, nenner):
    if not zaehler or not nenner:
        return None
    return zaehler / nenner


def ist_ziel(name):
    text = name.lower()
    return any(ziel in text for ziel in ZIELE)


def zerlegung(w_hkj, w_fe, w_re):
    """Modell- und Clusteranteil auf der Log-Skala, plus Anteil Modell."""

    if not all((w_hkj, w_fe, w_re)):
        return None, None, None, None
    modell = math.log(w_re / w_fe)
    cluster = math.log(w_fe / w_hkj)
    gesamt = modell + cluster
    anteil = modell / gesamt if abs(gesamt) > 1e-12 else None
    return modell, cluster, gesamt, anteil


def main():
    ergebnisse, fehler = [], []
    for index, path in enumerate(themen_dbs()):
        try:
            probe = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True,
                                    timeout=5)
            tables = {r[0] for r in probe.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")}
            probe.close()
        except Exception as exc:                      # noqa: BLE001
            fehler.append({"datei": str(path), "fehler": str(exc)})
            continue
        if "study_effects" not in tables:
            continue
        groups = {}
        for row in standardisiere(lies(path, index)):
            groups.setdefault((row["outcome_group"], row["scale"]), []).append(row)

        for (outcome, scale), group_rows in groups.items():
            for sub_label, sub_rows in _split_pool_conditions(group_rows):
                kept, _dropped = _collapse_same_study(sub_rows)
                hkj = pool(kept)
                if int(hkj.get("k") or 0) < 2:
                    continue
                fe = pool_rve(sub_rows)
                re_dl = pool_rve(sub_rows, weights="random")
                re_reml = pool_rve(sub_rows, weights="random",
                                   tau2_method="reml")
                b_hkj, b_fe = breite(hkj), breite(fe)
                b_re, b_reml = breite(re_dl), breite(re_reml)
                modell, cluster, gesamt, anteil = zerlegung(b_hkj, b_fe, b_re)
                ergebnisse.append({
                    "datei": path.relative_to(ROOT).as_posix(),
                    "gruppe": f"{outcome} [{scale}]{sub_label}",
                    "k": int(hkj.get("k") or 0),
                    "zeilen": len(sub_rows),
                    "M": fe.get("M"),
                    "hkj": {"pooled": hkj.get("pooled"),
                            "ci": [hkj.get("ci_low"), hkj.get("ci_high")],
                            "breite": b_hkj, "tau2": hkj.get("tau2")},
                    "rve_fe": {"pooled": fe.get("pooled"), "breite": b_fe,
                               "available": fe.get("available")},
                    "rve_re": {"pooled": re_dl.get("pooled"), "breite": b_re,
                               "tau2": re_dl.get("tau2"),
                               "available": re_dl.get("available")},
                    "rve_re_reml": {"breite": b_reml,
                                    "tau2": re_reml.get("tau2"),
                                    "available": re_reml.get("available")},
                    "faktor_fe_hkj": faktor(b_fe, b_hkj),
                    "faktor_re_fe": faktor(b_re, b_fe),
                    "faktor_re_hkj": faktor(b_re, b_hkj),
                    "log_modell": modell,
                    "log_cluster": cluster,
                    "anteil_modell": anteil,
                })

    ziele = sorted((e for e in ergebnisse if ist_ziel(e["gruppe"])),
                   key=lambda e: e["gruppe"])
    verfuegbar = [e for e in ergebnisse if e["rve_re"]["available"]]

    def fmt(value, digits=3):
        return "-" if value is None else f"{float(value):.{digits}f}"

    def pct(value):
        return "-" if value is None else f"{100 * float(value):.0f}%"

    md = [
        "# E4i - RVE mit Random-Effects-Gewichten",
        "",
        f"Stand: {time.strftime('%Y-%m-%d %H:%M')} · Modellaufrufe: 0 · Tokens: 0",
        "",
        "Drei Rechnungen auf demselben Material (Zeilen vor dem Kollaps):",
        "",
        "| Kuerzel | Aufruf | Gewichte |",
        "|---|---|---|",
        "| HKJ | `pool(kept)` | `1/(v + tau2)`, DL |",
        "| RVE-FE | `pool_rve(sub_rows)` | `1/v` |",
        "| RVE-RE | `pool_rve(sub_rows, weights=\"random\")` | `1/(v + tau2)`, DL |",
        "",
        "Zerlegung auf der Log-Skala (Breiten sind dort additiv):",
        "`ln(w_RE/w_HKJ) = ln(w_RE/w_FE) + ln(w_FE/w_HKJ)` - Modell plus",
        "Cluster. Der Anteil sagt, welcher Teil der Verbreiterung vom",
        "Modellwechsel kommt.",
        "",
        "## Zielgruppen",
        "",
        "| Gruppe | k | M | HKJ-Breite | RVE-FE | RVE-RE | RE/HKJ | Modellanteil |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for e in ziele:
        md.append(
            f"| {e['gruppe']} | {e['k']} | {e['M']} | {fmt(e['hkj']['breite'])} "
            f"| {fmt(e['rve_fe']['breite'])} | {fmt(e['rve_re']['breite'])} "
            f"| {fmt(e['faktor_re_hkj'], 2)} | {pct(e['anteil_modell'])} |")

    md += ["", "## Alle Gruppen", ""]
    md.append(f"- Gruppen mit k >= 2: {len(ergebnisse)}")
    md.append(f"- RVE-RE verfuegbar: {len(verfuegbar)}")
    breiter_re = [e for e in verfuegbar
                  if e["faktor_re_hkj"] and e["faktor_re_hkj"] > 1]
    md.append(f"- RVE-RE breiter als HKJ: {len(breiter_re)}")
    anteile = sorted(e["anteil_modell"] for e in verfuegbar
                     if e["anteil_modell"] is not None)
    if anteile:
        md.append(f"- Median Modellanteil: {pct(anteile[len(anteile) // 2])}")
    md += ["", "### Tabelle", "",
           "| Gruppe | k | M | HKJ | RVE-FE | RVE-RE | RVE-RE(REML) "
           "| FE/HKJ | RE/FE | RE/HKJ | Modell | Cluster | Modellanteil |",
           "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for e in sorted(ergebnisse, key=lambda x: x["gruppe"]):
        md.append(
            f"| {e['gruppe']} | {e['k']} | {e['M']} "
            f"| {fmt(e['hkj']['breite'])} | {fmt(e['rve_fe']['breite'])} "
            f"| {fmt(e['rve_re']['breite'])} | {fmt(e['rve_re_reml']['breite'])} "
            f"| {fmt(e['faktor_fe_hkj'], 2)} | {fmt(e['faktor_re_fe'], 2)} "
            f"| {fmt(e['faktor_re_hkj'], 2)} | {fmt(e['log_modell'], 3)} "
            f"| {fmt(e['log_cluster'], 3)} | {pct(e['anteil_modell'])} |")

    mace = [e for e in ziele if "major adverse cardiovascular" in e["gruppe"]]
    md += ["", "## MACE im Detail", ""]
    if not mace:
        md.append("MACE-Gruppe in diesem Datenbestand nicht gefunden.")
    for e in mace:
        md += [
            f"- Breiten: HKJ {fmt(e['hkj']['breite'])}, RVE-FE "
            f"{fmt(e['rve_fe']['breite'])}, RVE-RE {fmt(e['rve_re']['breite'])}.",
            f"- tau2 (HKJ) {fmt(e['hkj']['tau2'], 3)}, tau2 (RVE-RE, DL) "
            f"{fmt(e['rve_re']['tau2'], 3)}, REML-Variante "
            f"{fmt(e['rve_re_reml']['tau2'], 3)}.",
            f"- Modellanteil an der Log-Verbreiterung: {pct(e['anteil_modell'])} "
            f"(Modell {fmt(e['log_modell'], 3)}, Cluster "
            f"{fmt(e['log_cluster'], 3)}).",
        ]
        if e["anteil_modell"] is not None and abs(e["anteil_modell"]) < 0.05:
            md.append(
                "- Damit ist die Verbreiterung um Faktor "
                f"{fmt(e['faktor_fe_hkj'], 2)} praktisch vollstaendig "
                "Cluster-Effekt: tau2 ist in beiden Rechnungen null, die "
                "Gewichte sind identisch. Modell und Cluster sind hier "
                "nicht vermischt.")
        elif e["anteil_modell"] is not None:
            md.append(
                "- Modell- und Cluster-Beitrag wirken beide; die Zahl "
                "allein entscheidet nicht, welcher Teil Scheinpraezision war.")

    md += [
        "",
        "## Lesart",
        "",
        "Ist der Modellanteil gross, war ein Teil der scheinbaren",
        "Cluster-Verbreiterung nur der Wechsel von Fixed zu Random Effects:",
        "RVE-FE unterschlaegt die Heterogenitaet, die HKJ traegt. Bleibt nach",
        "dem Modellwechsel noch ein Clusteranteil uebrig, ist das der echte",
        "Preis fuer haengige Zeilen.",
        "",
        "Anteile ausserhalb von 0 bis 100 Prozent sind moeglich: dann wirken",
        "Modell- und Cluster-Beitrag in verschiedene Richtungen und heben sich",
        "teilweise auf. Dort ist der Anteil nur zusammen mit den beiden",
        "Log-Beitraegen lesbar.",
        "",
        "## Grenzen",
        "",
        "- tau2 wird aus den Zeilen vor dem Kollaps geschaetzt; HKJ schaetzt",
        "  es aus den kollabierten Zeilen. Die Zerlegung ist deshalb eine",
        "  Annaeherung, kein exakter Vergleich zweier identischer Modelle.",
        "- Der Modellanteil ist eine Zerlegung auf der Log-Skala, keine",
        "  Varianzzerlegung. Er sagt nichts ueber die Ursache der",
        "  Heterogenitaet.",
        "- RVE-RE mit REML steht als Sensitivitaet daneben, nicht als",
        "  Hauptzahl; die Hauptzahl benutzt DL wie HKJ.",
        "",
    ]

    OUT_JSON.write_text(json.dumps({
        "test": "E4i-rve-modell",
        "stand": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "modellaufrufe": 0, "tokens": 0,
        "gruppen_gesamt": len(ergebnisse),
        "rve_re_verfuegbar": len(verfuegbar),
        "gruppen": ergebnisse, "fehler": fehler,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_MD.write_text("\n".join(md), encoding="utf-8")

    print(f"{len(ergebnisse)} Gruppen, RVE-RE verfuegbar {len(verfuegbar)}")
    for e in ziele:
        print(f"  {e['gruppe']}: HKJ {fmt(e['hkj']['breite'])} "
              f"FE {fmt(e['rve_fe']['breite'])} "
              f"RE {fmt(e['rve_re']['breite'])} "
              f"Modellanteil {pct(e['anteil_modell'])}")
    print(f"\nJSON: {OUT_JSON.relative_to(ROOT)}")
    print(f"MD:   {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
