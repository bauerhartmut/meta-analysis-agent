"""Prueft Goldstandard-Annotationen gegen die Regeln des Schemas.

Kein vollstaendiger JSON-Schema-Validator (das Paket `jsonschema` ist im
Projekt nicht installiert und wird nicht nachgezogen). Geprueft werden die
Regeln, die fuer die Annotation zaehlen: Pflichtfelder, Enum-Werte, Quote-
Span gegen den Volltext, Effekt innerhalb des KI, doppelte IDs und Dokumente
ohne Zeile ohne Begruendung.

Mit --entwurf gelten Dokumente ohne Zeile und ohne Begruendung als "offen"
(nicht als Fehler); so lassen sich die leeren Gerueste pruefen. Ohne
--entwurf ist ein solches Dokument ein Fehler.

Aufruf:
    export PYTHONIOENCODING=utf-8
    .venv/bin/python.exe scripts/pruefe_goldstandard.py --entwurf data/golden_effects/goldstandard_A.json
    .venv/bin/python.exe scripts/pruefe_goldstandard.py data/golden_effects/*.json

Exit 0 = keine Fehler. Exit 1 = mindestens ein Fehler.
Der SHA-256 jeder Datei wird ausgegeben (zum Einfrieren).
"""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "docs" / "internal" / "goldstandard_schema.json"


def lade_schema() -> dict:
    return json.loads(SCHEMA.read_text(encoding="utf-8"))


def pruefe_datei(pfad: Path, schema: dict, entwurf: bool = False):
    fehler, offen = [], []
    try:
        daten = json.loads(pfad.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{pfad.name}: nicht lesbar ({exc})"], []

    def f(meldung: str) -> None:
        fehler.append(f"{pfad.name}: {meldung}")

    for feld in schema["required"]:
        if feld not in daten:
            f(f"Pflichtfeld '{feld}' fehlt")
    if daten.get("dataset") != "goldstandard_effects":
        f("dataset muss 'goldstandard_effects' sein")
    if daten.get("version") != "1.0":
        f("version muss '1.0' sein")
    if daten.get("annotator") not in ("A", "B", "consensus"):
        f("annotator muss A, B oder consensus sein")
    if daten.get("blind") is not True and daten.get("annotator") != "consensus":
        f("blind muss true sein (Konsens ausgenommen)")

    effects_schema = schema["$defs"]["effect"]
    erlaubte_typen = effects_schema["properties"]["effect_type"]["enum"]
    erlaubte_designs = schema["$defs"]["document"]["properties"]["design_category"]["enum"]
    erlaubte_schichten = schema["$defs"]["document"]["properties"]["stratum"]["enum"]
    pflicht_effect = effects_schema["required"]
    pflicht_doc = schema["$defs"]["document"]["required"]

    docs = daten.get("documents")
    if not isinstance(docs, list) or not docs:
        f("documents muss eine nicht-leere Liste sein")
        return fehler, offen

    gesehen_docs = set()
    zeilen_gesamt = 0
    for index, doc in enumerate(docs, start=1):
        name = f"Dokument {index} ({str(doc.get('document_id', '?'))[:10]})"
        for feld in pflicht_doc:
            if feld not in doc:
                f(f"{name}: Pflichtfeld '{feld}' fehlt")
        doc_id = str(doc.get("document_id") or "")
        if doc_id in gesehen_docs:
            f(f"{name}: document_id doppelt")
        gesehen_docs.add(doc_id)
        if doc.get("design_category") not in erlaubte_designs:
            f(f"{name}: design_category '{doc.get('design_category')}' unbekannt")
        if doc.get("stratum") not in erlaubte_schichten:
            f(f"{name}: stratum '{doc.get('stratum')}' unbekannt")

        rel = str(doc.get("path") or "")
        if rel != f"fulltext/{doc_id}.txt":
            f(f"{name}: path passt nicht zur document_id (erwartet fulltext/{doc_id}.txt)")
        volltext = ROOT / "data" / rel
        if not volltext.exists():
            f(f"{name}: Volltext fehlt ({rel})")
            text = ""
        else:
            text = volltext.read_text(encoding="utf-8", errors="replace")

        effekte = doc.get("effects")
        if not isinstance(effekte, list):
            f(f"{name}: effects muss eine Liste sein")
            continue
        if not effekte and not str(doc.get("no_effect_reason") or "").strip():
            meldung = f"{name}: keine Zeile und keine Begruendung (no_effect_reason)"
            (offen if entwurf else fehler).append(f"{pfad.name}: {meldung}")

        ids = set()
        for eff in effekte:
            zeilen_gesamt += 1
            eid = str(eff.get("effect_id") or "")
            for feld in pflicht_effect:
                if feld not in eff:
                    f(f"{name}/{eid}: Pflichtfeld '{feld}' fehlt")
            if eid in ids:
                f(f"{name}: effect_id '{eid}' doppelt")
            ids.add(eid)
            typ = eff.get("effect_type")
            if typ not in erlaubte_typen:
                f(f"{name}/{eid}: effect_type '{typ}' unbekannt")
            if eff.get("certainty") not in ("high", "medium", "low"):
                f(f"{name}/{eid}: certainty '{eff.get('certainty')}' unbekannt")

            effekt = eff.get("effect")
            lo, hi = eff.get("ci_low"), eff.get("ci_high")
            if effekt is not None and not isinstance(effekt, (int, float)):
                f(f"{name}/{eid}: effect ist keine Zahl")
            if lo is not None and hi is not None and effekt is not None:
                if not (min(lo, hi) - 1e-9 <= effekt <= max(lo, hi) + 1e-9):
                    f(f"{name}/{eid}: effect {effekt} liegt ausserhalb des KI [{lo}; {hi}]")
            if typ in ("or", "rr", "hr"):
                for feld, wert in (("effect", effekt), ("ci_low", lo), ("ci_high", hi)):
                    if wert is not None and wert <= 0:
                        f(f"{name}/{eid}: {feld} muss bei {typ} positiv sein")
            if lo is None and hi is None and eff.get("se") is None:
                f(f"{name}/{eid}: weder KI noch SE angegeben")

            quote = str(eff.get("quote") or "")
            start, ende = eff.get("quote_start"), eff.get("quote_end")
            if isinstance(start, int) and isinstance(ende, int) and text:
                if ende <= start:
                    f(f"{name}/{eid}: quote_end ({ende}) <= quote_start ({start})")
                elif text[start:ende] != quote:
                    f(f"{name}/{eid}: Quote passt nicht zum Span [{start}:{ende}]")

    return fehler, offen


def main(argv: list) -> int:
    entwurf = "--entwurf" in argv
    dateien = [a for a in argv if a != "--entwurf"]
    if not dateien:
        print(__doc__)
        return 1
    schema = lade_schema()
    alle = []
    for arg in dateien:
        pfad = Path(arg)
        if not pfad.is_absolute():
            pfad = ROOT / pfad
        if not pfad.exists():
            alle.append(f"{pfad}: Datei fehlt")
            continue
        fehler, offen = pruefe_datei(pfad, schema, entwurf)
        digest = hashlib.sha256(pfad.read_bytes()).hexdigest()
        print(f"{pfad.name}: {len(fehler)} Fehler, {len(offen)} offen, sha256={digest}")
        alle.extend(fehler)
        for eintrag in offen:
            print(f"  offen: {eintrag}")
    if alle:
        print("\nFEHLER:")
        for zeile in alle:
            print(f"  - {zeile}")
        return 1
    print("\nOK: keine Regelverstoesse.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
