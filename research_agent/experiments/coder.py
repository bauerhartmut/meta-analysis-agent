"""Write the Python simulation script for a protocol.

Three rules keep it honest: it must take the protocol's numbers from the
generated ``sim_params`` module (not hardcode or invent them), it may only
import from a small allowlist - no filesystem, no network, no subprocess, even
before the sandbox blocks it - and it must print the agreed JSON result line.

Reading the numbers instead of hardcoding them is what makes the pre-run smoke
test possible: the same script runs once at a tiny sample size before the real
study, so a broken contract is caught before any result exists.
"""

import ast
import logging
import re
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

ALLOWED_MODULES = {
    "math", "random", "statistics", "json", "itertools", "collections",
    "functools", "numpy", "scipy", "dataclasses", "typing",
    # Generated next to the script for every run: carries the protocol numbers
    # (n, effect, noise, alpha, seed, replications) as plain literals.
    "sim_params",
}

PARAM_NAMES = (
    "N", "EFFECT", "NOISE", "ALPHA", "SEED", "REPLICATIONS",
    "GRID", "TRIALS", "REFERENCE_N", "THRESHOLD", "COMPARISON", "METRIC_KIND",
)


def check_uses_params(code: str) -> Tuple[bool, str]:
    """Require the script to read its numbers from ``sim_params``.

    A script with hardcoded numbers cannot be smoke-tested at a small n, and it
    silently decides its own design instead of the preregistered one.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return False, f"syntax error: {exc.msg} (line {exc.lineno})"

    imported_as = None
    imported_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "sim_params":
                    imported_as = alias.asname or "sim_params"
        elif isinstance(node, ast.ImportFrom) and node.module == "sim_params":
            imported_names.update(alias.name for alias in node.names)
    if not imported_as and not imported_names:
        return False, (
            "the script does not import sim_params, so it ignores the "
            "preregistered numbers (use `import sim_params as P`)"
        )
    used = any(
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == imported_as
        for node in ast.walk(tree)
    ) if imported_as else True
    if imported_names or used:
        return True, ""
    return False, (
        "the script imports sim_params but never reads from it; use "
        f"{', '.join('P.' + name for name in PARAM_NAMES[:6])} and, for a meta "
        "design, P.GRID, P.TRIALS, P.REFERENCE_N, P.THRESHOLD, P.COMPARISON, "
        "P.METRIC_KIND"
    )


def check_imports(code: str) -> Tuple[bool, str]:
    """Reject imports outside the allowlist (also blocks ``__import__`` tricks)."""
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return False, f"syntax error: {exc.msg} (line {exc.lineno})"

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root not in ALLOWED_MODULES:
                    return False, f"import '{root}' is not allowed"
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root and root not in ALLOWED_MODULES:
                return False, f"import from '{root}' is not allowed"
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in {"__import__", "eval", "exec", "compile", "open", "input"}:
                return False, f"call to '{node.func.id}' is not allowed"
        elif isinstance(node, ast.Attribute) and node.attr in {"system", "popen", "remove", "unlink"}:
            return False, f"attribute '{node.attr}' is not allowed"
    return True, ""


def _strip_fences(text: str) -> str:
    text = (text or "").strip()
    fence = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
    return (fence.group(1) if fence else text).strip()


class SimulationWriter:
    def __init__(self, llm, max_attempts: int = 2):
        self.llm = llm
        self.max_attempts = max(1, int(max_attempts or 1))

    async def write(self, protocol, feedback: str = "") -> Tuple[Optional[str], str]:
        """Return (code, error). Static guards get one rewrite attempt here."""
        for attempt in range(1, self.max_attempts + 1):
            code = await self._ask(protocol, feedback)
            if not code:
                return None, "the model returned no code"
            ok, reason = check_imports(code)
            if ok:
                ok, reason = check_uses_params(code)
            if ok:
                return code, ""
            logger.warning(f"Simulation script rejected ({reason}), attempt {attempt}")
            truncation_hint = ""
            if any(marker in reason.lower() for marker in
                   ("never closed", "unexpected eof", "syntax error")):
                truncation_hint = (
                    " Your answer may have been cut off: return a shorter script "
                    "without docstrings or long comments. "
                )
            feedback = (
                f"Your previous script was rejected: {reason}.{truncation_hint} "
                f"Only these modules are allowed: {', '.join(sorted(ALLOWED_MODULES))}. "
                "Read n, effect, noise, alpha, seed and replications from "
                "`sim_params` - never hardcode them."
            )
        return None, feedback

    async def _ask_meta(self, protocol, feedback: str = "") -> str:
        """Prompt for a meta design: a grid of sample sizes times inner trials."""
        messages = [
            {
                "role": "system",
                "content": (
                    "You write a Python script that measures a property of a statistical "
                    "procedure - its power, its bias or its interval coverage. This is "
                    "NOT a single study: each replication runs `TRIALS` inner studies for "
                    "every sample size in `GRID`, and the metric is computed over them.\n\n"
                    "Hard requirements:\n"
                    "- Use only these modules: " + ", ".join(sorted(ALLOWED_MODULES)) + ".\n"
                    "- No file access, no network, no user input, no subprocess.\n"
                    "- Read every number from `sim_params`: `GRID` (list of sample "
                    "sizes), `TRIALS` (inner studies per cell), `REFERENCE_N` (the cell "
                    "the prediction is about), `THRESHOLD`, `COMPARISON` \"at_least\" | "
                    "\"at_most\", `METRIC_KIND` \"power\" | \"bias\" | \"coverage\", "
                    "`EFFECT` (true effect), `NOISE`, `ALPHA`, `SEED`, `REPLICATIONS`. "
                    "Never hardcode them: the same script is first run at a tiny grid.\n"
                    "- Trials must be independent draws, not the same data reused.\n\n"
                    "Per replication r (seed SEED + r):\n"
                    "1. For each n in GRID run TRIALS inner studies of two groups "
                    "(group 1 N(0, NOISE), group 2 N(EFFECT, NOISE)) and compute the "
                    "metric:\n"
                    "   power    = share with p < ALPHA\n"
                    "   coverage = share whose 95% CI contains EFFECT\n"
                    "   bias     = mean(|estimate - EFFECT|), the mean absolute deviation\n"
                    "2. Take the cell at n == REFERENCE_N: its metric is this "
                    "replication's `value`; its observations give this replication's "
                    "`p_value` from a one-sided test against THRESHOLD:\n"
                    "   power/coverage: stats.binomtest(hits, TRIALS, THRESHOLD, "
                    "alternative=alt) where alt = \"greater\" for at_least, \"less\" for "
                    "at_most.\n"
                    "   bias: stats.ttest_1samp(deviations, THRESHOLD, alternative=alt) "
                    "with the same alt and the per-trial |estimate - EFFECT| values.\n"
                    "- SENSITIVITY: repeat the REFERENCE_N cell once at NOISE x 0.5 and "
                    "once at NOISE x 2.0, with the same threshold test.\n"
                    "- Print exactly ONE JSON object as the last line, with keys: n "
                    "(REFERENCE_N), metric, test, alpha, seed, replications, value "
                    "(mean over replications), ci_low, ci_high (95% interval over the "
                    "replication values), p_value (median over replications), values, "
                    "p_values, significant_share, direction_share, sensitivity, cells "
                    "([{\"n\": ..., \"metric\": ..., \"trials\": ...}, ...], metric "
                    "averaged over replications per grid cell), grid, trend (share of "
                    "adjacent grid steps that move as predicted: rising for "
                    "power/coverage, falling for bias; null when GRID has only one "
                    "value, because then there are no steps).\n"
                    "- direction_share = share of replications where value meets the "
                    "threshold the way COMPARISON says; significant_share = share of "
                    "replications with p < ALPHA.\n"
                    "- Runtime under 90 seconds: vectorise with numpy, keep TRIALS x len(GRID) "
                    "x REPLICATIONS simulations feasible (numpy randn in batches).\n"
                    "- Print nothing else after the JSON line.\n\n"
                    "Return ONLY the Python code, no explanation and no markdown fences.\n\n"
                    "SKELETON:\n"
                    "```python\n"
                    "import json\n"
                    "import numpy as np\n"
                    "from scipy import stats\n"
                    "import sim_params as P\n"
                    "\n"
                    "ALT = 'greater' if P.COMPARISON == 'at_least' else 'less'\n"
                    "\n"
                    "def cell(seed, n, noise):\n"
                    "    rng = np.random.default_rng(seed)\n"
                    "    obs, estimates = 0.0, []\n"
                    "    deviations = []\n"
                    "    for _ in range(P.TRIALS):\n"
                    "        a = rng.normal(0.0, noise, n)\n"
                    "        b = rng.normal(P.EFFECT, noise, n)\n"
                    "        t = stats.ttest_ind(a, b, equal_var=False)\n"
                    "        est = float(b.mean() - a.mean())\n"
                    "        estimates.append(est)\n"
                    "        deviations.append(abs(est - P.EFFECT))\n"
                    "        ci = t.confidence_interval(0.95)\n"
                    "        if P.METRIC_KIND == 'power':\n"
                    "            obs += float(t.pvalue < P.ALPHA)\n"
                    "        elif P.METRIC_KIND == 'coverage':\n"
                    "            obs += float(ci.low <= P.EFFECT <= ci.high)\n"
                    "    if P.METRIC_KIND == 'bias':\n"
                    "        return {'n': n, 'metric': float(np.mean(deviations)), 'trials': P.TRIALS}, deviations\n"
                    "    return {'n': n, 'metric': obs / P.TRIALS, 'trials': P.TRIALS}, None\n"
                    "\n"
                    "def threshold_p(hits, deviations):\n"
                    "    if P.METRIC_KIND == 'bias':\n"
                    "        return float(stats.ttest_1samp(deviations, P.THRESHOLD, alternative=ALT).pvalue)\n"
                    "    return float(stats.binomtest(int(hits), P.TRIALS, P.THRESHOLD, alternative=ALT).pvalue)\n"
                    "\n"
                    "# loop replications and grid cells, collect per-replication value/p_value,\n"
                    "# average cells over replications, compute trend over adjacent cells,\n"
                    "# print the JSON line with all keys above\n"
                    "```"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"PROTOCOL:\n{protocol.to_json()}\n\n"
                    f"Prediction: {protocol.prediction}\n"
                    f"Falsification condition: {protocol.falsification}\n"
                    + (f"\n{feedback}\n" if feedback else "")
                ),
            },
        ]
        try:
            reply = await self.llm.chat(messages, temperature=0.1, max_tokens=3200)
        except Exception as exc:  # noqa: BLE001 - a failed write must not break a cycle
            logger.warning(f"Meta simulation script generation failed: {exc}")
            return ""
        return _strip_fences(reply)

    async def _ask(self, protocol, feedback: str = "") -> str:
        if getattr(protocol, "is_meta", False):
            return await self._ask_meta(protocol, feedback)
        messages = [
            {
                "role": "system",
                "content": (
                    "You write a Python script that runs ONE simulated study - the way a "
                    "scientist would: several independent replications with fresh noise, "
                    "then a sensitivity check that varies the assumptions.\n\n"
                    "Hard requirements:\n"
                    "- Use only these modules: " + ", ".join(sorted(ALLOWED_MODULES)) + ".\n"
                    "- No file access, no network, no user input, no subprocess.\n"
                    "- Read every number from the module `sim_params`: it is generated "
                    "next to your script before each run and holds `N`, `EFFECT`, "
                    "`NOISE`, `ALPHA`, `SEED`, `REPLICATIONS` as plain values. Start with "
                    "`import sim_params as P`. Never hardcode or invent these numbers: "
                    "the same script is first run at a tiny n to test it.\n"
                    "- REPLICATIONS: run the study `replications` times. Replication i uses "
                    "seed + i as its random seed and generates its data independently. "
                    "Store the estimated effect of each run in `values` and its p-value in "
                    "`p_values`.\n"
                    "- SENSITIVITY: run the same study once more at noise x 0.5 and once at "
                    "noise x 2.0 (effect, n and alpha unchanged), so the result cannot "
                    "depend silently on the noise assumption. Put them in `sensitivity` "
                    "as {\"noise_multiplier\": 0.5, \"value\": ..., \"p_value\": ...}.\n"
                    "- Print exactly ONE JSON object as the last line of output, with keys: "
                    "n, metric, test, alpha, seed, replications, value, ci_low, ci_high, "
                    "p_value, values, p_values, significant_share, direction_share, "
                    "sensitivity.\n"
                    "- `value` is the mean estimate over the replications, `p_value` the "
                    "median p-value, `ci_low`/`ci_high` a 95% interval over the "
                    "replication estimates, `significant_share` the fraction of runs with "
                    "p < alpha and `direction_share` the fraction with the predicted sign.\n"
                    "- Runtime under 90 seconds; keep memory small.\n"
                    "- Print nothing else after the JSON line.\n\n"
                    "Return ONLY the Python code, no explanation and no markdown fences.\n\n"
                    "SKELETON (fill in the data generation and the test, keep the shape):\n"
                    "```python\n"
                    "import json\n"
                    "import numpy as np\n"
                    "from scipy import stats\n"
                    "\n"
                    "import sim_params as P\n"
                    "\n"
                    "N = P.N\n"
                    "EFFECT = P.EFFECT\n"
                    "NOISE = P.NOISE\n"
                    "ALPHA = P.ALPHA\n"
                    "SEED = P.SEED\n"
                    "REPLICATIONS = P.REPLICATIONS\n"
                    "\n"
                    "def run(seed, noise):\n"
                    "    rng = np.random.default_rng(seed)\n"
                    "    # draw the groups from the stated design ...\n"
                    "    # estimate = ...\n"
                    "    # p = stats.ttest_ind(...).pvalue\n"
                    "    return estimate, float(p)\n"
                    "\n"
                    "values, p_values = [], []\n"
                    "for i in range(REPLICATIONS):\n"
                    "    v, p = run(SEED + i, NOISE)\n"
                    "    values.append(v); p_values.append(p)\n"
                    "\n"
                    "sensitivity = []\n"
                    "for mult in (0.5, 2.0):\n"
                    "    v, p = run(SEED, NOISE * mult)\n"
                    "    sensitivity.append({'noise_multiplier': mult, 'value': v, 'p_value': p})\n"
                    "\n"
                    "# print the JSON line with all keys above\n"
                    "```"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"PROTOCOL:\n{protocol.to_json()}\n\n"
                    f"Falsification condition: {protocol.falsification}\n"
                    + (f"\n{feedback}\n" if feedback else "")
                ),
            },
        ]
        try:
            reply = await self.llm.chat(messages, temperature=0.1, max_tokens=2200)
        except Exception as exc:  # noqa: BLE001 - a failed write must not break a cycle
            logger.warning(f"Simulation script generation failed: {exc}")
            return ""
        return _strip_fences(reply)
