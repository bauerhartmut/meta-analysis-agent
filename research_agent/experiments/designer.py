"""Design a simulated study for a hypothesis.

The designer only ever produces a *protocol* - a design with numbers, fixed
before anything runs. It refuses hypotheses whose prediction is not measurable
("X is ethically problematic" cannot be simulated), which is the honest answer
and better than a script that measures nothing.
"""

import logging
from typing import Optional

from .protocol import ExperimentProtocol

logger = logging.getLogger(__name__)


class ExperimentDesigner:
    def __init__(self, llm):
        self.llm = llm

    async def design(self, hypothesis: dict, replications: int = 5) -> Optional[ExperimentProtocol]:
        """Return a validated protocol, or None if the hypothesis is untestable."""
        try:
            replications = int(replications)
        except (TypeError, ValueError):
            replications = 5
        replications = min(ExperimentProtocol.MAX_REPLICATIONS,
                           max(ExperimentProtocol.MIN_REPLICATIONS, replications))
        messages = [
            {
                "role": "system",
                "content": (
                    "You design simulated studies that test scientific predictions.\n\n"
                    "Given a hypothesis with its prediction and falsification condition, "
                    "decide whether a simulation can test it, and if so, design one.\n\n"
                    "A simulation is appropriate when the prediction is about a measurable "
                    "quantity under a stated mechanism (effect of X on Y, a rate, a bias, "
                    "a power analysis, a selection response). It is NOT appropriate for "
                    "ethical, normative or definitional claims.\n\n"
                    "Rules:\n"
                    "- Fix ONE design before seeing any result: population, sample size n, "
                    "expected effect size, noise level, the metric and the statistical test.\n"
                    "- n between 30 and 2,000,000; effect non-zero and <= 5; noise > 0; "
                    "alpha between 0.001 and 0.2.\n"
                    "- `n` is the sample size of the study (per group where the design "
                    "has groups), never the number of Monte-Carlo trials.\n"
                    "- If the hypothesis names specific sample sizes or effect sizes, "
                    "use exactly those numbers; do not substitute your own.\n"
                    f"- The study is repeated {replications} times with fresh noise at "
                    f"consecutive seeds starting at `seed`. Set \"replications\": "
                    f"{replications}.\n"
                    "- The design must be executable with numpy/scipy on synthetic data.\n"
                    "- State the prediction direction by the sign of `effect`.\n"
                    "- Be explicit about which parameter values are assumptions; the "
                    "explanation goes into `design`.\n\n"
                    "DESIGN TYPE - choose one:\n"
                    "* \"one_shot\" (default): the hypothesis is about the world, e.g. \"X "
                    "raises Y\". Each replication draws one dataset and estimates the "
                    "effect.\n"
                    "* \"meta\": the hypothesis is about a statistical procedure itself - "
                    "its power, its bias, the coverage of its confidence interval, its "
                    "false-positive rate. One dataset says nothing about that: each "
                    "replication runs `trials` inner studies over a grid of sample "
                    "sizes, and the prediction is a threshold on that summary.\n"
                    "  For meta set: design_type=\"meta\", metric_kind (power|bias|coverage), "
                    "trials (integer 50..200000), grid (increasing sample sizes, 1..6 "
                    "values, each >= 10), threshold (the predicted value of the metric "
                    "at n; a proportion for power/coverage, a tolerance for bias) and "
                    "comparison (\"at_least\" or \"at_most\"). `n` MUST be one of the grid "
                    "values: it is the cell the prediction talks about.\n"
                    "  Example: \"power at n=200 is at least 0.6 for d=0.3\" -> n=200, "
                    "grid=[100,200,400], threshold=0.6, comparison=\"at_least\", "
                    "metric_kind=\"power\", trials=2000.\n\n"
                    "Return JSON: {\"designable\": true|false, \"reason\": \"...\", "
                    "\"protocol\": {\"claim\": \"...\", \"prediction\": \"...\", "
                    "\"falsification\": \"...\", \"design\": \"...\", \"population\": \"...\", "
                    "\"n\": 500, \"effect\": 0.3, \"noise\": 1.0, \"metric\": \"...\", "
                    "\"test\": \"...\", \"alpha\": 0.05, \"seed\": 12345, "
                    "\"replications\": " + str(replications) + ", "
                    "\"design_type\": \"one_shot|meta\", \"metric_kind\": \"\", "
                    "\"trials\": 0, \"grid\": [], \"threshold\": 0.0, "
                    "\"comparison\": \"at_least\"}}"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"HYPOTHESIS: {hypothesis.get('claim', '')}\n"
                    f"PREDICTIONS: {hypothesis.get('predictions', '[]')}\n"
                    f"FALSIFICATION CONDITIONS: {hypothesis.get('falsification_conditions', '[]')}\n"
                    f"CONFIDENCE: {hypothesis.get('confidence', 0.5)}"
                ),
            },
        ]
        try:
            reply = await self.llm.chat_json(messages, temperature=0.2, max_tokens=900)
        except Exception as exc:  # noqa: BLE001 - a failed design must not break a cycle
            logger.warning(f"Experiment design failed: {exc}")
            return None
        if not isinstance(reply, dict):
            return None
        if reply.get("designable") is False:
            logger.info(f"Hypothesis not simulatable: {str(reply.get('reason'))[:140]}")
            return None

        protocol = ExperimentProtocol.from_dict(
            reply.get("protocol") or reply, hypothesis_id=hypothesis.get("id", "")
        )
        if protocol is None:
            return None
        if not protocol.claim:
            protocol.claim = (hypothesis.get("claim") or "")[:400]
        protocol.hypothesis_id = hypothesis.get("id", "") or protocol.hypothesis_id
        # The lab's replication count wins: the protocol may not quietly drop to
        # a single run, because a single run proves nothing.
        protocol.replications = replications
        ok, reason = protocol.validate()
        if not ok:
            logger.info(f"Rejected experiment protocol: {reason}")
            return None
        return protocol
