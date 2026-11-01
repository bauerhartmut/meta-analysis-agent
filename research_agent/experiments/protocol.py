"""Preregistration of a simulated experiment.

The point of writing this down *before* the script runs is the same as a
preregistration in real science: the analysis cannot be bent afterwards. The
protocol fixes population, sample size, expected effect, noise, test and alpha;
the script has to implement exactly that, and the interpretation compares the
result against the prediction stated here.

Two design families, because two kinds of hypothesis exist:

* ``one_shot`` - a claim about the world. Each replication draws one dataset and
  estimates the effect; the verdict asks whether the effect survives fresh noise.
* ``meta`` - a claim about a *statistical procedure*: how much power a design has,
  whether an estimator is biased, whether a confidence interval covers the true
  value. One dataset says nothing here; each replication runs many inner trials
  and summarises them, and the prediction is a threshold on that summary
  (``power at n=200 is at least 0.6``).
"""

import json
from dataclasses import asdict, dataclass, field
from typing import List, Optional, Tuple


def _int_list(value) -> List[int]:
    """Best-effort ints from loose model output; unusable entries are dropped."""
    if not isinstance(value, (list, tuple)):
        return []
    out = []
    for item in value:
        try:
            out.append(int(item))
        except (TypeError, ValueError):
            continue
    return out


@dataclass
class ExperimentProtocol:
    hypothesis_id: str
    claim: str
    prediction: str
    falsification: str
    design: str
    population: str
    n: int
    effect: float
    noise: float
    metric: str
    test: str
    alpha: float = 0.05
    seed: int = 12345
    # One run at one seed is an anecdote. The protocol fixes how often the
    # study is repeated with fresh noise before anything runs, so "it worked
    # once" cannot be reported as "it works".
    replications: int = 5

    # Meta designs: a property of the procedure, measured over inner trials.
    design_type: str = "one_shot"
    metric_kind: str = ""            # power | bias | coverage
    trials: int = 0                  # inner trials per grid cell
    grid: List[int] = field(default_factory=list)   # sample sizes, increasing
    threshold: float = 0.0           # predicted value of the metric at n
    comparison: str = "at_least"     # at_least | at_most

    MIN_N = 30
    MAX_N = 2_000_000
    MIN_REPLICATIONS = 3
    MAX_REPLICATIONS = 20
    MIN_TRIALS = 50
    MAX_TRIALS = 200_000
    MAX_GRID = 6
    DESIGNS = ("one_shot", "meta")
    METRIC_KINDS = ("power", "bias", "coverage")

    def validate(self) -> Tuple[bool, str]:
        """Return (ok, reason). A protocol that fails here never runs."""
        for field_name, minimum in (
            ("claim", 10), ("prediction", 8), ("falsification", 8),
            ("design", 8), ("population", 3), ("metric", 3), ("test", 3),
        ):
            value = str(getattr(self, field_name) or "").strip()
            if len(value) < minimum:
                return False, f"{field_name} is too short for a usable protocol"
        try:
            n = int(self.n)
        except (TypeError, ValueError):
            return False, "n is not an integer"
        if not (self.MIN_N <= n <= self.MAX_N):
            return False, f"n={n} outside [{self.MIN_N}, {self.MAX_N}]"
        try:
            effect = float(self.effect)
            noise = float(self.noise)
            alpha = float(self.alpha)
        except (TypeError, ValueError):
            return False, "effect/noise/alpha must be numbers"
        if not (0.0 < abs(effect) <= 5.0):
            return False, "effect must be non-zero and at most 5"
        if not (0.0 < noise <= 10.0):
            return False, "noise must be positive and at most 10"
        if not (0.001 <= alpha <= 0.2):
            return False, "alpha must be between 0.001 and 0.2"
        if int(self.seed) < 0:
            return False, "seed must be non-negative"
        try:
            replications = int(self.replications)
        except (TypeError, ValueError):
            return False, "replications is not an integer"
        if not (self.MIN_REPLICATIONS <= replications <= self.MAX_REPLICATIONS):
            return False, (
                f"replications={replications} outside "
                f"[{self.MIN_REPLICATIONS}, {self.MAX_REPLICATIONS}]: a single run "
                "is not a replication"
            )

        design_type = str(self.design_type or "one_shot").strip()
        if design_type not in self.DESIGNS:
            return False, f"unknown design_type '{design_type}'"
        if design_type == "meta":
            return self._validate_meta(n)
        return True, ""

    def _validate_meta(self, n: int) -> Tuple[bool, str]:
        """A meta design needs a grid, inner trials and a threshold to compare to."""
        kind = str(self.metric_kind or "").strip()
        if kind not in self.METRIC_KINDS:
            return False, (
                f"metric_kind '{kind}' is not one of {', '.join(self.METRIC_KINDS)}"
            )
        try:
            trials = int(self.trials)
        except (TypeError, ValueError):
            return False, "trials is not an integer"
        if not (self.MIN_TRIALS <= trials <= self.MAX_TRIALS):
            return False, (
                f"trials={trials} outside [{self.MIN_TRIALS}, {self.MAX_TRIALS}]: "
                "a few trials estimate noise, not power"
            )
        grid = self.normalized_grid()
        if not grid:
            return False, "grid of sample sizes is empty"
        if len(grid) > self.MAX_GRID:
            return False, f"grid has {len(grid)} values, at most {self.MAX_GRID} are allowed"
        if grid[0] < 10:
            return False, "grid sample sizes must be at least 10"
        if any(b <= a for a, b in zip(grid, grid[1:])):
            return False, "grid must be strictly increasing"
        if n not in grid:
            return False, f"n={n} is not one of the grid sample sizes {grid}"
        try:
            threshold = float(self.threshold)
        except (TypeError, ValueError):
            return False, "threshold is not a number"
        if kind == "bias":
            if not (0.0 <= threshold <= 5.0):
                return False, "bias tolerance must be between 0 and 5"
        elif not (0.0 < threshold < 1.0):
            return False, f"threshold for {kind} must be a proportion between 0 and 1"
        comparison = str(self.comparison or "at_least").strip()
        if comparison not in ("at_least", "at_most"):
            return False, f"comparison '{comparison}' is not at_least or at_most"
        return True, ""

    def normalized_grid(self) -> List[int]:
        """The grid as ints, ignoring anything unusable (LLM output is loose)."""
        raw = self.grid
        if not isinstance(raw, (list, tuple)):
            return []
        values = []
        for item in raw:
            try:
                values.append(int(item))
            except (TypeError, ValueError):
                continue
        return values

    @property
    def is_meta(self) -> bool:
        return str(self.design_type or "one_shot").strip() == "meta"

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Optional[dict], hypothesis_id: str = "") -> Optional["ExperimentProtocol"]:
        if not isinstance(data, dict):
            return None

        def text(*keys, default=""):
            for key in keys:
                value = data.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
            return default

        def number(key, default, cast=float):
            try:
                return cast(data.get(key, default))
            except (TypeError, ValueError):
                return cast(default)

        return cls(
            hypothesis_id=text("hypothesis_id", default=hypothesis_id),
            claim=text("claim", "research_claim"),
            prediction=text("prediction", "predicted_effect"),
            falsification=text("falsification", "falsification_condition"),
            design=text("design", "simulated_study"),
            population=text("population", "synthetic"),
            n=number("n", 500, int),
            effect=number("effect", 0.3, float),
            noise=number("noise", 1.0, float),
            metric=text("metric", "effect"),
            test=text("test", "significance test"),
            alpha=number("alpha", 0.05, float),
            seed=number("seed", 12345, int),
            replications=number("replications", 5, int),
            design_type=text("design_type", default="one_shot"),
            metric_kind=text("metric_kind", default=""),
            trials=number("trials", 0, int),
            grid=_int_list(data.get("grid")),
            threshold=number("threshold", 0.0, float),
            comparison=text("comparison", default="at_least"),
        )
