"""Aus einer PDF-Seite ein Bild-PDF ohne Textebene erzeugen (Scan-Attrappe).

Dient der Grenzpruefung: ein echtes Scan-PDF hat nur Pixel, keinen Text. Der
Bestand in ``data/origpdf`` enthaelt keinen einzigen Scan, deshalb wird hier
Seite 1 eines PDF gerastert und als PDF mit genau einem Bildobjekt
zurueckgeschrieben. Das Ergebnis ist fuer jeden Leser nicht von einem Scan zu
unterscheiden: es gibt keinen Textlayer, nur eine Zeichenanweisung.

Ohne Pillow: Pixel kommen aus pypdfium2, das Bild geht als rohe RGB-Daten mit
``/FlateDecode`` in ein von Hand gebautes PDF.

Aufruf:
    .venv/bin/python.exe scripts/make_scan_probe.py <quelle.pdf> <ziel.pdf> [--scale 2]
"""

from __future__ import annotations

import argparse
import sys
import zlib
from pathlib import Path


def raster_rgb(bitmap) -> tuple[int, int, bytes]:
    """Pixelpuffer von pypdfium2 in RGB bringen (3 oder 4 Byte je Pixel)."""
    width, height, stride = bitmap.width, bitmap.height, bitmap.stride
    bpp = stride // width
    buf = memoryview(bitmap.buffer)
    if bpp == 3:
        return width, height, bytes(buf[:height * stride])
    if bpp != 4:
        raise ValueError(f"unerwartetes Pixelformat: {bpp} Byte je Pixel")
    out = bytearray(width * height * 3)
    for y in range(height):  # BGRA -> RGB zeilenweise
        line = bytes(buf[y * stride:y * stride + width * 4])
        row = bytearray(width * 3)
        row[0::3] = line[2::4]
        row[1::3] = line[1::4]
        row[2::3] = line[0::4]
        out[y * width * 3:(y + 1) * width * 3] = row
    return width, height, bytes(out)


def build_image_pdf(width: int, height: int, rgb: bytes, scale: float) -> bytes:
    """Minimales PDF mit einer Seite und einem Bild, ohne jeden Text."""
    image = zlib.compress(rgb, 6)
    page_w, page_h = width / scale, height / scale
    content = (f"q {page_w:.2f} 0 0 {page_h:.2f} 0 0 cm /Im0 Do Q").encode("ascii")

    objects = [
        b"<</Type/Catalog/Pages 2 0 R>>",
        b"<</Type/Pages/Kids[3 0 R]/Count 1>>",
        (f"<</Type/Page/Parent 2 0 R/MediaBox[0 0 {page_w:.2f} {page_h:.2f}]"
         f"/Resources<</XObject<</Im0 4 0 R>>>>/Contents 5 0 R>>").encode("ascii"),
        (f"<</Type/XObject/Subtype/Image/Width {width}/Height {height}"
         f"/ColorSpace/DeviceRGB/BitsPerComponent 8/Filter/FlateDecode"
         f"/Length {len(image)}>>").encode("ascii") + b"\nstream\n" + image + b"\nendstream",
        (f"<</Length {len(content)}>>").encode("ascii") + b"\nstream\n" + content + b"\nendstream",
    ]

    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for num, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{num} 0 obj\n".encode("ascii") + body + b"\nendobj\n"

    xref_pos = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode("ascii")
    out += b"0000000000 65535 f \n"
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode("ascii")
    out += (f"trailer\n<</Size {len(objects) + 1}/Root 1 0 R>>\n"
            f"startxref\n{xref_pos}\n%%EOF\n").encode("ascii")
    return bytes(out)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("target")
    ap.add_argument("--scale", type=float, default=2.0)
    args = ap.parse_args(argv[1:])

    import pypdfium2 as pdfium

    source, target = Path(args.source), Path(args.target)
    if not source.is_file():
        print(f"Quelle fehlt: {source}")
        return 2

    doc = pdfium.PdfDocument(str(source))
    bitmap = doc[0].render(scale=args.scale)
    width, height, rgb = raster_rgb(bitmap)
    doc.close()

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(build_image_pdf(width, height, rgb, args.scale))
    print(f"{target}  {width}x{height} px  {target.stat().st_size} Bytes "
          f"(nur Bild, kein Textlayer)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
