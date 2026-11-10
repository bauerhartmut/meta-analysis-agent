"""Die poolbaren Pass-B-Zeilen ohne Zwilling: echter Fund oder fehlende Gegenlesung?

Die Dedup-Regel verwirft nur Kopien. Uebrig bleiben Zweitlesungen, die in Pass 1
keinen Zwilling haben (Textschluessel, Wert oder Quote). Diese Zeilen sind im
Pool, aber niemand hat sie gegengelesen. Hier wird jede einzeln klassifiziert -
read-only auf Kopien, ohne Modellaufruf:

* nur_pass_b ............. Pass 1 hat fuer diese Quelle gar keine Zeile
* gleicher_wert_andere_se  gleiche Quelle, gleiche Zahl, aber SE fehlt/weicht
* gleiche_stelle .......... gleiche Quelle, Quote teilt den Anfang, Text weicht ab
* anderes_outcome ......... Pass 1 las dieselbe Quelle fuer ein anderes Mass
* andere_aussage .......... Pass 1 las dieselbe Quelle, aber anderen Kontrast

Die Definition der "ohne Zwilling"-Menge ist die aus
`messe_lesepass_dedup_20261110.py` (Teil D), damit die Zahl 45 reproduzierbar
bleibt.

Aufruf:
    export PYTHONIOENCODING=utf-8
    .venv/bin/python.exe scripts/klassifiziere_pass_b_20261110.py
"""

import json
import sqlite3
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from messe_quote_luecken_bestand import kopiere, aufraeumen            # noqa: E402
from messe_effekt_duplikate import gruppe                        # noqa: E402
from research_agent.meta.pooling import build_analysis, standardize    # noqa: E402

VALIDIERUNG = ROOT / "data" / "bench" / "validierung"
OUT_JSON = VALIDIERUNG / "pass_b_ohne_zwilling_20261110.json"
OUT_MD = VALIDIERUNG / "pass_b_ohne_zwilling_20261110.md"


def pass_nummer(row):
    try:
        return int(row.get("extraction_pass") or 1)
    except (TypeError, ValueError):
        return 1


def zahl(feld, row):
    wert = row.get(feld)
    if wert is None:
        return None
    try:
        return round(float(wert), 9)
    except (TypeError, ValueError):
        return None


def schluessel(row):
    return tuple(
        " ".join(str(row.get(feld) or "").split()).lower()
        for feld in ("source_id", "outcome", "comparison", "direction")
    )


def wert(row):
    return (str(row.get("source_id") or ""), zahl("effect", row), zahl("se", row))


def zitat(row):
    return (str(row.get("source_id") or ""),
            " ".join(str(row.get("quote") or "").split()).lower()[:200])


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


def klassifiziere(row, erst, texte, werte, zitate):
    """Eine Zeile ohne Zwilling einordnen - mit dem Material, das Pass 1 hat."""
    quelle = str(row.get("source_id") or "")
    erst_quelle = [r for r in erst if str(r.get("source_id") or "") == quelle]
    basis = {
        "quelle": quelle,
        "outcome": str(row.get("outcome") or ""),
        "effect": zahl("effect", row),
        "se": zahl("se", row),
        "disputed": int(row.get("disputed") or 0),
        "erstlesungen_der_quelle": len(erst_quelle),
        "outcomes_pass_1": sorted({str(r.get("outcome") or "")
                                   for r in erst_quelle})[:5],
    }
    if not erst_quelle:
        return "nur_pass_b", basis

    gleicher_effekt = ([r for r in erst_quelle
                        if zahl("effect", r) == zahl("effect", row)]
                       if zahl("effect", row) is not None else [])
    if gleicher_effekt:
        basis["pass_1_se"] = [zahl("se", r) for r in gleicher_effekt][:3]
        return "gleicher_wert_andere_se", basis

    anfang = zitat(row)[1][:60]
    if anfang:
        teilt = [r for r in erst_quelle
                 if zitat(r)[1][:60] and (zitat(r)[1][:60] in anfang
                                          or anfang in zitat(r)[1][:60])]
        if teilt:
            basis["pass_1_zitat"] = [zitat(r)[1][:60] for r in teilt][:2]
            return "gleiche_stelle", basis

    gleiches_outcome = [r for r in erst_quelle
                        if str(r.get("outcome") or "").strip().lower()
                        == str(row.get("outcome") or "").strip().lower()]
    if not gleiches_outcome:
        return "anderes_outcome", basis
    basis["pass_1_vergleiche"] = sorted(
        {str(r.get("comparison") or "") for r in gleiches_outcome})[:3]
    return "andere_aussage", basis


def main() -> int:
    db_pfade = [p for p in sorted((ROOT / "data").rglob("*.db"))
                if "-usage" not in p.name]
    verteilung = Counter()
    eintraege = []
    fehler = []
    geprueft = 0
    for index, path in enumerate(db_pfade):
        try:
            rows = lies(path, index)
        except Exception as exc:                              # noqa: BLE001
            fehler.append({"datei": path.relative_to(ROOT).as_posix(),
                           "fehler": str(exc)})
            continue
        if not rows:
            continue
        # Dieselbe Grundgesamtheit wie Teil D der E5-Messung: nur die
        # Themen-DBs, nicht Alt- und Testbestände.
        if gruppe(path) != "themen":
            continue
        geprueft += 1
        erst = [r for r in rows if pass_nummer(r) == 1]
        ueber = [r for r in rows if pass_nummer(r) > 1]
        if not ueber:
            continue
        texte = {schluessel(r) for r in erst}
        werte = {wert(r) for r in erst}
        zitate = {zitat(r) for r in erst}

        # Poolbarkeit im Hauptpfad: landet die Zeile nach build_analysis in
        # einer Gruppe? Ueber Quelle, Zahl und SE gematcht.
        try:
            analyse = build_analysis(rows)
        except Exception:                                     # noqa: BLE001
            analyse = {"groups": {}}
        im_pool = {
            (str(r.get("source_id") or ""), round(float(r["est"]), 9),
             round(float(r["se"]), 9))
            for group in (analyse.get("groups") or {}).values()
            for r in group.get("rows") or []
            if r.get("est") is not None and r.get("se") is not None
        }
        for row in ueber:
            if (schluessel(row) in texte or wert(row) in werte
                    or zitat(row) in zitate):
                continue
            klasse, basis = klassifiziere(row, erst, texte, werte, zitate)
            basis.update({
                "klasse": klasse,
                "datei": path.relative_to(ROOT).as_posix(),
                "id": row.get("id"),
                "pass": pass_nummer(row),
                # Poolbar heisst: standardize akzeptiert die Zeile. Eine
                # vorhandene Zahl genuegt nicht - Review-Aggregate und
                # fehlende Belege fallen dort heraus.
                "poolbar": standardize(row)[3] == "",
                "im_pool": (str(row.get("source_id") or ""),
                            zahl("effect", row), zahl("se", row)) in im_pool,
            })
            if not basis["poolbar"]:
                basis["klasse"] = klasse + "_unpoolbar"
            verteilung[basis["klasse"]] += 1
            eintraege.append(basis)

    ergebnis = {
        "definition": "Pass > 1 ohne Treffer in Textschluessel, Wert oder "
                      "Quote gegen alle Zeilen aus Pass 1",
        "dbs_geprueft": geprueft,
        "dbs_ohne_tabelle": fehler,
        "ohne_zwilling_gesamt": len(eintraege),
        "davon_poolbar": sum(1 for e in eintraege if e["poolbar"]),
        "davon_im_pool": sum(1 for e in eintraege if e["im_pool"]),
        "verteilung": dict(verteilung.most_common()),
        "eintraege": eintraege,
    }
    VALIDIERUNG.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(ergebnis, ensure_ascii=False, indent=2),
                        encoding="utf-8")

    zeilen = [
        "# Pass-B-Zeilen ohne Zwilling (2026-11-10)",
        "",
        f"Geprueft: {geprueft} Datenbanken mit `study_effects`, "
        f"{len(fehler)} ohne Tabelle (siehe JSON).",
        "",
        "Definition: `extraction_pass > 1` ohne Treffer in Textschluessel "
        "(Quelle, Outcome, Vergleich, Richtung), Wert (Quelle, Effekt, SE) "
        "oder Quote (Quelle, erste 200 Zeichen) gegen alle Zeilen aus Pass 1. "
        "Dieselbe Definition wie Teil D der E5-Messung.",
        "",
        f"**{len(eintraege)} Zeilen ohne Zwilling**, davon "
        f"{ergebnis['davon_poolbar']} mit Zahl und SE und "
        f"{ergebnis['davon_im_pool']} nach `build_analysis` in einer Gruppe.",
        "",
        "## Verteilung",
        "",
        "| Klasse | Zeilen | Bedeutung |",
        "|---|---:|---|",
    ]
    bedeutung = {
        "nur_pass_b": "Pass 1 hat die Quelle nicht gelesen - echter Fund",
        "gleicher_wert_andere_se": "gleiche Zahl, aber SE fehlt/weicht - "
                                   "Grenzfall der Wertregel",
        "gleiche_stelle": "Quote teilt den Anfang, Text weicht ab - Grenzfall "
                          "der Zitatregel",
        "anderes_outcome": "Pass 1 las dieselbe Quelle fuer ein anderes Mass - "
                           "eigenstaendiger Fund",
        "andere_aussage": "Pass 1 las dieselbe Quelle, anderen Kontrast - "
                          "eigenstaendiger Fund",
    }
    for klasse, anzahl in verteilung.most_common():
        basis = klasse.replace("_unpoolbar", "")
        zeilen.append(f"| `{klasse}` | {anzahl} | {bedeutung.get(basis, '-')} |")
    zeilen += ["", "## Beispiele", ""]
    for klasse, _ in verteilung.most_common():
        beispiele = [e for e in eintraege if e["klasse"] == klasse][:4]
        zeilen.append(f"### `{klasse}` ({len(beispiele)} von "
                      f"{verteilung[klasse]} gezeigt)")
        zeilen.append("")
        for e in beispiele:
            zeilen.append(
                f"- {Path(e['datei']).name}: `{e['quelle']}` / "
                f"'{e['outcome']}' / Effekt {e['effect']} / SE {e['se']} / "
                f"Pass-1-Zeilen der Quelle: {e['erstlesungen_der_quelle']}"
                + (f" / dort: {', '.join(e['outcomes_pass_1'])}"
                   if e.get("outcomes_pass_1") else "")
            )
        zeilen.append("")
    OUT_MD.write_text("\n".join(zeilen), encoding="utf-8")

    print(f"DBs: {geprueft}, ohne Tabelle: {len(fehler)}")
    print(f"Ohne Zwilling: {len(eintraege)} "
          f"(poolbar {ergebnis['davon_poolbar']}, "
          f"im Pool {ergebnis['davon_im_pool']})")
    for klasse, anzahl in verteilung.most_common():
        print(f"  {klasse}: {anzahl}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
