"""Tests fuer den Abgleich Goldstandard gegen Pipeline."""

import pytest

from research_agent.goldstandard_abgleich import (
    aehnlichkeit, dedupe, ist_poolbar, jaccard, matche, token, werte,
)


def gold(outcome, effekt_wert, typ="hr", vergleich="Intervention vs Kontrolle"):
    return {"outcome_normalized": outcome, "comparison_verbatim": vergleich,
            "effect_type": typ, "effect": effekt_wert}


def pipe(outcome, effekt_wert, typ="hr", vergleich="Intervention vs Kontrolle",
         se=None, ci_low=None, ci_high=None, quote_start=0, quote="",
         disputed=0, rejection_reason=""):
    return {"outcome": outcome, "comparison": vergleich,
            "effect_type": typ, "effect": effekt_wert,
            "se": se, "ci_low": ci_low, "ci_high": ci_high,
            "quote": quote, "quote_start": quote_start, "disputed": disputed,
            "rejection_reason": rejection_reason}


def test_token_entfernt_stoppwoerter():
    assert token("Risk of depressive symptoms in patients") == {"depressive", "symptoms"}


def test_jaccard_identisch_und_leer():
    assert jaccard({"a", "b"}, {"a", "b"}) == 1.0
    assert jaccard(set(), {"a"}) == 0.0


def test_aehnlichkeit_hoch_bei_gleicher_zeile():
    s = aehnlichkeit(gold("cancer recurrence", 0.83), pipe("cancer recurrence", 0.83))
    assert s == pytest.approx(1.0)


def test_aehnlichkeit_niedrig_bei_anderem_outcome():
    s = aehnlichkeit(gold("cancer recurrence", 0.83), pipe("sleep quality", 0.83))
    assert s < 0.55


def test_matche_paart_bestes_paar_zuerst():
    g = [gold("cancer recurrence", 0.83), gold("fatigue", 0.5, typ="md")]
    p = [pipe("cancer recurrence", 0.83)]
    paare, nur_g, nur_p = matche(g, p)
    assert len(paare) == 1
    assert paare[0][1]["outcome_normalized"] == "cancer recurrence"
    assert len(nur_g) == 1
    assert not nur_p


def test_matche_keine_doppelzuweisung():
    g = [gold("cancer recurrence", 0.83), gold("cancer recurrence", 0.83)]
    p = [pipe("cancer recurrence", 0.83)]
    paare, nur_g, _ = matche(g, p)
    assert len(paare) == 1
    assert len(nur_g) == 1


def test_werte_precision_recall_und_typquote():
    docs = [{"document_id": "d1", "stratum": "rct"}]
    g = {"d1": [gold("cancer recurrence", 0.83), gold("fatigue", 0.5, typ="md")]}
    p = {"d1": [pipe("cancer recurrence", 0.83, typ="or"), pipe("sleep quality", 1.2)]}
    r = werte(g, p, docs, annotiert={"d1"})
    s = r["gesamt"]
    assert (s["tp"], s["fp"], s["fn"]) == (1, 1, 1)
    assert s["precision"] == pytest.approx(0.5)
    assert s["recall"] == pytest.approx(0.5)
    assert s["typquote"] == 0.0
    assert s["wertquote"] == 1.0


def test_werte_laesst_offene_dokumente_aus():
    docs = [{"document_id": "d1", "stratum": "rct"},
            {"document_id": "d2", "stratum": "cohort"}]
    g = {"d1": [gold("cancer recurrence", 0.83)]}
    p = {"d1": [pipe("cancer recurrence", 0.83)],
         "d2": [pipe("irgendwas", 1.0)]}
    r = werte(g, p, docs, annotiert={"d1"})
    assert r["gesamt"]["n_annotiert"] == 1
    assert r["gesamt"]["n_offen"] == 1
    assert r["gesamt"]["fp"] == 0
    assert r["gesamt"]["precision"] == pytest.approx(1.0)


def test_werte_negativkontrolle_zaehlt_pipeline_als_falsch_positiv():
    docs = [{"document_id": "d1", "stratum": "negative_control"}]
    r = werte({}, {"d1": [pipe("irgendwas", 1.0)]}, docs, annotiert={"d1"})
    assert r["gesamt"]["fp"] == 1
    assert r["gesamt"]["tp"] == 0
    assert r["gesamt"]["precision"] == 0.0


def test_werte_ohne_annotation():
    docs = [{"document_id": "d1", "stratum": "rct"}]
    r = werte({}, {"d1": [pipe("irgendwas", 1.0)]}, docs, annotiert=set())
    assert r["gesamt"]["n_annotiert"] == 0
    assert r["gesamt"]["n_offen"] == 1
    assert r["gesamt"]["precision"] is None
    assert r["gesamt"]["recall"] is None
    assert r["gesamt"]["poolbare_quote"] is None
    assert r["gesamt"]["ausbeute_poolbar"] is None


def test_poolbar_mit_se_oder_ki():
    assert ist_poolbar(pipe("x", 1.0, se=0.1))
    assert ist_poolbar(pipe("x", 1.0, ci_low=0.8, ci_high=1.2))


def test_nicht_poolbar_ohne_praezision():
    assert not ist_poolbar(pipe("x", 1.0))


def test_nicht_poolbar_ohne_zitatspan():
    assert not ist_poolbar(pipe("x", 1.0, se=0.1, quote_start=-1))


def test_nicht_poolbar_disputed_oder_verworfen():
    assert not ist_poolbar(pipe("x", 1.0, se=0.1, disputed=1))
    assert not ist_poolbar(pipe("x", 1.0, se=0.1, rejection_reason="kein Effektwert"))


def test_poolbare_quote_und_ausbeute():
    docs = [{"document_id": "d1", "stratum": "rct"},
            {"document_id": "d2", "stratum": "rct"}]
    g = {"d1": [gold("cancer recurrence", 0.83)], "d2": []}
    p = {"d1": [pipe("cancer recurrence", 0.83, se=0.1),
                pipe("fatigue", 0.5, typ="md")],
         "d2": [pipe("schmerz", 1.1, se=0.2)]}
    r = werte(g, p, docs, annotiert={"d1", "d2"})
    s = r["gesamt"]
    assert s["pipeline_zeilen_annotiert"] == 3
    assert s["poolbar"] == 2
    assert s["poolbare_quote"] == pytest.approx(2 / 3)
    assert s["ausbeute_poolbar"] == pytest.approx(1.0)
    assert s["zeilen_pro_dokument"] == pytest.approx(1.5)
    assert s["poolbar_tp"] == 1
    assert s["poolbare_quote_tp"] == pytest.approx(1.0)


def test_dedupe_entfernt_wert_zwilling():
    behalten, duplikate = dedupe([pipe("x", 1.0, se=0.1), pipe("x", 1.0, se=0.1)])
    assert len(behalten) == 1
    assert duplikate == 1


def test_dedupe_entfernt_zitat_zwilling_auch_bei_anderem_wert():
    behalten, duplikate = dedupe([
        pipe("x", 1.0, se=0.1, quote="Risk 1.0 (0.8-1.2)"),
        pipe("y", 2.0, se=0.2, quote="Risk  1.0 (0.8-1.2)"),
    ])
    assert len(behalten) == 1
    assert duplikate == 1


def test_dedupe_ohne_beleg_verwirft_nichts():
    behalten, duplikate = dedupe([pipe("x", 1.0), pipe("y", 2.0)])
    assert len(behalten) == 2
    assert duplikate == 0


def test_ausbeute_unique_entfernt_doppelzeilen():
    docs = [{"document_id": "d1", "stratum": "rct"},
            {"document_id": "d2", "stratum": "rct"}]
    p = {"d1": [pipe("x", 1.0, se=0.1), pipe("x", 1.0, se=0.1),
                pipe("y", 2.0, se=0.2)],
         "d2": [pipe("z", 3.0, se=0.3)]}
    r = werte({"d1": [], "d2": []}, p, docs, annotiert={"d1", "d2"})
    s = r["gesamt"]
    assert s["pipeline_zeilen_annotiert"] == 4
    assert s["unique"] == 3
    assert s["duplikate"] == 1
    assert s["ausbeute_poolbar"] == pytest.approx(2.0)
    assert s["ausbeute_poolbar_unique"] == pytest.approx(1.5)
    assert s["duplikatquote"] == pytest.approx(0.25)


def test_baseline_duplikate_auch_ohne_annotation():
    docs = [{"document_id": "d1", "stratum": "rct"}]
    p = {"d1": [pipe("x", 1.0, se=0.1), pipe("x", 1.0, se=0.1)]}
    r = werte({}, p, docs, annotiert=set())
    s = r["gesamt"]
    assert s["pipeline_zeilen"] == 2
    assert s["pipeline_unique"] == 1
    assert s["pipeline_duplikate"] == 1
    assert s["baseline_duplikatquote"] == pytest.approx(0.5)
    assert s["ausbeute_poolbar_unique"] is None


def test_ausbeute_nur_annotierte_dokumente():
    docs = [{"document_id": "d1", "stratum": "rct"},
            {"document_id": "d2", "stratum": "rct"}]
    r = werte({"d1": []}, {"d1": [pipe("x", 1.0, se=0.1)],
                           "d2": [pipe("y", 1.0, se=0.1)]},
              docs, annotiert={"d1"})
    assert r["gesamt"]["pipeline_zeilen"] == 2
    assert r["gesamt"]["pipeline_zeilen_annotiert"] == 1
    assert r["gesamt"]["ausbeute_poolbar"] == pytest.approx(1.0)
