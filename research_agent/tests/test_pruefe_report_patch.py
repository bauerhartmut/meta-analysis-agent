"""Tests fuer das Pruefskript der geschuetzten Report-Datei.

Die geschuetzte Datei selbst wird nicht getestet (sie ist gitignored und in
einem frischen Klon nicht vorhanden). Getestet wird die Prueflogik: Sie muss
fehlende Marker finden, nicht nur vorhandene bestaetigen.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

SKRIPT = Path(__file__).resolve().parents[2] / "scripts" / "pruefe_report_patch.py"


def _lade_skript():
    spec = importlib.util.spec_from_file_location("pruefe_report_patch", SKRIPT)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def test_marker_definition_deckt_die_wirkung_ab():
    modul = _lade_skript()
    dateien = {relativ: marker for relativ, marker in modul.CHECKS}

    assert "research_agent/report.py" in dateien
    assert 'group.get("single_cluster")' in dateien["research_agent/report.py"]
    assert "Kein Konfidenzintervall" in dateien["research_agent/report.py"]
    # Das Gate selbst und sein Aufruf gehoeren zum selben Nachweis.
    assert "research_agent/meta/pool_gates.py" in dateien
    assert "research_agent/meta/pooling.py" in dateien


def test_vollstaendiger_text_meldet_nichts():
    modul = _lade_skript()
    marker = ('group.get("single_cluster")', "Kein Konfidenzintervall")
    text = (
        'if pooled_enough and group.get("single_cluster"):\n'
        '    add("- **Kein Konfidenzintervall:** ...")\n'
    )

    assert modul.pruefe_text(text, marker) == []


def test_fehlender_hinweis_wird_gemeldet():
    modul = _lade_skript()
    marker = ('group.get("single_cluster")', "Kein Konfidenzintervall")
    text = 'if pooled_enough and group.get("single_cluster"):\n    pass\n'

    assert modul.pruefe_text(text, marker) == ["Kein Konfidenzintervall"]


def test_fehlender_zweig_wird_gemeldet():
    modul = _lade_skript()
    marker = ('group.get("single_cluster")', "Kein Konfidenzintervall")
    text = 'if pooled_enough:\n    add("- Kein Konfidenzintervall: ...")\n'

    assert modul.pruefe_text(text, marker) == ['group.get("single_cluster")']


def test_leerer_text_meldet_alle_marker():
    modul = _lade_skript()
    marker = ("a", "b", "c")

    assert modul.pruefe_text("", marker) == ["a", "b", "c"]


def test_alter_stand_wird_nicht_als_wirksam_gemeldet():
    """Der Zustand vor dem Patch darf nicht durchrutschen."""

    modul = _lade_skript()
    marker = ('group.get("single_cluster")', "Kein Konfidenzintervall")
    alt = (
        "for line in meta_pooling.forest_table(display):\n"
        "    add(line)\n"
        "add(\"\")\n"
        "if pooled_enough:\n"
        "    add(f\"- Gepoolter Effekt: {_meta_num(group.get('pooled'))}\")\n"
    )

    assert len(modul.pruefe_text(alt, marker)) == 2
