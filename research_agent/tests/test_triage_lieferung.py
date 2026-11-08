"""Tests fuer die Liefer-Triage: Dateiname, Einordnung, k-Stand, CSV-Abgleich."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "triage_lieferung",
    Path(__file__).resolve().parents[2] / "scripts" / "triage_lieferung.py")
_MOD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)


def test_pmid_aus_dateiname():
    assert _MOD.stamm_pmid("41122831.pdf") == "41122831"
    assert _MOD.stamm_pmid("PMID_33157425.pdf") == "33157425"
    assert _MOD.stamm_pmid("14566165-volltext.pdf") == "14566165"
    assert _MOD.stamm_pmid("probe_artikel_1.pdf") is None


def test_dateiname_ohne_pmid_bleibt_fremd():
    assert _MOD.stamm_pmid("") is None


def test_scan_wird_als_scan_erkannt():
    doc = {"file": "x.pdf", "chars": 0, "error": "kein Textlayer"}
    assert _MOD.triage_dokument(doc) == "scan"


def test_poolbare_zeile_gewinnt_gegen_alles_andere():
    doc = {"file": "x.pdf", "sol_rows": 1, "sol_poolable": 1,
           "arm_stored": 0, "direct_stored": 1}
    assert _MOD.triage_dokument(doc) == "poolbar"


def test_sol_zeile_ohne_speicherung_ist_leser_luecke():
    doc = {"file": "x.pdf", "sol_rows": 1, "sol_poolable": 0,
           "arm_stored": 0, "direct_stored": 0}
    assert _MOD.triage_dokument(doc) == "leser_luecke"


def test_endpunkt_nicht_berichtet_ist_kein_fehler():
    doc = {"file": "x.pdf", "sol_rows": 0, "sol_poolable": 0,
           "arm_candidates": 0, "direct_candidates": 0}
    assert _MOD.triage_dokument(doc) == "endpunkt_nicht_berichtet"


def test_abgelehnte_kandidaten_sind_ein_eigener_zustand():
    doc = {"file": "x.pdf", "sol_rows": 0, "sol_poolable": 0,
           "arm_candidates": 3, "direct_candidates": 1,
           "arm_stored": 0, "direct_stored": 0}
    assert _MOD.triage_dokument(doc) == "kandidaten_abgelehnt"


def test_k_stand_zaehlt_nur_poolbare_dateien():
    k = _MOD.k_stand(1, 1, 2)
    assert k == {"basis_k": 1, "zuwachs": 1, "k_neu": 2, "ziel": 2,
                 "erreicht": True, "fehlt_bis_ziel": 0}


def test_k_stand_ohne_zuwachs_bleibt_offen():
    k = _MOD.k_stand(1, 0, 2)
    assert k["k_neu"] == 1 and not k["erreicht"] and k["fehlt_bis_ziel"] == 1


def test_naechster_schritt_nennt_bei_ziel_kein_pooling_verbot():
    k = _MOD.k_stand(1, 1, 2)
    assert "poolen" in _MOD.naechster_schritt(k, ["poolbar"])
    k_offen = _MOD.k_stand(1, 0, 2)
    assert "Keine gepoolte Zahl" in _MOD.naechster_schritt(k_offen, ["scan"])


def test_tabellenzeile_schreibt_kein_none():
    scan = _MOD.tabellenzeile({"file": "scan.pdf", "pmid": None,
                               "prioritaet": "", "zustand": "scan",
                               "chars": 0, "error": "kein Textlayer",
                               "sol_rows": None, "sol_poolable": None})
    assert "None" not in scan
    assert scan.startswith("| scan.pdf | - | - | scan |")
    assert scan.rstrip().endswith("| - | - | - |")


def test_leere_lieferung_schreibt_bericht_und_meldet_2(tmp_path):
    """Ohne PDF bleibt k unveraendert, aber der Befund wird festgehalten."""
    pdf_dir = tmp_path / "volltext"
    pdf_dir.mkdir()
    out = tmp_path / "lieferung.json"
    rc = _MOD.main([
        "--dir", str(pdf_dir),
        "--work-dir", str(tmp_path / "work"),
        "--json", str(out),
        "--md", str(tmp_path / "lieferung.md"),
        "--erwartet", str(tmp_path / "keine.csv"),
        "--basis-k", "1",
    ])
    assert rc == 2
    bericht = json.loads(out.read_text(encoding="utf-8"))
    assert bericht["documents"] == []
    assert bericht["k"]["k_neu"] == 1
    assert bericht["k"]["erreicht"] is False
    assert "keine Lieferung eingetroffen" in bericht["naechster_schritt"]


def test_zugangsliste_wird_gelesen(tmp_path):
    path = tmp_path / "liste.csv"
    path.write_text(
        "prioritaet,pmid,doi,jahr,zeitschrift,titel" + chr(10)
        + "A,41122831,10.1/x,2026,Zeitschrift,Testtitel" + chr(10)
        + "B,22222222,10.1/y,2020,Zeitschrift,Anderer" + chr(10),
        encoding="utf-8")
    liste = _MOD.load_erwartet(path)
    assert set(liste) == {"41122831", "22222222"}
    assert liste["41122831"]["prioritaet"] == "A"
    assert liste["41122831"]["titel"] == "Testtitel"
    assert _MOD.load_erwartet(tmp_path / "fehlt.csv") == {}
