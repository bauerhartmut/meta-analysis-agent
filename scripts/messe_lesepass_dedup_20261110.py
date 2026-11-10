"""E5 - Wirkung des Lesepass-Filters: wie viele Zeilen, welches k, welches KI?

Drei Teile, alle deterministisch und ohne Modellaufruf:

A. Datenlage: Verteilung von `extraction_pass` in allen DBs mit `study_effects`.
B. Mechanismusprobe an echten Zeilen: je poolbarer Zeile eine Zweitlesung
   (identische Zahl, identisches SE, `extraction_pass = 2`) und dann
   `standardize` + `pool` - einmal mit Filter (neu) und einmal mit der Kopie
   als Erstlesung (ohne Regel). Gezeigt wird k, Punktschaetzer und KI-Breite.
C. Wo der Hauptpfad `build_analysis` betroffen ist: alt (alle Zeilen als
   Erstlesung) gegen neu (Original) auf den echten Zeilen der Themen-DBs.

B ist eine deklarierte Konstruktion, kein Messwert ueber die Datenlage: sie
zeigt den Mechanismus, weil gespeicherte Doppelpässe in den Daten fehlen.
Alles read-only auf Kopien, die Kopie wird gelesen und geloescht.

Aufruf:
    export PYTHONIOENCODING=utf-8
    .venv/bin/python.exe scripts/messe_lesepass_dedup_20261110.py
"""

import json
import statistics
import sqlite3
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from messe_quote_luecken_bestand import kopiere, aufraeumen            # noqa: E402
from messe_effekt_duplikate import gruppe                             # noqa: E402
from research_agent.meta.outcome_labels import normalize_outcome       # noqa: E402
from research_agent.meta.pooling import (                              # noqa: E402
    _drop_zweitlesungen, build_analysis, pool, standardize,
)

VALIDIERUNG = ROOT / "data" / "bench" / "validierung"
OUT_JSON = VALIDIERUNG / "lesepass_filter_20261110.json"
OUT_MD = VALIDIERUNG / "lesepass_filter_20261110.md"


def lies(path: Path, index: int):
    dest = kopiere(path, index)
    conn = None
    try:
        conn = sqlite3.connect(dest, timeout=10)
        conn.row_factory = sqlite3.Row
        rows = [dict(r) for r in conn.execute("SELECT * FROM study_effects")]
    finally:
        if conn is not None:
            conn.close()
        aufraeumen(dest)
    return rows


def standardisierte(rows):
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
            "_roh": row,
        })
        out.append(item)
    return out


def nach_gruppe(items):
    g = {}
    for item in items:
        g.setdefault((item["outcome_group"], item["scale"]), []).append(item)
    return g


def kurz(res):
    if res is None or res.get("pooled") is None:
        return None
    return {
        "k": int(res["k"]),
        "pooled": round(float(res["pooled"]), 6),
        "ci": [round(float(res["ci_low"]), 6), round(float(res["ci_high"]), 6)],
        "breite": round(float(res["ci_high"]) - float(res["ci_low"]), 6),
    }


def schluessel(row):
    """Textschluessel wie `_match_key`: Quelle, Outcome, Vergleich, Richtung."""
    return tuple(
        " ".join(str(row.get(feld) or "").split()).lower()
        for feld in ("source_id", "outcome", "comparison", "direction")
    )


def wert(row):
    """Hartes Duplikatmerkmal: gleiche Quelle, gleiche Zahl, gleiches SE."""
    def zahl(feld):
        v = row.get(feld)
        return None if v is None else round(float(v), 9)
    return (str(row.get("source_id") or ""), zahl("effect"), zahl("se"))


def zitat(row):
    return (str(row.get("source_id") or ""),
            " ".join(str(row.get("quote") or "").split()).lower()[:200])


def paarung(rows):
    """Hat jede Zeile ueber Pass 1 eine Erstlesung? Text, Wert und Quote."""
    erst = [r for r in rows if pass_nummer(r) == 1]
    ueber = [r for r in rows if pass_nummer(r) > 1]
    texte = {schluessel(r) for r in erst}
    werte = {wert(r) for r in erst}
    zitate = {zitat(r) for r in erst}
    mit_text = sum(1 for r in ueber if schluessel(r) in texte)
    mit_wert = sum(1 for r in ueber if wert(r) in werte)
    mit_zitat = sum(1 for r in ueber if zitat(r) in zitate)
    ohne = sum(1 for r in ueber
               if schluessel(r) not in texte and wert(r) not in werte
               and zitat(r) not in zitate)
    return {
        "pass_ueber_1": len(ueber),
        "mit_erstlesung": mit_text,
        "ohne_erstlesung": len(ueber) - mit_text,
        "mit_wert_zwilling": mit_wert,
        "mit_zitat_zwilling": mit_zitat,
        "ohne_jeden_zwilling": ohne,
    }


def pass_nummer(row):
    try:
        return int(row.get("extraction_pass") or 1)
    except (TypeError, ValueError):
        return 1


def main() -> int:
    db_pfade = [p for p in sorted((ROOT / "data").rglob("*.db"))
                if "-usage" not in p.name]
    gelesen = []
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
        gelesen.append({
            "datei": path.relative_to(ROOT).as_posix(),
            "gruppe": gruppe(path),
            "rows": rows,
        })

    # ---- A: Datenlage -----------------------------------------------------
    verteilung = Counter()
    je_db = []
    for eintrag in gelesen:
        z = Counter(str(r.get("extraction_pass")) for r in eintrag["rows"])
        verteilung.update(z)
        if any(pass_nummer(r) > 1 for r in eintrag["rows"]):
            je_db.append({
                "datei": eintrag["datei"],
                "verteilung": dict(z),
                "zeilen_ueber_1": sum(1 for r in eintrag["rows"]
                                      if pass_nummer(r) > 1),
            })

    # ---- B: Mechanismusprobe an echten Zeilen -----------------------------
    kandidaten = []
    for eintrag in gelesen:
        items = standardisierte(eintrag["rows"])
        if items:
            kandidaten.append((len(items), eintrag["datei"], items))
    kandidaten.sort(reverse=True)
    probe_db, probe_gruppen, probe_agg = None, [], {}
    if kandidaten:
        _, probe_db, items = kandidaten[0]
        for (outcome, scale), basis in sorted(nach_gruppe(items).items()):
            if len(basis) < 2:
                continue
            roh = [it["_roh"] for it in basis]
            ohne = standardisierte(roh + [dict(r, extraction_pass=1) for r in roh])
            kopien, _ = _drop_zweitlesungen(
                roh + [dict(r, extraction_pass=2) for r in roh])
            mit = standardisierte(kopien)
            ref = pool(basis)
            res_ohne = pool([i for i in ohne
                             if (i["outcome_group"], i["scale"]) == (outcome, scale)])
            res_mit = pool([i for i in mit
                            if (i["outcome_group"], i["scale"]) == (outcome, scale)])
            a, b, c = kurz(ref), kurz(res_ohne), kurz(res_mit)
            if a is None or b is None or c is None:
                continue
            probe_gruppen.append({
                "outcome": outcome, "scale": scale, "n_zeilen": len(basis),
                "referenz": a, "ohne_regel": b, "mit_regel": c,
                "breite_ohne_regel_rel": round(
                    (a["breite"] - b["breite"]) / a["breite"], 4)
                if a["breite"] else None,
                "filter_haelt_referenz": c["k"] == a["k"],
            })
        if probe_gruppen:
            rel = [g["breite_ohne_regel_rel"] for g in probe_gruppen
                   if g["breite_ohne_regel_rel"] is not None]
            probe_agg = {
                "gruppen": len(probe_gruppen),
                "k_summe_referenz": sum(g["referenz"]["k"] for g in probe_gruppen),
                "k_summe_ohne_regel": sum(g["ohne_regel"]["k"] for g in probe_gruppen),
                "k_summe_mit_regel": sum(g["mit_regel"]["k"] for g in probe_gruppen),
                "gruppen_mit_k_verdoppelt": sum(
                    1 for g in probe_gruppen
                    if g["ohne_regel"]["k"] == 2 * g["referenz"]["k"]),
                "filter_haelt_referenz": all(g["filter_haelt_referenz"]
                                             for g in probe_gruppen),
                "breiten_reduktion_median": (round(statistics.median(rel), 4)
                                             if rel else None),
                "breiten_reduktion_max": round(max(rel), 4) if rel else None,
            }

    # ---- C: Hauptpfad build_analysis auf echten Zeilen --------------------
    haupt = []
    for eintrag in gelesen:
        if eintrag["gruppe"] != "themen":
            continue
        rows = eintrag["rows"]
        alt = build_analysis([dict(r, extraction_pass=1) for r in rows])
        neu = build_analysis(rows)
        k_alt = sum(int(g.get("k") or 0) for g in alt["groups"].values())
        k_neu = sum(int(g.get("k") or 0) for g in neu["groups"].values())
        haupt.append({
            "datei": eintrag["datei"],
            "zeilen": len(rows),
            "pass_ueber_1": sum(1 for r in rows if pass_nummer(r) > 1),
            "gruppen": len(neu["groups"]),
            "k_summe_alt": k_alt,
            "k_summe_neu": k_neu,
            "abgelehnt_alt": len(alt["excluded"]),
            "abgelehnt_neu": len(neu["excluded"]),
            "paarung": paarung(rows),
        })

    print(f"{len(gelesen)} DBs gelesen, {len(fehler)} Fehler")
    print("Verteilung extraction_pass:",
          dict(sorted(verteilung.items(), key=lambda kv: str(kv[0]))))
    print(f"DBs mit Pass > 1: {len(je_db)}")
    if probe_agg:
        print(f"Mechanismusprobe: {probe_agg['gruppen']} Gruppen aus {probe_db}, "
              f"k {probe_agg['k_summe_referenz']} -> "
              f"{probe_agg['k_summe_ohne_regel']} (ohne Regel) -> "
              f"{probe_agg['k_summe_mit_regel']} (mit Regel), "
              f"KI-Breite median {probe_agg['breiten_reduktion_median']:.1%} "
              f"enger ohne Regel")
    print(f"Hauptpfad: {sum(h['pass_ueber_1'] for h in haupt)} Zeilen mit "
          f"Pass > 1 in {len(haupt)} Themen-DBs")

    ergebnis = {
        "test": "E5-lesepass-filter",
        "stand": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "modellaufrufe": 0,
        "tokens": 0,
        "datenlage": {
            "dbs": len(gelesen),
            "zeilen": sum(len(e["rows"]) for e in gelesen),
            "verteilung": dict(verteilung),
            "dbs_mit_pass_ueber_1": je_db,
        },
        "mechanismusprobe": {
            "datei": probe_db,
            "hinweis": "Konstruktion: echte Zeilen, je einmal zusaetzlich als "
                       "Zweitlesung. Kein Messwert ueber die Datenlage.",
            "aggregat": probe_agg,
            "gruppen": probe_gruppen,
        },
        "hauptpfad": haupt,
        "fehler": fehler,
    }
    OUT_JSON.write_text(json.dumps(ergebnis, ensure_ascii=False, indent=2),
                        encoding="utf-8")

    md = [
        "# E5 - Wirkung des Lesepass-Filters auf Pool und Intervall",
        "",
        f"Stand: {time.strftime('%Y-%m-%d %H:%M')} · Modellaufrufe: 0 · Tokens: 0",
        "",
        "Read-only auf Kopien. Teil B ist eine Konstruktion an echten Zeilen,",
        "kein Messwert ueber die Datenlage.",
        "",
        "## A. Datenlage: welche Lesepaesse sind gespeichert?",
        "",
        f"{len(gelesen)} DBs mit {ergebnis['datenlage']['zeilen']} Zeilen gelesen.",
        "",
        "| extraction_pass | Zeilen |",
        "|---|---:|",
    ]
    for key, wert in sorted(verteilung.items(), key=lambda kv: str(kv[0])):
        md.append(f"| {key} | {wert} |")
    md += [
        "",
        f"DBs mit mindestens einer Zeile ueber Pass 1: **{len(je_db)}**.",
        "",
    ]
    if not je_db:
        md += [
            "Die direkte Wirkung auf gespeicherte Daten ist derzeit null:",
            "Doppelpässe wurden bisher nicht persistiert (der Doppelpass-Lauf",
            "schrieb bewusst nichts). Der Filter ist Vorsorge, keine Korrektur",
            "vorhandener Zahlen.",
            "",
        ]
    if probe_agg:
        md += [
            "## B. Mechanismusprobe: was eine Doppellesung anrichten wuerde",
            "",
            f"Datenbasis: `{probe_db}`, {probe_agg['gruppen']} Gruppen mit k >= 2.",
            "Je Gruppe drei Rechnungen: Referenz (echte Zeilen), ohne Regel",
            "(jede Zeile zusaetzlich als Erstlesung) und mit Regel (zusaetzliche",
            "Zeile als Zweitlesung).",
            "",
            f"- k-Summe: {probe_agg['k_summe_referenz']} Referenz, "
            f"{probe_agg['k_summe_ohne_regel']} ohne Regel, "
            f"{probe_agg['k_summe_mit_regel']} mit Regel.",
            f"- In {probe_agg['gruppen_mit_k_verdoppelt']} von "
            f"{probe_agg['gruppen']} Gruppen verdoppelt die Rechnung ohne Regel "
            "das k.",
            f"- KI-Breite ohne Regel im Median "
            f"{probe_agg['breiten_reduktion_median']:.1%} enger, maximal "
            f"{probe_agg['breiten_reduktion_max']:.1%}.",
            f"- Filter haelt die Referenz in allen Gruppen: "
            f"{'ja' if probe_agg['filter_haelt_referenz'] else 'NEIN'}.",
            "",
            "| Outcome | Skala | n | k ref | k ohne | k mit | gepoolt ref | "
            "KI-Breite ref | Breite ohne | enger um |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
        for g in sorted(probe_gruppen,
                        key=lambda x: -(x["breite_ohne_regel_rel"] or 0))[:12]:
            md.append(
                f"| {g['outcome']} | {g['scale']} | {g['n_zeilen']} | "
                f"{g['referenz']['k']} | {g['ohne_regel']['k']} | "
                f"{g['mit_regel']['k']} | {g['referenz']['pooled']} | "
                f"{g['referenz']['breite']} | {g['ohne_regel']['breite']} | "
                f"{(g['breite_ohne_regel_rel'] or 0):.1%} |")
        md += [""]
    md += [
        "## C. Hauptpfad `build_analysis` auf den echten Zeilen",
        "",
        "| Datei | Zeilen | Pass > 1 | Gruppen | k alt | k neu | "
        "abgelehnt alt | abgelehnt neu |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for h in haupt:
        md.append(f"| {h['datei']} | {h['zeilen']} | {h['pass_ueber_1']} | "
                  f"{h['gruppen']} | {h['k_summe_alt']} | {h['k_summe_neu']} | "
                  f"{h['abgelehnt_alt']} | {h['abgelehnt_neu']} |")
    md += [
        "",
        "## D. Paarung: hat jede Zweitlesung eine Erstlesung?",
        "",
        "Schluessel wie `_match_key`: Quelle, Outcome, Vergleich, Richtung.",
        "Ohne Pendant ist die Zeile eine Aussage nur aus Pass B - sie faellt",
        "durch den Filter aus dem Pool, ohne je gegengelesen worden zu sein.",
        "",
        "| Datei | Pass > 1 | Text-Zwilling | Wert-Zwilling | Zitat-Zwilling | ohne jeden Zwilling |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for h in haupt:
        pd = h["paarung"]
        md.append(f"| {h['datei']} | {pd['pass_ueber_1']} | "
                  f"{pd['mit_erstlesung']} | {pd['mit_wert_zwilling']} | "
                  f"{pd['mit_zitat_zwilling']} | {pd['ohne_jeden_zwilling']} |")
    md += [
        "",
        "## Grenzen",
        "",
        "",
        "- Teil B verdoppelt jede Zeile einer Gruppe, auch unabhaengige Arme.",
        "  Das ist die Obergrenze des Fehlers, nicht sein typischer Wert.",
        "- Teil B nutzt `pool` ohne `_collapse_same_study`. Im Hauptpfad faengt",
        "  der Kollaps gleiche Quelle und gleiches Outcome bereits ab; deshalb",
        "  ist Teil C die ehrliche Zahl fuer den Berichtspfad.",
        "- Ohne gespeicherte Doppelpässe kann Teil C die Regel nicht zeigen -",
        "  die Null dort ist eine Aussage ueber die Daten, nicht ueber den Code.",
    ]
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"JSON: {OUT_JSON.relative_to(ROOT)}")
    print(f"MD:   {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
