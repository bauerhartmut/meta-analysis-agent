"""Direkte SOL-Effekte lesen, deren Kopf die Skala nicht nennt.

Enger Sonderfall: Der Spaltenkopf sagt nur "Estimate (95% CI)", die Zeile
nennt aber die Einheit ("Sleep latency", Minuten). Der strikte Leser
verwirft solche Zeilen zu Recht, weil "Estimate" allein keine Skala ist.
Hier wird die Einheit aus der Zeilenbeschriftung uebernommen - als
ausdrueckliche Annahme, in der Zeile markiert, nicht stillschweigend.
"""

from __future__ import annotations

import datetime as dt
import json
import re
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_agent.coverage.manager import _xml_to_text  # noqa: E402
from research_agent.database import Database  # noqa: E402
from research_agent.meta.effect_columns import (  # noqa: E402
    effect_word,
    parse_effect_cell,
)
from research_agent.meta.extraction import check_plausibility, derive_se  # noqa: E402
from research_agent.research.fulltext import locate_quote  # noqa: E402
from research_agent.research.jats_tables import _pipe_row, parse_jats  # noqa: E402

SOL = re.compile(r"sleep[- ]onset|sleep[- ]latency|\bSOL\b", re.I)
MINUTES = re.compile(r"\(\s*min(?:ute)?s?\b|minutes\b", re.I)
ESTIMATE_CI = re.compile(r"estimate", re.I)
CI = re.compile(r"\bCI\b|confidence\s+interval", re.I)
SCREEN = re.compile(r"melatonin", re.I)
NOT_MELATONIN = re.compile(
    r"ramelteon|tasimelteon|agomelatine|valerian|cherry|vitamin|exercise|"
    r"dexmedetomidine|temazepam|zolpidem", re.I)
PLAUSIBLE_MIN = 300.0


def main() -> int:
    pairs = json.loads(Path("data/bench/sol2/manifest_pairs.json").read_text(encoding="utf-8"))
    screened = [p for p in pairs
                if SCREEN.search(str(p.get("title") or ""))
                and not NOT_MELATONIN.search(str(p.get("title") or ""))]
    db_path = Path("data/bench/sol2/direct_unit.db")
    if db_path.exists():
        db_path.unlink()
    db = Database(str(db_path))
    now = dt.datetime.now(dt.timezone.utc).isoformat()

    documents, stored_total = [], 0
    for pair in screened:
        pmc = pair["pmc"]
        xml = (Path("data/bench/sol2/xml") / f"{pmc}.xml").read_text(encoding="utf-8", errors="replace")
        text = _xml_to_text(xml)
        source_id = f"doi:{pair['doi']}"
        row = db.save_source_text(source_id, text, kind="xml",
                                  origin_url=f"https://www.ncbi.nlm.nih.gov/pmc/{pmc}/")
        text_id = (row or {}).get("id", "")
        rows_out = []
        for table in parse_jats(Path("data/bench/sol2/xml") / f"{pmc}.xml"):
            for table_row in table.rows:
                cells = list(table_row.cells)
                if not cells or not SOL.search(_pipe_row(cells)):
                    continue
                label = str(cells[0] or "")
                if not MINUTES.search(label):
                    continue
                for index, head in enumerate(table.header):
                    if index >= len(cells):
                        continue
                    head_text = str(head or "")
                    if not (ESTIMATE_CI.search(head_text) and CI.search(head_text)):
                        continue
                    if effect_word(head_text)[0]:
                        continue
                    parsed = parse_effect_cell(cells[index])
                    if not parsed:
                        continue
                    point, low, high = parsed
                    if max(abs(point), abs(low), abs(high)) > PLAUSIBLE_MIN:
                        continue
                    quote = _pipe_row(cells)
                    span = locate_quote(text, quote)
                    if not span:
                        continue
                    se = derive_se(low, high, 0.95)
                    if se is None or se <= 0:
                        continue
                    entry = {
                        "id": uuid.uuid4().hex, "source_id": source_id,
                        "outcome": label[:90], "outcome_key": label[:90],
                        "comparison": head_text[:120], "effect_type": "mean_diff",
                        "effect": point, "se": se, "ci_low": low, "ci_high": high,
                        "ci_level": 0.95, "n": None, "design": "", "population": "",
                        "direction": "Vorzeichen folgt der Gruppenreihenfolge der Tabelle",
                        "unit": "Mitteldifferenz (Rohskala, Einheit aus Zeile angenommen)",
                        "quote": quote, "quote_start": span.start, "quote_end": span.end,
                        "source_text_id": text_id, "extractor": "effect-column/1+unit-rule",
                        "extraction_pass": 1, "disputed": 0, "rejection_reason": "",
                        "adjusted": -1, "time_point": "",
                        "moderators": json.dumps({"column": head_text,
                                                  "assumed_unit": "minutes",
                                                  "reason": "Kopf nennt nur Estimate (95% CI)"},
                                                 ensure_ascii=False),
                        "created_at": now,
                    }
                    if check_plausibility(entry):
                        continue
                    db.save_study_effect(entry)
                    stored_total += 1
                    rows_out.append({"outcome": label[:60], "effect": point,
                                     "ci": [low, high], "quote": quote[:140]})
        if rows_out:
            documents.append({"pmc": pmc, "year": pair.get("year"), "rows": rows_out})

    report = {"generated": dt.datetime.now().isoformat(timespec="seconds"),
              "screened": len(screened), "rows": stored_total,
              "k": len(documents), "documents": documents}
    Path("data/bench/sol2/direct_unit.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"gescreent={len(screened)} zeilen={stored_total} k={len(documents)}")
    for doc in documents:
        for row in doc["rows"]:
            print(f"  {doc['pmc']} | {row['outcome']} | MD={row['effect']} | CI={row['ci']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
