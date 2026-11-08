"""Diagnose: warum findet der MENDS-Text keine Effektspalte im Tabellenkopf?

Der Lauf ``vergleich_txt_columnar.py`` meldet fuer ``23098680.txt`` (831 KB,
MENDS) 48 Bloecke, aber 404 verworfene Zeilen mit dem Grund "keine
Effektspalte im Kopf". Dieser Grund entsteht in
``meta/effect_columns.header_effect_kind``: eine Kopfzelle muss **selbst** ein
Effektwort (g, SMD, mean difference, OR, RR, HR, beta) **und** eine
CI-Markierung (``CI`` oder ``confidence interval``) tragen.

Das Skript beantwortet drei Fragen, ohne etwas zu aendern:

1. Wo steht die Einschaflatenz im Text, und in welchem Block landet sie?
2. Was steht in den Kopfzeilen der erkannten Bloecke - fehlt das Effektwort,
   die CI-Markierung oder beides?
3. Liegt die SOL-Zeile ueberhaupt in einem Block, oder erkennt der Leser sie
   gar nicht als Tabellenzeile?

Read-only, kein Netz, kein Modell.

Aufruf:
    .venv/bin/python.exe scripts/diagnose_mends_kopf.py
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = Path(__file__).resolve().parent
for path in (ROOT, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import read_pdf_corpus  # noqa: E402
from research_agent.meta.effect_columns import (  # noqa: E402
    _CI,
    effect_word,
    effects_from_row,
    header_effect_kind,
)
from research_agent.meta.pdf_text import normalize  # noqa: E402
from research_agent.research.table_extractor import find_table_blocks  # noqa: E402

TXT = ROOT / "data/bench/sol2/volltext/23098680.txt"
OUT_DIR = ROOT / "data/bench/sol2/gegencheck"
SOL_RE = re.compile(r"sleep[-\s]?onset|\bSOL\b", re.IGNORECASE)


def zeile_um(text: str, pos: int) -> tuple[int, str]:
    """Zeilennummer und Zeilentext an einer Zeichenposition."""
    start = text.rfind("\n", 0, pos) + 1
    end = text.find("\n", pos)
    end = len(text) if end == -1 else end
    return text.count("\n", 0, start) + 1, text[start:end]


def fliesstext_funde(text: str) -> list[dict]:
    """SOL-Saetze mit Intervall - das, was kein Tabellenleser sieht."""
    zeilen = text.splitlines()
    funde: list[dict] = []
    gesehen: set[str] = set()
    for i, zeile in enumerate(zeilen):
        if not (SOL_RE.search(zeile) and _CI.search(zeile)):
            continue
        start, end = i, i
        while start > 0 and zeilen[start - 1].strip():
            start -= 1
        while end < len(zeilen) - 1 and zeilen[end].strip():
            end += 1
        abschnitt = " ".join(x.strip() for x in zeilen[start:end + 1])
        abschnitt = re.sub(r"\s{2,}", " ", abschnitt).strip()
        if abschnitt in gesehen:
            continue
        gesehen.add(abschnitt)
        funde.append({"zeile": i + 1, "abschnitt": abschnitt[:700]})
    return funde


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raw = TXT.read_text(encoding="utf-8", errors="replace")
    text = normalize(raw)
    blocks = find_table_blocks(text)
    fliesstext = fliesstext_funde(text)

    # 1. Wo steht die Einschaflatenz?
    fundstellen = []
    for m in SOL_RE.finditer(text):
        nr, zeile = zeile_um(text, m.start())
        fundstellen.append({"zeile": nr, "text": zeile.strip()[:160]})

    # 2. Kopfzeilen der erkannten Bloecke
    koepfe = Counter()
    kopf_befund = Counter()
    bloecke = []
    for i, block in enumerate(blocks, 1):
        body = getattr(block, "body", "") or ""
        header, rows = read_pdf_corpus.rows_from_block(body)
        caption = str(getattr(block, "caption", "") or "").strip()
        kopf = " | ".join(str(h).strip() for h in header)[:120]
        koepfe[kopf] += 1
        mit_ci = sum(1 for h in header if _CI.search(str(h)))
        mit_wort = sum(1 for h in header if effect_word(str(h))[0])
        mit_beidem = sum(1 for h in header if header_effect_kind(str(h))[0])
        if mit_beidem:
            kopf_befund["Effektwort + CI in einer Zelle"] += 1
        elif mit_wort:
            kopf_befund["Effektwort ohne CI"] += 1
        elif mit_ci:
            kopf_befund["CI ohne Effektwort"] += 1
        else:
            kopf_befund["weder Effektwort noch CI"] += 1

        gruende = Counter()
        treffer = []
        for cells in rows:
            found, reason = effects_from_row(header, cells, body, caption=caption)
            if found:
                treffer.extend(found)
            else:
                gruende[str(reason)[:60]] += 1
        sol_im_block = bool(SOL_RE.search(body))
        bloecke.append({
            "nr": i, "caption": caption[:100], "kopf": kopf,
            "spalten": len(header), "zeilen": len(rows),
            "zellen_mit_ci": mit_ci, "zellen_mit_effektwort": mit_wort,
            "zellen_mit_beidem": mit_beidem,
            "effekte": len(treffer), "gruende": dict(gruende.most_common(4)),
            "sol_im_block": sol_im_block,
            "sol_zeilen": [str(c)[:150] for c in rows
                           if SOL_RE.search(" ".join(str(x) for x in c))],
        })

    # 3. Bloecke mit Einschaflatenz
    sol_bloecke = [b for b in bloecke if b["sol_im_block"]]

    result = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "txt": str(TXT.relative_to(ROOT)),
        "raw_chars": len(raw),
        "norm_chars": len(text),
        "bloecke": len(blocks),
        "fundstellen": fundstellen,
        "fundstellen_gesamt": len(fundstellen),
        "fliesstext_effekte": fliesstext,
        "kopf_befund": dict(kopf_befund),
        "haeufigste_koepfe": koepfe.most_common(12),
        "sol_bloecke": sol_bloecke,
        "bloecke_detail": bloecke,
    }
    (OUT_DIR / "mends_kopf_20261108.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Warum der MENDS-Text keine Effektspalte im Kopf findet",
        "",
        f"Stand: {result['generated']}. Quelle: `{result['txt']}`. "
        "Read-only, kein Netz, kein Modell.",
        "",
        f"Roh: {len(raw)} Zeichen, normalisiert: {len(text)} Zeichen, "
        f"erkannte Bloecke: **{len(blocks)}**.",
        "",
        "## Ablehnungsregel",
        "",
        "`header_effect_kind` akzeptiert eine Kopfzelle nur, wenn sie **selbst** "
        "ein Effektwort (g, SMD, mean difference, OR, RR, HR, beta) **und** "
        "eine CI-Markierung (`CI` oder `confidence interval`) enthaelt. "
        "Punktschaetzer und Intervall in zwei getrennten Spalten gelten nur, "
        "wenn die Punktspalte links daneben ein Effektwort traegt "
        "(`_paired_point`).",
        "",
        "## Befund je Block (Kopfzeile)",
        "",
        "| Befund | Bloecke |",
        "|---|---:|",
    ]
    for name, count in kopf_befund.most_common():
        lines.append(f"| {name} | {count} |")

    lines += ["", "## Haeufigste Kopfzeilen", ""]
    for kopf, count in koepfe.most_common(12):
        lines.append(f"- {count}x `{kopf or '(leer)'}`")

    lines += [
        "",
        "## Einschaflatenz im Text",
        "",
        f"{len(fundstellen)} Fundstellen von 'sleep onset' / 'SOL'.",
        "",
    ]
    for fund in fundstellen[:25]:
        lines.append(f"- Zeile {fund['zeile']}: `{fund['text']}`")
    if len(fundstellen) > 25:
        lines.append(f"- ... {len(fundstellen) - 25} weitere")

    lines += [
        "",
        "## Bloecke, die die Einschaflatenz enthalten",
        "",
        f"{len(sol_bloecke)} von {len(blocks)} Bloecken.",
        "",
    ]
    if not sol_bloecke:
        lines.append("Keiner: der Text nennt die Einschaflatenz, aber der "
                     "Block-Leser legt sie in keinen Block.")
    for b in sol_bloecke:
        lines += [
            f"### Block {b['nr']}: `{b['caption'] or '(ohne Caption)'}`",
            "",
            f"- Kopf: `{b['kopf'] or '(leer)'}`",
            f"- Spalten: {b['spalten']}, Zeilen: {b['zeilen']}",
            f"- Kopfzellen mit CI: {b['zellen_mit_ci']}, mit Effektwort: "
            f"{b['zellen_mit_effektwort']}, mit beidem: {b['zellen_mit_beidem']}",
            f"- gelesene Effekte: {b['effekte']}",
            f"- Ablehnungsgruende: {b['gruende']}",
            "",
        ]
        for zeile in b["sol_zeilen"][:6]:
            lines.append(f"  - `{zeile}`")
        lines.append("")

    lines += [
        "",
        "## Effektgroesse im Fliesstext",
        "",
        f"{len(fliesstext)} SOL-Saetze mit Intervall. Kein Tabellenleser sieht "
        "sie: `effects_from_row` arbeitet nur auf Zeilen erkannter Bloecke, "
        "und ein Satz ist kein Block.",
        "",
    ]
    for fund in fliesstext:
        lines.append(f"- Zeile {fund['zeile']}: {fund['abschnitt']}")
    if not fliesstext:
        lines.append("- keiner")

    lines += ["## Grenzen", "",
              "- Nur eine Datei (MENDS-Doppelpublikation).",
              "- Blockbildung und Kopfzeile haengen davon ab, wie die `.txt` "
              "umgebrochen ist; die Produktionskette liest die PDF.",
              "- Die Diagnose aendert keinen Code und keine Daten."]
    (OUT_DIR / "mends_kopf_20261108.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")

    print(f"bloecke={len(blocks)} sol_fundstellen={len(fundstellen)} "
          f"sol_bloecke={len(sol_bloecke)} fliesstext={len(fliesstext)}")
    for fund in fliesstext:
        print(f"  FLIESSTEXT {fund['zeile']}: {fund['abschnitt'][:260]}")
    print("kopf:", dict(kopf_befund))
    for kopf, count in koepfe.most_common(6):
        print(f"  {count}x {kopf[:100]}")
    for b in sol_bloecke:
        print(f"  SOL-Block {b['nr']} spalten={b['spalten']} zeilen={b['zeilen']} "
              f"ci={b['zellen_mit_ci']} wort={b['zellen_mit_effektwort']} "
              f"beides={b['zellen_mit_beidem']} effekte={b['effekte']}")
        print(f"    kopf: {b['kopf'][:140]}")
        for zeile in b["sol_zeilen"][:4]:
            print(f"    zeile: {zeile[:140]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
