"""Markdown report -> PDF via Edge headless print-to-pdf.

build_report() asks for a PDF next to every markdown report, so a finished
agent run "publishes" its meta-analysis as a printable document. The
conversion is deliberately boring: python-markdown renders the report body,
one static HTML/CSS template styles it for print, and an installed Edge
(Windows ships one) prints it to PDF headlessly. No extra dependency apart
from the pure-python ``markdown`` package; if Edge cannot be found the export
fails softly - the markdown report stays the source of truth.
"""

import logging
import shutil
import subprocess
from pathlib import Path
logger = logging.getLogger(__name__)

_EDGE_CANDIDATES = (
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
)

_TEMPLATE = """<!DOCTYPE html>
<html lang="{lang}">
<head><meta charset="utf-8"><title>{title}</title>
<style>
  @page {{ size: A4; margin: 20mm 18mm; }}
  body {{ font-family: Georgia, 'Times New Roman', serif; font-size: 10.5pt;
         line-height: 1.45; color: #111; }}
  h1 {{ font-size: 19pt; margin: 0 0 6pt; }}
  h2 {{ font-size: 14pt; border-bottom: 1px solid #999; padding-bottom: 2pt;
       margin-top: 18pt; }}
  h3 {{ font-size: 12pt; margin-top: 14pt; }}
  table {{ border-collapse: collapse; width: 100%; margin: 6pt 0;
          font-size: 9pt; }}
  th, td {{ border: 1px solid #999; padding: 2.5pt 4pt; text-align: left;
           vertical-align: top; }}
  th {{ background: #eee; }}
  code {{ font-family: Consolas, monospace; font-size: 9pt; }}
  blockquote {{ border-left: 3px solid #bbb; margin-left: 0;
               padding-left: 8pt; color: #333; }}
  ul, ol {{ margin: 4pt 0; padding-left: 18pt; }}
  .meta {{ color: #555; font-size: 9pt; margin-bottom: 14pt;
          border-bottom: 1px solid #ccc; padding-bottom: 6pt; }}
  .avoid-break {{ page-break-inside: avoid; }}
</style></head>
<body>{body}</body></html>
"""


def _find_edge() -> str | None:
    for cand in _EDGE_CANDIDATES:
        p = Path(cand)
        if p.is_file():
            return str(p)
    found = shutil.which("msedge") or shutil.which("chrome")
    return found  # may be None -> caller reports a soft failure


def markdown_to_pdf(md_path: str | Path) -> str | None:
    """Render ``md_path`` next to itself as ``.pdf``; returns the pdf path
    or None when the conversion could not run (missing Edge)."""
    import markdown as _md

    md_path = Path(md_path)
    html_body = _md.markdown(
        md_path.read_text(encoding="utf-8"),
        extensions=["tables", "fenced_code"],
    )
    title = md_path.stem.replace("-", " ")
    html = _TEMPLATE.format(lang="de", title=title, body=html_body)
    tmp_html = md_path.with_suffix(".print.html")
    tmp_html.write_text(html, encoding="utf-8")
    pdf_path = md_path.with_suffix(".pdf")

    edge = _find_edge()
    if not edge:
        tmp_html.unlink(missing_ok=True)
        logger.warning("PDF-Export uebersprungen: msedge.exe nicht gefunden")
        return None

    # --headless=new prints a stable box model; --no-first-run avoids the
    # profile picker on fresh Windows profiles.
    cmd = [
        edge,
        "--headless=new",
        "--disable-gpu",
        "--no-first-run",
        "--run-all-compositor-stages-before-draw",
        "--print-to-pdf=" + str(pdf_path.resolve()),
        Path(tmp_html).resolve().as_uri(),
    ]
    try:
        subprocess.run(cmd, capture_output=True, timeout=90)
    except (OSError, subprocess.TimeoutExpired) as e:
        logger.warning("PDF-Export fehlgeschlagen: %s", e)
        tmp_html.unlink(missing_ok=True)
        return None
    ok = pdf_path.is_file() and pdf_path.stat().st_size > 500
    tmp_html.unlink(missing_ok=True)
    if ok:
        logger.info("PDF gebaut: %s", pdf_path)
        return str(pdf_path)
    logger.warning("PDF-Export fehlgeschlagen: Edge erzeugte keine Datei")
    return None
