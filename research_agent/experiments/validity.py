"""Known-answer tests: check the routine before trusting its result.

A simulation script can be syntactically perfect, follow the result contract,
and still compute the wrong quantity. The audit catches some of that, but it
reads code; these checks read *numbers against theory*, which is what a
scientist does before running an unfamiliar routine.

Every check uses a parameter set whose answer is known without knowing the
routine's internals:

* **Null rate** - with no effect, a valid test rejects at `alpha` (and a valid
  95% interval covers in 95% of cases). A routine that reports power 0.9 at
  effect zero is broken, whatever its code looks like.
* **Effect scaling** - tripling the effect must not lower power/coverage.
* **Determinism** - the same seed twice must give the same numbers, otherwise
  the replications are not replications.
* **Analytic anchor** - when the routine is a t-test and the claim is about
  power, the noncentral t distribution gives the true power for these
  parameters (both the one- and two-sided answer; whichever the measurement
  matches is the one it is judged against). Compared by a binomial test, so a
  routine that inflates power is caught even though the null rate and the
  scaling still look fine.
* **Overwhelming effect** - power must reach 1 for d=5. True for any consistent
  test, so this check needs no formula and also covers tests with no closed-form
  power.
* **Unbiasedness** (one-shot designs) - with no effect the estimate must be
  centred on zero. Analytic, and independent of which test the script uses.

Failing checks are blocking: a routine that disagrees with theory does not get
to produce evidence. The writer receives the numbers and has to fix the script.
"""

import logging
import math
from dataclasses import dataclass, field
from typing import List, Optional

from scipy import stats

logger = logging.getLogger(__name__)

DEFAULT_TRIALS = 400
MAX_SAMPLE = 2000
# |z| beyond this is treated as a real disagreement, not sampling noise.
Z_LIMIT = 4.0


@dataclass
class ValidityCheck:
    name: str
    passed: bool
    detail: str

    def to_dict(self) -> dict:
        return {"name": self.name, "passed": self.passed, "detail": self.detail}


@dataclass
class ValidityReport:
    checks: List[ValidityCheck] = field(default_factory=list)

    def add(self, name: str, passed: bool, detail: str) -> None:
        self.checks.append(ValidityCheck(name=name, passed=bool(passed), detail=detail))

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)

    @property
    def failures(self) -> List[str]:
        return [f"{c.name}: {c.detail}" for c in self.checks if not c.passed]

    def to_json(self) -> str:
        import json

        return json.dumps([check.to_dict() for check in self.checks], ensure_ascii=False)


def analytic_t_power(n: int, effect: float, noise: float, alpha: float = 0.05,
                     sides: int = 2) -> float:
    """Power of the two-sample t-test, from the noncentral t distribution.

    This is the textbook answer the simulation must reproduce: sample size `n`
    per group, true standardised effect d = effect/noise, Student df = 2n-2.
    `sides` must match the test the script runs, or a correct one-sided routine
    would be judged against the wrong number.
    """
    if n < 2:
        return 0.0
    d = abs(float(effect)) / (float(noise) or 1.0)
    df = 2 * n - 2
    noncentrality = d * math.sqrt(n / 2.0)
    if sides == 1:
        critical = stats.t.ppf(1.0 - alpha, df)
        return float(1.0 - stats.nct.cdf(critical, df, noncentrality))
    critical = stats.t.ppf(1.0 - alpha / 2.0, df)
    return float(
        1.0
        - stats.nct.cdf(critical, df, noncentrality)
        + stats.nct.cdf(-critical, df, noncentrality)
    )


# Spellings that mean "a t-test runs here". Matching a single function name is
# how a routine slipped past the analytic anchor once: it computed a t-test
# through `ttest_ind_from_stats` and the check simply did not fire.
T_TEST_MARKERS = (
    "ttest", "t_test", "t-test", "student_t", "tstat", "t_stat",
    "TTestInd", "TTest",
)


def looks_like_t_test(code: str, declared_test: str = "") -> bool:
    haystack = f"{code or ''}\n{declared_test or ''}".lower()
    return any(marker.lower() in haystack for marker in T_TEST_MARKERS)


def analytic_t_power_options(n: int, effect: float, noise: float,
                             alpha: float = 0.05) -> List[tuple]:
    """Both admissible analytic answers for a t-test: ``(label, power)``.

    Reading the sidedness off the code is unreliable - routines mix a one-sided
    threshold test with a two-sided effect test. Accepting whichever analytic
    value the measured power matches answers the real question ("is this a t-test
    with the right power?") without pretending to parse the script.
    """
    return [
        ("two-sided", analytic_t_power(n, effect, noise, alpha, sides=2)),
        ("one-sided", analytic_t_power(n, effect, noise, alpha, sides=1)),
    ]


class KnownAnswerTest:
    """Runs the script against parameters whose answer theory fixes."""

    def __init__(self, runner, trials: int = DEFAULT_TRIALS,
                 max_sample: int = MAX_SAMPLE, z_limit: float = Z_LIMIT):
        self.runner = runner
        self.trials = max(50, int(trials or DEFAULT_TRIALS))
        self.max_sample = max(10, int(max_sample or MAX_SAMPLE))
        self.z_limit = float(z_limit or Z_LIMIT)

    async def run(self, experiment_id: str, protocol, code: str) -> ValidityReport:
        report = ValidityReport()
        try:
            if getattr(protocol, "is_meta", False):
                await self._meta_checks(experiment_id, protocol, code, report)
            else:
                await self._one_shot_checks(experiment_id, protocol, code, report)
        except Exception as exc:  # noqa: BLE001 - a broken check must not crash the run
            logger.warning(f"Known-answer test crashed: {exc}")
            report.add("known-answer test", False, f"the checks crashed: {exc}")
        return report

    # === helpers ===

    @staticmethod
    def _failure_detail(run: dict) -> str:
        """The error plus the traceback tail, so the writer can actually repair it.

        The runner keeps the message in ``error`` and the Python traceback in
        ``stderr``; a repair that receives only "script exited with code 1" has
        nothing to work with.
        """
        message = str(run.get("error") or "the run failed")[:180]
        tail = [line for line in str(run.get("stderr") or "").strip().splitlines()
                if line.strip()][-3:]
        return message + (" — " + " / ".join(tail)[-400:] if tail else "")

    def _meta_params(self, protocol, effect: float, n: int, trials: int) -> dict:
        return {
            "N": int(n),
            "GRID": [int(n)],
            "TRIALS": int(trials),
            "REFERENCE_N": int(n),
            "THRESHOLD": float(getattr(protocol, "threshold", 0.0) or 0.0),
            "COMPARISON": str(getattr(protocol, "comparison", "at_least")),
            "METRIC_KIND": str(getattr(protocol, "metric_kind", "")),
            "EFFECT": float(effect),
            "NOISE": float(getattr(protocol, "noise", 1.0) or 1.0),
            "ALPHA": float(getattr(protocol, "alpha", 0.05) or 0.05),
            "SEED": int(getattr(protocol, "seed", 1) or 1),
            "REPLICATIONS": 1,
        }

    async def _execute(self, experiment_id: str, suffix: str, code: str, params: dict) -> dict:
        return await self.runner.run_async(f"{experiment_id}_kat_{suffix}", code, params)

    @staticmethod
    def _meta_fingerprint(run: dict) -> tuple:
        """Everything a seeded routine must reproduce exactly.

        Comparing only the headline metric makes the determinism check flaky:
        an unseeded routine can hit the same rounded share by chance. The full
        cell and sensitivity vector makes that unlikely.
        """
        result = run.get("result") or {}
        cells = tuple(
            round(float(cell.get("metric", 0.0)), 12)
            for cell in (result.get("cells") or [])
            if isinstance(cell, dict)
        )
        sensitivity = tuple(
            round(float(point.get("value", 0.0)), 12)
            for point in (result.get("sensitivity") or [])
            if isinstance(point, dict)
        )
        return (cells, sensitivity, result.get("value"), result.get("p_value"))

    @staticmethod
    def _metric(run: dict) -> Optional[float]:
        cells = (run.get("result") or {}).get("cells")
        if isinstance(cells, list) and cells and isinstance(cells[0], dict):
            try:
                return float(cells[0].get("metric"))
            except (TypeError, ValueError):
                return None
        return None

    def _z(self, hits: float, total: int, expected: float) -> Optional[float]:
        if total <= 0:
            return None
        variance = total * expected * (1.0 - expected)
        if variance <= 0:
            return None
        return (hits - total * expected) / math.sqrt(variance)

    # === meta designs ===

    async def _meta_checks(self, experiment_id: str, protocol, code: str,
                           report: ValidityReport) -> None:
        n = min(int(protocol.n), self.max_sample)
        # The checks use their own trial count, not the study's: 150 inner trials
        # cannot tell a power of 0.91 from 1.0, and a wrong routine must not be
        # excused by a small preregistered trial count.
        trials = self.trials
        alpha = float(getattr(protocol, "alpha", 0.05) or 0.05)
        effect = float(getattr(protocol, "effect", 0.0) or 0.0)
        kind = str(getattr(protocol, "metric_kind", ""))
        base = self._meta_params(protocol, effect, n, trials)

        run_effect = await self._execute(experiment_id, "effect", code, base)
        run_repeat = await self._execute(experiment_id, "repeat", code, dict(base))
        run_null = await self._execute(
            experiment_id, "null", code, {**base, "EFFECT": 0.0}
        )
        run_triple = await self._execute(
            experiment_id, "effect3", code, {**base, "EFFECT": effect * 3.0}
        )
        # Overwhelming effect: power must reach 1 whatever the test is. That is
        # analytically true without knowing the routine, so it also covers tests
        # with no closed-form power.
        run_strong = (
            await self._execute(
                experiment_id, "strong", code,
                {**base, "EFFECT": 5.0, "NOISE": 1.0},
            )
            if kind == "power" else None
        )

        broken = [run for run in (run_effect, run_repeat, run_null, run_triple, run_strong)
                  if run is not None and not run.get("ok")]
        if broken:
            report.add(
                "script runs under the known-answer parameters", False,
                self._failure_detail(broken[0]),
            )
            return

        m_effect = self._metric(run_effect)
        m_repeat = self._metric(run_repeat)
        m_null = self._metric(run_null)
        m_triple = self._metric(run_triple)
        if None in (m_effect, m_repeat, m_null, m_triple):
            report.add(
                "script reports a metric", False,
                "no 'cells[0].metric' in the known-answer output",
            )
            return

        report.add(
            "deterministic for a fixed seed",
            self._meta_fingerprint(run_effect) == self._meta_fingerprint(run_repeat),
            f"metric {m_effect:.4g} vs {m_repeat:.4g} on a repeat run",
        )

        if kind in ("power", "coverage"):
            expected = alpha if kind == "power" else 1.0 - alpha
            hits = m_null * trials
            z = self._z(hits, trials, expected)
            report.add(
                f"null rate is {'alpha' if kind == 'power' else '1-alpha'}",
                z is not None and abs(z) <= self.z_limit,
                f"{kind} at effect 0 was {m_null:.3f} in {trials} trials, "
                f"theory says {expected:.3f}"
                + (f" (z={z:.1f})" if z is not None else ""),
            )
            report.add(
                "effect scaling",
                m_triple >= m_effect - 0.02,
                f"{kind} at 3x effect was {m_triple:.3f} vs {m_effect:.3f} at 1x",
            )
            if kind == "power" and run_strong is not None:
                m_strong = self._metric(run_strong)
                report.add(
                    "power is 1 for an overwhelming effect",
                    m_strong is not None and m_strong >= 0.97,
                    f"power at d=5 was {m_strong if m_strong is not None else float('nan'):.3f} "
                    "(a consistent test must always reject)",
                )
        else:
            finite = math.isfinite(m_null) and m_null >= 0.0
            report.add(
                "metric is a finite non-negative deviation", finite,
                f"bias at effect 0 was {m_null:.4g}",
            )

        if kind == "power" and looks_like_t_test(code, getattr(protocol, "test", "")):
            noise = float(getattr(protocol, "noise", 1.0) or 1.0)
            measured = m_effect * trials
            candidates = []
            for label, expected in analytic_t_power_options(n, effect, noise, alpha):
                z = self._z(measured, trials, expected)
                if z is not None:
                    candidates.append((label, expected, z))
            if candidates:
                label, expected, z = min(candidates, key=lambda c: abs(c[2]))
                others = ", ".join(
                    f"{c[0]} {c[1]:.3f}" for c in candidates if c[0] != label
                )
                report.add(
                    "matches the analytic t-test power",
                    abs(z) <= self.z_limit,
                    f"measured power {m_effect:.3f} vs analytic {expected:.3f} "
                    f"({label}; {others}; n={n} per group, "
                    f"d={abs(effect) / noise:.2f}), z={z:.1f}",
                )

    # === one-shot designs ===

    async def _one_shot_checks(self, experiment_id: str, protocol, code: str,
                               report: ValidityReport) -> None:
        alpha = float(getattr(protocol, "alpha", 0.05) or 0.05)
        effect = float(getattr(protocol, "effect", 0.0) or 0.0)
        repetitions = 5
        base = self.runner.protocol_params(protocol, replications=repetitions)

        run_effect = await self._execute(experiment_id, "effect", code, dict(base))
        run_repeat = await self._execute(experiment_id, "repeat", code, dict(base))
        run_null = await self._execute(
            experiment_id, "null", code, {**base, "EFFECT": 0.0}
        )
        run_triple = await self._execute(
            experiment_id, "effect3", code, {**base, "EFFECT": effect * 3.0}
        )

        broken = [run for run in (run_effect, run_repeat, run_null, run_triple)
                  if not run.get("ok")]
        if broken:
            report.add(
                "script runs under the known-answer parameters", False,
                self._failure_detail(broken[0]),
            )
            return

        values_effect = self._values(run_effect)
        values_repeat = self._values(run_repeat)
        values_null = (run_null.get("result") or {}).get("values")
        values_triple = (run_triple.get("result") or {}).get("values")
        if None in (values_effect, values_repeat) or not values_null or not values_triple:
            report.add(
                "script reports replication estimates", False,
                "no 'values' list in the known-answer output",
            )
            return

        report.add(
            "deterministic for a fixed seed",
            values_effect == values_repeat,
            f"{len(values_effect)} replication estimates "
            + ("are identical" if values_effect == values_repeat else "differ on a repeat run"),
        )

        p_values = (run_null.get("result") or {}).get("p_values") or []
        significant = sum(1 for p in p_values if isinstance(p, (int, float)) and p < alpha)
        share = significant / len(p_values) if p_values else 0.0
        report.add(
            "no effect means no finding",
            share <= 0.6,
            f"{significant}/{len(p_values)} runs significant at effect 0 "
            f"(expected about {alpha:.2f})",
        )

        # Analytic anchor: with no effect the estimator must be centred on zero.
        # Unlike a p-value this does not depend on which test the script runs;
        # it only assumes the estimate is unbiased, which any usable estimator is.
        null_numbers = [float(v) for v in values_null
                        if isinstance(v, (int, float))]
        if len(null_numbers) >= 3:
            mean_null = sum(null_numbers) / len(null_numbers)
            variance = sum((v - mean_null) ** 2 for v in null_numbers)
            standard_error = math.sqrt(variance / (len(null_numbers) - 1) / len(null_numbers))
            # A tolerance of 4 standard errors keeps a correct routine from being
            # punished for sampling noise while still catching an offset.
            tolerance = max(4.0 * standard_error, 1e-9)
            report.add(
                "estimate is centred on zero without an effect",
                abs(mean_null) <= tolerance,
                f"mean estimate at effect 0 was {mean_null:.3g} "
                f"(tolerance {tolerance:.3g}, {len(null_numbers)} replications)",
            )

        mean_effect = sum(values_effect) / len(values_effect)
        mean_triple = sum(values_triple) / len(values_triple)
        grows = abs(mean_triple) >= 1.5 * abs(mean_effect)
        same_sign = (mean_triple >= 0) == (mean_effect >= 0)
        report.add(
            "estimate scales with the effect",
            grows and same_sign,
            f"mean estimate {mean_effect:.3g} at 1x, {mean_triple:.3g} at 3x",
        )

    @staticmethod
    def _values(run: dict) -> Optional[list]:
        values = (run.get("result") or {}).get("values")
        return list(values) if isinstance(values, list) and values else None
