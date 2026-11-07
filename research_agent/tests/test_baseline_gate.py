"""Tests fuer ``scripts/measure_baseline_gate.py``.

Geprueft werden die beiden Muster, mit denen die Messung arbeitet, und die
Zuordnung Zeile -> Tabelle ueber das gespeicherte Zitat. Kein Netz, kein Modell.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def _load():
    spec = importlib.util.spec_from_file_location(
        "measure_baseline_gate", SCRIPTS / "measure_baseline_gate.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


measure = _load()


def test_baseline_caption_erkennt_ausgangslagentabellen():
    assert measure.BASELINE_CAPTION.search(
        "Table 1 Baseline demographics summary of study participants")
    assert measure.BASELINE_CAPTION.search(
        "Table 1. Demographic Characteristics of Participants.")
    assert not measure.BASELINE_CAPTION.search(
        "Table 2. Sleep as measured by polysomnography")


def test_se_kopf_wird_nur_ohne_sd_als_se_gezaehlt():
    se_head = "Particulars | Placebo ( n = 35), mean \u00b1 SE | VE ( n = 37), mean \u00b1 SE"
    sd_head = "Variable | Melatonin Mean (SD) | Placebo Mean (SD)"

    assert measure.SE_HEADER.search(se_head) and not measure.SD_HEADER.search(se_head)
    assert not (measure.SE_HEADER.search(sd_head) and not measure.SD_HEADER.search(sd_head))


def test_norm_entfernt_zeilenumbrueche_und_doppelte_leerzeichen():
    assert measure._norm("  a |\n b\t c ") == "a | b c"
