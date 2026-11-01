"""Pool the simulated studies of one hypothesis into a single estimate.

A scientist does not average evidence by counting papers: studies are combined
with inverse-variance weighting, and the spread between them is reported as
heterogeneity. Two experiments that disagree are not "two supporting results",
they are a conflict, and I² makes that visible.

Deliberately LLM-free: pooling must be reproducible from stored numbers alone,
also when the backend is down.
"""

import json
import logging
import math
from dataclasses import dataclass
from typing import List, Optional

logger = logging.getLogger(__name__)

# 95% interval under normality: 1.96 * 2
_CI_TO_SE = 3.92


@dataclass
class PooledEstimate:
    k: int
    pooled: float
    ci_low: float
    ci_high: float
    heterogeneity: float   # I² between 0 and 1
    replications: int      # total replication runs behind the pooled estimate
    supports: int
    contradicts: int
    neutral: int
    summary: str


def _result(row: dict) -> dict:
    raw = row.get("result")
    if isinstance(raw, dict):
        return raw
    try:
        parsed = json.loads(raw or "{}")
    except (TypeError, ValueError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _estimate(row: dict):
    """(effect, standard error) of one experiment, or (None, None)."""
    result = _result(row)
    values = result.get("values")
    try:
        value = float(result.get("value"))
    except (TypeError, ValueError):
        value = None
    if value is None:
        return None, None

    try:
        low = float(result.get("ci_low"))
        high = float(result.get("ci_high"))
    except (TypeError, ValueError):
        low = high = None
    if low is not None and high is not None and high > low:
        return value, (high - low) / _CI_TO_SE

    if isinstance(values, (list, tuple)) and len(values) >= 2:
        try:
            numbers = [float(v) for v in values]
        except (TypeError, ValueError):
            numbers = []
        if len(numbers) >= 2:
            mean = sum(numbers) / len(numbers)
            spread = (sum((x - mean) ** 2 for x in numbers) / (len(numbers) - 1)) ** 0.5
            if spread > 0:
                return value, spread / math.sqrt(len(numbers))
    return value, None


def pool(experiments: List[dict]) -> Optional[PooledEstimate]:
    """Inverse-variance pool of completed experiments of one hypothesis."""
    rows = [e for e in (experiments or []) if (e.get("status") or "") == "completed"]
    if not rows:
        return None

    estimates = []
    for row in rows:
        value, se = _estimate(row)
        if value is None:
            continue
        estimates.append((value, se))
    if not estimates:
        return None

    known = [(v, se) for v, se in estimates if se and se > 0]
    if len(known) == len(estimates) and known:
        weights = [1.0 / (se ** 2) for _, se in known]
        values = [v for v, _ in known]
    else:
        # Unknown precision: equal weights, and no heterogeneity claim.
        weights = [1.0] * len(estimates)
        values = [v for v, _ in estimates]

    total = sum(weights)
    pooled = sum(w * v for w, v in zip(weights, values)) / total
    se_pooled = (1.0 / total) ** 0.5

    heterogeneity = 0.0
    if len(values) > 1 and len(known) == len(estimates):
        q = sum(w * (v - pooled) ** 2 for w, v in zip(weights, values))
        df = len(values) - 1
        if q > 0:
            heterogeneity = max(0.0, (q - df) / q)

    supports = sum(1 for e in rows if (e.get("verdict") or "") == "supports")
    contradicts = sum(1 for e in rows if (e.get("verdict") or "") == "contradicts")
    neutral = sum(1 for e in rows if (e.get("verdict") or "") == "neutral")
    replications = 0
    for row in rows:
        values_raw = _result(row).get("values")
        replications += len(values_raw) if isinstance(values_raw, (list, tuple)) else 1

    ci_low = pooled - 1.96 * se_pooled
    ci_high = pooled + 1.96 * se_pooled
    summary = (
        f"{len(values)} Experiment(e), {replications} Wiederholungen: "
        f"gepoolter Effekt {pooled:.3g} [95%-KI {ci_low:.3g}; {ci_high:.3g}]"
        + (f", I²={heterogeneity:.0%}" if len(values) > 1 else "")
    )
    return PooledEstimate(
        k=len(values),
        pooled=pooled,
        ci_low=ci_low,
        ci_high=ci_high,
        heterogeneity=heterogeneity,
        replications=replications,
        supports=supports,
        contradicts=contradicts,
        neutral=neutral,
        summary=summary,
    )


def group_by_hypothesis(experiments: List[dict]) -> dict:
    """{hypothesis_id: [experiment rows]} for pooling per hypothesis."""
    grouped = {}
    for row in experiments or []:
        key = row.get("hypothesis_id") or ""
        if not key:
            continue
        grouped.setdefault(key, []).append(row)
    return grouped
