"""Die Korpus-Dokumente ohne lokale Datei gezielt als XML nachladen.

Grundlage ist ``data/bench/sol/pdf_verfuegbarkeit_20261108.json``: dort sind
10 der 33 Dokumente als "nur PMC abgeleitet" gefuehrt - genau die Quellen,
deren Europe-PMC-Abruf in Lauf 1 mit HTTP 500 abbrach. Dieses Skript holt
ausschliesslich diese 10 Dokumente, einzeln, mit Pause, und schreibt sie in
ein eigenes Verzeichnis. Keine Suche, kein Modell, kein Backoff-Ring.

Zwei Anbieter, weil Europe PMC fuer diese zehn PMCIDs reproduzierbar HTTP 500
liefert:
    --provider epmc  https://www.ebi.ac.uk/europepmc/webservices/rest/<PMC>/fullTextXML
    --provider ncbi  https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi

Der Standard ist ``--dry-run``: ohne ``--ja`` wird nichts heruntergeladen,
sondern nur die geplante Anfrage je Dokument ausgegeben.

Aufruf:
    .venv/bin/python.exe scripts/fetch_missing_corpus_xml.py --dry-run
    .venv/bin/python.exe scripts/fetch_missing_corpus_xml.py --ja --provider ncbi
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = {
    "epmc": "https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/fullTextXML",
    "ncbi": ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
             "?db=pmc&id={numeric}&rettype=xml"),
}
AGENT = "meta-analysis-agent/1.0"


def targets(availability: Path) -> list:
    """Eintraege ohne lokale XML-/Inbox-Datei."""
    data = json.loads(availability.read_text(encoding="utf-8"))
    return [entry for entry in data["eintraege"]
            if not entry.get("lokale_xml") and not entry.get("inbox_datei")]


def fetch(url: str, timeout: float) -> tuple:
    """(status, body, fehler) - ohne Retry, damit die Telemetrie ehrlich bleibt."""
    request = urllib.request.Request(url, headers={"User-Agent": AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read(), ""
    except urllib.error.HTTPError as error:
        return error.code, b"", f"HTTP {error.code}"
    except Exception as error:                     # noqa: BLE001 - Netzfehler sammeln
        return 0, b"", f"{type(error).__name__}: {error}"


def looks_like_xml(body: bytes) -> bool:
    """Ein echtes Artikel-XML, kein Fehlerdokument."""
    head = body[:4000].lower()
    return b"<article" in head and len(body) > 2000


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--availability", default="data/bench/sol/pdf_verfuegbarkeit_20261108.json")
    parser.add_argument("--provider", choices=sorted(TEMPLATES), default="epmc")
    parser.add_argument("--out-dir", default="")
    parser.add_argument("--json", default="")
    parser.add_argument("--delay", type=float, default=1.5)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--ja", action="store_true",
                        help="Anfragen wirklich ausfuehren (ohne: nur Plan)")
    args = parser.parse_args(argv)

    entries = targets(Path(args.availability))
    template = TEMPLATES[args.provider]
    suffix = "" if args.provider == "epmc" else f"_{args.provider}"
    out_dir = Path(args.out_dir or f"data/bench/sol/xml_fetch{suffix}")
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir
    json_path = Path(args.json or f"data/bench/sol/xml_fetch{suffix}_20261108.json")

    plan = [{"pmc": e["pmc"], "doi": e.get("doi", ""),
             "title": e.get("title", "")[:120],
             "url": template.format(pmc=e["pmc"], numeric=e["pmc"].replace("PMC", ""))}
            for e in entries]

    if args.dry_run or not args.ja:
        print(json.dumps({"provider": args.provider, "geplant": len(plan), "ziele": plan},
                         ensure_ascii=False, indent=2))
        print("\nKein Download ohne --ja.", file=sys.stderr)
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for index, item in enumerate(plan):
        status, body, error = fetch(item["url"], args.timeout)
        ok = status == 200 and looks_like_xml(body)
        path = ""
        if ok:
            target = out_dir / f"{item['pmc']}.xml"
            target.write_bytes(body)
            path = str(target.relative_to(ROOT)).replace("\\", "/")
        elif status == 200 and not error:
            error = f"kein Artikel-XML ({len(body)} Bytes)"
        results.append({**item, "status": status, "bytes": len(body), "ok": ok,
                        "pfad": path, "fehler": error})
        print(f"{index + 1:2d}/{len(plan)} {item['pmc']:14s} status={status} "
              f"bytes={len(body):7d} {'OK' if ok else (error or 'zu klein')}")
        if index + 1 < len(plan):
            time.sleep(args.delay)

    loaded = [r for r in results if r["ok"]]
    report = {
        "generated": dt.datetime.now().isoformat(timespec="seconds"),
        "provider": args.provider,
        "geplant": len(plan),
        "geladen": len(loaded),
        "fehlgeschlagen": len(plan) - len(loaded),
        "pause_s": args.delay,
        "ziele": results,
    }
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"geladen": len(loaded), "fehlgeschlagen": len(plan) - len(loaded),
                      "json": str(json_path)}, ensure_ascii=False))
    return 0 if loaded else 1


if __name__ == "__main__":
    raise SystemExit(main())
