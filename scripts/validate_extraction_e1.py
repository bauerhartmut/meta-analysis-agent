"""E1: Findet der Harness die MENDS-Effekte im Volltext?

Ruft den tatsaechlichen, deterministischen Lesepfad auf - Tabellenbloecke,
Arm-Text-Leser, Change-Arm-Leser - auf dem lokalen MENDS-Text. Kein Modell,
kein Netz, keine vorgegebenen Werte.

Sollwerte (dokumentiert in ``mends_hta_zusatz_20261108.md``):
  * Schlaftagebuch:  -37,49 min (95% CI -55,27 bis -19,71), SE 9,0818
  * Aktigraphie:     -45,34 min (95% CI -68,75 bis -21,93), SE 11,9645

Bewertung: Ein Effekt gilt als gefunden, wenn ein Kandidat eines Lesers den
Wert auf 0,01 min trifft. Zusaetzlich wird gemessen, ob der Satz mit dem Wert
in einem erkannten Tabellenblock liegt - das ist die Fehlerursache, nicht die
Vermutung.

Schreibt ``data/bench/validierung/e1_extraktion_20261108.{json,md}``.
Aendert keine Implementierung und keine Analysedaten.
"""

from __future__ import annotations

import json
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research_agent.meta.arm_change import change_candidates  # noqa: E402
from research_agent.meta.arm_text import text_arm_candidates  # noqa: E402
from research_agent.meta.effect_columns import (  # noqa: E402
    effects_from_row,
    header_effect_kind,
    parse_effect_cell,
)
from research_agent.meta.pdf_text import normalize  # noqa: E402
from research_agent.research.table_extractor import find_table_blocks  # noqa: E402
from scripts.read_pdf_corpus import rows_from_block  # noqa: E402

QUELLE = ROOT / "data/bench/sol2/volltext/23098680.txt"
OUT_DIR = ROOT / "data/bench/validierung"
TOLERANZ = 0.01

SOLL = (
    {"id": "MENDS-Tagebuch", "est": -37.49, "ci_low": -55.27, "ci_high": -19.71,
     "se": 9.0818, "methode": "sleep diary"},
    {"id": "MENDS-Aktigraphie", "est": -45.34, "ci_low": -68.75,
     "ci_high": -21.93, "se": 11.9645, "methode": "actigraphy"},
)

WERT_FELDER = ("effect", "est", "value", "mean_diff", "smd", "g", "d")

# Korrektur an meiner eigenen Ursachenangabe - nicht am Messergebnis.
KORREKTUREN = (
    {
        "fall": "Befundtext im Erstlauf",
        "text": (
            "Der erste Bericht behauptete, der Wert stehe nur im Fliesstext "
            "und ein Satz sei kein Tabellenblock. Die Messung widerlegt das: "
            "-37.49 und -45.34 stehen in Block 6 als Wert mit Intervall in "
            "einer Zelle (`-37.49 (-55.27 to -19.71)`). Korrigiert ist die "
            "Ursachenangabe, nicht das Messergebnis (0 Treffer)."
        ),
    },
)


def zahlen(kandidat: dict) -> list[tuple[str, float]]:
    """Alle numerischen Effektfelder eines Kandidaten, ohne Interpretation."""
    werte = []
    for feld in WERT_FELDER:
        wert = kandidat.get(feld)
        if isinstance(wert, (int, float)):
            werte.append((feld, float(wert)))
    return werte


def lese(text: str) -> dict:
    """Alle deterministischen Leser auf denselben Text anwenden."""
    arm = text_arm_candidates(text)
    change = change_candidates(text)

    gruende = Counter()
    direkt = []
    blocks = find_table_blocks(text)
    for block in blocks:
        header, rows = rows_from_block(block.body)
        if not rows:
            continue
        for cells in rows:
            found, reason = effects_from_row(
                header, cells, block.body, caption=block.caption)
            if found:
                direkt.extend(found)
            else:
                gruende[str(reason)[:60]] += 1

    return {
        "blocks": len(blocks),
        "arm": arm,
        "change": change,
        "direkt": direkt,
        "gruende": gruende,
        "block_bodies": [str(b.body) for b in blocks],
    }


def pruefe(soll: dict, gelesen: dict) -> dict:
    """Trifft irgendein Kandidat den Sollwert?"""
    treffer = []
    for pfad, kandidaten in (("arm_text", gelesen["arm"]),
                             ("arm_change", gelesen["change"]),
                             ("direkt", gelesen["direkt"])):
        for kandidat in kandidaten:
            for feld, wert in zahlen(kandidat):
                if abs(wert - soll["est"]) <= TOLERANZ:
                    treffer.append({
                        "pfad": pfad, "feld": feld, "wert": wert,
                        "outcome": str(kandidat.get("outcome") or "")[:80],
                        "se": kandidat.get("se"),
                    })
    return {
        "id": soll["id"],
        "soll_est": soll["est"],
        "soll_se": soll["se"],
        "soll_ci": [soll["ci_low"], soll["ci_high"]],
        "treffer": treffer,
        "status": "PASS" if treffer else "FAIL",
    }


def satz_lage(text: str, wert: float, gelesen: dict) -> dict:
    """Wo steht der Wert - im Fliesstext oder in einem Block?"""
    marke = f"{abs(wert):.2f}"
    zeilen = [i + 1 for i, z in enumerate(text.splitlines()) if marke in z]
    in_block = 0
    for body in gelesen["block_bodies"]:
        if marke in body:
            in_block += 1
    return {
        "marke": marke,
        "zeilen": zeilen[:6],
        "zeilen_gesamt": len(zeilen),
        "bloecke_mit_marke": in_block,
        "im_fliesstext": len(zeilen) > 0 and in_block == 0,
    }


def zell_befund(block_bodies: list[str], wert: float) -> dict | None:
    """Steht der Wert als lesbare Effektzelle in einem Block?"""
    marke = f"{abs(wert):.2f}"
    for nummer, body in enumerate(block_bodies, 1):
        header, rows = rows_from_block(body)
        for cells in rows:
            for index, cell in enumerate(cells):
                if marke not in cell:
                    continue
                kopfzelle = header[index] if index < len(header) else ""
                kind, _, beides = header_effect_kind(kopfzelle)
                geparst = parse_effect_cell(cell)
                return {
                    "block": nummer,
                    "zelle": cell.strip(),
                    "zelle_lesbar": geparst is not None,
                    "geparst": geparst,
                    "kopfzelle": kopfzelle.strip(),
                    "kopf_ist_effektspalte": bool(beides),
                    "kopf_effektwort": kind,
                }
    return None


def schreibe_bericht(ergebnis: dict) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "e1_extraktion_20261108.json").write_text(
        json.dumps(ergebnis, ensure_ascii=False, indent=2),
        encoding="utf-8", newline="\n")

    z = [
        "# E1 - MENDS-Extraktion durch den Harness",
        "",
        f"Stand: {ergebnis['stand']}. Test-ID `{ergebnis['test_id']}`.",
        f"Eingabe: `{ergebnis['quelle']}` ({ergebnis['zeichen']} Zeichen "
        f"normalisiert, {ergebnis['blocks']} Tabellenbloecke). "
        "Modellaufrufe: keine. Netz: keines.",
        "",
        "## Soll gegen Ist",
        "",
        "| Effekt | Soll | Toleranz | Gefunden | Ergebnis |",
        "|---|---:|---:|---|---|",
    ]
    for p in ergebnis["pruefungen"]:
        gefunden = ", ".join(f"{t['pfad']}:{t['wert']}" for t in p["treffer"]) or "-"
        z.append(f"| {p['id']} | {p['soll_est']} min | {TOLERANZ} | {gefunden} | "
                 f"**{p['status']}** |")

    g = ergebnis["gelesen"]
    z += [
        "",
        "## Was die Leser geliefert haben",
        "",
        f"- `text_arm_candidates`: {g['arm']} Kandidaten",
        f"- `change_candidates`: {g['change']} Kandidaten",
        f"- Tabellenpfad (`effects_from_row`): {g['direkt']} direkte Effekte "
        f"aus {g['blocks']} Bloecken",
        "",
        "Ablehnungsgruende des Tabellenpfads:",
        "",
        "| Grund | Anzahl |",
        "|---|---:|",
    ]
    for grund, anzahl in sorted(g["gruende"].items(), key=lambda kv: -kv[1])[:10]:
        z.append(f"| `{grund}` | {anzahl} |")

    z += ["", "## Fehlerbeschreibung", ""]
    for p in ergebnis["pruefungen"]:
        lage = p["lage"]
        z.append(
            f"- **{p['id']}**: Wert {p['soll_est']} steht in "
            f"{lage['zeilen_gesamt']} Textzeile(n) "
            f"({', '.join(map(str, lage['zeilen'])) or '-'}), in "
            f"{lage['bloecke_mit_marke']} erkannten Tabellenblock/Bloecken. "
            f"Gefunden: {len(p['treffer'])}."
        )
        if p.get("zelle"):
            zz = p["zelle"]
            z.append(
                f"  - Zelle `{zz['zelle']}` in Block {zz['block']}; "
                f"`parse_effect_cell` -> {zz['geparst']}; Kopfzelle "
                f"`{zz['kopfzelle']}` -> Effektspalte: "
                f"{zz['kopf_ist_effektspalte']}."
            )

    if ergebnis.get("korrekturen"):
        z += ["", "## Korrektur am Bericht", ""]
        for k in ergebnis["korrekturen"]:
            z.append(f"- **{k['fall']}**: {k['text']}")

    z += [
        "",
        "## Befund",
        "",
        ergebnis["befund"],
        "",
        "## Grenzen",
        "",
        "- Geprueft ist der deterministische Lesepfad. Der LLM-Extraktor "
        "(`EffectExtractor`) wurde nicht aufgerufen (keine Modellaufrufe ohne "
        "Freigabe); er ist der naechste Schritt, nicht dieser.",
        "- Eingabe ist die lokale Textebene (`23098680.txt`), nicht das PDF. "
        "Die Produktionskette liest das PDF; der Text ist dessen Extrakt.",
        "- Ein FAIL hier heisst: dieser Lesepfad findet die Zahl nicht. Es "
        "heisst nicht, dass die Zahl im Dokument fehlt.",
        "",
        "## Reproduktion",
        "",
        "```bash",
        "export PYTHONIOENCODING=utf-8",
        ".venv/bin/python.exe scripts/validate_extraction_e1.py",
        "```",
        "",
        f"Laufzeit: {ergebnis['laufzeit_s']:.3f} s. "
        f"Gesamtergebnis: **{ergebnis['gesamt']}**.",
        "",
    ]
    (OUT_DIR / "e1_extraktion_20261108.md").write_text(
        "\n".join(z), encoding="utf-8", newline="\n")


def main() -> int:
    start = time.perf_counter()
    roh = QUELLE.read_text(encoding="utf-8", errors="replace")
    text = normalize(roh)
    gelesen = lese(text)

    pruefungen = []
    for soll in SOLL:
        p = pruefe(soll, gelesen)
        p["lage"] = satz_lage(text, soll["est"], gelesen)
        p["zelle"] = zell_befund(gelesen["block_bodies"], soll["est"])
        pruefungen.append(p)

    gefunden = sum(1 for p in pruefungen if p["status"] == "PASS")
    alles_ok = gefunden == len(SOLL)
    lesbar = [p for p in pruefungen
              if p.get("zelle") and p["zelle"]["zelle_lesbar"]]
    if alles_ok:
        befund = f"Alle {len(SOLL)} berichteten Effekte wurden gefunden."
    else:
        befund = (
            f"{gefunden} von {len(SOLL)} Effekten wurden von keinem Leser "
            f"gefunden. {len(lesbar)} von {len(SOLL)} stehen jedoch als Wert "
            "mit Intervall in einer Tabellenzelle und sind mit "
            "`parse_effect_cell` lesbar; der Tabellenleser erreicht sie nicht, "
            "weil die zugehoerige Kopfzelle keine Effektspalte ist "
            "(`header_effect_kind` False). Der Blocker sitzt damit in der "
            "Kopfzeilenerkennung, nicht im Fehlen der Daten - der Effekt steht "
            "zusaetzlich als Satz im Fliesstext, aber er steht auch in der "
            "Tabelle."
        )

    ergebnis = {
        "test_id": "E1-extraktion-20261108",
        "stand": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "quelle": str(QUELLE.relative_to(ROOT)),
        "zeichen": len(text),
        "blocks": gelesen["blocks"],
        "modell": "keiner",
        "netz": "keines",
        "toleranz": TOLERANZ,
        "pruefungen": pruefungen,
        "gelesen": {
            "blocks": gelesen["blocks"],
            "arm": gelesen["arm"][:20],
            "change": gelesen["change"][:20],
            "direkt": gelesen["direkt"][:20],
            "anzahl_arm": len(gelesen["arm"]),
            "anzahl_change": len(gelesen["change"]),
            "anzahl_direkt": len(gelesen["direkt"]),
            "gruende": dict(gelesen["gruende"].most_common(20)),
        },
        "befund": befund,
        "korrekturen": KORREKTUREN,
        "gesamt": "PASS" if alles_ok else "FAIL",
        "laufzeit_s": time.perf_counter() - start,
    }
    # Zaehlungen fuer den Bericht flach halten
    ergebnis["gelesen"]["arm"] = ergebnis["gelesen"]["anzahl_arm"]
    ergebnis["gelesen"]["change"] = ergebnis["gelesen"]["anzahl_change"]
    ergebnis["gelesen"]["direkt"] = ergebnis["gelesen"]["anzahl_direkt"]
    schreibe_bericht(ergebnis)

    print(f"Quelle: {QUELLE.name}, {len(text)} Zeichen, "
          f"{gelesen['blocks']} Bloecke")
    print(f"Leser: arm={len(gelesen['arm'])} change={len(gelesen['change'])} "
          f"direkt={len(gelesen['direkt'])}")
    for p in pruefungen:
        lage = p["lage"]
        print(f"  {p['id']:<20} soll {p['soll_est']:>7}  "
              f"gefunden {len(p['treffer'])}  "
              f"zeilen {lage['zeilen_gesamt']}  "
              f"bloecke {lage['bloecke_mit_marke']}  {p['status']}")
    for grund, anzahl in gelesen["gruende"].most_common(5):
        print(f"    abgelehnt: {anzahl:>4}x {grund}")
    print(f"\nGESAMT: {ergebnis['gesamt']}  ({ergebnis['laufzeit_s']:.3f} s)")
    print(f"Bericht: {OUT_DIR.relative_to(ROOT)}/e1_extraktion_20261108.md")
    return 0 if alles_ok else 1


if __name__ == "__main__":
    sys.exit(main())
