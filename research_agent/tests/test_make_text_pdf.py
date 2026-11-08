"""Tests fuer den Text-PDF-Generator (Probelauf der Kette)."""

from __future__ import annotations

import importlib.util
import io
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "make_text_pdf",
    Path(__file__).resolve().parents[2] / "scripts" / "make_text_pdf.py")
_MOD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)


def test_text_pdf_traegt_texlayer():
    from pypdf import PdfReader

    data = _MOD.build_text_pdf(["Sleep onset latency was 18.3 +- 7.2 min."])
    text = PdfReader(io.BytesIO(data)).pages[0].extract_text()
    assert "Sleep onset latency" in text


def test_klammern_werden_escaped():
    data = _MOD.build_text_pdf(["Wert (SD 7.2) und (n = 20)"])
    from pypdf import PdfReader

    text = PdfReader(io.BytesIO(data)).pages[0].extract_text()
    assert "(SD 7.2)" in text


def test_zu_viele_zeilen_wirft_fehler():
    with pytest.raises(ValueError):
        _MOD.build_text_pdf(["x"] * (_MOD.MAX_LINES + 1))
