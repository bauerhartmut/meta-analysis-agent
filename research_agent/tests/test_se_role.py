"""Tests fuer die Streuungsart einer Zelle in ``parse_mean_spread``.

Hintergrund: Ein Kopf ``Placebo ( n = 35), mean +- SE`` wurde als
Standardabweichung gelesen, weil der Zweig fuer ``Wert +- Wert`` die Art
unbedingt auf ``sd`` setzte. Die Rolle aus dem Spaltenkopf war bekannt und wurde
verworfen - g war dadurch um ein Vielfaches zu gross.
"""

from __future__ import annotations

import pytest

from research_agent.meta.arm_level import arms_from_row, parse_mean_spread

SE_HEADER = ["Particulars", "Placebo ( n = 35), mean \u00b1 SE",
             "VE ( n = 37), mean \u00b1 SE"]
SE_ROW = ["Sleep latency (min)", "74.26 \u00b1 5.24", "89.39 \u00b1 8.20"]


def test_plus_minus_mit_se_rolle_ist_ein_standardfehler():
    assert parse_mean_spread("74.26 \u00b1 5.24", role="se") == (74.26, 5.24, "se")


def test_plus_minus_ohne_etikett_bleibt_sd():
    assert parse_mean_spread("15.6 \u00b1 16.0") == (15.6, 16.0, "sd")


def test_sd_im_text_schlaegt_die_se_rolle():
    assert parse_mean_spread("15.6 \u00b1 16.0 (SD)", role="se")[2] == "sd"


def test_ci_rolle_macht_aus_plus_minus_kein_intervall():
    assert parse_mean_spread("74.26 \u00b1 5.24", role="ci") is None


def test_arm_aus_kopf_mean_se_rechnet_sd_aus_dem_standardfehler():
    arms, reason = arms_from_row(SE_HEADER, SE_ROW)

    assert reason == ""
    assert [arm.sd_source for arm in arms] == ["se", "se"]
    assert arms[0].sd == pytest.approx(5.24 * 35 ** 0.5, rel=1e-6)
