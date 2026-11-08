"""Geschichtete Sichtungsliste der SOL-Kandidaten (Obergrenze aus Paket A).

Die Obergrenze - wie viele Dokumente des Korpus ueberhaupt einen poolbaren
SOL-Effekt enthalten - braucht menschliche Sichtung. 946 Kandidaten komplett
zu lesen ist unrealistisch; deshalb zieht dieses Skript eine begruendete
Stichprobe:

* Zensus der Dokumente, in denen bereits eine SOL-Zeile gespeichert wurde
  (dort ist die Frage "Enthalten sie einen poolbaren SOL-Effekt?" fast schon
  beantwortet - sie werden mitgezaehlt, nicht neu gesucht),
* Zensus der Dokumente mit gespeicherten Effektzeilen ohne SOL-Label,
* Zensus der Dokumente, deren Titel Einschaflatenz nennt,
* Zufallsstichprobe aus dem Rest (fester Seed, Hash-Reihenfolge, damit die
  Auswahl unabhaengig von Sortierung und Python-Version ist),
* Fehlerprobe aus den Nicht-Kandidaten (prueft das Kandidaten-Gate selbst).

Die Hochrechnung ist bewusst konservativ: fuer die Zufallsstichprobe wird die
einseitige 95-%-Obergrenze der Praevalenz benutzt (Clopper-Pearson; bei null
Treffern entspricht das der Regel der Drei 3/n).

Aufruf:
    .venv/bin/python.exe scripts/sample_sol_candidates.py \
        --manifest data/bench/sol/manifest_all.json \
        --funnel data/bench/sol/funnel_label2_20261108.json \
        --db-dir data/bench/sol \
        --out data/bench/sol/sichtung_obergrenze_20261108
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

SOL_PATTERN = r"(sleep[- ]onset|sleep[- ]latency|einschlaflatenz|\bsol\b)"
TITLE_PATTERN = r"(sleep[- ]onset|sleep[- ]latency|einschlaflatenz)"
DBS = ("direct_label2.db", "arm_label2.db", "text_arms.db", "change_arms.db")


# --------------------------------------------------------------------------
# reine Funktionen (durch Tests abgedeckt)
# --------------------------------------------------------------------------
def matches(pattern: str, text: str | None) -> bool:
    import re

    return bool(re.search(pattern, (text or "").lower()))


def stable_order(ids: list[str], seed: str) -> list[str]:
    """Feste Reihenfolge per Hash - unabhaengig von Sortierung und Version."""
    return sorted(ids, key=lambda i: hashlib.sha256(f"{seed}:{i}".encode()).hexdigest())


def pick(pool: list[str], n: int, seed: str) -> list[str]:
    ordered = stable_order(sorted(pool), seed)
    return ordered[:n]


def binomial_cdf(k: int, n: int, p: float) -> float:
    if p <= 0.0:
        return 1.0
    if p >= 1.0:
        return 1.0 if k >= n else 0.0
    total = 0.0
    for i in range(0, min(k, n) + 1):
        total += math.comb(n, i) * (p ** i) * ((1.0 - p) ** (n - i))
    return total


def upper_bound(hits: int, n: int, alpha: float = 0.05) -> float:
    """Einseitige (1-alpha)-Obergrenze der Praevalenz, exakt (Bisektion).

    Bei hits = 0 ist das Ergebnis 1 - alpha**(1/n), fuer n = 60 also 4,87 %.
    Das ist die exakte Form der Regel der Drei (3/n = 5,0 % ist die Naeherung).
    """
    if n <= 0:
        return 1.0
    if hits >= n:
        return 1.0
    lo, hi = 0.0, 1.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if binomial_cdf(hits, n, mid) > alpha:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def classify_document(rows: list[dict], title: str | None) -> dict:
    """Zeilen eines Dokuments in SOL-Kennzahlen uebersetzen."""
    sol_rows = [r for r in rows if matches(SOL_PATTERN, r.get("outcome_key") or r.get("outcome"))]
    poolable = [r for r in sol_rows if r.get("_poolable")]
    return {
        "stored_rows": len(rows),
        "sol_rows": len(sol_rows),
        "sol_poolable": len(poolable),
        "title_names_sleep": matches(TITLE_PATTERN, title),
    }


# --------------------------------------------------------------------------
# Daten laden
# --------------------------------------------------------------------------
def load_poolable():
    spec = importlib.util.spec_from_file_location("cut", "scripts/cut_against_sol.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.poolable


def source_key(value: str) -> str:
    value = (value or "").strip().lower()
    for prefix in ("doi:", "pmc:"):
        if value.startswith(prefix):
            return value[len(prefix):]
    return value


def rows_by_source(db_dir: Path, is_poolable) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for name in DBS:
        path = db_dir / name
        if not path.is_file():
            continue
        conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        for row in conn.execute("select * from study_effects"):
            data = dict(row)
            data["_poolable"] = bool(is_poolable(data))
            out.setdefault(source_key(data.get("source_id", "")), []).append(data)
        conn.close()
    return out


def read_pmcs(xml_dirs: list[Path]) -> set[str]:
    found: set[str] = set()
    for directory in xml_dirs:
        if not directory.is_dir():
            continue
        for path in directory.glob("*.xml"):
            found.add(path.stem.upper())
    return found


# --------------------------------------------------------------------------
# Auswahl bauen
# --------------------------------------------------------------------------
def build(manifest, funnel_docs, rows, already_read, seed, rest_n, noncand_n) -> dict:
    meta = {}
    for entry in manifest:
        pmc = (entry.get("pmc") or "").upper()
        key = source_key(entry.get("doi") or "")
        for k in (pmc, key):
            if k:
                meta[k] = entry

    docs = []
    candidates = []
    for doc in funnel_docs:
        pmc = (doc.get("pmc") or "").upper()
        info = meta.get(pmc) or meta.get(source_key(doc.get("doi") or "")) or {}
        keys = {pmc, source_key(doc.get("doi") or ""), source_key(info.get("doi") or "")}
        rows_here = []
        for k in keys:
            key = source_key(k)
            if key and key in rows:
                rows_here = rows[key]
                break
        stats = classify_document(rows_here, info.get("title"))
        item = {
            "pmc": pmc,
            "doi": doc.get("doi") or info.get("doi") or "",
            "title": info.get("title") or "",
            "year": info.get("year") or "",
            "sol_kandidat": bool(doc.get("sol_kandidat")),
            "tabellen": doc.get("tabellen", 0),
            "zeilen": doc.get("zeilen", 0),
            "candidates": doc.get("kandidaten", 0),
            "bereits_gelesen": pmc in already_read,
            **stats,
        }
        docs.append(item)
        if item["sol_kandidat"]:
            candidates.append(item)

    def stratum(item):
        if item["sol_poolable"]:
            return "A"
        if item["sol_rows"]:
            return "B"
        if item["stored_rows"]:
            return "C"
        if item["title_names_sleep"]:
            return "D"
        return "E"

    for item in docs:
        item["stratum"] = stratum(item) if item["sol_kandidat"] else "X"

    by_stratum: dict[str, list[dict]] = {}
    for item in docs:
        by_stratum.setdefault(item["stratum"], []).append(item)

    census = {s: by_stratum.get(s, []) for s in ("A", "B", "C", "D")}
    rest = by_stratum.get("E", [])
    rest_ids = [i["pmc"] for i in rest]
    chosen = set(pick(rest_ids, rest_n, seed))
    rest_sample = [i for i in rest if i["pmc"] in chosen]

    noncand = by_stratum.get("X", [])
    nc_chosen = set(pick([i["pmc"] for i in noncand], noncand_n, seed + ":x"))
    noncand_sample = [i for i in noncand if i["pmc"] in nc_chosen]

    for items in census.values():
        for i in items:
            i["auswahl"] = "Zensus"
    for i in rest_sample:
        i["auswahl"] = f"Zufall (Seed {seed})"
    for i in noncand_sample:
        i["auswahl"] = "Fehlerprobe"

    n_rest_total = len(rest)
    n_rest_sample = len(rest_sample)
    bound = upper_bound(0, n_rest_sample) if n_rest_sample else 1.0
    known_positive = sum(1 for i in census["A"] + census["B"] if i["sol_poolable"])
    projected = known_positive + bound * (n_rest_total - n_rest_sample)

    return {
        "generated": datetime.now().replace(microsecond=0).isoformat(),
        "seed": seed,
        "strata": {
            "A": {"name": "poolbare SOL-Zeile gespeichert (Intervention ungeprueft)",
                  "total": len(census["A"])},
            "B": {"name": "SOL-Zeile gespeichert, nicht poolbar", "total": len(census["B"])},
            "C": {"name": "Effektzeilen ohne SOL-Label", "total": len(census["C"])},
            "D": {"name": "Titel nennt Einschaflatenz", "total": len(census["D"])},
            "E": {"name": "Rest der SOL-Kandidaten", "total": len(rest),
                  "sample": n_rest_sample},
            "X": {"name": "Nicht-Kandidaten (Fehlerprobe)", "total": len(noncand),
                  "sample": len(noncand_sample)},
        },
        "hochrechnung": {
            "kandidaten": len(candidates),
            "zensus": sum(len(v) for v in census.values()),
            "rest_gesamt": n_rest_total,
            "rest_stichprobe": n_rest_sample,
            "praevalenz_obergrenze_95": round(bound, 4),
            "bekannt_poolbar": known_positive,
            "melatonin_im_titel": sum(1 for i in census["A"]
                                    if matches(r"melatonin", i["title"])),
            "obergrenze_dokumente": round(projected, 1),
        },
        "auswahl": {s: sorted(census[s], key=lambda i: i["pmc"]) for s in census}
                  | {"E": sorted(rest_sample, key=lambda i: i["pmc"]),
                     "X": sorted(noncand_sample, key=lambda i: i["pmc"])},
    }


def write_markdown(result: dict, path: Path) -> None:
    strata = result["strata"]
    hoch = result["hochrechnung"]
    lines = [
        "# Sichtungsliste: Obergrenze der SOL-Kandidaten",
        "",
        f"Stand: {result['generated']}. Seed `{result['seed']}`. Erzeugt von "
        "`scripts/sample_sol_candidates.py`.",
        "",
        "## Wozu diese Liste",
        "",
        f"Die Obergrenze aus Paket A fragt: Wie viele der {hoch['kandidaten']} "
        "SOL-Kandidaten enthalten ueberhaupt einen poolbaren SOL-Effekt "
        "(Melatonin gegen Placebo, Mittelwert plus Streuung je Arm)? Ohne diese "
        "Zahl laesst sich ein verlorener Effekt nicht als legitim oder als "
        "Leserdefekt einordnen.",
        "",
        "## Auswahl",
        "",
        "| Stratum | Bedeutung | Umfang | Auswahl |",
        "|---|---|---:|---|",
    ]
    labels = {
        "A": ("poolbare SOL-Zeile gespeichert (Intervention ungeprueft)", "Zensus"),
        "B": ("SOL-Zeile gespeichert, nicht poolbar", "Zensus"),
        "C": ("Effektzeilen ohne SOL-Label", "Zensus"),
        "D": ("Titel nennt Einschaflatenz", "Zensus"),
        "E": ("Rest der SOL-Kandidaten", f"Zufall, {strata['E']['sample']} von {strata['E']['total']}"),
        "X": ("Nicht-Kandidaten (Fehlerprobe)", f"Zufall, {strata['X']['sample']} von {strata['X']['total']}"),
    }
    for key in ("A", "B", "C", "D", "E", "X"):
        name, mode = labels[key]
        lines.append(f"| {key} | {name} | {strata[key]['total']} | {mode} |")
    lines += [
        "",
        "## Hochrechnung",
        "",
        f"- Zensus: {hoch['zensus']} Dokumente (A-D), davon {hoch['bekannt_poolbar']} "
        "mit einer poolbaren SOL-Zeile.",
        f"- Engere Frage (Melatonin gegen Placebo): {hoch['melatonin_im_titel']} dieser "
        "Dokumente nennt Melatonin schon im Titel. Der Zensus belegt nur, dass eine "
        "poolbare SOL-Zeile existiert, nicht fuer welche Intervention - das entscheidet "
        "die Sichtung.",
        f"- Rest: {hoch['rest_gesamt']} Dokumente, davon {hoch['rest_stichprobe']} gesichtet.",
        f"- Einseitige 95-%-Obergrenze der Praevalenz bei 0 Treffern in der "
        f"Stichprobe: **{hoch['praevalenz_obergrenze_95'] * 100:.1f} %**.",
        f"- Daraus die Obergrenze fuer den ganzen Korpus: "
        f"**{hoch['obergrenze_dokumente']} Dokumente mit poolbarer SOL-Zeile** "
        f"(Zensus-Treffer plus Obergrenze fuer den Rest).",
        "",
        "Die Zahl ist eine Obergrenze, keine Schaetzung: sie gilt, wenn in der "
        "gesichteten Stichprobe kein weiterer poolbarer Effekt gefunden wird. "
        "Jeder Treffer erhoeht den Zensus und senkt den unsicheren Rest.",
        "",
        "## Sichtungsanleitung",
        "",
        "1. Dokument oeffnen (PMC-ID bei Europe PMC oder NCBI; XML liegt, wo "
        "vorhanden, unter `data/bench/sol/xml/`).",
        "2. Ergebnistabellen ansehen, nicht den Abstract: gesucht ist eine Zeile "
        "mit Einschaflatenz (SOL) oder Schlafbeginn, Mittelwert und Streuung "
        "(SD oder SE) je Arm, Interventionsarm Melatonin gegen Placebo.",
        "3. Urteil vergeben: `poolbar` (Armdaten vorhanden), `nur Baseline` "
        "(Wert ist Tag 0 oder vor Intervention), `kein SOL` (anderes Zielmass), "
        "`kein RCT` (Review, Beobachtung), `kein Volltext` (Zugang fehlt).",
        "4. Treffer sofort in die Mess-DB aufnehmen, damit der Zensus waechst.",
        "5. Nach 20 `nein` in Folge in Stratum E darf die Sichtung dort enden - "
        "das ist die Abbruchregel; sie wird im Protokoll vermerkt.",
        "",
        "## Arbeitsliste",
        "",
    ]
    for key in ("A", "B", "C", "D", "E", "X"):
        items = result["auswahl"][key]
        if not items:
            continue
        name, _ = labels[key]
        lines += [f"### Stratum {key} - {name} ({len(items)})", "",
                  "| # | PMC | Jahr | Titel | Zeilen | SOL-Zeilen | poolbar | gelesen | Urteil |",
                  "|---:|---|---:|---|---:|---:|---:|---|---|"]
        for n, item in enumerate(items, 1):
            title = (item["title"] or "")[:90].replace("|", "/")
            lines.append(
                f"| {n} | {item['pmc']} | {item['year']} | {title} | "
                f"{item['stored_rows']} | {item['sol_rows']} | {item['sol_poolable']} | "
                f"{'ja' if item['bereits_gelesen'] else ''} | |"
            )
        lines.append("")
    lines += [
        "## Belege",
        "",
        "- `sichtung_obergrenze_20261108.json` - dieselbe Auswahl maschinenlesbar.",
        "- `funnel_label2_20261108.json` - Kandidatenmenge (946 von 1.056 Dokumenten).",
        "- `manifest_all.json` - PMC, DOI, Titel, Jahr je Dokument.",
        "- Mess-DBs `direct_label2.db`, `arm_label2.db`, `text_arms.db`, `change_arms.db` - "
        "gespeicherte Zeilen und SOL-Labels.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="data/bench/sol/manifest_all.json")
    ap.add_argument("--funnel", default="data/bench/sol/funnel_label2_20261108.json")
    ap.add_argument("--db-dir", default="data/bench/sol")
    ap.add_argument("--xml-dirs", default="data/bench/sol/xml,data/bench/sol/xml_q1,"
                                         "data/bench/sol/xml_fetch_ncbi")
    ap.add_argument("--seed", default="20261108")
    ap.add_argument("--rest-sample", type=int, default=60)
    ap.add_argument("--noncandidate-sample", type=int, default=30)
    ap.add_argument("--out", default="data/bench/sol/sichtung_obergrenze_20261108")
    args = ap.parse_args(argv[1:])

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    funnel = json.loads(Path(args.funnel).read_text(encoding="utf-8"))
    rows = rows_by_source(Path(args.db_dir), load_poolable())
    read = read_pmcs([Path(p) for p in args.xml_dirs.split(",") if p.strip()])

    result = build(manifest, funnel["documents"], rows, read, args.seed,
                   args.rest_sample, args.noncandidate_sample)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(result, out.with_suffix(".md"))

    h = result["hochrechnung"]
    print(f"Kandidaten: {h['kandidaten']} | Zensus A-D: {h['zensus']} | "
          f"Rest-Stichprobe: {h['rest_stichprobe']} von {h['rest_gesamt']}")
    print(f"Obergrenze (95 %) bei 0 Treffern: {h['praevalenz_obergrenze_95'] * 100:.1f} % "
          f"-> {h['obergrenze_dokumente']} Dokumente")
    print(f"geschrieben: {out.with_suffix('.json')}, {out.with_suffix('.md')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
