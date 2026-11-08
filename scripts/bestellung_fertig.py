"""Setzt Name und Einrichtung in die Signatur der Bestellanfrage ein.

Die Angaben lassen sich nicht aus dem Projekt ableiten, deshalb stehen sie
in der Vorlage als Platzhalter. Dieses Skript ersetzt genau diese zwei
Zeilen, schreibt eine versandfertige Fassung und prueft, dass sich sonst
nichts aendert.

    --name "Vorname Nachname" --einrichtung "Einrichtung, Fachbereich"
    --pruefen    Zustand der Vorlage und der versandfertigen Fassung

Ohne Argumente passiert nichts. Kein Netz, kein Modell.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASIS = ROOT / "data/bench/sol2"
VORLAGE = BASIS / "bestellanfrage_20261108.txt"
ZIEL = BASIS / "bestellanfrage_20261108_versandfertig.txt"

FELD_NAME = "[Name]  <- AUSFUELLEN"
FELD_EINRICHTUNG = "[Einrichtung, Fachbereich]  <- AUSFUELLEN"
PLATZHALTER = (FELD_NAME, FELD_EINRICHTUNG)


def lies(pfad: Path) -> str:
    if not pfad.exists():
        raise SystemExit(f"Vorlage fehlt: {pfad}")
    return pfad.read_text(encoding="utf-8")


def offene_felder(text: str) -> list[str]:
    return [feld for feld in PLATZHALTER if feld in text]


def einsetzen(text: str, name: str, einrichtung: str) -> str:
    """Ersetzt die zwei Signaturzeilen und prueft den Rest zeichengenau."""
    for feld, wert, bezeichnung in (
        (FELD_NAME, name, "Name"),
        (FELD_EINRICHTUNG, einrichtung, "Einrichtung"),
    ):
        if text.count(feld) != 1:
            raise SystemExit(
                f"Platzhalter fuer {bezeichnung} kommt {text.count(feld)}x vor, "
                "erwartet genau 1x - Vorlage geaendert?"
            )
        if feld not in wert:
            text = text.replace(feld, wert)
    return text


def zeilen_diff(vorher: str, nachher: str) -> list[tuple[int, str, str]]:
    a, b = vorher.splitlines(), nachher.splitlines()
    if len(a) != len(b):
        raise SystemExit(
            f"Zeilenzahl geaendert ({len(a)} -> {len(b)}) - Abbruch."
        )
    return [
        (i + 1, x, y) for i, (x, y) in enumerate(zip(a, b)) if x != y
    ]


def pruefen() -> int:
    vorlage = lies(VORLAGE)
    offen = offene_felder(vorlage)
    print(f"Vorlage: {VORLAGE.relative_to(ROOT)}")
    print(f"  Zeichen: {len(vorlage)}, Zeilen: {len(vorlage.splitlines())}")
    print(f"  offene Platzhalter: {len(offen)}")
    for feld in offen:
        print(f"    - {feld}")

    if not ZIEL.exists():
        print(f"\nVersandfertige Fassung: fehlt ({ZIEL.name})")
        print("Aufruf mit --name und --einrichtung erzeugt sie.")
        return 1

    fertig = lies(ZIEL)
    rest = offene_felder(fertig)
    diff = zeilen_diff(vorlage, fertig)
    print(f"\nVersandfertige Fassung: {ZIEL.relative_to(ROOT)}")
    print(f"  Zeichen: {len(fertig)}, geaenderte Zeilen: {len(diff)}")
    for nummer, alt, neu in diff:
        print(f"    Zeile {nummer}: {alt.strip()!r} -> {neu.strip()!r}")
    if rest:
        print(f"  FEHLER: Platzhalter noch vorhanden: {rest}")
        return 1
    if len(diff) != 2:
        print("  FEHLER: es muessen genau 2 Zeilen geaendert sein.")
        return 1
    print("  in Ordnung: nur die zwei Signaturzeilen ersetzt.")
    return 0


def schreiben(name: str, einrichtung: str, ziel: Path) -> int:
    name, einrichtung = name.strip(), einrichtung.strip()
    if not name or not einrichtung:
        raise SystemExit("Name und Einrichtung duerfen nicht leer sein.")
    if "[" in name or "]" in name or "AUSFUELLEN" in name.upper():
        raise SystemExit(f"Name sieht nach Platzhalter aus: {name!r}")
    if "[" in einrichtung or "]" in einrichtung or "AUSFUELLEN" in einrichtung.upper():
        raise SystemExit(f"Einrichtung sieht nach Platzhalter aus: {einrichtung!r}")

    vorlage = lies(VORLAGE)
    text = einsetzen(vorlage, name, einrichtung)
    diff = zeilen_diff(vorlage, text)
    if len(diff) != 2:
        raise SystemExit(f"Erwartet 2 geaenderte Zeilen, gefunden {len(diff)}.")

    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(text, encoding="utf-8", newline="\n")
    print(f"geschrieben: {ziel}")
    print(f"Zeichen: {len(vorlage)} -> {len(text)}")
    for nummer, alt, neu in diff:
        print(f"  Zeile {nummer}: {alt.strip()!r} -> {neu.strip()!r}")
    print("Naechster Schritt: --pruefen, dann Text aus der Datei ins Mailprogramm.")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--name", default="")
    p.add_argument("--einrichtung", default="")
    p.add_argument("--ziel", default="", help="abweichender Zielpfad (Test)")
    p.add_argument("--pruefen", action="store_true")
    args = p.parse_args()

    if args.pruefen:
        return pruefen()
    if not (args.name and args.einrichtung):
        p.print_help()
        return 2
    ziel = Path(args.ziel) if args.ziel else ZIEL
    return schreiben(args.name, args.einrichtung, ziel)


if __name__ == "__main__":
    sys.exit(main())
