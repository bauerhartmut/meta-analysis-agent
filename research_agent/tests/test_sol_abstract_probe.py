"""Tests fuer ``scripts/sol_abstract_probe.py`` (Lauf 1 der SOL-Hypothese).

Geprueft wird die Auswahl der Stichprobe und das Einlesen des bestehenden
Korpus - beides ohne Netz. Die Anfragen selbst werden hier nicht getestet;
sie sind im Bericht mit Status und Trefferzahl belegt.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def _load():
    spec = importlib.util.spec_from_file_location(
        "sol_abstract_probe", SCRIPTS / "sol_abstract_probe.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


probe = _load()


def _result(name: str, hits: int, records: list[dict]) -> dict:
    return {"name": name, "hitCount": hits, "records": records}


def test_pick_zieht_q1_zuerst_und_zaehlt_jede_ablehnung():
    q1 = _result("Q1", 235, [
        {"pmcid": "PMC1", "doi": "10.1/a", "title": "", "year": "", "query": "Q1"},
        {"pmcid": "", "doi": "10.1/b", "title": "", "year": "", "query": "Q1"},
        {"pmcid": "PMC9", "doi": "10.1/c", "title": "", "year": "", "query": "Q1"},
    ])
    q2 = _result("Q2", 40, [
        {"pmcid": "PMC1", "doi": "10.1/a", "title": "", "year": "", "query": "Q2"},
        {"pmcid": "PMC2", "doi": "10.1/d", "title": "", "year": "", "query": "Q2"},
    ])

    picked, stats = probe.pick([q1, q2], {"PMC9"}, limit=10)

    assert [entry["pmcid"] for entry in picked] == ["PMC1", "PMC2"]
    assert [entry["query"] for entry in picked] == ["Q1", "Q2"]
    assert stats["Q1_ohne_pmcid"] == 1
    assert stats["Q1_dublette"] == 1
    assert stats["Q2_dublette"] == 1
    assert stats["stichprobe"] == 2


def test_pick_haelt_das_limit_ein_und_zaehlt_den_rest():
    records = [{"pmcid": f"PMC{i}", "doi": "", "title": "", "year": "", "query": "Q1"}
               for i in range(1, 6)]
    picked, stats = probe.pick([_result("Q1", 5, records)], set(), limit=3)

    assert len(picked) == 3
    assert stats["Q1_ueber_limit"] == 2
    assert stats["stichprobe"] == 3


def test_existing_pmcids_liest_manifest_und_vorhandene_xml(tmp_path):
    (tmp_path / "xml").mkdir()
    (tmp_path / "xml" / "PMC7.xml").write_text("<article/>", encoding="utf-8")
    (tmp_path / "manifest_all.json").write_text(
        json.dumps([{"pmc": "PMC7", "doi": "10.1/a"}, {"pmc": "PMC8", "doi": "10.1/b"}]),
        encoding="utf-8")

    seen = probe.existing_pmcids(tmp_path)

    assert seen == {"PMC7", "PMC8"}
