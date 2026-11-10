"""Erkennt einen neuen B-Ruecklauf und startet den Trockenlauf.

Standardmaessig wird data/golden_effects/goldstandard_B_ruecklauf.json
beobachtet. Sobald die Datei neu ist oder sich ihr SHA-256 aendert, laeuft
scripts/pruefe_b_ruecklauf.py mit --keine-notiz. Es wird nie automatisch
eingefroren und keine Abgabenotiz geschrieben.

Beispiele:
    .venv/bin/python.exe scripts/b_ruecklauf_eingang.py
    .venv/bin/python.exe scripts/b_ruecklauf_eingang.py --einmal
    .venv/bin/python.exe scripts/b_ruecklauf_eingang.py --datei data/tmp_b.json --intervall 5

Exit-Codes mit --einmal:
    0 = Trockenlauf bestanden
    1 = Trockenlauf mit Fehlern
    2 = Datei fehlt oder Aufruf ungueltig
"""

from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STANDARD = ROOT / "data" / "golden_effects" / "goldstandard_B_ruecklauf.json"
REFERENZ = ROOT / "data" / "golden_effects" / "goldstandard_B.json"
PKT_REFERENZ = (ROOT / "data" / "golden_effects" / "blind_b_20261110"
                / "data" / "golden_effects" / "goldstandard_B.json")
CHECKER = ROOT / "scripts" / "pruefe_b_ruecklauf.py"


def anzeige(pfad: Path) -> str:
    try:
        return pfad.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(pfad)


def sha256(pfad: Path) -> str:
    return hashlib.sha256(pfad.read_bytes()).hexdigest()


def pruefe(pfad: Path) -> int:
    args = [sys.executable, str(CHECKER), str(pfad), "--keine-notiz"]
    # Ein direkt ausgefuelltes kanonisches B ist nicht gegen sich selbst
    # pruefbar; dann dient die separate Paketkopie als Referenz.
    if pfad.resolve() == REFERENZ.resolve():
        args += ["--referenz", str(PKT_REFERENZ)]

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    print(f"\n[{datetime.now():%Y-%m-%d %H:%M:%S}] Trockenlauf: {anzeige(pfad)}")
    print(f"SHA-256: {sha256(pfad)}")
    ergebnis = subprocess.run(args, cwd=str(ROOT), env=env, text=True,
                             encoding="utf-8", errors="replace")
    if ergebnis.returncode == 0:
        print("OK: Trockenlauf bestanden. Einfrieren mit:")
        print(f"  .venv/bin/python.exe scripts/pruefe_b_ruecklauf.py {anzeige(pfad)}")
    else:
        print("FEHLER: Trockenlauf nicht bestanden; Datei pruefen und erneut einlesen.")
    return ergebnis.returncode


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, OSError):
        pass
    parser = argparse.ArgumentParser(
        description="Beobachtet den B-Ruecklauf und startet den Trockenlauf.")
    parser.add_argument(
        "--datei", default=str(STANDARD),
        help="zu beobachtende Datei (Default: data/golden_effects/goldstandard_B_ruecklauf.json)")
    parser.add_argument(
        "--intervall", type=float, default=10.0,
        help="Sekunden zwischen zwei Pruefungen (Default: 10, Minimum: 1)")
    parser.add_argument(
        "--einmal", action="store_true",
        help="nur einmal pruefen und beenden, nicht dauerhaft beobachten")
    args = parser.parse_args(argv)

    pfad = Path(args.datei)
    if not pfad.is_absolute():
        pfad = (ROOT / pfad).resolve()

    if args.einmal:
        if not pfad.is_file():
            print(f"Keine Datei: {anzeige(pfad)}")
            return 2
        return pruefe(pfad)

    print(f"Beobachte: {anzeige(pfad)}")
    print(f"Intervall: {max(1.0, args.intervall):g} s; Trockenlauf ohne Einfrieren.")
    letzte = ""
    gemeldet = False
    try:
        while True:
            if pfad.is_file():
                try:
                    aktuell = sha256(pfad)
                except OSError as exc:
                    print(f"Datei nicht lesbar: {exc}")
                    time.sleep(max(1.0, args.intervall))
                    continue
                if aktuell != letzte:
                    letzte = aktuell
                    pruefe(pfad)
                gemeldet = False
            elif not gemeldet:
                print(f"Warte auf Datei: {anzeige(pfad)}")
                gemeldet = True
                letzte = ""
            time.sleep(max(1.0, args.intervall))
    except KeyboardInterrupt:
        print("\nBeendet.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
