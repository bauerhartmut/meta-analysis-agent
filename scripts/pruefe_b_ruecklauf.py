"""Prueft einen B-Ruecklauf und friert ihn mit einer Abgabenotiz ein.

Das Skript liest ausschliesslich das B-Geruest, den Ruecklauf, das Schema
und die Volltexte. Es oeffnet keine A-Datei. Geprueft werden:

- Dokument-ID-Satz gegen das B-Geruest (30 Dokumente, keine Doppelten,
  keine fehlenden oder zusaetzlichen IDs),
- unveraenderte Designmetadaten (path, design_category, stratum),
- Vollstaendigkeit: je Dokument Zeilen oder no_effect_reason, nie beides,
- Effekt-IDs global eindeutig,
- alle Regeln von pruefe_goldstandard.py ohne --entwurf (Pflichtfelder,
  Quote-Span, KI, Ratio-Vorzeichen, offene Dokumente).

Nur bei 0 Fehlern und 0 offenen Dokumenten wird eine Abgabenotiz mit
SHA-256 geschrieben. Existiert die Notiz bereits, bricht das Skript ab,
damit ein einmal eingefrorener Stand nicht ueberschrieben wird.

Aufruf:
    export PYTHONIOENCODING=utf-8
    .venv/bin/python.exe scripts/pruefe_b_ruecklauf.py data/golden_effects/goldstandard_B_ruecklauf.json
    .venv/bin/python.exe scripts/pruefe_b_ruecklauf.py <pfad> --keine-notiz
    .venv/bin/python.exe scripts/pruefe_b_ruecklauf.py <pfad> --out docs/internal/abgabe_B.md

Exit 0 = geprueft und eingefroren (oder mit --keine-notiz nur geprueft).
Exit 1 = Fehler; es wird keine Notiz geschrieben.
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from pruefe_goldstandard import lade_schema, pruefe_datei  # noqa: E402

REFERENZ = ROOT / "data" / "golden_effects" / "goldstandard_B.json"
STANDARD_AUSGABE = ROOT / "docs" / "internal"


def lade(pfad: Path):
    return json.loads(pfad.read_text(encoding="utf-8"))


def sha256(pfad: Path) -> str:
    return hashlib.sha256(pfad.read_bytes()).hexdigest()


def anzeige(pfad: Path) -> str:
    try:
        return pfad.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(pfad)


def pruefe(ruecklauf: Path, referenz: Path):
    fehler = []
    if "goldstandard_A" in ruecklauf.name:
        return ["Eingabe ist eine A-Datei; B-Ruecklauf erwartet."], {}, 0, 0
    if not ruecklauf.exists():
        return [f"Ruecklauf fehlt: {ruecklauf}"], {}, 0, 0
    if not referenz.exists():
        return [f"Referenz fehlt: {referenz}"], {}, 0, 0
    if ruecklauf.resolve() == referenz.resolve():
        return ["Ruecklauf und Referenz sind dieselbe Datei; das Geruest ist keine Abgabe."], {}, 0, 0

    try:
        daten = lade(ruecklauf)
        geruest = lade(referenz)
    except (OSError, json.JSONDecodeError) as exc:
        return [f"JSON nicht lesbar: {exc}"], {}, 0, 0

    if daten.get("annotator") != "B":
        fehler.append(f"annotator ist {daten.get('annotator')!r}, erwartet 'B'.")
    if daten.get("blind") is not True:
        fehler.append("blind ist nicht true.")

    ref_docs = geruest.get("documents")
    docs = daten.get("documents")
    if not isinstance(ref_docs, list) or len(ref_docs) != 30:
        return ["B-Geruest hat nicht genau 30 Dokumente."], {}, 0, 0
    if not isinstance(docs, list):
        return ["documents ist keine Liste."], {}, 0, 0

    ref_ids = [str(d.get("document_id") or "") for d in ref_docs]
    ids = [str(d.get("document_id") or "") for d in docs]
    if len(ref_ids) != len(set(ref_ids)):
        fehler.append("B-Geruest enthaelt doppelte document_id.")
    if len(ids) != len(set(ids)):
        fehler.append("Ruecklauf enthaelt doppelte document_id.")
    fehlend = sorted(set(ref_ids) - set(ids))
    extra = sorted(set(ids) - set(ref_ids))
    if fehlend:
        fehler.append("fehlende document_id: " + ", ".join(fehlend))
    if extra:
        fehler.append("zusaetzliche document_id: " + ", ".join(extra))
    if len(docs) != 30:
        fehler.append(f"Ruecklauf hat {len(docs)} Dokumente, erwartet 30.")

    ref_by_id = {str(d.get("document_id")): d for d in ref_docs}
    rows = 0
    reasons = 0
    offen = 0
    effekt_ids = set()
    for d in docs:
        did = str(d.get("document_id") or "?")
        ref = ref_by_id.get(did)
        if ref is None:
            continue
        for feld in ("path", "design_category", "stratum"):
            if d.get(feld) != ref.get(feld):
                fehler.append(f"{did[:10]}: {feld} geaendert ({ref.get(feld)!r} -> {d.get(feld)!r}).")
        effects = d.get("effects") or []
        grund = str(d.get("no_effect_reason") or "").strip()
        if effects and grund:
            fehler.append(f"{did[:10]}: Zeilen und no_effect_reason gleichzeitig gesetzt.")
        if not effects and not grund:
            offen += 1
            fehler.append(f"{did[:10]}: weder Zeile noch no_effect_reason.")
        if grund:
            reasons += 1
        rows += len(effects)
        for eff in effects:
            eid = str(eff.get("effect_id") or "")
            if eid in effekt_ids:
                fehler.append(f"{did[:10]}: effect_id global doppelt ({eid}).")
            effekt_ids.add(eid)

    schema = lade_schema()
    pruef_fehler, pruef_offen = pruefe_datei(ruecklauf, schema, entwurf=False)
    fehler.extend(pruef_fehler)
    offen = max(offen, len(pruef_offen))

    zahlen = {
        "dokumente": len(docs),
        "zeilen": rows,
        "begruendungen": reasons,
        "offen": offen,
        "referenz_sha256": sha256(referenz),
    }
    if fehler:
        return fehler, zahlen, rows, reasons
    return [], zahlen, rows, reasons


def schreibe_notiz(pfad: Path, ruecklauf: Path, digest: str, zahlen: dict, docs: list, zeitpunkt: str):
    zeilen = [
        f"# B-Abgabe ({zeitpunkt[:10]})",
        "",
        f"- Ruecklauf: `{anzeige(ruecklauf)}`",
        f"- SHA-256: `{digest}`",
        f"- Geprueft: `{zeitpunkt}`",
        f"- Referenzgeruest: `{anzeige(REFERENZ)}`",
        f"- Referenz-Hash: `{zahlen['referenz_sha256']}`",
        f"- Dokumente: {zahlen['dokumente']}",
        f"- Zeilen: {zahlen['zeilen']}",
        f"- Begruendungen: {zahlen['begruendungen']}",
        f"- Offen: {zahlen['offen']}",
        "- Pruefer: `scripts/pruefe_goldstandard.py` ohne `--entwurf`, 0 Fehler.",
        "",
        "## Vollstaendigkeit",
        "",
        "| Dokument | Zeilen | Begruendung |",
        "|---|---|---|",
    ]
    for d in docs:
        did = str(d.get("document_id") or "?")[:10]
        n = len(d.get("effects") or [])
        grund = "ja" if str(d.get("no_effect_reason") or "").strip() else "nein"
        zeilen.append(f"| {did} | {n} | {grund} |")
    zeilen += [
        "",
        "## Status",
        "",
        "- A wurde von diesem Skript nicht gelesen.",
        "- Diese Datei ist der eingefrorene Abgabestand; den Ruecklauf nicht mehr aendern.",
        "- Naechster Schritt: A oeffnen, Kappa und Konflikte berechnen.",
        "",
    ]
    pfad.parent.mkdir(parents=True, exist_ok=True)
    pfad.write_text("\n".join(zeilen), encoding="utf-8")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Prueft einen B-Ruecklauf und friert ihn ein.")
    parser.add_argument("ruecklauf", help="Pfad zur B-Ruecklaufdatei")
    parser.add_argument("--referenz", default=str(REFERENZ), help="B-Geruest als Referenz")
    parser.add_argument("--out", default="", help="Pfad der Abgabenotiz")
    parser.add_argument("--keine-notiz", action="store_true", help="nur pruefen, nichts schreiben")
    args = parser.parse_args(argv)

    ruecklauf = Path(args.ruecklauf)
    if not ruecklauf.is_absolute():
        ruecklauf = (Path.cwd() / ruecklauf).resolve()
    referenz = Path(args.referenz)
    if not referenz.is_absolute():
        referenz = (Path.cwd() / referenz).resolve()

    if "goldstandard_A" in ruecklauf.name:
        print("FEHLER: Eingabe ist eine A-Datei; B-Ruecklauf erwartet.")
        print("Keine Abgabenotiz geschrieben.")
        return 1

    fehler, zahlen, rows, reasons = pruefe(ruecklauf, referenz)
    digest = sha256(ruecklauf) if ruecklauf.exists() else ""
    print(f"B-Ruecklauf: {anzeige(ruecklauf)}")
    print(f"Dokumente: {zahlen.get('dokumente', 0)}, Zeilen: {rows}, Begruendungen: {reasons}, offen: {zahlen.get('offen', 0)}")
    if digest:
        print(f"SHA-256: {digest}")

    if fehler:
        print("\nFEHLER:")
        for eintrag in fehler:
            print(f"  - {eintrag}")
        print("\nKeine Abgabenotiz geschrieben.")
        return 1

    if args.keine_notiz:
        print("OK: vollstaendig, keine Notiz geschrieben.")
        return 0

    ziel = Path(args.out) if args.out else STANDARD_AUSGABE / f"goldstandard_B_abgabe_{datetime.now().strftime('%Y%m%d')}.md"
    if not ziel.is_absolute():
        ziel = (Path.cwd() / ziel).resolve()
    if ziel.exists():
        print(f"\nFEHLER: Abgabenotiz existiert bereits: {ziel}")
        print("Ein eingefrorener Stand wird nicht ueberschrieben.")
        return 1

    zeitpunkt = datetime.now().astimezone().isoformat(timespec="seconds")
    schreibe_notiz(ziel, ruecklauf, digest, zahlen, lade(ruecklauf)["documents"], zeitpunkt)
    print(f"Notiz: {anzeige(ziel)}")
    print("OK: B-Ruecklauf geprueft und eingefroren.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
