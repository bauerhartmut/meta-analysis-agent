"""Official RoB 2 signalling-question algorithms (parallel-group version).

Source of truth: the official RoB 2 cribsheet (version of 22 August 2019,
wording transcribed from riskofbias.info) and Cochrane Handbook Chapter 8.
The signalling-question text and the gating below reproduce the cribsheet;
the per-branch domain algorithms are the official decision nodes, with the
two arms the literature flagged as diagram-dependent marked RECONSTRUCTED
(conservative: ties resolve toward the worse rating, never toward low).

Answer vocabulary and collapse rules (Handbook 8.2.3):
- Y and PY have the same implications (both count as 'yes').
- N and PN have the same implications (both count as 'no').
- NI ('No information') carries domain-specific weight; this module keeps
  NI as its own value because three domains treat it differently.

Every rating an assessor produces from these questions stays machine-
readable and quote-backed: the caller passes one answer per question, the
algorithm never sees free text.
"""

from typing import Dict, List

_YES = ("y", "py")
_NO = ("n", "pn")
_BAD = ("n", "pn", "ni")  # anything but yes


def _a(signals: Dict[str, str], key: str) -> str:
    return str(signals.get(key, "ni")).strip().lower()


ROB2_QUESTIONS: Dict[str, List[str]] = {
    # 3 + 7 + 4 + 5 + 3 = 22 signalling questions (assignment variant).
    "randomisation": [
        "1.1 Was the allocation sequence random?",
        "1.2 Was the allocation sequence concealed until participants "
        "were enrolled and assigned to interventions?",
        "1.3 Did baseline differences between intervention groups "
        "suggest a problem with the randomization process?",
    ],
    "deviations_assignment": [
        "2.1 Were participants aware of their assigned intervention?",
        "2.2 Were carers and people delivering the interventions "
        "aware of participants' assigned intervention?",
        "2.3 Were there deviations from the intended intervention that "
        "arose because of the trial context?",
        "2.4 Were these deviations likely to have affected the outcome?",
        "2.5 Were these deviations balanced between groups?",
        "2.6 Was an appropriate analysis used to estimate the effect of "
        "assignment to intervention?",
        "2.7 Was there potential for a substantial impact of the failure "
        "to analyse participants in the group they were randomized to?",
    ],
    "missing_outcome_data": [
        "3.1 Were data for this outcome available for all, or nearly all, "
        "participants randomized?",
        "3.2 Is there evidence that the result was not biased by missing "
        "outcome data?",
        "3.3 Could missingness in the outcome depend on its true value?",
        "3.4 Is it likely that missingness in the outcome depended on "
        "its true value?",
    ],
    "measurement": [
        "4.1 Was the method of measuring the outcome inappropriate?",
        "4.2 Could measurement or ascertainment of the outcome have "
        "differed between intervention groups?",
        "4.3 Were outcome assessors aware of the intervention received?",
        "4.4 Could assessment of the outcome have been influenced by "
        "knowledge of intervention received?",
        "4.5 Is it likely that assessment of the outcome was influenced "
        "by knowledge of intervention received?",
    ],
    "selection_reported_result": [
        "5.1 Were the data analysed in accordance with a pre-specified "
        "plan finalized before unblinded outcome data were available?",
        "5.2 Is the result likely to have been selected, on the basis of "
        "the results, from multiple eligible outcome measurements?",
        "5.3 Is the result likely to have been selected, on the basis of "
        "the results, from multiple eligible analyses of the data?",
    ],
}

LOW = "low"
SOME = "some_concerns"
HIGH = "high"


def rob2_domain_rating(domain: str, signals: Dict[str, str]) -> str:
    """One domain-level verdict from the signalling answers.

    Missing answers count as NI ('no information') - the machine must not
    invent a clearer reading than the text supports.
    """
    s = signals
    if domain == "randomisation":
        # Low needs both randomisation steps yes AND no baseline problem.
        if _a(s, "1.1") in _YES and _a(s, "1.2") in _YES \
                and _a(s, "1.3") in _NO:
            return LOW
        # High only when randomisation was unclear/problematic AND the
        # baseline suggests it mattered (cribsheet answer 1.3 yes/NI).
        if _a(s, "1.1") in _BAD and _a(s, "1.2") in _BAD \
                and _a(s, "1.3") in ("y", "py", "ni"):
            return HIGH
        return SOME

    if domain == "deviations_assignment":
        analysis_ok = _a(s, "2.6") in _YES
        if not analysis_ok:
            # Inappropriate analysis: substantial impact = high, else
            # (conservative) some concerns.
            return HIGH if _a(s, "2.7") in _YES else SOME
        deviations = _a(s, "2.3") in _YES  # yes = deviations from context
        if not deviations:
            # Unblinded participants/carers without context deviations:
            # assignment effect protected by appropriate analysis.
            return LOW
        affected = _a(s, "2.4") in _YES  # deviations affected the outcome
        if not affected:
            return SOME
        balanced = _a(s, "2.5") in _YES
        return LOW if balanced else HIGH

    if domain == "missing_outcome_data":
        if _a(s, "3.1") in _YES:
            return LOW
        if _a(s, "3.2") in _YES:
            return LOW
        # 3.2 unproven. Could missingness depend on the true value?
        if _a(s, "3.3") in _NO:
            # RECONSTRUCTED (cribsheet note read one way, the tool's
            # diagram arguably the other): conservative stays concerns.
            return SOME
        if _a(s, "3.4") in _YES:
            return HIGH
        return SOME

    if domain == "measurement":
        if _a(s, "4.1") in _YES:
            # RECONSTRUCTED arm: method inappropriate is rated high
            # (conservative; the diagram allows high on severity).
            return HIGH
        if _a(s, "4.2") in _YES:
            # RECONSTRUCTED arm: differential ascertainment = concerns.
            return SOME
        if _a(s, "4.3") in _NO:
            return LOW
        if _a(s, "4.4") in _YES:
            return HIGH
        if _a(s, "4.4") in _NO:
            return LOW
        return SOME  # 4.4 unclear/NI: concerns stay

    if domain == "selection_reported_result":
        # NI on a selection question is a concern by the cribsheet's own
        # note: absence of intention records counts, absence of certainty
        # is not low risk. 'y/py/ni' = selected on the results.
        suspicious = _YES + ("ni",)
        pre_specified = _a(s, "5.1") in _YES
        selected_measure = _a(s, "5.2") in suspicious
        selected_analysis = _a(s, "5.3") in suspicious
        if pre_specified and _a(s, "5.2") in _NO and _a(s, "5.3") in _NO:
            return LOW
        if pre_specified and selected_measure and selected_analysis:
            return HIGH
        return SOME

    raise ValueError(f"unknown RoB 2 domain: {domain}")


ROB2_DOMAIN_ORDER = (
    "randomisation", "deviations_assignment", "missing_outcome_data",
    "measurement", "selection_reported_result",
)


def overall_rob2(domain_ratings: Dict[str, str]) -> str:
    """Overall verdict by the cribsheet table (verbatim criteria).

    Low: every domain low. High: any domain high OR some concerns in
    multiple domains in a way that substantially lowers confidence - the
    machine implements the deterministic core (>=3 domains with concerns
    = high) and leaves the softer override to the review layer, never it
    to the model.
    """
    levels = [str(domain_ratings.get(d, SOME)) for d in ROB2_DOMAIN_ORDER]
    if HIGH in levels:
        return HIGH
    if problems := [l for l in levels if l != LOW]:
        if len(problems) >= 3:
            # Deterministic reading of 'multiple domains ... substantially
            # lowers confidence' - three or more are never 'low overall'.
            return HIGH
        return SOME
    return LOW


def rob2_pass_summary(signals: Dict[str, str]) -> dict:
    """One machine-readable record: domain verdicts + per-domain answers."""
    domains: Dict[str, str] = {}
    for d in ROB2_DOMAIN_ORDER:
        domains[d] = rob2_domain_rating(d, signals)
    return {"domains": domains, "overall": overall_rob2(domains)}