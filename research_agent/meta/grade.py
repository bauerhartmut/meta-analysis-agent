"""Machine GRADE-style confidence - decided by rules over stored numbers.

The user's 31.10.2026 decision removed the human-judgement requirement, so the
grade is computed here, deterministically and without any LLM: start level by
study design, then downgrade per transparent criterion. Every downgrade names
its rule, so a reader can check the arithmetic instead of trusting a judgement.

What this is not: a GRADE panel run by methodologists. The label `maschinell`
travels with every output.
"""

from __future__ import annotations

from typing import Dict, List, Optional

LEVELS = {"high": 3, "moderate": 2, "low": 1, "very_low": 0}
_NAMES = {v: k for k, v in LEVELS.items()}

_RCT_WORDS = {"rct", "randomized", "randomised", "randomisiert", "trial"}
# Scales whose null is 1 rather than 0.
_RATIO_SCALES = {"or", "log_or", "rr", "log_rr", "hr", "log_ratio"}

_IMPRECISION_MIN_N = 200
_INCONSISTENCY_I2 = 75.0
_EGGER_P = 0.10
_MAX_DOWNGRADES = 3


def grade_group(analysis: Dict, rob_overalls: Optional[Dict[str, str]] = None) -> Dict:
    """Grade one pooled group.

    ``analysis`` is a `pool()`/build_analysis group dict (k, pooled, ci_low,
    ci_high, i2, egger, rows...); ``rob_overalls`` maps source id / doi to the
    machine bias overall rating, when known.
    """
    rows = list(analysis.get("rows") or [])
    k = int(analysis.get("k") or len(rows))
    out: Dict = {
        "rating": "very_low",
        "start": "low",
        "downgrades": [],
        "k": k,
        "i2": analysis.get("i2"),
    }
    if k < 1:
        return out

    designs = [str(r.get("design") or "").strip().lower() for r in rows]
    rct_share = (sum(1 for d in designs if d in _RCT_WORDS) / len(designs)
                 if designs else 0.0)
    start = "high" if rct_share >= 0.999 else "low"
    out["start"] = start
    level = LEVELS[start]

    downgrades: List[str] = []

    # 1. Risk of bias (maschinelle RoB-Lektüre, quote-belegt): one rated-high
    #    study is enough to cost the group a level.
    if rob_overalls:
        rated = [v for v in rob_overalls.values() if v in LEVELS]
        if rated and any(v == "high" for v in rated):
            downgrades.append(
                "Risk of Bias: mindestens eine Studie mit maschinell "
                "'high' bewertetem Verzerrungsrisiko"
            )

    # 2. Inconsistency - the stored spread, not a judgement.
    try:
        i2 = float(analysis.get("i2") or 0.0)
    except (TypeError, ValueError):
        i2 = 0.0
    if level > 0 and i2 >= _INCONSISTENCY_I2:
        downgrades.append(f"Inkonsistenz: I² = {i2:.0f}% >= {_INCONSISTENCY_I2:.0f}%")

    # 3. Imprecision - no pooled estimate, small body, or a very wide interval.
    pooled = analysis.get("pooled")
    if level > 0 and (k < 2 or pooled is None):
        downgrades.append(
            "Imprecision: kein gepoolter Schätzer (k unterhalb der "
            "Pooling-Schwelle)"
        )
    else:
        try:
            n_total = sum(int(r.get("n") or 0) for r in rows)
        except (TypeError, ValueError):
            n_total = 0
        if n_total < _IMPRECISION_MIN_N:
            downgrades.append(
                f"Imprecision: Stichprobensumme {n_total} < {_IMPRECISION_MIN_N}"
            )
        try:
            ci_low = float(analysis.get("ci_low"))
            ci_high = float(analysis.get("ci_high"))
        except (TypeError, ValueError):
            ci_low = ci_high = None
        if ci_low is not None:
            span = ci_high - ci_low
            if span > 1.0:
                downgrades.append(
                    f"Imprecision: 95%-KI-Breite {span:.2f} überspannt die "
                    "praktisch relevante Spanne"
                )

    # 4. Publication bias - the stored Egger test, only a fair signal at k >= 10.
    egger = analysis.get("egger") or {}
    try:
        egger_p = float(egger.get("p")) if egger.get("p") is not None else None
    except (TypeError, ValueError):
        egger_p = None
    if level > 0 and egger_p is not None and k >= 10 and egger_p < _EGGER_P:
        downgrades.append(
            f"Publikationsbias: Egger p = {egger_p:.3f} < {_EGGER_P:.2f}"
        )

    out["downgrades"] = downgrades[:_MAX_DOWNGRADES]
    level = max(0, level - len(out["downgrades"]))
    out["rating"] = _NAMES[level]
    return out
