"""Prueft die Extraktionsvorlage fuer die eintreffende Fernleih-Lieferung.

Drei Bloecke werden erzwungen, die die Fassung vom 2026-11-08 offen liess:
  - Register-ID mit Fundstelle und Abgleich gegen Registerangaben
  - gepaarte Streuung bei Crossover (Pfad C1/C2/C4/C5 nach crossover_regel_20261108.md)
  - Dedup-Check gegen die drei eingeschlossenen Studien S1/S2/S3

Aufrufe:
  python scripts/pruefe_extraktion_20261109.py --vorlage   # CSV anlegen
  python scripts/pruefe_extraktion_20261109.py --check     # CSV pruefen
  python scripts/pruefe_extraktion_20261109.py --selbsttest

Exit 0 nur, wenn keine Fehler gefunden wurden. Warnungen allein sind Exit 0.
Kein Netz, kein Modellaufruf, keine Bewertung von Inhalten.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

BASE = Path("data/bench/sol2")
CSV_PATH = BASE / "extraktion_vorlage_20261109.csv"

SPALTEN = [
    # A - Identitaet
    "studie_id", "pmid", "doi", "kurzname", "studiengruppe",
    # B - Design, inkl. Crossover-Entscheidung
    "design", "n_perioden", "washout", "periodeneffekt", "carryover_bewertung",
    "erste_periode_auswertbar", "crossover_pfad", "sd_diff_quelle", "se_unpaired",
    # C - Population
    "population", "altersgruppe", "n_randomisiert", "n_verum_randomisiert",
    "n_placebo_randomisiert", "n_analysiert", "n_verum", "n_placebo", "dropout",
    # D - Intervention
    "dosis_mg", "dosis_mg_kg", "dauer", "einnahmezeit", "praeparat",
    # E - Outcome
    "messmethode", "outcome_name", "zeitpunkt", "verum_mean", "verum_sd",
    "placebo_mean", "placebo_sd", "streuungsart", "einheit", "sol_primaer",
    # F - Effekt und Streuung
    "effekt_min", "se", "herkunft_effekt", "sd_diff", "se_diff", "ci_untere",
    "ci_obere", "r", "r_geschaetzt", "adjustiert", "adjustierte_kovariaten",
    # G - Pruefung und Herkunft
    "fundstelle", "zitat", "rob2_domaene_periode",
    # H - Register
    "register_id", "register_fundstelle", "register_abgleich_n",
    "register_abgleich_endpunkt",
    # I - Dedup gegen die drei eingeschlossenen Studien
    "dedup_gegen", "dedup_merkmal", "dedup_ergebnis", "dedup_beleg",
    # J - Status
    "status", "anmerkung", "extrahiert_von", "datum",
]

LEER = {"", "entfaellt", "entfaellt:", "nicht berichtet", "offen", "-"}

REGISTER_PRAEFIX = (
    "NCT", "ISRCTN", "EU-CTR", "ACTRN", "ChiCTR", "DRKS", "CTRI", "JPRN", "TCTR",
)

DEDUP_GEGEN = {"S1", "S2", "S3", "S1+S2", "S1+S3", "S2+S3", "S1+S2+S3", "keins"}
DEDUP_ERGEBNIS = {"unabhaengig", "Verdacht", "Doppel", "ungeklaert"}
CROSSOVER_PFAD = {"C1", "C2", "C4", "C5-erste-Periode", "C5-Ausschluss"}
STATUS = {
    "offen", "poolbar", "Zahlen fehlen", "Endpunkt nicht berichtet",
    "ausgeschlossen", "nicht auswertbar",
}
DESIGN = {"parallel", "crossover", "faktoriell", "offen"}

CROSSOVER_FELDER = (
    "n_perioden", "washout", "periodeneffekt", "carryover_bewertung",
    "erste_periode_auswertbar", "sd_diff", "se_diff", "rob2_domaene_periode",
)


def zahl(value: str):
    """Liest eine Zahl mit deutschem oder englischem Dezimaltrennzeichen."""
    text = (value or "").strip().replace(" ", "")
    if text.lower() in LEER:
        return None
    text = text.replace(".", "").replace(",", ".") if "," in text else text
    try:
        return float(text)
    except ValueError:
        return None


def ist_leer(value: str) -> bool:
    return (value or "").strip().lower() in LEER


def pruefe_zeile(row: dict) -> tuple[list[str], list[str]]:
    """Gibt (Fehler, Warnungen) fuer eine Zeile zurueck."""
    fehler: list[str] = []
    warnungen: list[str] = []
    nummer = row.get("pmid") or row.get("studie_id") or "?"

    def feld(name: str) -> str:
        return (row.get(name) or "").strip()

    # E01 - Identitaet ist immer Pflicht, der Rest erst ab bearbeiteter Zeile
    for name in ("studie_id", "pmid", "doi"):
        if not feld(name):
            fehler.append(f"E01 Pflichtfeld leer: {name}")
    if feld("status") == "offen":
        return fehler, warnungen
    for name in ("design", "register_id", "dedup_gegen", "dedup_ergebnis",
                 "dedup_beleg", "status"):
        if not feld(name):
            fehler.append(f"E01 Pflichtfeld leer: {name}")

    if feld("status") and feld("status") not in STATUS:
        fehler.append(f"E02 status unzulaessig: {feld('status')}")
    if feld("design") and feld("design") not in DESIGN:
        fehler.append(f"E02 design unzulaessig: {feld('design')}")
    if feld("design") in {"parallel", "faktoriell"} and feld("crossover_pfad"):
        fehler.append("E02 crossover_pfad bei nicht-Crossover gesetzt")

    # E03-E07 - Crossover
    if feld("design") == "crossover":
        pfad = feld("crossover_pfad")
        if pfad not in CROSSOVER_PFAD:
            fehler.append("E03 Crossover ohne gueltigen crossover_pfad")
        if pfad == "C1":
            if not (zahl(feld("sd_diff")) or zahl(feld("se_diff"))
                    or zahl(feld("ci_untere"))):
                fehler.append("E04 Pfad C1 ohne sd_diff, se_diff oder CI")
        if pfad == "C2":
            if zahl(feld("r")) != 0.5:
                fehler.append("E05 Pfad C2 verlangt r = 0,5")
            if feld("r_geschaetzt") != "ja":
                fehler.append("E05 Pfad C2 verlangt r_geschaetzt = ja")
        if pfad == "C4" and not zahl(feld("se_unpaired")):
            fehler.append("E06 Pfad C4 ohne se_unpaired")
        if pfad == "C5-erste-Periode" and feld("erste_periode_auswertbar") != "ja":
            fehler.append("E07 Pfad C5 verlangt erste_periode_auswertbar = ja")
        if pfad == "C5-Ausschluss" and feld("status") != "ausgeschlossen":
            fehler.append("E07 Pfad C5-Ausschluss verlangt status = ausgeschlossen")

    # E08 - gepaarte SE muss kleiner sein als die ungepaarte
    se = zahl(feld("se"))
    se_unpaired = zahl(feld("se_unpaired"))
    if se is not None and se_unpaired is not None and se >= se_unpaired:
        fehler.append(
            f"E08 se ({se}) nicht kleiner als se_unpaired ({se_unpaired}): "
            "gepaarte und ungepaarte Streuung verwechselt?"
        )

    # E09 - Doppel darf nicht poolbar sein
    if feld("dedup_ergebnis") == "Doppel" and feld("status") != "ausgeschlossen":
        fehler.append("E09 dedup_ergebnis = Doppel verlangt status = ausgeschlossen")
    if feld("dedup_gegen") and feld("dedup_gegen") not in DEDUP_GEGEN:
        fehler.append(f"E14 dedup_gegen unzulaessig: {feld('dedup_gegen')}")
    if feld("dedup_ergebnis") and feld("dedup_ergebnis") not in DEDUP_ERGEBNIS:
        fehler.append(f"E14 dedup_ergebnis unzulaessig: {feld('dedup_ergebnis')}")

    # E10 - designbedingte Leerstellen heissen entfaellt, nicht leer
    if feld("design") == "parallel" and feld("status") != "offen":
        for name in CROSSOVER_FELDER:
            if not feld(name):
                warnungen.append(f"E10 {name} leer statt entfaellt (Parallelstudie)")

    # E11 - Streuungsart, wenn Armwerte gefuellt sind
    if (zahl(feld("verum_sd")) is not None or zahl(feld("placebo_sd")) is not None) \
            and ist_leer(feld("streuungsart")):
        fehler.append("E11 Armwerte vorhanden, streuungsart fehlt")

    # E12 - Einheit Minuten
    if feld("einheit") and feld("einheit") != "min" and "60" not in feld("anmerkung"):
        fehler.append("E12 Einheit nicht min und keine Umrechnung in anmerkung")

    # E13 - Register
    register = feld("register_id")
    if register and register != "offen":
        if register.lower() in {"nicht berichtet", "ohne", "keine"}:
            if not feld("register_abgleich_n") or feld("register_abgleich_n") == "offen":
                fehler.append("E13 fehlende Registrierung ohne register_abgleich_n")
            if not feld("register_fundstelle"):
                fehler.append("E13 fehlende Registrierung ohne register_fundstelle")
        elif not any(register.upper().startswith(p) for p in REGISTER_PRAEFIX):
            warnungen.append(f"E13 unbekanntes Registerpraefix: {register}")
        if feld("status") not in {"offen"} and not feld("register_fundstelle"):
            fehler.append("E13 register_id ohne register_fundstelle")

    # E15 - poolbar verlangt Effekt und Streuung
    if feld("status") == "poolbar":
        if zahl(feld("effekt_min")) is None:
            fehler.append("E15 status poolbar ohne effekt_min")
        if se is None:
            fehler.append("E15 status poolbar ohne se")

    if feld("status") != "offen" and ist_leer(feld("zitat")):
        warnungen.append("E16 Zitat fehlt bei bearbeiteter Zeile")
    if feld("status") != "offen" and ist_leer(feld("fundstelle")):
        warnungen.append("E16 Fundstelle fehlt bei bearbeiteter Zeile")

    _ = nummer
    return fehler, warnungen


def check(path: Path = CSV_PATH) -> int:
    if not path.exists():
        print(f"FEHLT: {path}. Erst --vorlage ausfuehren.")
        return 2
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != SPALTEN:
            fehlend = [s for s in SPALTEN if s not in (reader.fieldnames or [])]
            extra = [s for s in (reader.fieldnames or []) if s not in SPALTEN]
            print(f"SPALTEN ABWEICHEND. Fehlend: {fehlend}. Unbekannt: {extra}")
            return 2
        rows = list(reader)

    gesamt_fehler: list[str] = []
    gesamt_warnungen: list[str] = []
    offen = 0
    for zeile_nr, row in enumerate(rows, start=2):
        fehler, warnungen = pruefe_zeile(row)
        if (row.get("status") or "").strip() == "offen":
            offen += 1
        gesamt_fehler += [f"Zeile {zeile_nr}: {f}" for f in fehler]
        gesamt_warnungen += [f"Zeile {zeile_nr}: {w}" for w in warnungen]

    print(f"Zeilen: {len(rows)}, davon offen: {offen}")
    print(f"Fehler: {len(gesamt_fehler)}, Warnungen: {len(gesamt_warnungen)}")
    for text in gesamt_fehler:
        print(f"  FEHLER {text}")
    for text in gesamt_warnungen[:20]:
        print(f"  WARNUNG {text}")
    if len(gesamt_warnungen) > 20:
        print(f"  ... {len(gesamt_warnungen) - 20} weitere Warnungen")
    return 1 if gesamt_fehler else 0


def nachname(author: str) -> str:
    """Erstautor-Nachname ohne Initialen, mit Praefixen wie 'van Maanen'."""
    teile = (author or "").split()
    if len(teile) >= 2 and re.fullmatch(r"[A-Z]{1,3}", teile[-1]):
        return " ".join(teile[:-1])
    return teile[0] if teile else ""


def vorlage() -> int:
    sys.path.insert(0, str(Path("scripts").resolve()))
    from erstelle_fernleihliste import TRIAGE, parse_b_xml  # noqa: E402

    rows = list(csv.DictReader(
        (BASE / "zugangsliste_20261108.csv").open(encoding="utf-8")
    ))
    zitationen = {
        z["pmid"]: z
        for z in json.loads((BASE / "zitationen_a.json").read_text("utf-8"))
    }
    b_meta = parse_b_xml()

    auswahl = [
        r for r in rows
        if r["prioritaet"] == "A"
        or (r["prioritaet"] == "B" and TRIAGE.get(r["pmid"]) != "D")
    ]
    assert len(auswahl) == 20, len(auswahl)

    eintraege = []
    for r in auswahl:
        pmid = r["pmid"].strip()
        if r["prioritaet"] == "A":
            z = zitationen[pmid]
            erster = z.get("author", "").split(",")[0].strip()
            kurz = f"{nachname(erster)} {z.get('year', r['jahr'])}" if erster else ""
        else:
            meta = b_meta.get(pmid, {})
            autoren = meta.get("authors") or []
            erster = autoren[0] if autoren else ""
            kurz = f"{nachname(erster)} {meta.get('year') or r['jahr']}" if erster else ""
        zeile = {spalte: "" for spalte in SPALTEN}
        zeile["studie_id"] = f"NEU_{pmid}"
        zeile["pmid"] = pmid
        zeile["doi"] = r["doi"].strip()
        zeile["kurzname"] = kurz
        zeile["design"] = "offen"
        zeile["register_id"] = "offen"
        zeile["dedup_gegen"] = "offen"
        zeile["dedup_ergebnis"] = "offen"
        zeile["status"] = "offen"
        eintraege.append(zeile)

    with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=SPALTEN)
        writer.writeheader()
        writer.writerows(eintraege)
    print(f"{CSV_PATH}: {len(eintraege)} Zeilen, {len(SPALTEN)} Spalten")
    return 0


def selbsttest() -> int:
    """Prueft, ob die Regeln greifen. Erwartete Codes muessen erscheinen."""
    basis = {spalte: "" for spalte in SPALTEN}
    basis.update({
        "studie_id": "T1", "pmid": "1", "doi": "10.1/x", "design": "parallel",
        "register_id": "NCT00397189", "register_fundstelle": "Methoden, Absatz 1",
        "register_abgleich_n": "stimmt", "register_abgleich_endpunkt": "stimmt",
        "dedup_gegen": "S1", "dedup_merkmal": "Register-ID; n; Zentren",
        "dedup_ergebnis": "unabhaengig", "dedup_beleg": "andere Register-ID",
        "status": "poolbar", "effekt_min": "-15,6", "se": "4,92",
        "einheit": "min", "streuungsart": "SD", "zitat": "x", "fundstelle": "y",
    })

    faelle: list[tuple[str, dict, list[str]]] = []

    gueltig = dict(basis)
    faelle.append(("gueltige Parallelzeile", gueltig, []))

    unbearbeitet = {spalte: "" for spalte in SPALTEN}
    unbearbeitet.update({
        "studie_id": "NEU_1", "pmid": "1", "doi": "10.1/x",
        "design": "offen", "register_id": "offen", "dedup_gegen": "offen",
        "dedup_ergebnis": "offen", "status": "offen",
    })
    faelle.append(("unbearbeitete Zeile", unbearbeitet, []))

    doppel = dict(basis)
    doppel["dedup_ergebnis"] = "Doppel"
    faelle.append(("Doppel ohne Ausschluss", doppel, ["E09"]))

    cx_ohne_pfad = dict(basis)
    cx_ohne_pfad["design"] = "crossover"
    faelle.append(("Crossover ohne Pfad", cx_ohne_pfad, ["E03"]))

    cx_c2_ohne_r = dict(basis)
    cx_c2_ohne_r.update({"design": "crossover", "crossover_pfad": "C2"})
    faelle.append(("C2 ohne r", cx_c2_ohne_r, ["E05"]))

    verwechselt = dict(basis)
    verwechselt["se_unpaired"] = "4,00"
    faelle.append(("se groesser als se_unpaired", verwechselt, ["E08"]))

    kein_register = dict(basis)
    kein_register.update({"register_id": "ohne", "register_fundstelle": ""})
    faelle.append(("fehlende Registrierung ohne Beleg", kein_register, ["E13"]))

    fehler_gesamt = 0
    for name, zeile, erwartet in faelle:
        fehler, _ = pruefe_zeile(zeile)
        codes = {f.split()[0] for f in fehler}
        ok = codes == set(erwartet)
        print(f"{'OK  ' if ok else 'FAIL'} {name}: erwartet {erwartet or '-'}, "
              f"erhalten {sorted(codes) or '-'}")
        if not ok:
            fehler_gesamt += 1
    print(f"Selbsttest: {len(faelle) - fehler_gesamt}/{len(faelle)} bestanden")
    return 1 if fehler_gesamt else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vorlage", action="store_true", help="CSV neu anlegen")
    parser.add_argument("--check", action="store_true", help="CSV pruefen")
    parser.add_argument("--selbsttest", action="store_true", help="Regeln testen")
    args = parser.parse_args()

    if args.vorlage:
        return vorlage()
    if args.selbsttest:
        return selbsttest()
    if args.check:
        return check()
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
