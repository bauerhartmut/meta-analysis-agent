"""Tests fuer den Scan-Generator: Bild-PDF ohne Textlayer, Pixelformat."""

from __future__ import annotations

import importlib.util
import io
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "make_scan_probe",
    Path(__file__).resolve().parents[2] / "scripts" / "make_scan_probe.py")
_MOD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)


def test_bild_pdf_hat_keinen_textlayer():
    from pypdf import PdfReader

    rgb = bytes([255, 255, 255] * (20 * 10))
    reader = PdfReader(io.BytesIO(_MOD.build_image_pdf(20, 10, rgb, 2.0)))

    assert len(reader.pages) == 1
    page = reader.pages[0]
    assert (page.extract_text() or "").strip() == ""
    assert len(page["/Resources"]["/XObject"]) == 1


class _FakeBitmap:
    def __init__(self, width, height, stride, data):
        self.width, self.height, self.stride = width, height, stride
        self.buffer = data


def test_bgra_wird_zu_rgb():
    width, height, rgb = _MOD.raster_rgb(_FakeBitmap(1, 1, 4, bytes([10, 20, 30, 255])))
    assert (width, height) == (1, 1)
    assert tuple(rgb) == (30, 20, 10)


def test_drei_byte_pixel_bleiben_unveraendert():
    _, _, rgb = _MOD.raster_rgb(_FakeBitmap(1, 1, 3, bytes([1, 2, 3])))
    assert tuple(rgb) == (1, 2, 3)
