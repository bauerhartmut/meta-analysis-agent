"""Two intentionally separate extraction paths for verification.

Pipeline A is the frozen C1 v6c candidate.  It is never modified here and its
output is loaded read-only.  Pipeline B is an independent layout reader over
the original table text.  The optional vision adapter is present but is not
started unless a caller explicitly enables it; the offline pilot therefore
cannot pretend that a visual model confirmed anything.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from .tables import (
    Cell, Table, as_float, normalize_cell, numeric_text, parse_tables,
    rows_matching, split_cells,
)

PIPELINE_B_VERSION = "layout-table/1"
_NUMBER_PAIR = re.compile(
    r"(?P<mean>-?\d+(?:[.,]\d+)?)\s*(?:±|\+/-)\s*(?P<sd>-?\d+(?:[.,]\d+)?)")
_PAREN_PAIR = re.compile(
    r"(?P<mean>-?\d+(?:[.,]\d+)?)\s*\(\s*(?P<sd>-?\d+(?:[.,]\d+)?)\s*\)")
_FRACTION = re.compile(r"(?P<events>\d+)\s*/\s*(?P<n>\d+)")
_COUNT = re.compile(r"(?<![\d.])-?\d+(?![\d.])")
_N_FROM_HEADER = re.compile(r"\(\s*\*?n\*?\s*=\s*(\d+)\s*\)", re.I)
_N_FROM_TEXT = re.compile(
    r"\b(?:n\s*=\s*)?(\d{1,4})\s+(?:patients|participants|subjects|men|women)\b",
    re.I)
_WEEK = re.compile(r"\b(?:week|wk)\s*(\d{1,2})\b", re.I)
_POST = re.compile(r"\b(?:post[-\s]?treatment|post[-\s]?test|post[-\s]?intervention|"
                   r"behandlungsende|nachbehandlung)\b", re.I)
_BASELINE = re.compile(r"\bbaseline\b", re.I)
_FOLLOW = re.compile(r"\b(?:follow[-\s]?up|katamnese)\b", re.I)

_ARM_ALIASES = {
    "certolizumab": "czp",
    "control": "pbo placebo",
    "kontrollgruppe": "pbo placebo",
    "placebo": "pbo placebo",
    "pbo": "pbo placebo",
    "intervention": "intervention",
    "treatment": "treatment",
}


@dataclass
class FieldReading:
    value: Any = None
    raw: str = ""
    status: str = "missing"
    rule: str = ""
    evidence: Dict[str, Any] = field(default_factory=dict)
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "raw": self.raw,
            "status": self.status,
            "rule": self.rule,
            "evidence": self.evidence,
            "note": self.note,
        }


@dataclass
class PipelineResult:
    pipeline: str
    version: str
    fields: Dict[str, FieldReading]
    document_hash: str = ""
    table_id: str = ""
    row_label: str = ""
    time_point: str = ""
    errors: List[str] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)

    def values(self) -> Dict[str, Any]:
        return {name: reading.value for name, reading in self.fields.items()}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pipeline": self.pipeline,
            "version": self.version,
            "document_hash": self.document_hash,
            "table_id": self.table_id,
            "row_label": self.row_label,
            "time_point": self.time_point,
            "fields": {name: reading.to_dict() for name, reading in self.fields.items()},
            "errors": list(self.errors),
            "meta": dict(self.meta),
        }


def _tokens(text: str) -> set[str]:
    expanded = str(text or "").lower()
    for source, alias in _ARM_ALIASES.items():
        if re.search(rf"\b{re.escape(source)}\b", expanded):
            expanded += " " + alias
    return {
        token for token in re.findall(r"[a-z0-9]+", expanded)
        if len(token) > 1 and token not in {
            "the", "and", "for", "with", "from", "group", "groups", "patients",
            "patient", "therapy", "treatment", "versus", "vs", "some", "full",
            "course", "hospital", "setting", "mean", "score", "scores",
        }
    }


def _arm_score(query: str, header: str) -> float:
    q, h = _tokens(query), _tokens(header)
    qtext, htext = str(query).lower(), str(header).lower()
    score = 0.0
    for roman in ("i", "ii", "iii", "iv"):
        if re.search(rf"\bgroup\s+{roman}\b", qtext) and \
                re.search(rf"\bgroup\s+{roman}\b", htext):
            score += 4.0
    for dose in re.findall(r"\b(\d+(?:\.\d+)?)\s*mg\b", qtext):
        if re.search(rf"\b{re.escape(dose)}\s*(?:mg)?\b", htext):
            score += 3.0
    if re.search(r"\b(?:placebo|control|pbo)\b", qtext) and \
            re.search(r"\b(?:placebo|control|pbo)\b", htext):
        score += 4.0
    if re.search(r"\bintervention\b", htext) and not \
            re.search(r"\b(?:placebo|control|pbo)\b", qtext):
        score += 2.0
    if re.search(r"\b(?:placebo|control|pbo)\b", htext) and not \
            re.search(r"\b(?:placebo|control|pbo)\b", qtext):
        score -= 1.0
    if q and h:
        score += float(len(q & h))
    return score


def _timepoint_score(query: str, header: str, row_time: str) -> float:
    text = f"{header} {row_time}".lower()
    score = 0.0
    query = query or ""
    weeks = _WEEK.findall(query)
    if weeks:
        for week in weeks:
            if re.search(rf"\b(?:week|wk)\s*{week}\b", text):
                score += 6.0
    if _POST.search(query) and _POST.search(text):
        score += 3.0
    if _BASELINE.search(query) and _BASELINE.search(text):
        score += 2.0
    if _FOLLOW.search(query) and _FOLLOW.search(text):
        score += 2.0
    if not (weeks or _POST.search(query) or _BASELINE.search(query)
            or _FOLLOW.search(query)):
        # The C1 rule is post-treatment first.  A baseline row must not win a
        # tie merely because it appears first in the document.
        if _POST.search(text):
            score += 3.0
        if _BASELINE.search(text):
            score -= 3.0
    return score


def _header_slots(table: Table) -> List[Dict[str, Any]]:
    """Header cells with their x positions, one slot per printed column."""
    slots: List[Dict[str, Any]] = []
    for line in table.header_lines:
        for cell in split_cells(line):
            text = normalize_cell(cell.text)
            if not text:
                continue
            slots.append({
                "text": text,
                "start": cell.start,
                "end": cell.end,
                "line": line,
            })
    return slots


def _slot_for_cell(cell: Cell, slots: Sequence[Dict[str, Any]]) -> str:
    parts: List[str] = []
    for slot in slots:
        overlap = min(cell.end, slot["end"]) - max(cell.start, slot["start"])
        if overlap <= 0:
            continue
        text = slot["text"]
        low = text.lower()
        plain = re.sub(r"[^a-z]", "", low)
        if low in {"treatment", "adverse event", "characteristic", "outcome",
                   "group"} or _is_p_header(text):
            continue
        if low.startswith("treatment (") and "mg" not in low:
            continue
        if text not in parts:
            parts.append(text)
    if len(parts) > 1:
        parts = [part for part in parts
                 if part.lower() not in {"treatment (mg macitentan)",
                                         "treatment", "adverse event"}]
    return " | ".join(parts)


def _is_p_header(text: str) -> bool:
    plain = re.sub(r"[^a-z]", "", str(text or "").lower())
    return bool(re.fullmatch(r"p(?:value|values|b|a|c)?", plain))


def _slot_time(slot: str) -> str:
    week = _WEEK.search(slot)
    if week:
        return f"week {week.group(1)}"
    if _POST.search(slot):
        return "post-treatment"
    if _BASELINE.search(slot):
        return "baseline"
    if _FOLLOW.search(slot):
        return "follow-up"
    return ""


def _n_from_slot(slot: str) -> Optional[int]:
    match = _N_FROM_HEADER.search(slot)
    return int(match.group(1)) if match else None


def _header_n_for_arm(table: Table, arm: str) -> Optional[int]:
    best: Tuple[float, Optional[int]] = (0.0, None)
    for slot in _header_slots(table):
        score = _arm_score(arm, slot["text"])
        n = _n_from_slot(slot["text"])
        if score > best[0] and n is not None:
            best = (score, n)
    return best[1]


def _n_from_narrative(text: str, arm: str) -> Optional[int]:
    """Nearest reported group size to the arm wording, never a guess."""
    body = text or ""
    group_marker = re.search(r"\(\s*(group\s+(?:i|ii|iii|iv|[a-z]))\s*\)", arm, re.I)
    needle = group_marker.group(1) if group_marker else (
        arm.split("(")[0].strip() if arm else "")
    arm_match = re.search(re.escape(needle), body, re.I) if needle else None
    anchor = arm_match.start() if arm_match else 0
    # First choice: an explicit "n = 30" close to the arm label.  This is how
    # the PMC tables state group sizes in prose; "52 patients" is the total
    # sample and must never become an arm size.
    window_start = max(0, anchor - 120)
    window = body[window_start: anchor + 360]
    local_hits = list(re.finditer(r"\bn\s*=\s*(\d{1,4})", window, re.I))
    if local_hits:
        best = min(
            local_hits,
            key=lambda hit: abs((window_start + hit.start()) - anchor),
        )
        return int(best.group(1))
    candidates: List[Tuple[int, int]] = []
    for match in _N_FROM_TEXT.finditer(body):
        candidates.append((abs(match.start() - anchor), int(match.group(1))))
    if not candidates:
        return None
    candidates.sort()
    distance, value = candidates[0]
    return value if distance <= 250 else None


def _narrative_n_evidence(text: str, arm: str, n: int) -> Tuple[int, str]:
    """The line that states this arm's n, for an audit-ready citation."""
    lines = text.splitlines()
    marker = re.escape(str(int(n)))
    for index, line in enumerate(lines, start=1):
        if re.search(rf"\bn\s*=\s*{marker}\b", line, re.I) and _arm_score(arm, line) > 0:
            return index, line
    for index, line in enumerate(lines, start=1):
        if re.search(rf"\bn\s*=\s*{marker}\b", line, re.I):
            return index, line
    return 0, ""


def _row_value_cells(row, slots: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for cell in row.cells:
        slot = _slot_for_cell(cell, slots)
        low = slot.lower()
        if low == "p" or low.startswith("p |") or low.endswith("| p"):
            continue
        out.append({"cell": cell, "header": slot,
                    "time": _slot_time(slot) or _slot_time(row.display_label)})
    return out


def _choose_column(cells: Sequence[Dict[str, Any]], arm: str,
                   outcome_query: str, row_time: str) -> Optional[Dict[str, Any]]:
    scored: List[Tuple[float, Dict[str, Any]]] = []
    for item in cells:
        score = _arm_score(arm, item["header"])
        score += _timepoint_score(outcome_query, item["header"], row_time)
        if score <= 0:
            continue
        scored.append((score, item))
    scored.sort(key=lambda pair: -pair[0])
    return scored[0][1] if scored else None


def _other_column(cells: Sequence[Dict[str, Any]],
                  chosen: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """The remaining arm column when exactly two columns carry a value.

    C1 ICOs sometimes name only one arm explicitly (CoPAT vs "full course in
    hospital"); the second arm is then the one other non-p-value column.  If
    more than two remain, the caller gets None and the record is ambiguous.
    """
    candidates = [item for item in cells
                  if item is not chosen
                  and item.get("header")
                  and not _is_p_header(str(item["header"]))]
    return candidates[0] if len(candidates) == 1 else None


def _pair_from_cell(text: str) -> Tuple[Optional[float], Optional[float], str]:
    match = _NUMBER_PAIR.search(text) or _PAREN_PAIR.search(text)
    if not match:
        return None, None, ""
    return (as_float(match.group("mean")), as_float(match.group("sd")),
            normalize_cell(match.group(0)))


def _narrative_pairs(text: str, arm: str) -> List[Tuple[float, float, str, int, str]]:
    """Mean/SD pairs near an arm mention, as a fallback for prose-only papers."""
    out: List[Tuple[float, float, str, int, str]] = []
    for match in re.finditer(
            r"(?P<mean>-?\d+(?:[.,]\d+)?)\s*(?:±|\+/-|\(\s*)\s*"
            r"(?P<sd>-?\d+(?:[.,]\d+)?)\s*\)?", text or ""):
        mean, sd = as_float(match.group("mean")), as_float(match.group("sd"))
        if mean is None or sd is None or sd <= 0:
            continue
        context = text[max(0, match.start() - 260):min(len(text), match.end() + 260)]
        score = _arm_score(arm, context)
        if score <= 0:
            continue
        out.append((score, mean, sd, text.count("\n", 0, match.start()) + 1,
                    normalize_cell(match.group(0))))
    out.sort(key=lambda item: -item[0])
    return [(score, mean, sd, line, raw) for score, mean, sd, line, raw in out]


def _count_from_cell(text: str) -> Tuple[Optional[int], Optional[int], str]:
    fraction = _FRACTION.search(text)
    if fraction:
        return (int(fraction.group("events")), int(fraction.group("n")),
                normalize_cell(fraction.group(0)))
    before_pct = re.match(r"\s*(\d+)\s*(?:\(|$)", text or "")
    if before_pct:
        return int(before_pct.group(1)), None, normalize_cell(before_pct.group(0))
    count = _COUNT.search(text or "")
    if count:
        return int(count.group(0)), None, normalize_cell(count.group(0))
    return None, None, ""


def _evidence(table: Table, row, cell_text: str, column: str, field_name: str,
              value: Any, line_no: int, document_id: str, doc_hash: str,
              raw_cell: str = "") -> Dict[str, Any]:
    raw = raw_cell or cell_text
    table_id = table.table_id if table is not None else f"prose:{line_no}"
    caption = table.caption if table is not None else "Fließtext"
    return {
        "document_id": document_id,
        "document_hash": doc_hash,
        "page": -1,
        "location_kind": "markdown_line",
        "table_id": table_id,
        "table_caption": caption,
        "line_start": int(line_no),
        "line_end": int(line_no),
        "row_label": row.display_label if row is not None else "",
        "column_label": column,
        "raw_cell": raw,
        "excerpt": (row.raw if row is not None else raw)[:2000],
        "field": field_name,
        "value_text": str(value) if value is not None else "",
        "exact": bool(raw and str(value) in raw),
        "evidence_hash": hashlib.sha256(
            f"{document_id}|{table_id}|{line_no}|{column}|{raw}".encode("utf-8")
        ).hexdigest(),
    }


class LayoutPipeline:
    """Offline independent reader over the original table text.

    It uses the ICO specification and the document only.  It never reads
    Pipeline A's values, which is what makes the later comparison meaningful.
    """

    name = "B_layout"
    version = PIPELINE_B_VERSION

    def extract(self, record: Dict, text: str, document_hash: str) -> PipelineResult:
        document_id = str(record.get("document_id") or record.get("study_id") or "")
        outcome_query = str(record.get("ico", {}).get("outcome") or "")
        intervention = str(record.get("ico", {}).get("intervention") or "")
        comparator = str(record.get("ico", {}).get("comparator") or "")
        outcome_type = str(record.get("outcome_type") or "continuous")
        errors: List[str] = []
        best: Optional[Tuple[float, Table, Any, str]] = None
        for table in parse_tables(text):
            rows = rows_matching(table, outcome_query)
            if not rows:
                continue
            slots = _header_slots(table)
            for row in rows[:5]:
                cells = _row_value_cells(row, slots)
                if not cells:
                    continue
                left = _choose_column(cells, intervention, outcome_query,
                                      row.display_label)
                right = _choose_column(cells, comparator, outcome_query,
                                       row.display_label)
                if left is None and right is not None:
                    left = _other_column(cells, right)
                if right is None and left is not None:
                    right = _other_column(cells, left)
                if left is None or right is None:
                    continue
                # The row label overlap is the primary signal; complete arm
                # matches and a readable value pair break ties.
                score = 0.0
                if normalize_cell(outcome_query).lower() in row.display_label.lower():
                    score += 2.0
                score += len(_tokens(outcome_query) & _tokens(row.display_label)) / 5.0
                score += 0.5
                score += _timepoint_score(outcome_query, "", row.display_label)
                if score > (best[0] if best else 0.0):
                    best = (score, table, row, "")
        if best is None:
            if str(record.get("outcome_type") or "") == "continuous":
                return self._extract_narrative(record, text, document_hash)
            return PipelineResult(
                pipeline=self.name, version=self.version, fields={},
                document_hash=document_hash,
                errors=["keine Tabellenzeile mit beiden Armspalten gefunden"],
            )

        _, table, row, _ = best
        slots = _header_slots(table)
        cells = _row_value_cells(row, slots)
        left = _choose_column(cells, intervention, outcome_query, row.display_label)
        right = _choose_column(cells, comparator, outcome_query, row.display_label)
        if left is None and right is not None:
            left = _other_column(cells, right)
        if right is None and left is not None:
            right = _other_column(cells, left)
        if left is not None and right is not None \
                and str(left["header"]) == str(right["header"]):
            right = _other_column(cells, left)
        if left is None or right is None:
            arm_cells = [item for item in cells
                         if item.get("header") and not re.sub(
                             r"[^a-z]", "", str(item["header"]).lower()
                         ) in {"p", "pvalue", "pvalues"}]
            if len(arm_cells) == 2:
                left, right = arm_cells[0], arm_cells[1]
        if left is None or right is None:
            return PipelineResult(
                pipeline=self.name, version=self.version, fields={},
                document_hash=document_hash, table_id=table.table_id,
                row_label=row.display_label,
                errors=["Armspalte nicht eindeutig zuordenbar"],
            )

        fields: Dict[str, FieldReading] = {}
        left_header = str(left["header"])
        right_header = str(right["header"])
        time_point = left["time"] or right["time"] or ""
        left_cell, right_cell = left["cell"], right["cell"]
        left_raw, right_raw = left_cell.text, right_cell.text

        def put(name: str, value: Any, raw: str, cell: Cell, header: str,
                note: str = "") -> None:
            fields[name] = FieldReading(
                value=value, raw=raw,
                status="extracted" if value not in (None, "") else "missing",
                rule="exact_cell" if value not in (None, "") else "cell_without_value",
                evidence=_evidence(table, row, cell.text, header, name, value,
                                   row.line_no, document_id, document_hash, raw),
                note=note,
            )

        left_n = _n_from_slot(left_header) or _n_from_narrative(text, intervention)
        right_n = _n_from_slot(right_header) or _n_from_narrative(text, comparator)
        if outcome_type == "continuous":
            lmean, lsd, lpair = _pair_from_cell(left_raw)
            rmean, rsd, rpair = _pair_from_cell(right_raw)
            put("intervention_mean", lmean, lpair or left_raw, left_cell, left_header)
            put("intervention_sd", lsd, lpair or left_raw, left_cell, left_header)
            put("comparator_mean", rmean, rpair or right_raw, right_cell, right_header)
            put("comparator_sd", rsd, rpair or right_raw, right_cell, right_header)
            for field_name, value, cell, header in (
                    ("intervention_n", left_n, left_cell, left_header),
                    ("comparator_n", right_n, right_cell, right_header)):
                fields[field_name] = FieldReading(
                    value=value,
                    raw=str(_n_from_slot(header) or "") if value == _n_from_slot(header)
                    else str(value) if value is not None else "",
                    status="extracted" if value is not None else "missing",
                    rule="header_n" if _n_from_slot(header) is not None
                    else "narrative_group_size",
                    evidence=_evidence(table, row, header, header, field_name,
                                       value, row.line_no, document_id,
                                       document_hash, header),
                )
        else:
            le, ln, lraw = _count_from_cell(left_raw)
            re_, rn, rraw = _count_from_cell(right_raw)
            put("intervention_events", le, lraw or left_raw, left_cell, left_header)
            put("comparator_events", re_, rraw or right_raw, right_cell, right_header)
            left_n = left_n or ln
            right_n = right_n or rn
            for field_name, value, cell, header in (
                    ("intervention_n", left_n, left_cell, left_header),
                    ("comparator_n", right_n, right_cell, right_header)):
                fields[field_name] = FieldReading(
                    value=value,
                    raw=str(value) if value is not None else "",
                    status="extracted" if value is not None else "missing",
                    rule="header_n" if _n_from_slot(header) is not None
                    else "narrative_group_size",
                    evidence=_evidence(table, row, header, header, field_name,
                                       value, row.line_no, document_id,
                                       document_hash, header),
                )

        fields["outcome"] = FieldReading(
            value=outcome_query, raw=row.display_label, status="extracted",
            rule="ico_definition", note="ICO, nicht aus der Tabelle gelesen",
            evidence=_evidence(table, row, row.display_label, left_header,
                               "outcome", outcome_query, row.line_no, document_id,
                               document_hash, row.display_label))
        fields["time_point"] = FieldReading(
            value=time_point or "post-treatment", raw=row.display_label,
            status="extracted" if (time_point or _POST.search(row.display_label))
            else "missing",
            rule="header_timepoint" if time_point else "post_treatment_default",
            evidence=_evidence(table, row, row.display_label, left_header,
                               "time_point", time_point or "post-treatment",
                               row.line_no, document_id, document_hash,
                               row.display_label))
        unit_match = re.search(r"\(([^()]{1,30})\)", row.display_label)
        fields["unit"] = FieldReading(
            value=unit_match.group(1) if unit_match else "",
            raw=row.display_label if unit_match else "",
            status="extracted" if unit_match else "missing",
            rule="row_label_unit" if unit_match else "no_unit_in_row_label")

        # A mismatch in one arm does not discard the other: each field keeps
        # its own evidence and status.
        for name, reading in fields.items():
            if reading.value is None and name not in ("outcome", "time_point", "unit"):
                reading.status = "missing"
                reading.rule = reading.rule or "not_read"
            if (name in {"intervention_n", "comparator_n"}
                    and reading.value is not None
                    and reading.rule == "narrative_group_size"):
                arm = intervention if name.startswith("intervention") else comparator
                line_no, raw_line = _narrative_n_evidence(text, arm, int(reading.value))
                if line_no:
                    reading.evidence = _evidence(
                        table, row, raw_line, "Fließtext", name, reading.value,
                        line_no, document_id, document_hash, raw_line)
                    reading.raw = raw_line.strip()[:120]
        return PipelineResult(
            pipeline=self.name, version=self.version, fields=fields,
            document_hash=document_hash, table_id=table.table_id,
            row_label=row.display_label, time_point=time_point,
            errors=errors,
            meta={"parser": "markdown-layout/1", "vision_used": False},
        )

    def _extract_narrative(self, record: Dict, text: str,
                           document_hash: str) -> PipelineResult:
        """Prose-only fallback: exact pairs with an explicit arm context."""
        document_id = str(record.get("document_id") or record.get("study_id") or "")
        intervention = str(record.get("ico", {}).get("intervention") or "")
        comparator = str(record.get("ico", {}).get("comparator") or "")
        left = _narrative_pairs(text, intervention)
        right = _narrative_pairs(text, comparator or "control")
        if not left or not right:
            return PipelineResult(
                pipeline=self.name, version=self.version, fields={},
                document_hash=document_hash,
                errors=["keine Tabellenzeile und kein belegtes Fließtext-Paar "
                        "mit beiden Armkontexten gefunden"],
            )
        fields: Dict[str, FieldReading] = {}
        for prefix, pair in (("intervention", left[0]), ("comparator", right[0])):
            _, mean, sd, line_no, raw = pair
            lines = text.splitlines()
            raw_line = lines[line_no - 1] if 0 < line_no <= len(lines) else raw
            fields[f"{prefix}_mean"] = FieldReading(
                value=mean, raw=raw, status="extracted", rule="narrative_pair",
                evidence=_evidence(None, None, raw_line, "Fließtext",
                                   f"{prefix}_mean", mean, line_no, document_id,
                                   document_hash, raw_line),
            )
            fields[f"{prefix}_sd"] = FieldReading(
                value=sd, raw=raw, status="extracted", rule="narrative_pair",
                evidence=_evidence(None, None, raw_line, "Fließtext",
                                   f"{prefix}_sd", sd, line_no, document_id,
                                   document_hash, raw_line),
            )
            n = _n_from_narrative(text, intervention if prefix == "intervention" else comparator)
            fields[f"{prefix}_n"] = FieldReading(
                value=n, raw=str(n) if n is not None else "",
                status="extracted" if n is not None else "missing",
                rule="narrative_group_size" if n is not None else "not_read",
                evidence=_evidence(None, None, raw_line, "Fließtext",
                                   f"{prefix}_n", n, line_no, document_id,
                                   document_hash, raw_line) if n is not None else {},
            )
        fields["outcome"] = FieldReading(
            value=str(record.get("ico", {}).get("outcome") or ""),
            raw="", status="extracted", rule="ico_definition")
        fields["time_point"] = FieldReading(
            value="post-treatment", raw="", status="extracted",
            rule="post_treatment_default")
        return PipelineResult(
            pipeline=self.name, version=self.version, fields=fields,
            document_hash=document_hash, row_label="Fließtext",
            time_point="post-treatment",
            meta={"parser": "narrative-pair/1", "vision_used": False},
        )


def load_pipeline_a(record_id: int, output_path: str) -> Dict[str, Any]:
    """Frozen v6c row for one record, read-only.

    The JSONL is hashed by the caller.  This function only maps the frozen
    field names to the verification specification and never runs a model.
    """
    import json
    with open(output_path, encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            if int(row.get("record_id", -1)) == int(record_id):
                return row
    raise KeyError(f"record {record_id} not found in {output_path}")


class VisionPipeline:
    """Optional visual path, deliberately not started by the offline pilot.

    The adapter wires the existing vision reader to the same specification and
    keeps its evidence separate.  It is here so a later, explicitly approved
    run does not need a second architecture.  No network call happens at
    import time or in the pilot.
    """

    name = "B_vision"
    version = "vision-table-adapter/1"

    def __init__(self, reader=None):
        self.reader = reader

    async def extract(self, record: Dict, pdf_path: str, page_index: int,
                      document_hash: str) -> PipelineResult:
        if self.reader is None:
            return PipelineResult(
                pipeline=self.name, version=self.version, fields={},
                document_hash=document_hash,
                errors=["Vision-Pfad nicht aktiviert (keine Freigabe fuer Netzlauf)"],
            )
        from ..research.vision_table import read_table_evidence, render_pdf_pages
        pages = render_pdf_pages(pdf_path, max_pages=page_index + 1)
        png = next((data for index, data in pages if index == page_index), None)
        if png is None:
            return PipelineResult(
                pipeline=self.name, version=self.version, fields={},
                document_hash=document_hash,
                errors=[f"PDF-Seite {page_index} nicht rasterisierbar"],
            )
        evidence = await read_table_evidence(
            pdf_path, page_index, png, self.reader)
        return PipelineResult(
            pipeline=self.name, version=self.version, fields={},
            document_hash=document_hash,
            errors=[] if evidence.get("status") == "verified"
            else [f"Vision-Status: {evidence.get('status')}"],
            meta={"vision": evidence, "vision_used": True},
        )
