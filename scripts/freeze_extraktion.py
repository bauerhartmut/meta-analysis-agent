"""Friere die bestehenden Extraktionszeilen ein und pruefe sie gegen das Manifest.

Zweck: Die drei Zeilen aus der Erhebung vom 2026-11-08 duerfen sich nicht
stillen aendern, wenn spaeter die zwoelf Volltexte nachgetragen werden.

Aufruf:
  --write            Manifest schreiben (nur einmal; danach --force noetig)
  --check            Manifest gegen die CSV pruefen, Exit 1 bei Abweichung
  --csv PATH         andere CSV pruefen (fuer den Negativtest)
  --manifest PATH    anderes Manifest

Der Hash laeuft ueber die kanonische JSON-Darstellung der Zeile (sortierte
Schluessel), nicht ueber Rohbytes. Zeilenende-Wechsel (LF/CRLF) aendern den
Hash damit nicht, ein geaenderter Wert schon.
"""

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

CSV_STD = Path("data/bench/sol2/extraktion_vorlage_20261108.csv")
MAN_STD = Path("data/bench/sol2/extraktion_freeze_20261108.json")


def lies(csv_pfad):
    with csv_pfad.open(encoding="utf-8", newline="") as f:
        return [r for r in csv.DictReader(f) if (r.get("studie_id") or "").strip()]


def hash_zeile(zeile):
    kanon = json.dumps(
        {k: (zeile.get(k) or "") for k in sorted(zeile)},
        ensure_ascii=False,
        sort_keys=True,
    )
    return hashlib.sha256(kanon.encode("utf-8")).hexdigest()


def gesamt_hash(zeilen):
    return hashlib.sha256(
        json.dumps(zeilen, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()


def schreiben(csv_pfad, man_pfad, force):
    if man_pfad.exists() and not force:
        print(f"Manifest existiert bereits: {man_pfad}")
        print("Ein zweites --write wuerde den Freeze aufheben. Nur mit --force.")
        return 2
    zeilen = {r["studie_id"]: hash_zeile(r) for r in lies(csv_pfad)}
    if not zeilen:
        print("Keine gefuellten Zeilen gefunden.")
        return 1
    daten = {
        "stand": "2026-11-08",
        "csv": str(csv_pfad),
        "zweck": "Freeze der drei Zeilen vor Eintreffen der zwoelf Volltexte",
        "zeilen": zeilen,
    }
    daten["gesamt"] = gesamt_hash(zeilen)
    man_pfad.write_text(json.dumps(daten, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    print(f"geschrieben: {man_pfad} | Zeilen: {len(zeilen)} | gesamt: {daten['gesamt'][:16]}")
    return 0


def pruefen(csv_pfad, man_pfad):
    daten = json.loads(man_pfad.read_text(encoding="utf-8"))
    aktuell = {r["studie_id"]: r for r in lies(csv_pfad)}
    fehler = 0
    for sid, soll in daten.get("zeilen", {}).items():
        if sid not in aktuell:
            print(f"FEHLT: {sid}")
            fehler += 1
        elif hash_zeile(aktuell[sid]) != soll:
            print(f"GEAENDERT: {sid}")
            fehler += 1
        else:
            print(f"unveraendert: {sid}")
    if gesamt_hash(daten.get("zeilen", {})) != daten.get("gesamt"):
        print("Manifest selbst weicht vom Gesamthash ab")
        fehler += 1
    neue = sorted(set(aktuell) - set(daten.get("zeilen", {})))
    if neue:
        print("neu, nicht eingefroren (erwartet nach Lieferung): " + ", ".join(neue))
    print("Ergebnis:", "ok" if fehler == 0 else f"{fehler} Abweichung(en)")
    return 0 if fehler == 0 else 1


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--write", action="store_true")
    p.add_argument("--check", action="store_true")
    p.add_argument("--force", action="store_true")
    p.add_argument("--csv", default=str(CSV_STD))
    p.add_argument("--manifest", default=str(MAN_STD))
    a = p.parse_args()
    if not (a.write or a.check):
        p.error("--write oder --check angeben")
    if a.write:
        return schreiben(Path(a.csv), Path(a.manifest), a.force)
    return pruefen(Path(a.csv), Path(a.manifest))


if __name__ == "__main__":
    sys.exit(main())
