"""Lauf 1 der SOL-Suchhypothese: Syntax-Probe, Q1-Seite, Stichprobe laden.

Der Lauf ist in ``data/bench/sol/suchhypothese_sol_20261108.md`` festgelegt und
vom Nutzer ausdruecklich freigegeben. Er besteht aus drei Teilen, alle ohne
Modell:

1. **Syntax-Probe** (6 Anfragen, je ``pageSize=1``): prueft, ob Europe PMC die
   Felder ``TITLE``, ``ABSTRACT`` und ``HAS_FULLTEXT`` auswertet. ``ABSTRACT``
   gilt nur dann als belegt, wenn die Trefferzahl deutlich unter der einer
   freien Suche nach demselben Wort liegt - andernfalls wird das Feld
   ignoriert und die Abfrage zaehlt nicht.
2. **Drei Seiten** (je 100 Treffer): Q1, Q2, Q3 in dieser Reihenfolge, Dubletten
   gegen den bestehenden Korpus (``manifest_all.json`` und ``xml/``) entfernt.
3. **Beschaffung**: XML fuer die ersten 40 neuen Dokumente, Q1 zuerst.

Kein LLM, kein Orchestrator. Aufruf:

    .venv/bin/python.exe scripts/sol_abstract_probe.py --download
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from sol_corpus_search import EPMC_SEARCH, EPMC_XML, _get  # noqa: E402

Q1 = ('(TITLE:"melatonin" OR ABSTRACT:"melatonin") '
      'AND (ABSTRACT:"sleep onset latency" OR ABSTRACT:"sleep latency" '
      'OR ABSTRACT:"SOL") '
      'AND (ABSTRACT:randomized OR ABSTRACT:randomised OR ABSTRACT:placebo '
      'OR ABSTRACT:"double-blind" OR ABSTRACT:crossover) '
      'AND HAS_FULLTEXT:y')

# Abweichung gegenueber dem Entwurf: statt ``"95% CI"`` wird
# ``"confidence interval"`` gesucht, weil das Prozentzeichen in einer
# Phrase die Abfrage zerlegen kann. Wird im Bericht vermerkt.
Q2 = (Q1 + ' AND (ABSTRACT:"mean difference" OR ABSTRACT:"effect size" '
      'OR ABSTRACT:Hedges OR ABSTRACT:"confidence interval" '
      'OR ABSTRACT:"standard deviation")')

Q3 = 'TITLE:"sleep onset latency" AND TITLE:melatonin AND HAS_FULLTEXT:y'

QUERIES = (("Q1", Q1), ("Q2", Q2), ("Q3", Q3))

PROBES = (
    ("frei_melatonin", "melatonin"),
    ("abstract_melatonin", 'ABSTRACT:"melatonin"'),
    ("titel_melatonin", 'TITLE:"melatonin"'),
    ("abstract_unsinn", 'ABSTRACT:"qqzzxx nonsenseterm"'),
)


def search(query: str, page_size: int = 1) -> dict:
    """Eine Europe-PMC-Anfrage; liefert Status, Trefferzahl und Eintraege."""
    import urllib.parse

    params = urllib.parse.urlencode({
        "query": query, "format": "json", "pageSize": page_size,
        "resultType": "core", "sort": "P_PDATE_D desc",
    })
    status, body = _get(f"{EPMC_SEARCH}?{params}")
    payload = {}
    if status == 200 and body:
        try:
            payload = json.loads(body.decode("utf-8", "ignore"))
        except ValueError:
            payload = {}
    records = []
    for item in (payload.get("resultList", {}) or {}).get("result", []) or []:
        records.append({
            "pmcid": str(item.get("pmcid") or "").strip(),
            "doi": str(item.get("doi") or "").strip(),
            "title": str(item.get("title") or "").strip(),
            "year": str(item.get("pubYear") or ""),
            "isOpenAccess": str(item.get("isOpenAccess") or ""),
            "hasAbstract": bool(str(item.get("abstractText") or "").strip()),
        })
    return {
        "query": query,
        "status": status,
        "hitCount": int(payload.get("hitCount") or 0),
        "records": records,
        "error": str(payload.get("errorMessage") or "") if status != 200 else "",
    }


def existing_pmcids(base: Path) -> set[str]:
    """Was schon im Korpus liegt: Manifest plus vorhandene XML-Dateien."""
    seen: set[str] = set()
    for name in ("manifest_all.json", "manifest.json"):
        path = base / name
        if not path.exists():
            continue
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            continue
        for entry in raw if isinstance(raw, list) else []:
            pmc = str(entry.get("pmc") or entry.get("pmcid") or "").strip()
            if pmc:
                seen.add(pmc)
    for folder in ("xml", "fulltext", "seed_xml"):
        path = base / folder
        if path.is_dir():
            seen.update(p.stem for p in path.glob("PMC*.xml"))
    return seen


def probe_fields() -> dict:
    probes = {}
    for name, query in PROBES:
        result = search(query, page_size=1)
        probes[name] = {"query": query, "status": result["status"],
                        "hitCount": result["hitCount"],
                        "error": result["error"]}
        print(f"  Probe {name:20s} status={result['status']:3d} "
              f"hits={result['hitCount']}", flush=True)
        time.sleep(0.3)
    plain = probes["frei_melatonin"]["hitCount"]
    abstract = probes["abstract_melatonin"]["hitCount"]
    abstract_ok = bool(abstract and plain and abstract < 0.9 * plain)
    probes["bewertung"] = {
        "abstract_feld_belegt": abstract_ok,
        "verhaeltnis_abstract_zu_frei": round(abstract / plain, 3) if plain else None,
        "begruendung": ("Trefferzahl des Abstract-Feldes liegt deutlich unter "
                        "der freien Suche" if abstract_ok else
                        "Abstract-Trefferzahl entspricht nahezu der freien Suche "
                        "- Feld wird vermutlich ignoriert"),
    }
    return probes


def pick(queries: list[dict], seen: set[str], limit: int) -> tuple[list[dict], dict]:
    """Erste ``limit`` neue Dokumente, Q1 zuerst; Dubletten werden gezaehlt."""
    picked: list[dict] = []
    stats: Counter = Counter()
    for result in queries:
        name = result["name"]
        stats[f"{name}_hits"] = result["hitCount"]
        stats[f"{name}_returned"] = len(result["records"])
        for record in result["records"]:
            pmc = record["pmcid"]
            if not pmc.startswith("PMC"):
                stats[f"{name}_ohne_pmcid"] += 1
                continue
            if pmc in seen:
                stats[f"{name}_dublette"] += 1
                continue
            if len(picked) >= limit:
                stats[f"{name}_ueber_limit"] += 1
                continue
            seen.add(pmc)
            picked.append({**record, "query": name})
    stats["stichprobe"] = len(picked)
    return picked, dict(stats)


def download(entries: list[dict], xml_dir: Path, sleep: float = 0.2) -> dict:
    xml_dir.mkdir(parents=True, exist_ok=True)
    loaded = present = failed = 0
    failures: list[dict] = []
    for number, entry in enumerate(entries, start=1):
        target = xml_dir / f"{entry['pmcid']}.xml"
        if target.exists() and target.stat().st_size > 500:
            present += 1
            continue
        status, body = _get(EPMC_XML.format(pmcid=entry["pmcid"]))
        if status == 200 and body and b"<article" in body[:4000]:
            target.write_bytes(body)
            loaded += 1
        else:
            failed += 1
            failures.append({"pmc": entry["pmcid"], "status": status})
        if number % 10 == 0:
            print(f"  ... {number}/{len(entries)} (geladen {loaded}, "
                  f"vorhanden {present}, Fehler {failed})", flush=True)
        time.sleep(sleep)
    return {"loaded": loaded, "present": present, "failed": failed,
            "failures": failures}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", default="data/bench/sol")
    ap.add_argument("--limit", type=int, default=40,
                    help="Dokumente fuer die Stichprobe (Kriterium A1: 40)")
    ap.add_argument("--xml-dir", default="data/bench/sol/xml_q1")
    ap.add_argument("--download", action="store_true", help="XML laden (Netz)")
    ap.add_argument("--json", default="data/bench/sol/q1_probe_20261108.json")
    ap.add_argument("--md", default="data/bench/sol/q1_probe_20261108.md")
    ap.add_argument("--manifest-out", default="data/bench/sol/q1_stichprobe_20261108.json")
    args = ap.parse_args(argv)

    base = Path(args.base)
    stamp = datetime.now(timezone.utc).isoformat()

    print("1) Syntax-Probe", flush=True)
    probes = probe_fields()

    print("2) Drei Seiten", flush=True)
    results = []
    for name, query in QUERIES:
        result = search(query, page_size=100)
        result["name"] = name
        results.append(result)
        print(f"  {name}: status={result['status']} hits={result['hitCount']} "
              f"zurueck={len(result['records'])}", flush=True)
        if result["status"] != 200:
            print(f"    Fehler: {result['error']}", flush=True)
        time.sleep(0.3)

    seen = existing_pmcids(base)
    print(f"  bestehender Korpus: {len(seen)} PMCIDs", flush=True)
    picked, stats = pick(results, seen, args.limit)
    print(f"  Stichprobe: {len(picked)} neue Dokumente {dict(stats)}", flush=True)

    manifest_path = Path(args.manifest_out)
    manifest_path.write_text(json.dumps(
        [{"pmc": e["pmcid"], "doi": e["doi"], "title": e["title"],
          "year": e["year"], "query": e["query"]} for e in picked],
        ensure_ascii=False, indent=1), encoding="utf-8")

    downloads = {}
    if args.download:
        print("3) XML laden", flush=True)
        downloads = download(picked, Path(args.xml_dir))

    per_query = Counter(e["query"] for e in picked)
    payload = {
        "generated": stamp,
        "limit": args.limit,
        "probes": probes,
        "queries": [{k: r[k] for k in ("name", "query", "status", "hitCount", "error")}
                    | {"returned": len(r["records"])} for r in results],
        "stats": stats,
        "per_query": dict(per_query),
        "download": downloads,
        "manifest": str(manifest_path),
    }
    Path(args.json).write_text(json.dumps(payload, ensure_ascii=False, indent=1),
                               encoding="utf-8")

    lines = [
        "# Lauf 1 der SOL-Suchhypothese: Syntax-Probe und Stichprobe",
        "",
        f"Stand: {stamp}. Kein Modell, kein Orchestrator; nur Europe PMC.",
        "",
        "## Syntax-Probe",
        "",
        "| Probe | Status | Treffer |",
        "|---|---:|---:|",
    ]
    for name, _ in PROBES:
        p = probes[name]
        lines.append(f"| `{p['query']}` | {p['status']} | {p['hitCount']} |")
    bewertung = probes["bewertung"]
    lines += [
        "",
        f"`ABSTRACT` gilt als belegt: **{'ja' if bewertung['abstract_feld_belegt'] else 'nein'}** "
        f"(Verhaeltnis zur freien Suche {bewertung['verhaeltnis_abstract_zu_frei']}). "
        f"{bewertung['begruendung']}.",
        "",
        "## Die drei Abfragen",
        "",
        "| Abfrage | Treffer | zurueck | neu in Stichprobe |",
        "|---|---:|---:|---:|",
    ]
    for r in results:
        lines.append(f"| {r['name']} | {r['hitCount']} | {len(r['records'])} | "
                     f"{per_query.get(r['name'], 0)} |")
    lines += [
        "",
        "## Stichprobe",
        "",
        f"- Ziel: {args.limit} Dokumente, erreicht: **{len(picked)}**",
        f"- bestehender Korpus (vorher): {len(seen) - len(picked)} PMCIDs",
    ]
    for key in sorted(stats):
        lines.append(f"- `{key}`: {stats[key]}")
    lines += ["", "## Beschaffung", ""]
    if downloads:
        lines += [
            f"- geladen: {downloads['loaded']}, vorhanden: {downloads['present']}, "
            f"Fehler: {downloads['failed']}",
            f"- Ausfallquote: "
            f"{100.0 * downloads['failed'] / max(1, len(picked)):.1f} % der Stichprobe",
        ]
        if downloads["failures"]:
            lines.append("- Fehlschlaege: " + ", ".join(
                f"{f['pmc']} ({f['status']})" for f in downloads["failures"][:10]))
    else:
        lines.append("- nicht geladen (`--download` fehlt)")
    lines.append("")
    Path(args.md).write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({"probe": {k: probes[k]["hitCount"] for k, _ in PROBES},
                      "stats": stats, "download": downloads.get("loaded"),
                      "failed": downloads.get("failed")}, ensure_ascii=False))
    print(f"MD: {args.md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
