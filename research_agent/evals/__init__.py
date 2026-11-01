"""
Ground-Truth Quality Eval (Paket D).

Scoring package that measures how well the current knowledge base
(facts / hypotheses / evidence / synthesis reports) covers a golden set of
seed questions.

Entry point:
    python -m research_agent.evals.quality_eval [--db PATH] [--json PATH]

Programmatic use:
    from research_agent.evals.quality_eval import run_eval
"""