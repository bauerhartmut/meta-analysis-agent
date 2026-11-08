"""Zweiter Lesedurchgang auf dem Q2-Korpus (offline, kein Netz).

Was gegenueber dem ersten Durchgang anders ist, und nur das:

* Titelscreening: nur Studien, deren Titel Melatonin als Intervention nennt;
  Agonisten (Ramelteon, Tasimelteon) und andere Wirkstoffe fallen heraus.
* Streuungs-Etikett aus der Caption: steht dort "mean (SD)" oder ein "±",
  gilt eine Zahl in Klammern als SD - gelesen, nicht geraten.
* Zeitpunkt-Spalten: bei "Baseline | Week 12"-Koepfen wird die letzte
  Nach-Baseline-Spalte je Arm genommen, nicht die Zeile verworfen.
* Fallzahl aus einer N-Zeile derselben Tabelle ("N | 86 | 86") oder aus dem
  Satz, der den Arm nennt ("melatonin (n = 32)").

Alles andere bleibt wie im ersten Durchgang: derselbe Konverter, dieselbe
Speicherregel (Zitat muss woertlich im Dokument stehen), keine Ergaenzung,
keine Interpolation.

Aufruf:
    .venv/bin/python.exe scripts/read_q2_extended.py
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_agent.coverage.manager import _xml_to_text  # noqa: E402
from research_agent.database import Database  # noqa: E402
from research_agent.meta.arm_level import (  # noqa: E402
    convert_row,
    store_arm_level_effects,
)
from research_agent.research.jats_tables import (  # noqa: E402
    _pipe_row,
    parse_jats,
)

SOL = re.compile(r"sleep[- ]onset|sleep[- ]latency|\bSOL\b", re.I)
NOT_MELATONIN_INTERVENTION = re.compile(
    r"ramelteon|tasimelteon|agomelatine|valerian|cherry|vitamin|exercise|"
    r"dexmedetomidine|temazepam|zolpidem|melatonin receptor agonist",
    re.I,
)
SD_CAPTION = re.compile(
    r"mean[s]?\s*\(\s*SD\s*\)|mean[s]?\s*±|figures?\s+are\s+mean|values?\s+are\s+mean",
    re.I,
)
POST_TIME = re.compile(r"\b(?:week|wk|visit|day|month)\s*(\d+)", re.I)
GENERIC_HEAD = re.compile(
    r"^(?:|parameter|variable|outcome|n|mean(?:\s*\(sd\))?|sd|se|change|"
    r"p\s*-?\s*value|difference.*|adjusted.*|estimate.*|short\s*term.*|"
    r"long\s*term.*|total.*)$", re.I,
)


def split_arm_prefix(head: str) -> str:
    """'Melatonin Week 12' -> 'Melatonin'; 'Placebo No of children' -> 'Placebo'."""
    text = re.sub(r"\s+", " ", str(head or "")).strip()
    text = re.split(
        r"\b(?:baseline|week|wk|visit|day|month|change|mean|sd|se|no\.?|number|n)\b",
        text, maxsplit=1, flags=re.I,
    )[0]
    return text.strip(" ,;:-")


def n_from_text(text: str, labels: list[str]) -> list[int] | None:
    """Fallzahl je Arm aus einem Satz, der den Arm nennt ("placebo (n = 32)").

    Nur belegte Zahlen: beide Arme muessen im Text stehen, sonst None.
    """
    found: list[int] = []
    for label in labels:
        token = re.escape(label.strip())
        match = re.search(rf"{token}[^.;]{{0,80}}?\bn\s*=\s*(\d+)", text, re.I)
        if not match:
            match = re.search(rf"\bn\s*=\s*(\d+)[^.;]{{0,80}}?{token}", text, re.I)
        if not match:
            return None
        value = int(match.group(1))
        if not 2 <= value <= 5000:
            return None
        found.append(value)
    return found


def n_row_carry(header: list[str], cells: list[str]) -> dict[int, int] | None:
    """Eine Zeile, die nur Fallzahlen traegt ("N | 86 | 86") - Spalte -> n."""
    first = str(cells[0] if cells else "").strip().lower()
    if first not in ("n", "no", "no.", "number"):
        return None
    values = {}
    for index, cell in enumerate(cells[1:], start=1):
        text = str(cell or "").strip()
        if re.fullmatch(r"\d{1,5}", text):
            values[index] = int(text)
    return values or None


def timepoint_view(header: list[str], cells: list[str],
                   carried: dict[int, int]) -> tuple[list[str], list[str], list[int]] | None:
    """Zwei Armspalten auf den letzten Nach-Baseline-Zeitpunkt reduzieren."""
    groups: dict[str, list[int]] = {}
    for index, head in enumerate(header):
        if index >= len(cells):
            continue
        prefix = split_arm_prefix(head)
        if not prefix or GENERIC_HEAD.match(prefix) or len(prefix) < 3:
            continue
        groups.setdefault(prefix, []).append(index)
    if len(groups) != 2:
        return None
    chosen: list[int] = []
    for prefix, columns in groups.items():
        scored = []
        for index in columns:
            match = POST_TIME.search(header[index])
            if match:
                scored.append((int(match.group(1)), index))
        if not scored:
            return None
        chosen.append(max(scored)[1])
    n_per_arm = []
    for index in chosen:
        if index in carried:
            n_per_arm.append(carried[index])
            continue
        prefix = split_arm_prefix(header[index])
        n_index = None
        for other, head in enumerate(header):
            if split_arm_prefix(head) == prefix and re.search(
                    r"\b(?:no\.?|number)\s+of\b|\bn\b", str(head), re.I):
                n_index = other
                break
        if n_index is None or n_index >= len(cells):
            return None
        text = str(cells[n_index] or "").strip()
        if not re.fullmatch(r"\d{1,5}", text):
            return None
        n_per_arm.append(int(text))
    new_header = [split_arm_prefix(header[index]) for index in chosen]
    new_cells = [cells[index] for index in chosen]
    return new_header, new_cells, n_per_arm


def main() -> int:
    pairs = json.loads(Path("data/bench/sol2/manifest_pairs.json").read_text(encoding="utf-8"))
    screened = [p for p in pairs
                if re.search(r"melatonin", str(p.get("title") or ""), re.I)
                and not NOT_MELATONIN_INTERVENTION.search(str(p.get("title") or ""))]
    print(f"Titelscreening: {len(screened)} von {len(pairs)} Dokumenten")

    db_path = Path("data/bench/sol2/extended.db")
    if db_path.exists():
        db_path.unlink()
    db = Database(str(db_path))

    documents, reasons_total, stored_total = [], Counter(), 0
    for pair in screened:
        pmc = pair["pmc"]
        xml = (Path("data/bench/sol2/xml") / f"{pmc}.xml").read_text(encoding="utf-8", errors="replace")
        text = _xml_to_text(xml)
        # Crossover: beide Arme sind dieselben Personen. Arm-Mittelwerte sind
        # lesbar, aber n je Arm ist nicht unabhaengig und SE(g) gilt fuer
        # parallele Gruppen. Nicht poolen, sondern als eigene Klasse melden.
        is_crossover = bool(re.search(r"cross[\s-]?over", text, re.I))
        source_id = f"doi:{pair['doi']}"
        row = db.save_source_text(source_id, text, kind="xml",
                                  origin_url=f"https://www.ncbi.nlm.nih.gov/pmc/{pmc}/")
        text_id = (row or {}).get("id", "")

        candidates, reasons = [], Counter()
        sol_rows = 0
        for table in parse_jats(Path("data/bench/sol2/xml") / f"{pmc}.xml"):
            caption = f"{table.label or ''} {table.caption or ''}".strip()
            hint = "sd" if SD_CAPTION.search(caption) else ""
            carried: dict[int, int] = {}
            for table_row in table.rows:
                quote = _pipe_row(table_row.cells)
                numbers = n_row_carry(table.header, table_row.cells)
                if numbers:
                    carried.update(numbers)
                    continue
                if not (SOL.search(quote) or SOL.search(caption)):
                    continue
                sol_rows += 1
                attempt = convert_row(table.header, table_row.cells,
                                      quote=quote, caption=caption,
                                      row_group=table_row.row_group,
                                      spread_hint=hint)
                if not attempt.get("ok") and attempt.get("reason") == "Fallzahl je Arm fehlt":
                    labels = [split_arm_prefix(h) for h in table.header
                              if split_arm_prefix(h)]
                    labels = [l for i, l in enumerate(labels) if l]
                    per_arm = n_from_text(text, labels[:2]) if len(labels) >= 2 else None
                    if per_arm:
                        attempt = convert_row(table.header, table_row.cells,
                                              quote=quote, caption=caption,
                                              row_group=table_row.row_group,
                                              spread_hint=hint, n_per_arm=per_arm)
                if not attempt.get("ok"):
                    view = timepoint_view(table.header, table_row.cells, carried)
                    if view:
                        new_header, new_cells, per_arm = view
                        attempt = convert_row(new_header, new_cells, quote=quote,
                                              caption=caption, spread_hint=hint,
                                              n_per_arm=per_arm)
                if attempt.get("ok"):
                    if is_crossover:
                        reasons["Crossover: Armwerte lesbar, n je Arm nicht unabhaengig"] += 1
                    else:
                        candidates.append(attempt)
                else:
                    reasons[attempt.get("reason") or "unbekannt"] += 1

        stored, rejected = store_arm_level_effects(db, source_id, text_id, text, candidates)
        for entry in rejected:
            reasons[entry.get("reason") or "unbekannt"] += 1
        stored_total += len(stored)
        reasons_total.update(reasons)
        documents.append({
            "pmc": pmc, "doi": pair["doi"], "year": pair.get("year"),
            "title": str(pair.get("title") or "")[:120],
            "sol_rows": sol_rows, "candidates": len(candidates),
            "stored": len(stored),
            "reasons": dict(reasons.most_common()),
            "effects": [{"outcome": e.get("outcome"), "g": e.get("effect"),
                         "se": e.get("se"), "n": e.get("n"),
                         "arms": json.loads(e.get("moderators") or "{}").get("arms", []),
                         "quote": str(e.get("quote") or "")[:160]} for e in stored],
        })

    mit_treffer = [d for d in documents if d["stored"]]
    report = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "documents_total": len(pairs),
        "screened_in": len(screened),
        "k": len(mit_treffer),
        "rows": stored_total,
        "reasons": dict(reasons_total.most_common()),
        "documents": documents,
    }
    Path("data/bench/sol2/extended.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Zweiter Lesedurchgang auf dem Q2-Korpus",
        "",
        f"Stand: {report['generated']}. Kein Netz. Titelscreening, "
        "Caption-SD, Zeitpunkt-Spalten und Fallzahl aus N-Zeile oder Satz.",
        "",
        f"- Dokumente im Korpus: {len(pairs)}",
        f"- nach Titelscreening: {len(screened)}",
        f"- **Studien mit gespeicherter Zeile (k): {report['k']}**",
        f"- gespeicherte Zeilen: {stored_total}",
        "",
        "## Dokumente mit Treffern",
        "",
        "| PMC | Jahr | Zeilen | k | Outcome | Arme |",
        "|---|---:|---:|---|---|---|",
    ]
    for doc in mit_treffer:
        for effect in doc["effects"]:
            arms = "; ".join(f"{a.get('label', '')[:20]} {a.get('mean')} ± {a.get('sd')} "
                             f"(n={a.get('n')})" for a in effect["arms"])
            lines.append(f"| {doc['pmc']} | {doc['year'] or ''} | {doc['sol_rows']} | "
                         f"{doc['stored']} | {str(effect['outcome'])[:38]} | {arms} |")
    if not mit_treffer:
        lines.append("| - | - | - | - | keine | - |")
    lines += ["", "## Ablehnungsgruende (alle gescreenten Dokumente)", ""]
    for reason, count in reasons_total.most_common():
        lines.append(f"- {count:4d}  {reason}")
    lines += ["", "## Je Dokument", "",
              "| PMC | Zeilen | Kandidaten | gespeichert |", "|---|---:|---:|---:|"]
    for doc in documents:
        lines.append(f"| {doc['pmc']} | {doc['sol_rows']} | {doc['candidates']} | {doc['stored']} |")
    Path("data/bench/sol2/extended.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"k = {report['k']}, Zeilen = {stored_total}")
    for doc in mit_treffer:
        print(f"  {doc['pmc']}: {doc['stored']} Zeilen aus {doc['sol_rows']} SOL-Zeilen")
    print("Ablehnungsgruende:")
    for reason, count in reasons_total.most_common(8):
        print(f"  {count:4d}  {reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
