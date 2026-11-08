"""PDF-Seiten als PNG rendern (pypdfium2 + stdlib, ohne Pillow).

Fuer die optische Kontrolle erzeugter Berichte: rendert jede Seite eines PDF
in eine PNG-Datei, damit man sie sich ansehen kann. PNG wird mit ``zlib``
geschrieben, weil Pillow in dieser Umgebung nicht installiert ist und fuer
diese Pruefung auch nicht gebraucht wird - pypdfium2 ist bereits vorhanden.

Aufruf:
    .venv/bin/python.exe scripts/render_pdf_pages.py <pdf> <zielordner> [--pages 1,2]
"""

from __future__ import annotations

import argparse
import struct
import sys
import zlib
from pathlib import Path


def write_png(path: Path, width: int, height: int, stride: int, buf: memoryview) -> None:
    """Pixelpuffer (RGB oder BGRA) zeilenweise als PNG schreiben.

    pypdfium2 liefert je nach Renderpfad 3 oder 4 Byte pro Pixel; die Breite
    des Puffers steht in ``stride``, also wird das Format daraus abgeleitet.
    """
    bpp = stride // width
    if bpp not in (3, 4):
        raise ValueError(f"unerwartetes Pixelformat: {bpp} Byte je Pixel")
    raw = bytearray()
    for y in range(height):
        line = buf[y * stride:y * stride + width * bpp]
        raw.append(0)  # Filtertyp "None"
        if bpp == 4:  # BGRA -> RGB
            rgb = bytearray(width * 3)
            rgb[0::3] = line[2::4]
            rgb[1::3] = line[1::4]
            rgb[2::3] = line[0::4]
            raw += rgb
        else:
            raw += line

    def chunk(kind: bytes, data: bytes) -> bytes:
        return (struct.pack(">I", len(data)) + kind + data
                + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))

    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(bytes(raw), 6))
           + chunk(b"IEND", b""))
    path.write_bytes(png)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("outdir")
    ap.add_argument("--pages", default="", help="z. B. 1,2 (leer = alle)")
    ap.add_argument("--scale", type=float, default=2.0)
    args = ap.parse_args(argv[1:])

    import pypdfium2 as pdfium

    pdf_path, outdir = Path(args.pdf), Path(args.outdir)
    if not pdf_path.is_file():
        print(f"PDF fehlt: {pdf_path}")
        return 2
    outdir.mkdir(parents=True, exist_ok=True)
    wanted = [int(p) for p in args.pages.split(",") if p.strip()]

    doc = pdfium.PdfDocument(str(pdf_path))
    total = len(doc)
    for i in range(total):
        if wanted and (i + 1) not in wanted:
            continue
        bitmap = doc[i].render(scale=args.scale)
        dst = outdir / f"{pdf_path.stem}_seite{i + 1}.png"
        write_png(dst, bitmap.width, bitmap.height, bitmap.stride, memoryview(bitmap.buffer))
        print(f"{dst}  {bitmap.width}x{bitmap.height}  {dst.stat().st_size} Bytes")
    doc.close()
    print(f"{total} Seite(n) in {pdf_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
