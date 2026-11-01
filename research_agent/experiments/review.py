"""Review a simulation script *before* it runs.

The post-run audit asks whether the result can be trusted. This reviewer asks
the cheaper question first: is this the right experiment at all? A script that
measures something adjacent to the prediction, or that reads its numbers from
somewhere other than the protocol, should never get to execute - once it has
produced a p-value, that p-value is in the database.

An unavailable reviewer approves and says so: infrastructure failures must not
silently close the queue. The post-run audit is still there, and evidence is
capped either way.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

MAX_PROBLEMS = 4


class ScriptReviewer:
    def __init__(self, llm):
        self.llm = llm

    async def review(
        self, protocol, code: str, smoke: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> dict:
        """Return {"approved": bool, "problems": [str], "unavailable": bool}."""
        smoke_line = ""
        if smoke:
            smoke_line = (
                f"SMOKE TEST OUTPUT (n={smoke.get('params', {}).get('N')}, "
                f"1 replication): {str(smoke.get('stdout') or '')[-800:]}\n"
            )
        # The engine of the parameters is generated next to the script. Without
        # them the reviewer invents absences ("REFERENCE_N is not defined").
        params_line = ""
        if params:
            params_line = (
                "sim_params contains exactly: "
                + ", ".join(f"{name}={value!r}" for name, value in params.items())
                + "\n"
            )
        messages = [
            {
                "role": "system",
                "content": (
                    "You review a simulation script before it is executed for a "
                    "research agent. Judge the script itself, not its results - none "
                    "exist yet.\n\n"
                    "Reject it if any of these holds:\n"
                    "- it does not measure the variable the prediction talks about\n"
                    "- the data generation presupposes the conclusion (e.g. it injects "
                    "the effect into the outcome it then 'discovers')\n"
                    "- there is no real statistical test, or the test does not fit the "
                    "design\n"
                    "- it hardcodes or invents n, effect, noise, alpha, seed or "
                    "replications instead of reading `sim_params`\n"
                    "- it will not print the agreed JSON line (keys: n, metric, test, "
                    "alpha, seed, replications, value, ci_low, ci_high, p_value, values, "
                    "p_values, significant_share, direction_share, sensitivity)\n"
                    "- for a meta design (power/bias/coverage): it measures the metric "
                    "from one dataset instead of over `TRIALS` inner studies per grid "
                    "cell, or it reports no `cells`/`grid`\n\n"
                    "Be strict about those points and tolerant about style. Return "
                    "JSON: {\"approved\": true|false, \"problems\": [\"...\"]}."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"PROTOCOL: {protocol.to_json()}\n\n"
                    f"PREDICTION: {protocol.prediction}\n"
                    f"FALSIFICATION: {protocol.falsification}\n\n"
                    f"{params_line}"
                    f"{smoke_line}"
                    f"SCRIPT:\n{code[:7000]}"
                ),
            },
        ]
        try:
            reply = await self.llm.chat_json(messages, temperature=0.0, max_tokens=500)
        except Exception as exc:  # noqa: BLE001 - a broken reviewer must not block
            logger.warning(f"Script review unavailable: {exc}")
            return {"approved": True, "problems": [], "unavailable": True}
        if not isinstance(reply, dict):
            return {"approved": True, "problems": [], "unavailable": True}

        problems = reply.get("problems") or []
        if not isinstance(problems, list):
            problems = [str(problems)]
        approved = bool(reply.get("approved"))
        if not approved and not problems:
            problems = ["the reviewer rejected the script without stating a reason"]
        return {
            "approved": approved,
            "problems": [str(problem)[:220] for problem in problems][:MAX_PROBLEMS],
            "unavailable": False,
        }
