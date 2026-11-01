"""The lab: one hypothesis becomes a preregistered, executed, judged simulation.

Flow and why each step exists:

1. **Design** - a protocol with numbers, written down before any result exists.
2. **Write** - a script that implements that protocol, checked against an import
   allowlist and required to read its numbers from ``sim_params``.
3. **Review** - an independent critic reads the script *before* it runs.
4. **Smoke test** - the same script once at a tiny n, to prove it executes and
   prints the agreed result line. A wrong shape costs seconds, not a study.
5. **Run** - sandbox directory, timeout, blocked network, no secrets.
6. **Repair** - a failed smoke test or run goes back to the writer with the
   actual error, instead of being retried blindly on the next cycle.
7. **Audit** - after the run, does the script test the prediction?
8. **Judge** - deterministic verdict from replication rate, direction,
   sensitivity and alpha.

Everything is persisted as it happens (``experiments``), so a crash mid-run
leaves a diagnosable record instead of a lost experiment.
"""

import json
import logging
from typing import Optional, Tuple

from ..models import gen_id, now_iso
from .coder import SimulationWriter
from .designer import ExperimentDesigner
from .interpreter import (
    SIMULATION_EVIDENCE_CAP, audit_script, interpret, merge_reviews,
)
from .review import ScriptReviewer
from .runner import ScriptRunner
from .validity import KnownAnswerTest

logger = logging.getLogger(__name__)


class SimulationLab:
    def __init__(
        self,
        db,
        llm,
        base_dir: str = "data/simulations",
        timeout: float = 180.0,
        cap: float = SIMULATION_EVIDENCE_CAP,
        replications: int = 5,
        max_attempts: int = 3,
        smoke_n: int = 30,
        smoke_timeout: float = 45.0,
        kat_enabled: bool = True,
        kat_trials: int = 400,
        designer: Optional[ExperimentDesigner] = None,
        writer: Optional[SimulationWriter] = None,
        runner: Optional[ScriptRunner] = None,
        reviewer: Optional[ScriptReviewer] = None,
        validity: Optional[KnownAnswerTest] = None,
    ):
        self.db = db
        self.llm = llm
        self.cap = float(cap or SIMULATION_EVIDENCE_CAP)
        # One run at one seed proves nothing: every protocol asks for repeated
        # studies with fresh noise, and the verdict is driven by how many hold.
        self.replications = max(3, int(replications or 5))
        # How many candidate scripts may be written for one experiment. Each
        # attempt costs a review and a smoke test, so the budget is small; the
        # point is that a script is repaired with its error, not retried blindly.
        self.max_attempts = max(1, int(max_attempts or 1))
        self.smoke_n = max(5, int(smoke_n or 30))
        self.smoke_timeout = float(smoke_timeout or 45.0)
        self.designer = designer or ExperimentDesigner(llm)
        self.writer = writer or SimulationWriter(llm)
        self.runner = runner or ScriptRunner(base_dir=base_dir, timeout=timeout)
        self.reviewer = reviewer or ScriptReviewer(llm)
        # Known-answer checks: the routine is compared against theory before its
        # result can become evidence.
        if validity is not None:
            self.validity = validity
        elif kat_enabled:
            self.validity = KnownAnswerTest(self.runner, trials=kat_trials)
        else:
            self.validity = None

    async def _prepare_script(
        self, experiment_id: str, protocol
    ) -> Tuple[int, Optional[str], dict, Optional[dict], str]:
        """Write, review, smoke-test and run a script, repairing what fails.

        Returns ``(attempts, code, review, run, error)`` with ``run is None``
        when no candidate produced a usable result. Each failed step feeds its
        own message back into the next draft: the dry-run traceback, a
        reviewer's objections, or the error of the real run. Retrying blind is
        what produced experiments that failed the same way twice.
        """
        feedback = ""
        errors = []
        best: Optional[Tuple[str, dict]] = None
        params = self.runner.protocol_params(protocol)

        for attempt in range(1, self.max_attempts + 1):
            code, error = await self.writer.write(protocol, feedback=feedback)
            if not code:
                last_error = error or "the model returned no code"
                errors.append(last_error)
                feedback = last_error
                logger.warning(
                    f"Experiment {experiment_id[:8]}: no script on attempt {attempt} "
                    f"({last_error[:100]})"
                )
                continue

            smoke = await self.runner.smoke_test(
                experiment_id, protocol, code,
                n=self.smoke_n, timeout=self.smoke_timeout,
            )
            if not smoke.get("ok"):
                last_error = f"the smoke test failed: {smoke.get('error', '')}"
                errors.append(last_error)
                feedback = last_error + "\n" + str(smoke.get("stderr") or "")[-800:]
                logger.info(
                    f"Experiment {experiment_id[:8]}: smoke test failed on attempt "
                    f"{attempt} - {last_error[:120]}"
                )
                continue

            if self.validity is not None:
                checks = await self.validity.run(experiment_id, protocol, code)
                self.db.update_experiment(experiment_id, {
                    "validity": checks.to_json(), "updated_at": now_iso(),
                })
                if not checks.passed:
                    last_error = "the known-answer test failed: " + "; ".join(
                        checks.failures
                    )
                    errors.append(last_error)
                    feedback = (
                        last_error
                        + "\nFix the routine itself: with no effect the test must "
                        "reject about ALPHA of the time, the metric must move with "
                        "the effect, and a fixed seed must give the same numbers. "
                        "Do not special-case the known answer."
                    )
                    logger.info(
                        f"Experiment {experiment_id[:8]}: known-answer test failed "
                        f"on attempt {attempt} - {last_error[:140]}"
                    )
                    continue

            review = await self.reviewer.review(
                protocol, code, smoke, params=self.runner.protocol_params(
                    protocol, n=self.smoke_n, replications=1, smoke=True
                ),
            )
            best = (code, review)
            if not review.get("approved") and attempt < self.max_attempts:
                last_error = "the reviewer rejected the script: " + "; ".join(
                    review.get("problems") or []
                )
                errors.append(last_error)
                feedback = (
                    last_error
                    + "\nFix exactly these points; keep everything the reviewer "
                    "did not object to."
                )
                logger.info(
                    f"Experiment {experiment_id[:8]}: reviewer rejected attempt "
                    f"{attempt} - {last_error[:140]}"
                )
                continue

            self.db.update_experiment(experiment_id, {
                "status": "running", "script": code, "updated_at": now_iso(),
            })
            run = await self.runner.run_async(experiment_id, code, params)
            if run.get("ok"):
                return attempt, code, review, run, ""
            last_error = f"the run failed: {run.get('error', '')}"
            errors.append(last_error)
            feedback = last_error + "\n" + str(run.get("stderr") or "")[-800:]
            logger.info(
                f"Experiment {experiment_id[:8]}: run failed on attempt {attempt} "
                f"- {last_error[:120]}"
            )

        # The reviewer never approved, but a candidate passed the smoke test:
        # run it rather than throw the work away. Its objections reach the
        # verdict through merge_reviews, so the evidence carries the doubt.
        if best is not None:
            code, review = best
            self.db.update_experiment(experiment_id, {
                "status": "running", "script": code, "updated_at": now_iso(),
            })
            run = await self.runner.run_async(experiment_id, code, params)
            if run.get("ok"):
                return self.max_attempts, code, review, run, ""
            errors.append(f"the run failed: {run.get('error', '')}")

        # Report the most informative failure, not whichever came last.
        summary = " | ".join(dict.fromkeys(errors[-3:])) if errors else "no attempt produced a script"
        return self.max_attempts, None, {}, None, summary

    async def run(self, hypothesis: dict, topic: str = "") -> dict:
        """Design, run and judge one simulation. Returns a handler-style outcome."""
        if not hypothesis or not hypothesis.get("id"):
            return {"ok": True, "note": "hypothesis no longer exists", "evidence": None}

        experiment_id = gen_id()
        created = now_iso()
        record = {
            "id": experiment_id,
            "topic": topic,
            "hypothesis_id": hypothesis["id"],
            "claim": (hypothesis.get("claim") or "")[:500],
            "status": "designing",
            "created_at": created,
            "updated_at": created,
        }
        self.db.save_experiment(record)

        protocol = await self.designer.design(
            hypothesis, replications=self.replications
        )
        if protocol is None:
            self.db.update_experiment(experiment_id, {
                "status": "not_testable",
                "error": "no simulatable prediction",
                "updated_at": now_iso(),
            })
            return {
                "ok": True,
                "note": "not simulatable (no measurable prediction)",
                "evidence": None,
                "experiment_id": experiment_id,
            }

        self.db.update_experiment(experiment_id, {
            "status": "designed",
            "claim": protocol.claim[:500],
            "prediction": protocol.prediction[:500],
            "falsification": protocol.falsification[:500],
            "protocol": protocol.to_json(),
            "design_type": str(getattr(protocol, "design_type", "one_shot")),
            "updated_at": now_iso(),
        })

        attempts, code, review, run, error = await self._prepare_script(
            experiment_id, protocol
        )
        if run is None:
            self.db.update_experiment(experiment_id, {
                "status": "failed",
                "attempts": attempts,
                "error": f"no runnable script: {error}"[:500],
                "updated_at": now_iso(),
            })
            return {"ok": False, "note": f"no runnable script: {error}"[:200],
                    "evidence": None, "experiment_id": experiment_id}

        audit = merge_reviews(review, await audit_script(
            self.llm, protocol, code, run["result"]
        ))
        verdict = interpret(protocol, run["result"], audit, cap=self.cap)

        self.db.update_experiment(experiment_id, {
            "status": "completed",
            "attempts": attempts,
            "script_path": run.get("script_path", ""),
            "script_sha256": run.get("script_sha256", ""),
            "exit_code": int(run.get("exit_code") or 0),
            "duration_s": float(run.get("duration_s") or 0.0),
            "result": json.dumps(run["result"], ensure_ascii=False),
            "audit": json.dumps(audit, ensure_ascii=False),
            "verdict": verdict.evidence_type,
            "replication_rate": float(verdict.replication_rate or 0.0),
            "deviations": json.dumps(verdict.deviations, ensure_ascii=False),
            "sensitivity": json.dumps(verdict.sensitivity, ensure_ascii=False),
            "updated_at": now_iso(),
        })

        evidence = {
            "id": gen_id(),
            "hypothesis_id": hypothesis["id"],
            "source_id": "",
            "evidence_type": verdict.evidence_type,
            "content": verdict.reasoning[:1000],
            "strength": verdict.strength,
            "date_added": now_iso(),
            "experiment_id": experiment_id,
        }
        logger.info(
            f"Simulation {experiment_id[:8]} -> {verdict.evidence_type} "
            f"(replicated {verdict.replication_rate:.0%}, strength "
            f"{verdict.strength:.2f}, {run.get('duration_s', 0):.1f}s): "
            f"{verdict.reasoning[:140]}"
        )
        return {
            "ok": True,
            "note": (
                f"simulation {verdict.evidence_type} "
                f"({verdict.replication_rate:.0%} of replications significant, "
                f"strength {verdict.strength:.2f}"
                + (f", {len(verdict.deviations)} protocol deviation(s)"
                   if verdict.deviations else "")
                + ")"
            ),
            "evidence": evidence,
            "experiment_id": experiment_id,
        }
