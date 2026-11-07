"""Ausbeute-Funnel des SOL-Korpus: wo gehen die Effektzeilen verloren?

Paket A des Plans. Der Funnel zaehlt neun Stufen und zu jeder Ablehnung den
Grund, ohne das Verhalten der Leser zu aendern: die Leser werden aufgerufen,
ihre Rueckgaben gezaehlt, nichts gespeichert und nichts gelockert.

Stufen (jede mit Zahl und Grund):
  1 dokumente        Manifest-Eintraege, XML vorhanden, fehlend
  2 sol_kandidaten   Dokumente mit deterministischem SOL-RCT-Muster
  3 tabellen         erkannte Tabellen, davon mit Kopfzeile
  4 zeilen           Tabellenzeilen
  5 kandidaten       Zeilen mit Spaltenpaar/Effektspalte (je Leser)
  6 gates            Ablehnungsgruende je Gate
  7 outcome          normalisierte Outcome-Namen, davon SOL-artig
  8 gespeichert      Zeilen in den Mess-DBs (nur wenn --*-db angegeben)
  9 poolbar          Zeilen, die das Pooling annehmen wuerde

Aufruf:
    .venv/bin/python.exe scripts/funnel_sol.py \
        --manifest data/bench/sol/manifest_all.json \
        --xml-dir data/bench/sol/xml \
        --out data/bench/sol/funnel_20261108

Die Ausgabe ist JSON plus Markdown; die Markdown-Datei enthaelt die
Verlust-Rangliste (welche Stufe den groessten Verlust traegt, absolut und
relativ zum Stufeneingang).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

STAGES = (
    "dokumente", "sol_kandidaten", "tabellen", "zeilen", "kandidaten",
    "gespeichert", "poolbar",
)

# Ein Dokument gilt als SOL-RCT-Kandidat, wenn es randomisiert, Placebo und
# Melatonin nennt und dabei die Einschlaflatenz adressiert. Das Muster ist
# absichtlich grob: es soll die Obergrenze ueberschaetzen, nie unterschaetzen.
_SOL_RCT = re.compile(r"melatonin", re.I)
_RANDOM = re.compile(r"randomi[sz]ed|placebo", re.I)
_SOL = re.compile(r"sleep onset latency|sleep[- ]onset insomnia|\bsol\b", re.I)

# Gate-Kategorien: der Grundtext der Leser wird einer Gruppe zugeordnet, damit
# die Verlust-Rangliste nach Gate und nicht nach Formulierung sortiert.
_GATE_PATTERNS: Tuple[Tuple[str, re.Pattern], ...] = (
    ("design", re.compile(r"design|baseline|querschnitt|cross[- ]section|"
                          r"behandlungseffekt|kein arm|vergleich ohne", re.I)),
    ("demografie", re.compile(r"alter|demograf|geschlecht|population|teilnehmer", re.I)),
    ("median", re.compile(r"median|iqr|interquartil", re.I)),
    ("sem_se", re.compile(r"\bsem\b|standard error|standardfehler|\bse\b", re.I)),
    ("tabellenrest", re.compile(r"spalte|kopfzeile|zelle|tabelle|zeile|"
                                r"zitat|beleg|pipe", re.I)),
)

_EFFECT_G = frozenset({"g", "smd", "d", "hedges_g", "mean_diff"})


def gate_of(reason: str) -> str:
    """Ablehnungsgrund -> Gate-Kategorie (deterministisch, ohne Modell)."""
    text = str(reason or "").strip()
    if not text:
        return "unbekannt"
    for name, pattern in _GATE_PATTERNS:
        if pattern.search(text):
            return name
    return "sonstig"


def loss_ranking(stages: Dict[str, int]) -> List[dict]:
    """Verlust je Stufe, absolut und relativ zum Stufeneingang.

    Die Stufen sind nicht durchgaengig (Tabellenzeilen sind keine Saetze),
    deshalb wird der Verlust nur dort gebildet, wo eine Stufe echt aus der
    vorherigen folgt: Dokumente -> SOL-Kandidaten, Zeilen -> Kandidaten,
    Kandidaten -> gespeichert, gespeichert -> poolbar.
    """
    pairs = (
        ("dokumente", "sol_kandidaten"),
        ("zeilen", "kandidaten"),
        ("kandidaten", "gespeichert"),
        ("gespeichert", "poolbar"),
    )
    out: List[dict] = []
    for source, target in pairs:
        before = int(stages.get(source) or 0)
        after = int(stages.get(target) or 0)
        lost = max(0, before - after)
        out.append({
            "from": source,
            "to": target,
            "input": before,
            "output": after,
            "lost": lost,
            "lost_share": (lost / before) if before else None,
        })
    return out


def biggest_loss(ranking: Iterable[dict]) -> Optional[dict]:
    """Die eine Stufe mit dem groessten absoluten Verlust."""
    rows = [row for row in ranking if row.get("lost")]
    if not rows:
        return None
    return max(rows, key=lambda row: row["lost"])


def _empty_reader() -> Dict:
    # candidates = Zeilen mit Treffer, effects = gefundene Effekte. Eine
    # Tabellenzeile kann mehrere Effekte tragen; die Stufe "Kandidaten"
    # zaehlt Effekte, damit sie mit "gespeichert" vergleichbar bleibt.
    return {"candidates": 0, "effects": 0, "stored": 0,
            "reasons": Counter(), "outcomes": Counter()}


def _fold(reader: Dict, ok: bool, reason: str = "", outcome: str = "",
          quote_ok: bool = True) -> None:
    """Einen Leser-Aufruf zaehlen: Kandidat oder Ablehnung mit Grund."""
    if ok and quote_ok:
        reader["candidates"] += 1
        reader["effects"] += 1
        if outcome:
            reader["outcomes"][outcome] += 1
        return
    reader["reasons"][str(reason or "unbekannt").strip() or "unbekannt"] += 1


def summarise_reader(reader: Dict, rows_in: int) -> Dict:
    """Konsistenz eines Lesers: Eingang = Kandidaten + Summe der Ablehnungen."""
    rejected = sum(reader["reasons"].values())
    return {
        "rows_in": rows_in,
        "candidates": reader["candidates"],
        "effects": reader["effects"],
        "rejected": rejected,
        "sum_ok": reader["candidates"] + rejected == rows_in,
        "reasons": dict(reader["reasons"].most_common()),
        "outcomes": dict(reader["outcomes"].most_common(20)),
    }


def gates_of(reasons: Dict[str, int]) -> Dict[str, int]:
    """Ablehnungsgruende zu Gate-Kategorien zusammenfassen."""
    out: Counter = Counter()
    for reason, count in reasons.items():
        out[gate_of(reason)] += int(count)
    return dict(out.most_common())


def write_markdown(report: Dict, path: Path) -> None:
    stages = report["stages"]
    ranking = report["loss_ranking"]
    top = report.get("biggest_loss") or {}
    lines = [
        "# Ausbeute-Funnel SOL-Korpus",
        "",
        f"Stand: {report['generated']}. Leser unveraendert; der Funnel zaehlt "
        "nur mit. Kein LLM, kein Netzzugriff.",
        "",
        "## Stufen",
        "",
        "| Stufe | Zahl |",
        "|---|---:|",
        f"| Manifest-Eintraege | {stages['manifest']} |",
        f"| XML vorhanden | {stages['dokumente']} |",
        f"| XML fehlend | {stages['fehlend']} |",
        f"| SOL-RCT-Kandidaten | {stages['sol_kandidaten']} |",
        f"| Tabellen erkannt | {stages['tabellen']} |",
        f"| Tabellenzeilen | {stages['zeilen']} |",
        f"| Saetze (Fliesstext) | {stages['saetze']} |",
        f"| Kandidaten (alle Leser) | {stages['kandidaten']} |",
        f"| gespeichert (DBs) | {stages['gespeichert']} |",
        f"| poolbar (Zeilen, nicht Gruppen) | {stages['poolbar']} |",
        "",
        "## Verlust-Rangliste",
        "",
        "| Von | Nach | Eingang | Ausgang | verloren | Anteil |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in ranking:
        share = ("-" if row["lost_share"] is None
                 else f"{row['lost_share'] * 100:.1f} %")
        lines.append(
            f"| {row['from']} | {row['to']} | {row['input']} | "
            f"{row['output']} | {row['lost']} | {share} |"
        )
    lines += ["", "## Groesster Verlust", ""]
    if top:
        share = ("unbekannt" if top["lost_share"] is None
                 else f"{top['lost_share'] * 100:.1f} %")
        lines.append(
            f"**{top['from']} -> {top['to']}**: {top['lost']} von "
            f"{top['input']} ({share}) gehen verloren."
        )
    else:
        lines.append("Kein Verlust auf den vergleichbaren Stufen.")
    lines += ["", "## Leser im Detail", ""]
    for name, stats in (report.get("readers") or {}).items():
        lines += [
            f"### {name}",
            "",
            f"- Eingang: {stats['rows_in']}, Kandidatenzeilen: {stats['candidates']}, "
            f"Effekte: {stats.get('effects', 0)}, "
            f"abgelehnt: {stats['rejected']}, Summe stimmt: "
            f"{'ja' if stats['sum_ok'] else 'NEIN'}",
            f"- Gates: {stats.get('gates') or {}}",
            "",
            "| Grund | Zahl |",
            "|---|---:|",
        ]
        for reason, count in list((stats.get("reasons") or {}).items())[:12]:
            lines.append(f"| {reason[:110]} | {count} |")
        lines.append("")
    lines += ["## Offen", ""]
    for item in report.get("open") or []:
        lines.append(f"- {item}")
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_manifest(path: Path) -> List[dict]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return [entry for entry in raw if entry.get("pmc")]


def funnel(manifest: Path, xml_dir: Path, out_stem: Path,
           limit: Optional[int] = None, with_text: bool = True,
           dbs: Optional[Dict[str, str]] = None,
           progress_every: int = 100) -> Dict:
    """Funnel ueber den Korpus rechnen und JSON + Markdown schreiben."""
    from research_agent.coverage.manager import _xml_to_text
    from research_agent.meta.arm_change import convert_sentence as change_sentence
    from research_agent.meta.arm_level import convert_row
    from research_agent.meta.arm_text import convert_sentence as text_sentence
    from research_agent.meta.arm_text import split_sentences
    from research_agent.meta.effect_columns import effects_from_row
    from research_agent.meta.outcome_labels import normalize_outcome
    from research_agent.research.jats_tables import _pipe_row, parse_jats

    entries = read_manifest(manifest)
    if limit:
        entries = entries[:limit]

    stages = Counter({key: 0 for key in (
        "manifest", "fehlend", "dokumente", "sol_kandidaten", "tabellen",
        "zeilen", "saetze", "kandidaten", "gespeichert", "poolbar",
    )})
    stages["manifest"] = len(entries)
    readers = {
        "effektspalten": _empty_reader(),
        "arm_tabelle": _empty_reader(),
        "arm_text": _empty_reader(),
        "change": _empty_reader(),
    }
    rows_in = Counter()
    documents: List[dict] = []
    missing: List[str] = []

    for index, entry in enumerate(entries, start=1):
        pmc = str(entry["pmc"])
        path = Path(xml_dir) / f"{pmc}.xml"
        if not path.is_file():
            missing.append(pmc)
            stages["fehlend"] += 1
            continue
        stages["dokumente"] += 1
        xml = path.read_text(encoding="utf-8", errors="replace")
        text = _xml_to_text(xml)
        is_candidate = bool(_SOL_RCT.search(text) and _RANDOM.search(text)
                            and _SOL.search(text))
        if is_candidate:
            stages["sol_kandidaten"] += 1

        doc = {"pmc": pmc, "doi": entry.get("doi") or "",
               "sol_kandidat": is_candidate, "tabellen": 0, "zeilen": 0,
               "kandidaten": 0, "reasons": Counter()}
        for table in parse_jats(path):
            stages["tabellen"] += 1
            doc["tabellen"] += 1
            caption = " ".join(filter(None, [table.label or "", table.caption or ""]))
            for table_row in table.rows:
                stages["zeilen"] += 1
                doc["zeilen"] += 1
                rows_in["effektspalten"] += 1
                rows_in["arm_tabelle"] += 1
                quote = _pipe_row(table_row.cells)

                direct, reason = effects_from_row(
                    table.header, table_row.cells, quote=quote, caption=caption)
                if direct:
                    # Eine Zeile ist ein Kandidat, auch wenn sie mehrere Effekte
                    # traegt: gezaehlt wird die Zeile, nicht der Effekt. Sonst
                    # passt die Stufensumme nicht mehr zum Zeileneingang.
                    readers["effektspalten"]["candidates"] += 1
                    readers["effektspalten"]["effects"] += len(direct)
                    for item in direct:
                        outcome = str(item.get("outcome") or "")
                        if outcome:
                            readers["effektspalten"]["outcomes"][outcome] += 1
                    stages["kandidaten"] += len(direct)
                    doc["kandidaten"] += len(direct)
                else:
                    _fold(readers["effektspalten"], False, reason)
                    doc["reasons"][str(reason or "unbekannt")] += 1

                arm = convert_row(table.header, table_row.cells, quote=quote,
                                  caption=caption)
                if arm.get("ok"):
                    _fold(readers["arm_tabelle"], True,
                          outcome=str(arm.get("outcome") or ""))
                    stages["kandidaten"] += 1
                    doc["kandidaten"] += 1
                else:
                    _fold(readers["arm_tabelle"], False, arm.get("reason"))
                    doc["reasons"][str(arm.get("reason") or "unbekannt")] += 1

        if with_text:
            sentences = split_sentences(text)
            stages["saetze"] += len(sentences)
            for _start, _end, sentence in sentences:
                rows_in["arm_text"] += 1
                rows_in["change"] += 1
                for name, converter in (("arm_text", text_sentence),
                                        ("change", change_sentence)):
                    found = converter(sentence)
                    if found.get("ok"):
                        _fold(readers[name], True,
                              outcome=str(found.get("outcome") or ""))
                        stages["kandidaten"] += 1
                        doc["kandidaten"] += 1
                    else:
                        _fold(readers[name], False, found.get("reason"))
                        doc["reasons"][str(found.get("reason") or "unbekannt")] += 1

        documents.append({**doc, "reasons": dict(doc["reasons"].most_common(8))})
        if progress_every and index % progress_every == 0:
            print(f"  {index}/{len(entries)} Dokumente, "
                  f"{stages['kandidaten']} Kandidaten", flush=True)

    reader_stats = {}
    for name, reader in readers.items():
        stats = summarise_reader(reader, rows_in[name])
        stats["gates"] = gates_of(reader["reasons"])
        reader_stats[name] = stats

    stages["gespeichert"] = _db_rows(dbs or {}, "stored")
    stages["poolbar"] = _db_rows(dbs or {}, "poolable")
    stages["outcomes"] = len({key for stats in reader_stats.values()
                              for key in stats["outcomes"]})
    stages["sol_outcomes"] = len({
        normalize_outcome(key) for stats in reader_stats.values()
        for key in stats["outcomes"]
        if "sleep onset" in normalize_outcome(key)
    })

    report = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "manifest": str(manifest),
        "xml_dir": str(xml_dir),
        "limit": limit,
        "with_text": with_text,
        "stages": dict(stages),
        "readers": reader_stats,
        "documents": documents,
        "missing_xml": missing,
        "loss_ranking": loss_ranking(dict(stages)),
        "open": [
            "Die Obergrenze (Dokumente mit einem tatsaechlich poolbaren "
            "SOL-Effekt) ist nicht gemessen; sie braucht menschliche Sichtung "
            "der SOL-Kandidaten.",
            "Stufe 'gespeichert' stammt aus den Mess-DBs, nicht aus diesem "
            "Lauf; ohne --*-db bleibt sie 0.",
        ],
    }
    report["biggest_loss"] = biggest_loss(report["loss_ranking"])

    out_stem = Path(out_stem)
    out_stem.parent.mkdir(parents=True, exist_ok=True)
    (out_stem.with_suffix(".json")).write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(report, out_stem.with_suffix(".md"))
    return report


def _db_rows(dbs: Dict[str, str], what: str) -> int:
    """Zeilen aus den Mess-DBs zaehlen: gespeichert oder poolbar."""
    from research_agent.database import Database
    from research_agent.meta.designs import is_primary_study

    total = 0
    for name, path in dbs.items():
        if not path or not Path(path).is_file():
            continue
        try:
            rows = Database(str(path)).get_study_effects() or []
        except Exception:
            continue
        if what == "stored":
            total += len(rows)
            continue
        for row in rows:
            if int(row.get("disputed") or 0) == 1:
                continue
            if str(row.get("rejection_reason") or "").strip():
                continue
            if str(row.get("effect_type") or "").strip().lower() not in _EFFECT_G:
                continue
            if row.get("se") is None and not (row.get("ci_low") is not None
                                              and row.get("ci_high") is not None):
                continue
            if not is_primary_study(row):
                continue
            total += 1
    return total


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="data/bench/sol/manifest_all.json")
    parser.add_argument("--xml-dir", default="data/bench/sol/xml")
    parser.add_argument("--out", default="data/bench/sol/funnel_20261108")
    parser.add_argument("--limit", type=int, default=0,
                        help="nur die ersten N Dokumente (0 = alle)")
    parser.add_argument("--no-text", action="store_true",
                        help="Fliesstext-Leser ueberspringen (schneller)")
    parser.add_argument("--direct-db", default="data/bench/sol/direct_all.db")
    parser.add_argument("--arm-db", default="data/bench/sol/arm_all.db")
    parser.add_argument("--text-db", default="data/bench/sol/text_arms.db")
    parser.add_argument("--change-db", default="data/bench/sol/change_arms.db")
    args = parser.parse_args(argv)

    report = funnel(
        Path(args.manifest), Path(args.xml_dir), Path(args.out),
        limit=args.limit or None, with_text=not args.no_text,
        dbs={"direct": args.direct_db, "arm": args.arm_db,
             "text": args.text_db, "change": args.change_db},
    )
    stages = report["stages"]
    print(json.dumps({key: stages[key] for key in STAGES}, ensure_ascii=False))
    top = report.get("biggest_loss") or {}
    if top:
        print(f"Groesster Verlust: {top['from']} -> {top['to']}: "
              f"{top['lost']} von {top['input']}")
    for name, stats in report["readers"].items():
        print(f"  {name}: {stats['candidates']} Kandidaten, "
              f"{stats['rejected']} abgelehnt, Summe stimmt: {stats['sum_ok']}")
        for reason, count in list(stats["reasons"].items())[:4]:
            print(f"    {count:6d}  {reason[:80]}")
    print(f"JSON: {args.out}.json")
    print(f"MD:   {args.out}.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
