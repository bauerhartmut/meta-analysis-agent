"""Judge a simulation result against the preregistered prediction.

Three independent steps:

* **Compliance** (deterministic): did the script use the numbers the protocol
  fixed before the run? A study that silently changes its sample size, alpha or
  seed is not the preregistered study, and real scientists report exactly that
  as a deviation instead of presenting the result as planned.
* **Audit** (LLM): does the script actually test the stated prediction, or does
  it compute something unrelated and print a number? A script that fails this
  may still be recorded, but only at half strength and with the concern in the
  evidence text - an experiment nobody can trust should not quietly raise a
  hypothesis' confidence.
* **Verdict** (deterministic, no LLM): replication rate, direction consistency,
  sensitivity to the noise assumption and alpha decide supports / contradicts /
  neutral, then the strength is capped, because a simulation tests the *logic*
  of a prediction, not the world.

The central rule: one significant run is not a finding. A single p-value below
alpha is what a scientist expects to see once in twenty runs of nothing, so the
verdict is driven by how often the effect survives fresh noise.
"""

import logging
import math
import statistics
from dataclasses import dataclass, field
from typing import List, Optional

logger = logging.getLogger(__name__)

SIMULATION_EVIDENCE_CAP = 0.6

# A verdict needs this many replications to speak about reproducibility at all.
MIN_REPLICATIONS_FOR_VERDICT = 3
# Share of replications that must be significant / in the predicted direction.
REPRODUCED = 0.8
# Below this share the effect is absent (or points the other way).
ABSENT = 0.2
# Between ABSENT and REPRODUCED the experiment is inconclusive, not a finding.
DIRECTION_LEAN = 0.8
# Tolerated relative deviation of the reported sample size from the protocol
# (group-vs-total conventions differ; a factor of two is not a deviation).
N_TOLERANCE = 0.33


@dataclass
class SimulationVerdict:
    evidence_type: str          # supports | contradicts | neutral
    strength: float
    reasoning: str
    replication_rate: float = 0.0
    deviations: List[str] = field(default_factory=list)
    sensitivity: List[dict] = field(default_factory=list)


def _to_float(value) -> Optional[float]:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def _to_float_list(value) -> List[float]:
    if not isinstance(value, (list, tuple)):
        return []
    out = []
    for item in value:
        number = _to_float(item)
        if number is not None:
            out.append(number)
    return out


def _sensitivity_points(result: dict) -> List[dict]:
    raw = result.get("sensitivity")
    if not isinstance(raw, (list, tuple)):
        return []
    points = []
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        value = _to_float(entry.get("value"))
        if value is None:
            continue
        points.append({
            "noise_multiplier": _to_float(entry.get("noise_multiplier")),
            "value": value,
            "p_value": _to_float(entry.get("p_value")),
        })
    return points[:10]


def replication_stats(protocol, result: dict) -> dict:
    """Share of replications that were significant and as predicted.

    A one-shot design predicts a direction of an effect (sign of ``effect``); a
    meta design predicts a threshold on a procedure's metric (power, bias,
    coverage), so "as predicted" means the metric lands on the side of the
    threshold that ``comparison`` states.
    """
    values = _to_float_list(result.get("values"))
    p_values = _to_float_list(result.get("p_values"))
    alpha = _to_float(getattr(protocol, "alpha", 0.05)) or 0.05
    expected = _to_float(getattr(protocol, "effect", 0.0)) or 0.0
    is_meta = str(getattr(protocol, "design_type", "one_shot")) == "meta"
    target = _to_float(getattr(protocol, "threshold", 0.0)) or 0.0
    at_least = str(getattr(protocol, "comparison", "at_least")) != "at_most"

    if len(values) >= 2 and len(p_values) == len(values):
        if is_meta:
            direction = [
                (value >= target) if at_least else (value <= target)
                for value in values
            ]
        else:
            direction = [(value >= 0) == (expected >= 0) for value in values]
        significant = [p < alpha for p in p_values]
        return {
            "k": len(values),
            "values": values,
            "p_values": p_values,
            "significant_share": sum(significant) / len(significant),
            "direction_share": sum(direction) / len(direction),
            "median_p": statistics.median(p_values),
            "mean_value": statistics.fmean(values),
            "spread": (max(values) - min(values)) if len(values) > 1 else 0.0,
        }

    value = _to_float(result.get("value"))
    p_value = _to_float(result.get("p_value"))
    single = [value] if value is not None else []
    return {
        "k": 1 if value is not None else 0,
        "values": single,
        "p_values": [p_value] if p_value is not None else [],
        "significant_share": (1.0 if (p_value is not None and p_value < alpha) else 0.0)
        if p_value is not None else None,
        "direction_share": (
            (1.0 if ((value >= target) if at_least else (value <= target)) else 0.0)
            if (value is not None and is_meta) else
            (1.0 if (value is not None and (value >= 0) == (expected >= 0)) else 0.0)
        ) if value is not None else None,
        "median_p": p_value,
        "mean_value": value,
        "spread": 0.0,
    }


def check_compliance(protocol, result: dict) -> List[str]:
    """Report where the executed study differs from the preregistered protocol.

    Only deviations that change what was tested are reported. A missing field is
    a deviation too: an unreported sample size cannot be checked, which is why
    preregistrations ask for it.
    """
    deviations: List[str] = []

    reported_n = _to_float(result.get("n"))
    planned_n = _to_float(getattr(protocol, "n", 0))
    if reported_n is None:
        deviations.append("sample size n not reported")
    elif planned_n:
        if reported_n <= 0:
            deviations.append(f"reported n={reported_n:g} is not usable")
        elif abs(reported_n - planned_n) / planned_n > N_TOLERANCE:
            deviations.append(
                f"n={reported_n:g} deviates from the preregistered n={planned_n:g}"
            )

    reported_alpha = _to_float(result.get("alpha"))
    planned_alpha = _to_float(getattr(protocol, "alpha", 0.05)) or 0.05
    if reported_alpha is not None and abs(reported_alpha - planned_alpha) > 1e-9:
        deviations.append(
            f"alpha={reported_alpha:g} differs from the preregistered "
            f"alpha={planned_alpha:g}"
        )

    reported_seed = _to_float(result.get("seed"))
    planned_seed = _to_float(getattr(protocol, "seed", 0))
    if reported_seed is not None and planned_seed is not None:
        if int(reported_seed) != int(planned_seed):
            deviations.append(
                f"base seed {int(reported_seed)} differs from the preregistered "
                f"{int(planned_seed)}"
            )

    planned_reps = int(getattr(protocol, "replications", 1) or 1)
    stats = replication_stats(protocol, result)
    if stats["k"] < planned_reps:
        deviations.append(
            f"{stats['k']} replication(s) instead of the preregistered {planned_reps}"
        )

    if not str(result.get("test") or "").strip():
        deviations.append("no statistical test reported")

    if str(getattr(protocol, "design_type", "one_shot")) == "meta":
        deviations.extend(_meta_deviations(protocol, result))

    return deviations[:6]


def _meta_deviations(protocol, result: dict) -> List[str]:
    """A meta study must report its grid and its inner-trial count."""
    deviations: List[str] = []
    planned_trials = int(getattr(protocol, "trials", 0) or 0)
    cells = result.get("cells")
    reported_trials = []
    if isinstance(cells, list):
        for cell in cells:
            if isinstance(cell, dict):
                trials = _to_float(cell.get("trials"))
                if trials:
                    reported_trials.append(int(trials))
    if not reported_trials:
        deviations.append("no inner-trial count reported per grid cell")
    elif planned_trials and min(reported_trials) < planned_trials:
        deviations.append(
            f"{min(reported_trials)} inner trials instead of the preregistered "
            f"{planned_trials}"
        )

    grid = result.get("grid")
    planned_grid = protocol.normalized_grid()
    if not isinstance(grid, list) or not grid:
        deviations.append("the grid of sample sizes is not reported")
    elif planned_grid:
        reported = {int(value) for value in (_to_float(item) for item in grid) if value}
        missing = [n for n in planned_grid if n not in reported]
        if missing:
            deviations.append(f"grid is missing the preregistered sizes {missing}")
    return deviations


async def audit_script(llm, protocol, code: str, result: dict) -> dict:
    """Ask the critic whether the script tests the preregistered prediction."""
    messages = [
        {
            "role": "system",
            "content": (
                "You audit simulation code for a research agent. Decide whether the "
                "script truly tests the stated prediction, using the preregistered "
                "design (sample size, effect, noise, test, alpha, replications).\n\n"
                "Look for: wrong outcome variable, data generated in a way that "
                "presupposes the result, no real statistical test, ignoring the "
                "protocol's parameters, hard-coded conclusions, replications that "
                "reuse the same random stream instead of fresh noise.\n"
                "For a meta design (power, bias, coverage over inner trials), also "
                "check that the inner studies are independent draws, that the metric "
                "is computed over them and not from a single dataset, and that the "
                "grid of sample sizes is actually run.\n\n"
                "Return JSON: {\"tests_the_prediction\": true|false, "
                "\"concerns\": [\"...\"]}"
            ),
        },
        {
            "role": "user",
            "content": (
                f"PROTOCOL: {protocol.to_json()}\n\n"
                f"RESULT: {result}\n\n"
                f"SCRIPT:\n{code[:6000]}"
            ),
        },
    ]
    try:
        reply = await llm.chat_json(messages, temperature=0.1, max_tokens=500)
    except Exception as exc:  # noqa: BLE001 - audit must not break the experiment
        logger.warning(f"Simulation audit unavailable: {exc}")
        return {
            "tests_the_prediction": False,
            "concerns": [f"audit unavailable: {exc}"],
            "unavailable": True,
        }
    if not isinstance(reply, dict):
        return {"tests_the_prediction": False, "concerns": ["audit returned no JSON"]}
    concerns = reply.get("concerns") or []
    if not isinstance(concerns, list):
        concerns = [str(concerns)]
    return {
        "tests_the_prediction": bool(reply.get("tests_the_prediction")),
        "concerns": [str(c)[:200] for c in concerns][:5],
    }


def merge_reviews(pre_review: Optional[dict], post_audit: Optional[dict]) -> dict:
    """Combine the pre-run review and the post-run audit into one judgement.

    Two independent critics, both must agree that the script tests the
    prediction; the concerns are collected rather than multiplied, so a script
    that fails both is halved once - not twice for the same defect.
    """
    pre = pre_review or {}
    post = post_audit or {}
    passed = pre.get("approved", True) is not False and post.get("tests_the_prediction") is not False
    concerns = list(pre.get("problems") or []) + list(post.get("concerns") or [])
    return {
        "tests_the_prediction": bool(passed),
        "concerns": [str(concern)[:200] for concern in concerns][:5],
    }


def interpret(
    protocol,
    result: dict,
    audit: Optional[dict] = None,
    cap: float = SIMULATION_EVIDENCE_CAP,
) -> SimulationVerdict:
    """Map replication rate, effect sign, sensitivity and alpha onto a verdict."""
    alpha = _to_float(getattr(protocol, "alpha", 0.05)) or 0.05
    expected = _to_float(getattr(protocol, "effect", 0.0)) or 0.0
    is_meta = str(getattr(protocol, "design_type", "one_shot")) == "meta"
    target = _to_float(getattr(protocol, "threshold", 0.0)) or 0.0
    comparison = str(getattr(protocol, "comparison", "at_least"))
    stats = replication_stats(protocol, result)
    deviations = check_compliance(protocol, result)
    sensitivity = _sensitivity_points(result)
    notes: List[str] = []

    value = stats["mean_value"]
    p_value = stats["median_p"]
    k = stats["k"]

    if value is None or p_value is None:
        evidence_type = "neutral"
        strength = 0.2
        detail = "simulation produced no usable effect estimate"
    elif k >= MIN_REPLICATIONS_FOR_VERDICT:
        significant = stats["significant_share"] or 0.0
        direction = stats["direction_share"] or 0.0
        if is_meta:
            detail = (
                f"{getattr(protocol, 'metric_kind', 'metric')} at n={protocol.n} "
                f"vs {target:g} ({comparison}): {round(direction * k)}/{k} "
                f"replications meet the threshold, "
                f"{sum(1 for p in stats['p_values'] if p < alpha)}/{k} significant, "
                f"mean {value:.3g}, median p={p_value:.3g}"
            )
        else:
            detail = (
                f"{sum(1 for p in stats['p_values'] if p < alpha)}/{k} replications "
                f"significant (p<{alpha:g}), predicted direction in "
                f"{round(direction * k)}/{k}, mean estimate {value:.3g}, "
                f"median p={p_value:.3g}, n={result.get('n', getattr(protocol, 'n', '?'))}"
            )
        if direction >= REPRODUCED and significant >= REPRODUCED:
            # Reproduced under fresh noise, in the predicted direction.
            evidence_type = "supports"
            strength = 0.25 + 0.35 * significant + 0.10 * direction
        elif direction >= DIRECTION_LEAN and significant >= 0.4:
            # Consistent direction but significance unstable: underpowered, so
            # the right reading is "hint", not "finding".
            evidence_type = "supports"
            strength = (0.25 + 0.35 * significant + 0.10 * direction) * 0.6
            notes.append(
                "direction consistent but significance unstable across replications "
                "(underpowered, not a confirmed finding)"
            )
        elif direction <= ABSENT and significant >= 0.6:
            evidence_type = "contradicts"
            strength = 0.30 + 0.25 * significant
            detail = (
                ("the metric landed on the wrong side of the threshold in every "
                 "replication; " if is_meta
                 else "effect reproduced in the direction opposite to the prediction; ")
                + detail
            )
        elif significant <= ABSENT:
            evidence_type = "neutral"
            strength = 0.3
            notes.append(
                "the threshold was not met beyond sampling noise" if is_meta
                else "effect did not reproduce under fresh noise"
            )
        else:
            evidence_type = "neutral"
            strength = 0.3
            notes.append("inconclusive: replication rate and direction disagree")
    elif stats["significant_share"] is not None:
        # Legacy single-run script: no replication data, so the verdict is
        # explicitly weak - exactly what a scientist says about n=1 studies.
        if (stats["significant_share"] or 0.0) > 0 and (stats["direction_share"] or 0.0) > 0:
            evidence_type = "supports"
            significance = min(1.0, max(0.0, -math.log10(max(p_value, 1e-12)) / 6.0))
            strength = (0.35 + 0.45 * significance) * 0.7
            detail = (
                f"effect in the predicted direction, single run only "
                f"(p={p_value:.3g}, estimate {value:.3g}, n={result.get('n', '?')})"
            )
            notes.append("not replicated: the script ran the study only once")
        elif (stats["significant_share"] or 0.0) > 0:
            evidence_type = "contradicts"
            strength = 0.3
            detail = (
                f"effect opposite to the prediction, single run only "
                f"(p={p_value:.3g}, estimate {value:.3g})"
            )
        else:
            evidence_type = "neutral"
            strength = 0.3
            detail = (
                f"no effect detected (p={p_value:.3g} >= alpha={alpha:g}, "
                f"estimate {value:.3g})"
            )
    else:
        evidence_type = "neutral"
        strength = 0.2
        detail = "simulation produced no usable effect estimate"

    if is_meta:
        trend = _to_float(result.get("trend"))
        cells = result.get("cells")
        # A single-cell grid has no adjacent steps: a "100% trend" there would
        # be a claim about nothing.
        if trend is not None and isinstance(cells, list) and len(cells) > 1:
            notes.append(
                f"grid trend as predicted in {trend:.0%} of adjacent steps"
            )

    # --- Sensitivity: does the conclusion survive different assumptions? ---
    if evidence_type in ("supports", "contradicts") and sensitivity:
        planned = _to_float(getattr(protocol, "noise", 0.0)) or 0.0
        flipped = []
        for point in sensitivity:
            same_sign = (point["value"] >= 0) == (expected >= 0)
            significant = (point["p_value"] is None) or (point["p_value"] < alpha)
            if not same_sign or not significant:
                flipped.append(point)
        if flipped:
            factor = 0.75 if evidence_type == "supports" else 0.85
            strength *= factor
            mults = ", ".join(
                f"x{p['noise_multiplier']:g}" if p.get("noise_multiplier") is not None else "?"
                for p in flipped
            )
            notes.append(
                f"conclusion does not hold under changed noise assumptions ({mults}"
                + (f"; preregistered noise {planned:g}" if planned else "")
                + ")"
            )
    elif evidence_type == "supports" and k >= MIN_REPLICATIONS_FOR_VERDICT and not sensitivity:
        notes.append("no sensitivity analysis: the result rests on one noise assumption")

    # --- Preregistration deviations ---
    if deviations:
        strength *= max(0.4, 1.0 - 0.15 * len(deviations))
        notes.append("preregistration deviations: " + "; ".join(deviations[:3]))

    # --- Audit ---
    audit = audit or {}
    concerns = audit.get("concerns") or []
    if audit.get("tests_the_prediction") is False:
        # Halved *and* capped at half the simulation cap: an experiment whose
        # script may not test the prediction must not reach normal strength.
        strength = min(strength * 0.5, float(cap) * 0.5)
        note = "; ".join(str(c) for c in concerns[:2]) or "audit failed"
        notes.append(f"audit concern: {note}")
        if evidence_type in ("supports", "contradicts"):
            # A study that measured the wrong thing cannot support or refute the
            # prediction, however small its p-value. Keep the run, drop the claim.
            evidence_type = "neutral"
            notes.append(
                "recorded as inconclusive: the script does not test the prediction"
            )

    strength = round(min(float(cap), max(0.0, strength)), 3)
    reasoning = f"Simulation ({str(getattr(protocol, 'design', '') or '')[:110]}): {detail}"
    if notes:
        reasoning += " - " + "; ".join(notes)

    return SimulationVerdict(
        evidence_type=evidence_type,
        strength=strength,
        reasoning=reasoning,
        replication_rate=round(stats["significant_share"] or 0.0, 3),
        deviations=deviations,
        sensitivity=sensitivity,
    )
