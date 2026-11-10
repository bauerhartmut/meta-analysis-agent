"""Tests fuer die Kappa- und Konfliktlogik des Goldstandards."""

import pytest

from research_agent.goldstandard_kappa import (
    als_text, cohens_kappa, schluessel, vergleiche,
)


def effekt(outcome, effekt_wert, typ="hr", vergleich="Intervention vs Kontrolle", zeit=None):
    return {"outcome_normalized": outcome, "comparison_verbatim": vergleich,
            "effect_type": typ, "effect": effekt_wert, "ci_low": 0.8, "ci_high": 1.0,
            "time_point": zeit}


def test_kappa_perfekte_uebereinstimmung():
    assert cohens_kappa([1] * 8, [1] * 8) == 1.0
    assert cohens_kappa([0] * 8, [0] * 8) == 1.0


def test_kappa_disjunkt_ist_negativ_eins():
    assert cohens_kappa([1, 0] * 5, [0, 1] * 5) == pytest.approx(-1.0)


def test_kappa_gegenpol_ist_null():
    assert cohens_kappa([1] * 10, [0] * 10) == 0.0


def test_kappa_bekannter_wert():
    # po = 0,75; pe = 0,5 -> kappa = 0,5
    assert cohens_kappa([1, 1, 0, 0], [1, 0, 0, 0]) == pytest.approx(0.5)


def test_kappa_leer_ist_none():
    assert cohens_kappa([], []) is None


def test_kappa_ungleiche_laenge_ist_fehler():
    with pytest.raises(ValueError):
        cohens_kappa([1, 0], [1])


def test_schluessel_normalisiert():
    a = schluessel("d1", effekt("Fatigue  Score", 0.8))
    b = schluessel("d1", effekt(" fatigue score ", 0.8))
    assert a == b
    assert a[0] == "d1"


def test_vergleich_treffer_und_konflikte():
    a = {"d1": [effekt("Schmerz", 0.8), effekt("Fatigue", 0.5, typ="md")],
         "d2": [effekt("Rezidiv", 1.2)]}
    b = {"d1": [effekt("Schmerz", 0.8), effekt("Fatigue", 0.5, typ="smd")],
         "d2": [effekt("Mortalitaet", 0.9)]}
    r = vergleiche(a, b)
    assert r["n_dokumente"] == 2
    assert r["n_keys"] == 4
    assert r["treffer"] == 1
    assert len(r["typ_abweichung"]) == 1
    assert len(r["nur_a"]) == 1
    assert len(r["nur_b"]) == 1
    assert r["kappa_zeile"] == pytest.approx(-1 / 3)


def test_vergleich_wert_ausserhalb_toleranz():
    a = {"d1": [effekt("Schmerz", 0.80)]}
    b = {"d1": [effekt("Schmerz", 0.90)]}
    r = vergleiche(a, b)
    assert len(r["wert_abweichung"]) == 1
    assert r["treffer"] == 0


def test_vergleich_wert_innerhalb_toleranz():
    a = {"d1": [effekt("Schmerz", 0.800)]}
    b = {"d1": [effekt("Schmerz", 0.804)]}
    r = vergleiche(a, b, toleranz=0.01)
    assert r["treffer"] == 1
    assert not r["wert_abweichung"]


def test_leere_gerueste_ergeben_keine_annotation():
    r = vergleiche({"d1": [], "d2": []}, {"d1": [], "d2": []})
    assert r["n_keys"] == 0
    assert r["kappa_zeile"] is None
    assert r["kappa_dokument"] is None
    assert "Noch keine Annotation" in als_text(r)
