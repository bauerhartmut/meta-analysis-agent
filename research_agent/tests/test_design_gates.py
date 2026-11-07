"""Tests fuer ``research_agent.meta.design_gates``.

Die beiden echten Faelle aus dem SOL-Korpus stehen im Mittelpunkt; dazu die
Gegenproben, die zeigen, dass das Gate nicht zu breit greift.
"""

from __future__ import annotations

from research_agent.meta.design_gates import (
    POOLED_REASON,
    PREDICTOR_REASON,
    design_violation,
    pooled_violation,
    predictor_violation,
)

# Table 3 "Meta-analysis of PSG of rTMS vs. Sham rTMS" (10.3389/fnins.2026.1816963)
POOLED_HEADER = ["Domain", "n", "No. of participants", "MD [95%CI]", "I 2 (%)", "p Value"]

# Table 2 "Predictors at Baseline for Better Sleep Quality" (10.2147/nss.s460882)
PREDICTOR_HEADER = ["N = 47 Variables",
                    "A Better Outcome (n = 24) Univariate p",
                    "A Better Outcome (n = 24) Multivariate Effect Size OR (95% CI)",
                    "p"]

# Gegenprobe: adjustierte Differenz in einer Tabelle mit Baseline-Spalten
JSR_HEADER = ["", "Control group N", "Control group Baseline Mean (SD)",
              "Control group 6 months Mean (SD)", "Intervention group N",
              "Intervention group Baseline Mean (SD)", "Intervention group 6 months Mean (SD)",
              "Adjusted mean difference between groups Beta (95% CI)"]

# Gegenprobe: Veraenderungswerte mit SE
CHANGE_HEADER = ["Sleep variable", "N (obs)", "Exercise change, Mean ( SE )",
                 "Control change, Mean ( SE )", "Main effect of trial * Mean difference (95% CI)"]


def test_metaanalyse_zeile_wird_erkannt():
    assert pooled_violation("Table 3 Meta-analysis of PSG of rTMS vs. Sham rTMS.",
                            POOLED_HEADER) == POOLED_REASON
    assert design_violation("Table 3. Polysomnographic Outcomes", POOLED_HEADER) == POOLED_REASON


def test_praediktortabelle_wird_erkannt():
    assert predictor_violation(
        "Table 2 Predictors at Baseline for Better Sleep Quality One Month After WMT in IBD",
        PREDICTOR_HEADER) == PREDICTOR_REASON


def test_adjustierte_differenz_bleibt_erlaubt():
    assert design_violation("TABLE 3 Sleep outcomes at baseline and after 6 months",
                            JSR_HEADER) == ""


def test_veraenderungswerte_bleiben_erlaubt():
    assert design_violation(
        "Table 2. Estimated marginal means and SEs of the pre-to-post change scores",
        CHANGE_HEADER) == ""


def test_overall_zeile_ohne_heterogenitaetsmass_bleibt_erlaubt():
    header = ["Subgroup", "Overall (95% CI)", "p"]
    assert pooled_violation("Table 2. Treatment effects by subgroup", header) == ""
