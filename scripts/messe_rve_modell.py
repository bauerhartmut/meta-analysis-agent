"""E4j - wie viel der RVE-Verbreiterung ist Modell, Cluster, Duplikation?

Vier Rechnungen, drei davon auf demselben Material (Zeilen vor dem Kollaps):

    HKJ(koll)  pool(kept)          RE, dedupliziert, w = 1/(v + tau2)
    HKJ(alle)  pool(sub_rows)      RE, alle Zeilen, w = 1/(v + tau2)
    RVE-FE     pool_rve(sub_rows)  FE, w = 1/v
    RVE-RE     pool_rve(sub_rows, weights="random")
                                   RE, w = 1/(v + tau2), Cluster-Sandwich

HKJ(alle) und RVE-RE benutzen dieselben Zeilen und dieselbe tau2-Schaetzung
(beide DL ueber `_tau2_dersimonian_laird`). Ihr Unterschied ist reine
Cluster-Korrektur. Die Zerlegung auf der Log-Skala:

    ln(w_RE / w_HKJ(koll)) = ln(w_RE / w_HKJ(alle))      Cluster
                           + ln(w_HKJ(alle) / w_HKJ(koll)) Duplikation

und getrennt davon der Modellwechsel FE -> RE:

    ln(w_RE / w_FE)                                        Modell

Modell und Cluster sind nicht additiv zueinander: Sie beantworten zwei
Fragen (Gewichte vs. Abhaengigkeit). Nur die Summe Cluster + Duplikation
ergibt die Verbreiterung gegenueber dem Report-Wert.

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


def logfaktor(zaehler, nenner):
    if not zaehler or not nenner:
        return None
    return math.log(zaehler / nenner)


def ist_ziel(name):
    text = name.lower()
    return any(ziel in text for ziel in ZIELE)


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
                hkj_alle = pool(sub_rows)
                fe = pool_rve(sub_rows)
                re_dl = pool_rve(sub_rows, weights="random")
                re_reml = pool_rve(sub_rows, weights="random",
                                   tau2_method="reml")
                b_hkj, b_alle = breite(hkj), breite(hkj_alle)
                b_fe, b_re = breite(fe), breite(re_dl)
                ergebnisse.append({
                    "datei": path.relative_to(ROOT).as_posix(),
                    "gruppe": f"{outcome} [{scale}]{sub_label}",
                    "k": int(hkj.get("k") or 0),
                    "zeilen": len(sub_rows),
                    "M": fe.get("M"),
                    "hkj": {"pooled": hkj.get("pooled"),
                            "ci": [hkj.get("ci_low"), hkj.get("ci_high")],
                            "breite": b_hkj, "tau2": hkj.get("tau2")},
                    "hkj_alle": {"pooled": hkj_alle.get("pooled"),
                                 "ci": [hkj_alle.get("ci_low"),
                                        hkj_alle.get("ci_high")],
                                 "breite": b_alle,
                                 "tau2": hkj_alle.get("tau2"),
                                 "k": hkj_alle.get("k")},
                    "rve_fe": {"pooled": fe.get("pooled"), "breite": b_fe,
                               "available": fe.get("available")},
                    "rve_re": {"pooled": re_dl.get("pooled"), "breite": b_re,
                               "tau2": re_dl.get("tau2"),
                               "available": re_dl.get("available")},
                    "rve_re_reml": {"breite": breite(re_reml),
                                    "tau2": re_reml.get("tau2"),
                                    "available": re_reml.get("available")},
                    "tau2_gleich": (hkj_alle.get("tau2") == re_dl.get("tau2")),
                    "faktor_re_hkj": faktor(b_re, b_hkj),
                    "faktor_re_hkj_alle": faktor(b_re, b_alle),
                    "faktor_re_fe": faktor(b_re, b_fe),
                    "log_cluster": logfaktor(b_re, b_alle),
                    "log_duplikation": logfaktor(b_alle, b_hkj),
                    "log_modell": logfaktor(b_re, b_fe),
                })

    ziele = sorted((e for e in ergebnisse if ist_ziel(e["gruppe"])),
                   key=lambda e: e["gruppe"])
    verfuegbar = [e for e in ergebnisse if e["rve_re"]["available"]]
    gleich = [e for e in verfuegbar if e["tau2_gleich"]]

    def fmt(value, digits=3):
        return "-" if value is None else f"{float(value):.{digits}f}"

    def pct_of(basis, teil):
        if basis is None or teil is None or abs(basis) < 1e-12:
            return "-"
        return f"{100 * teil / basis:.0f}%"

    md = [
        "# E4i - RVE mit Random-Effects-Gewichten",
        "",
        f"Stand: {time.strftime('%Y-%m-%d %H:%M')} · Modellaufrufe: 0 · Tokens: 0",
        "",
        "| Kuerzel | Aufruf | Material | Gewichte |",
        "|---|---|---|---|",
        "| HKJ | `pool(kept)` | kollabierte Zeilen | `1/(v + tau2)`, DL |",
        "| HKJ(alle) | `pool(sub_rows)` | Zeilen vor dem Kollaps | `1/(v + tau2)`, DL |",
        "| RVE-FE | `pool_rve(sub_rows)` | Zeilen vor dem Kollaps | `1/v` |",
        "| RVE-RE | `pool_rve(sub_rows, weights=\"random\")` | Zeilen vor dem Kollaps | `1/(v + tau2)`, DL |",
        "",
        "Zerlegung auf der Log-Skala, jede Stufe auf gleichen Gewichten:",
        "",
        "- **Cluster**: `ln(RE_RVE / HKJ(alle))` - gleiche Zeilen, gleiche tau2,",
        "  naiver SE gegen Cluster-Sandwich.",
        "- **Duplikation**: `ln(HKJ(alle) / HKJ(koll))` - mehr Zeilen als",
        "  unabhaengig gezaehlt; negativ heisst: die naive Rechnung wird",
        "  scheinbar praeziser, je mehr abhaengige Zeilen sie sieht.",
        "- **Modell**: `ln(RE_RVE / RVE_FE)` - der Wechsel der Gewichte.",
        "",
        "## Zielgruppen",
        "",
        "| Gruppe | k | Zeilen | M | HKJ(koll) | HKJ(alle) | RVE-FE | RVE-RE "
        "| RE/HKJ | RE/HKJ(alle) | Modell |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for e in ziele:
        md.append(
            f"| {e['gruppe']} | {e['k']} | {e['zeilen']} | {e['M']} "
            f"| {fmt(e['hkj']['breite'])} | {fmt(e['hkj_alle']['breite'])} "
            f"| {fmt(e['rve_fe']['breite'])} | {fmt(e['rve_re']['breite'])} "
            f"| {fmt(e['faktor_re_hkj'], 2)} | {fmt(e['faktor_re_hkj_alle'], 2)} "
            f"| {fmt(e['faktor_re_fe'], 2)} |")

    md += ["", "## Alle Gruppen", ""]
    md.append(f"- Gruppen mit k >= 2: {len(ergebnisse)}")
    md.append(f"- RVE-RE verfuegbar: {len(verfuegbar)}")
    md.append(f"- tau2 in HKJ(alle) und RVE-RE identisch: {len(gleich)} von "
              f"{len(verfuegbar)}")
    md += ["", "### Tabelle", "",
           "| Gruppe | k | M | HKJ(koll) | HKJ(alle) | RVE-FE | RVE-RE "
           "| RVE-RE(REML) | Cluster (log) | Duplikation (log) | Modell (log) "
           "| RE/HKJ | RE/HKJ(alle) |",
           "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for e in sorted(ergebnisse, key=lambda x: x["gruppe"]):
        md.append(
            f"| {e['gruppe']} | {e['k']} | {e['M']} "
            f"| {fmt(e['hkj']['breite'])} | {fmt(e['hkj_alle']['breite'])} "
            f"| {fmt(e['rve_fe']['breite'])} | {fmt(e['rve_re']['breite'])} "
            f"| {fmt(e['rve_re_reml']['breite'])} "
            f"| {fmt(e['log_cluster'], 3)} | {fmt(e['log_duplikation'], 3)} "
            f"| {fmt(e['log_modell'], 3)} "
            f"| {fmt(e['faktor_re_hkj'], 2)} | {fmt(e['faktor_re_hkj_alle'], 2)} |")

    for titel, schluessel in (("MACE", "major adverse cardiovascular"),
                              ("incident CVD", "incident cardiovascular")):
        treffer = [e for e in ziele if schluessel in e["gruppe"]]
        md += ["", f"## {titel} im Detail", ""]
        if not treffer:
            md.append("Gruppe in diesem Datenbestand nicht gefunden.")
            continue
        for e in treffer:
            gesamt = None
            if e["log_cluster"] is not None and e["log_duplikation"] is not None:
                gesamt = e["log_cluster"] + e["log_duplikation"]
            md += [
                f"- Breiten: HKJ(koll) {fmt(e['hkj']['breite'])}, "
                f"HKJ(alle) {fmt(e['hkj_alle']['breite'])}, RVE-FE "
                f"{fmt(e['rve_fe']['breite'])}, RVE-RE "
                f"{fmt(e['rve_re']['breite'])}.",
                f"- tau2: HKJ(koll) {fmt(e['hkj']['tau2'], 4)}, HKJ(alle) "
                f"{fmt(e['hkj_alle']['tau2'], 4)}, RVE-RE "
                f"{fmt(e['rve_re']['tau2'], 4)} "
                f"({e['zeilen']} Zeilen, {e['M']} Cluster).",
                f"- Cluster-Beitrag: {fmt(e['log_cluster'], 3)} "
                f"({pct_of(gesamt, e['log_cluster'])} der Gesamtverbreiterung), "
                f"Duplikation: {fmt(e['log_duplikation'], 3)} "
                f"({pct_of(gesamt, e['log_duplikation'])}), "
                f"Summe: {fmt(gesamt, 3)} = RE/HKJ "
                f"{fmt(e['faktor_re_hkj'], 2)}.",
                f"- Modellwechsel FE -> RE: {fmt(e['log_modell'], 3)} "
                f"(Faktor {fmt(e['faktor_re_fe'], 2)}), separat zu lesen.",
            ]

    md += [
        "",
        "## Lesart",
        "",
        "tau2 wird in HKJ(alle) und RVE-RE aus denselben Zeilen mit derselben",
        "Methode geschaetzt; der Unterschied zwischen beiden ist damit reine",
        "Cluster-Korrektur. Die Duplikation ist der Preis der kollabierten",
        "Rechnung: Sie sieht weniger Zeilen und wird dadurch breiter - aber",
        "nicht, weil sie ehrlicher waere, sondern weil ihr Information fehlt.",
        "",
        "Der Modellwechsel FE -> RE ist keine Stufe dieser Kette: Er",
        "beantwortet die Frage, ob die Gewichte die Heterogenitaet tragen.",
        "",
        "## Grenzen",
        "",
        "- HKJ(alle) behandelt abhaengige Zeilen als unabhaengig - genau der",
        "  Fehler, den RVE korrigiert. Der Vergleich ist die Zerlegung dieses",
        "  Effekts, kein Modellvergleich zweier korrekter Rechnungen.",
        "- Die Zerlegung ist logarithmisch in den Breiten, keine",
        "  Varianzzerlegung.",
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
        "tau2_identisch": len(gleich),
        "gruppen": ergebnisse, "fehler": fehler,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_MD.write_text("\n".join(md), encoding="utf-8")

    print(f"{len(ergebnisse)} Gruppen, RVE-RE verfuegbar {len(verfuegbar)}, "
          f"tau2 identisch {len(gleich)}")
    for e in ziele:
        print(f"  {e['gruppe']}: HKJ {fmt(e['hkj']['breite'])} "
              f"HKJ(alle) {fmt(e['hkj_alle']['breite'])} "
              f"FE {fmt(e['rve_fe']['breite'])} "
              f"RE {fmt(e['rve_re']['breite'])} "
              f"Cluster {fmt(e['log_cluster'], 3)} "
              f"Dup {fmt(e['log_duplikation'], 3)} "
              f"Modell {fmt(e['log_modell'], 3)}")
    print(f"\nJSON: {OUT_JSON.relative_to(ROOT)}")
    print(f"MD:   {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
