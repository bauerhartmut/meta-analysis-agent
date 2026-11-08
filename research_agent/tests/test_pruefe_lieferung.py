"""Tests fuer den Abgleich Triage-Bericht gegen die Schwellen-Erwartung."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "pruefe_lieferung",
    Path(__file__).resolve().parents[2] / "scripts" / "pruefe_lieferung.py")
_MOD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)


def _bericht(poolbar=1, scan=0, endpunkt=0, fehlend=None, k_neu=None):
    docs = []
    for _ in range(poolbar):
        docs.append({"file": "x.pdf", "zustand": "poolbar", "sol_rows": 1,
                     "sol_poolable": 1})
    for _ in range(scan):
        docs.append({"file": "s.pdf", "zustand": "scan", "error": "kein Textlayer"})
    for _ in range(endpunkt):
        docs.append({"file": "e.pdf", "zustand": "endpunkt_nicht_berichtet",
                     "sol_rows": 0, "sol_poolable": 0})
    return {
        "directory": "test",
        "pdfs": len(docs),
        "documents": docs,
        "k": {"basis_k": 1, "zuwachs": poolbar,
              "k_neu": poolbar + 1 if k_neu is None else k_neu,
              "ziel": 2, "erreicht": poolbar + 1 >= 2},
        "fehlend": fehlend or [],
        "fremd": [],
    }


def test_erwartungswert_und_nullrunde():
    e = _MOD.erwartung(5, 0.2)
    assert e["erwartet_poolbar"] == 1.0
    assert e["p_null_poolbar"] == round(0.8 ** 5, 3)


def test_erwartung_ohne_dokumente_ist_null():
    e = _MOD.erwartung(0, 0.2)
    assert e["erwartet_poolbar"] == 0.0 and e["p_null_poolbar"] == 1.0


def test_stimmiger_bericht_hat_keine_fehler():
    result = _MOD.pruefe(_bericht(poolbar=1, scan=1, endpunkt=1))
    assert result["fehler"] == 0
    assert result["kennzahlen"]["konsistent"] is True
    assert result["kennzahlen"]["k_neu"] == 2


def test_widerspruechliches_k_wird_als_fehler_gemeldet():
    result = _MOD.pruefe(_bericht(poolbar=1, k_neu=4))
    assert result["fehler"] == 1
    assert any("aus den Dateien folgt" in b["text"] for b in result["befunde"])


def test_verfehltes_ziel_ist_eine_abweichung():
    result = _MOD.pruefe(_bericht(poolbar=0, endpunkt=3))
    assert result["abweichungen"] >= 1
    assert any("Schritt-Ziel" in b["text"] for b in result["befunde"])


def test_ausbeute_ueber_der_annahme_ist_ein_hinweis():
    result = _MOD.pruefe(_bericht(poolbar=3, scan=1))
    assert any("ueber der Annahme" in b["text"] for b in result["befunde"])


def test_scan_und_fehlende_lieferung_werden_genannt():
    result = _MOD.pruefe(_bericht(poolbar=1, scan=1,
                                  fehlend=[{"pmid": "11292231"}]))
    texte = " ".join(b["text"] for b in result["befunde"])
    assert "ohne Textebene" in texte
    assert "11292231" in texte


def test_leere_lieferung_wird_als_leer_gemeldet():
    result = _MOD.pruefe({"documents": [], "pdfs": 0, "k": {},
                          "directory": "leer", "fehlend": [], "fremd": []})
    assert result["befunde"][0]["schwere"] == "leer"
    assert result["kennzahlen"]["pdfs"] == 0


def test_main_meldet_2_ohne_triage_bericht(tmp_path):
    rc = _MOD.main([
        "--bericht", str(tmp_path / "fehlt.json"),
        "--md", str(tmp_path / "p.md"),
        "--json", str(tmp_path / "p.json"),
    ])
    assert rc == 2
    daten = json.loads((tmp_path / "p.json").read_text(encoding="utf-8"))
    assert daten["kennzahlen"]["pdfs"] == 0
    assert "Keine PDF gelesen" in daten["befunde"][0]["text"]
    assert (tmp_path / "p.md").exists()


def test_main_meldet_0_bei_stimmigem_bericht(tmp_path):
    pfad = tmp_path / "lieferung.json"
    pfad.write_text(json.dumps(_bericht(poolbar=2)), encoding="utf-8")
    rc = _MOD.main(["--bericht", str(pfad),
                    "--md", str(tmp_path / "p.md"),
                    "--json", str(tmp_path / "p.json")])
    assert rc == 0
    daten = json.loads((tmp_path / "p.json").read_text(encoding="utf-8"))
    assert daten["kennzahlen"]["poolbar"] == 2
    assert daten["kennzahlen"]["k_neu"] == 3
