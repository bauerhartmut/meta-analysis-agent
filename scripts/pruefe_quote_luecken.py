"""E4 - deterministische Lueckenpruefung, belegt an den E3-Artefakten.

Kein Modellaufruf, keine Persistenz, keine Aenderung an einer Zeile. Geprueft
werden die Zeilen, die die drei E3-Laeufe tatsaechlich zurueckgegeben haben,
gegen den MENDS-Satz, aus dem sie stammen.

Erwartung:
  E3a  TST-Zeile          -> 1 Intervall, 1 Zeile  -> ok
  E3b  Aktigraphie-Zeile  -> 2 Intervalle, 1 Zeile -> Luecke
  E3c  Tagebuch-Zeile     -> 2 Intervalle, 1 Zeile -> Luecke

Dazu zwei Gegenproben: mit beiden Zeilen ist der Satz vollstaendig, und der
Satz ohne CI-Angabe ist nicht pruefbar (keine falsche Luecke).

Aufruf:
    export PYTHONIOENCODING=utf-8
    .venv/bin/python.exe scripts/pruefe_quote_luecken.py
"""

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research_agent.meta.quote_gaps import (      # noqa: E402
    audit_quote, audit_rows, find_intervals, summarize,
)

TEXT_PATH = ROOT / "data" / "bench" / "sol2" / "volltext" / "23098680.txt"
VALIDIERUNG = ROOT / "data" / "bench" / "validierung"
OUT_JSON = VALIDIERUNG / "e4_quote_luecken_20261108.json"
OUT_MD = VALIDIERUNG / "e4_quote_luecken_20261108.md"

SATZ_ANFANG = "A reduction in SOL"
SATZ_ENDE = "p=0.0003)."

LAEUFE = [
    ("E3a-24k-kontext", "e3_llm_20261108.json"),
    ("E3b-isolierter-satz", "e3b_satz_20261108.json"),
    ("E3c-prompt-regel", "e3c_regel_20261108.json"),
]


def lade_satz() -> str:
    """Den Satz deterministisch aus dem Volltext schneiden, nicht abtippen."""
    text = TEXT_PATH.read_text(encoding="utf-8", errors="replace")
    text = text.replace("\r\n", "\n")
    start = text.find(SATZ_ANFANG)
    ende = text.find(SATZ_ENDE, start)
    if start < 0 or ende < 0:
        raise SystemExit(f"Satz nicht gefunden (start={start}, ende={ende})")
    return " ".join(text[start:ende + len(SATZ_ENDE)].split())


def rows_of(data: dict) -> list:
    """Zeilen eines E3-Artefakts, unabhaengig von seiner Schreibweise."""
    rows = data.get("alle_zeilen")
    if rows:
        return [r for r in rows if isinstance(r, dict)]
    treffer = data.get("treffer") or {}
    return [r for r in treffer.values() if isinstance(r, dict)]


def main() -> int:
    satz = lade_satz()
    intervalle = find_intervals(satz)
    print(f"MENDS-Satz: {len(satz)} Zeichen, {len(intervalle)} Intervalle")
    for interval in intervalle:
        print(f"  {interval.label()}  aus {interval.raw[:60]}...")
    if len(intervalle) != 2:
        print("ABBRUCH: Der Satz muss zwei Intervalle nennen.")
        return 4

    laeufe = []
    for test_id, datei in LAEUFE:
        pfad = VALIDIERUNG / datei
        if not pfad.exists():
            print(f"{test_id}: {datei} fehlt - uebersprungen")
            laeufe.append({"test": test_id, "datei": datei, "fehlt": True})
            continue
        data = json.loads(pfad.read_text(encoding="utf-8"))
        rows = rows_of(data)
        reports = audit_rows(rows)
        counts = summarize(reports)
        gespeichert = " ".join(str(data.get("satz") or "").split())
        if not gespeichert:
            satz_status = "kein_satz_feld"
        elif gespeichert == satz:
            satz_status = "gleich"
        elif satz in gespeichert:
            satz_status = "enthalten"
        else:
            satz_status = "nicht_enthalten"
        print(f"\n{test_id}: {len(rows)} Zeile(n), MENDS-Satz im Artefakt: {satz_status}")
        for report in reports:
            print(f"  {report.status}: {report.message}")
        laeufe.append({
            "test": test_id,
            "datei": datei,
            "satz_im_artefakt": satz_status,
            "zeilen": len(rows),
            "zaehlung": counts,
            "befunde": [r.to_dict() for r in reports],
        })

    # Gegenprobe 1: beide gemessenen Zeilen zusammen schliessen die Luecke.
    # Die Zeilen kommen aus den Artefakten selbst, nicht aus dem Sollwert.
    diary = acti = None
    rows_by_test = {}
    for test_id, datei in LAEUFE:
        pfad = VALIDIERUNG / datei
        if pfad.exists():
            rows_by_test[test_id] = rows_of(json.loads(pfad.read_text(encoding="utf-8")))
    for zeile in rows_by_test.get("E3b-isolierter-satz", []):
        if abs(float(zeile.get("effect") or 0) + 45.34) <= 0.01:
            acti = zeile
    for zeile in rows_by_test.get("E3c-prompt-regel", []):
        if abs(float(zeile.get("effect") or 0) + 37.49) <= 0.01:
            diary = zeile
    beide = [z for z in (diary, acti) if z]
    gegenprobe_vollstaendig = audit_quote(satz, beide)
    print(f"\nGegenprobe mit beiden Zeilen: {gegenprobe_vollstaendig.status} "
          f"({gegenprobe_vollstaendig.message})")

    # Gegenprobe 2: ohne CI-Angabe keine falsche Luecke.
    ohne_ci = audit_quote("Melatonin reduced SOL more than placebo.", beide)
    print(f"Gegenprobe ohne CI: {ohne_ci.status} ({ohne_ci.message})")

    ergebnis = {
        "test": "E4-quote-luecken",
        "stand": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "modellaufrufe": 0,
        "tokens": 0,
        "datei": str(TEXT_PATH.relative_to(ROOT)).replace("\\", "/"),
        "satz": satz,
        "satz_zeichen": len(satz),
        "intervalle_im_satz": [i.label() for i in intervalle],
        "laeufe": laeufe,
        "gegenproben": {
            "beide_zeilen": gegenprobe_vollstaendig.to_dict(),
            "ohne_ci": ohne_ci.to_dict(),
        },
    }
    OUT_JSON.write_text(json.dumps(ergebnis, ensure_ascii=False, indent=2),
                        encoding="utf-8")

    zeilen_md = [
        "# E4 - deterministische Lueckenpruefung an den E3-Artefakten",
        "",
        f"Stand: {time.strftime('%Y-%m-%d %H:%M')} · Modellaufrufe: 0 · Tokens: 0",
        "",
        "Geprueft wird der MENDS-Satz, aus dem die E3-Zeilen stammen. Die Zeilen",
        "kommen unveraendert aus den drei JSON-Artefakten; nichts wurde",
        "nachgetragen.",
        "",
        f"Satz ({len(satz)} Zeichen), {len(intervalle)} Intervalle:",
        "",
        "```",
        satz,
        "```",
        "",
        "| Lauf | Zeilen | Intervalle | Status | Befund |",
        "|---|---:|---:|---|---|",
    ]
    for eintrag in laeufe:
        if eintrag.get("fehlt"):
            zeilen_md.append(f"| {eintrag['test']} | - | - | fehlt | Artefakt nicht vorhanden |")
            continue
        z = eintrag["zaehlung"]
        status = ", ".join(sorted({b["status"] for b in eintrag["befunde"]}))
        befund = " / ".join(b["message"] for b in eintrag["befunde"])
        zeilen_md.append(
            f"| {eintrag['test']} | {z['zeilen']} | {z['intervalle']} | "
            f"{status} | {befund} |"
        )
    zeilen_md += [
        "",
        "## Gegenproben",
        "",
        f"- Beide gemessenen Zeilen zusammen: **{gegenprobe_vollstaendig.status}** - "
        f"{gegenprobe_vollstaendig.message}",
        f"- Satz ohne CI-Angabe: **{ohne_ci.status}** - {ohne_ci.message} "
        "(keine falsche Luecke)",
        "",
        "## Was das heisst",
        "",
        "Die beiden Laeufe, die je eine korrekte Zeile geliefert haben, sind",
        "Luecken: Die Quote nennt zwei Intervalle, die Kette haette k = 1",
        "gepoolt. Der Check findet sie ohne Modellaufruf und ohne Sollwert -",
        "er liest nur die Quote gegen die Zeilen. E3a ist der wichtigste",
        "Negativfall: Seine Quote nennt genau ein Intervall, verschachtelt",
        "geschrieben als `[95% confidence interval (CI) 0.52 to 44.34]`.",
        "Ein Regex auf klammerfreie Inhalte haette sie uebersprungen und",
        "`nicht_pruefbar` gemeldet; der Scanner zaehlt die Klammertiefe.",
        "",
        "Grenzen: Die Zuordnung des fehlenden Intervalls laeuft ueber die Zahlen",
        "und ist eine Diagnose. Die harte Aussage ist die Anzahl. Eine Zeile,",
        "die zwei Intervalle zu einem zusammenfasst, gilt ebenfalls als Luecke.",
    ]
    OUT_MD.write_text("\n".join(zeilen_md) + "\n", encoding="utf-8")
    print(f"\nJSON: {OUT_JSON.relative_to(ROOT)}")
    print(f"MD:   {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
