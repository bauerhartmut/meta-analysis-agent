"""Tests fuer den Abgleich Goldstandard gegen Pipeline."""

import pytest

from research_agent.goldstandard_abgleich import (
    aehnlichkeit, jaccard, matche, token, werte,
)


def gold(outcome, effekt_wert, typ="hr", vergleich="Intervention vs Kontrolle"):
    return {"outcome_normalized": outcome, "comparison_verbatim": vergleich,
            "effect_type": typ, "effect": effekt_wert}


def pipe(outcome, effekt_wert, typ="hr", vergleich="Intervention vs Kontrolle"):
    return {"outcome": outcome, "comparison": vergleich,
            "effect_type": typ, "effect": effekt_wert}


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
