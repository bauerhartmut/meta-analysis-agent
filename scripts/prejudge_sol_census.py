"""Maschinelles Vorurteil fuer die Zensus-Dokumente der SOL-Sichtung.

Die Sichtungsliste (`sichtung_obergrenze_20261108.md`) hat 57 Zensus-Dokumente
und eine leere Urteilsspalte. Dieses Skript fuellt fuer jedes Dokument eine
Vorlage aus: Intervention, Design, ob eine SOL-Zeile im Text steht - jeweils
mit Belegsatz. Der Mensch muss dann nur noch bestaetigen oder verwerfen.

Wichtig: das Vorurteil ist kein Urteil. Es liest XML (Titel, Abstract,
Methodenteil) und die gespeicherten Zeilen; es erkennt Muster, keine Armdaten.
Deshalb steht in jeder Zeile, worauf der Vorschlag beruht.

Zwei Fallen, die der erste Entwurf nicht vermieden hat und die hier bewusst
behandelt sind:

* Referenzlisten nennen "melatonin" in fast jedem Schlafpapier. Sie werden
  abgeschnitten, und Melatonin zaehlt nur als Intervention, wenn es in einer
  Interventionsformulierung steht ("melatonin group", "3 mg melatonin",
  "received melatonin"), nicht als Outcome oder Zitat.
* "randomized" steht auch in Abstracts von Beobachtungsstudien, die es nur
  erwaehnen. Deshalb wird das Design aus Titel und Abstract bestimmt, nicht
  aus dem ganzen Text.

Aufruf:
    .venv/bin/python.exe scripts/prejudge_sol_census.py \
        --sighting data/bench/sol/sichtung_obergrenze_20261108.json \
        --xml-dirs data/bench/sol/xml,data/bench/sol/xml_q1,data/bench/sol/xml_fetch_ncbi \
        --out data/bench/sol/zensus_vorurteil_20261108
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path

SOL = r"(sleep[- ]onset|sleep[- ]latency|einschlaflatenz|\bsol\b|latency to sleep)"

# Melatonin nur als Intervention, nicht als Outcome oder Zitat.
MELATONIN_AS_INTERVENTION = (
    r"(melatonin\s+(group|arm|supplementation|administration|treatment|treated|therapy)"
    r"|melatonin\s+\d+(?:\.\d+)?\s*(?:mg|g)\b"
    r"|\d+(?:\.\d+)?\s*(?:mg|g)\s+(?:of\s+)?melatonin"
    r"|(received|taking|given|administered|oral|exogenous)\s+melatonin"
    r"|melatonin\s+(use|intake|consumption|exposure)"
    r"|melatonin\s+(versus|vs\.?)\s+placebo"
    r"|placebo\s+(versus|vs\.?)\s+melatonin)"
)

INTERVENTIONS = (
    ("melatonin", MELATONIN_AS_INTERVENTION),
    ("melatonin-agonist", r"\b(ramelteon|tasimelteon|agomelatine)\b"),
    ("rTMS", r"\b(rtms|transcranial magnetic stimulation)\b"),
    ("licht", r"\b(bright light|light therapy|light exposure|dim light)\b"),
    ("CBT", r"\b(cbt-?i\b|cognitive behavio(u)?ral therapy for insomnia|cognitive behavio(u)?ral therapy)\b"),
    ("ernaehrung", r"\b(dietary|diet\b|nutrition|nutritional|supplementation with|kale|almond)\b"),
    ("bewegung", r"\b(exercise|physical activity|activity break|walking)\b"),
    ("koffein", r"\bcaffeine\b"),
    ("akupunktur", r"\b(acupuncture)\b"),
    ("medikament-andere", r"\b(benzodiazepin|zolpidem|suvorexant|antidepressant|melatonin receptor agonist)\b"),
)

DESIGNS = (
    ("systematische Uebersicht", r"\b(systematic review|meta-analys)"),
    ("randomisierte Studie", r"\b(randomi[sz]ed|randomi[sz]ation|randomly assigned|\brct\b)"),
    ("Placebo-kontrolliert", r"\bplacebo[- ]controlled\b"),
    ("Crossover", r"\b(crossover|cross-over)\b"),
    ("doppelblind", r"\bdouble[- ]blind\b"),
    ("Beobachtung", r"\b(cohort|cross-sectional|observational|survey)\b"),
)

SUGGESTIONS = (
    "Melatonin: poolbare SOL-Zeile gespeichert",
    "Melatonin: SOL erwaehnt, keine poolbare Zeile",
    "Melatonin-Agonist (kein Melatonin)",
    "andere Intervention (kein Melatonin)",
    "kein SOL im Text",
    "kein RCT",
    "ungeprueft",
)


def plain(xml_text: str) -> str:
    """XML grob zu Fliesstext (Tags weg, Entities auf, Whitespace normal)."""
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", xml_text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return " ".join(text.split())


def extract_parts(xml_text: str) -> tuple[str, str]:
    """Titel plus Abstract (lead) und Anfang des Hauptteils ohne Referenzen."""
    head = re.split(r"<ref-list", xml_text, flags=re.I)[0]
    head = re.split(r"<back\b", head, flags=re.I)[0]
    title = " ".join(
        plain(m.group(1))
        for m in re.finditer(r"<article-title[^>]*>(.*?)</article-title>", head, re.S | re.I)
    )
    abstracts = " ".join(
        plain(m.group(1))
        for m in re.finditer(r"<abstract[^>]*>(.*?)</abstract>", head, re.S | re.I)
    )
    body = " ".join(
        plain(m.group(1))
        for m in re.finditer(r"<body[^>]*>(.*?)</body>", head, re.S | re.I)
    )
    lead = " ".join([title, abstracts]).strip() or " ".join(head.split()[:300])
    return lead, body[:8000]


def find(xml_text: str, pattern: str) -> str:
    hit = re.search(pattern, xml_text, re.I)
    return hit.group(1).strip() if hit else ""


def detect_interventions(text: str, lead: str = "") -> list[str]:
    """Interventionen aus Text; Melatonin braucht eine Interventionsformulierung."""
    found = []
    for name, pattern in INTERVENTIONS:
        hits = len(re.findall(pattern, text, re.I))
        in_lead = bool(re.search(pattern, lead, re.I)) if lead else False
        if name == "melatonin":
            if in_lead or hits >= 2 or (hits >= 1 and len(text) < 2000):
                found.append(name)
        elif hits >= 1 and (in_lead or hits >= 2 or len(text) < 2000):
            found.append(name)
    return found


def detect_design(text: str) -> list[str]:
    return [name for name, pattern in DESIGNS if re.search(pattern, text, re.I)]


def sol_snippet(text: str, limit: int = 190) -> str:
    """Ein kurzer Belegsatz um die erste SOL-Nennung."""
    for hit in re.finditer(SOL, text, re.I):
        start = max(0, hit.start() - 90)
        end = min(len(text), hit.end() + 110)
        snippet = " ".join(text[start:end].split())
        if re.search(r"\d", snippet):
            return snippet[:limit]
    return ""


def suggests(interventions: list[str], designs: list[str], sol_rows: int,
             sol_poolable: int, snippet: str) -> str:
    """Vorschlag aus Mustern - bewusst grob und in fester Reihenfolge."""
    randomised = any(d in designs for d in ("randomisierte Studie", "Placebo-kontrolliert",
                                            "Crossover"))
    if not randomised:
        return "kein RCT"
    has_sol = bool(snippet) or sol_rows > 0
    if not has_sol:
        return "kein SOL im Text"
    if "melatonin" in interventions:
        return ("Melatonin: poolbare SOL-Zeile gespeichert" if sol_poolable > 0
                else "Melatonin: SOL erwaehnt, keine poolbare Zeile")
    if "melatonin-agonist" in interventions:
        return "Melatonin-Agonist (kein Melatonin)"
    if interventions:
        return "andere Intervention (kein Melatonin)"
    return "ungeprueft"


def build(sighting: dict, xml_index: dict[str, Path]) -> dict:
    docs = []
    for stratum in ("A", "B", "C", "D"):
        for item in sighting["auswahl"].get(stratum, []):
            path = xml_index.get(item["pmc"])
            xml_text = path.read_text(encoding="utf-8", errors="ignore") if path else ""
            lead, body = extract_parts(xml_text) if xml_text else ("", "")
            if not lead:
                lead = item.get("title") or ""
            interventions = detect_interventions(f"{lead} {body}", lead)
            designs = detect_design(lead)
            snippet = sol_snippet(body) or sol_snippet(lead)
            docs.append({
                "stratum": stratum,
                "pmc": item["pmc"],
                "doi": item.get("doi", ""),
                "year": item.get("year", ""),
                "title": item.get("title", ""),
                "xml": bool(path),
                "stored_rows": item.get("stored_rows", 0),
                "sol_rows": item.get("sol_rows", 0),
                "sol_poolable": item.get("sol_poolable", 0),
                "interventions": interventions,
                "designs": designs,
                "suggestion": suggests(interventions, designs, item.get("sol_rows", 0),
                                       item.get("sol_poolable", 0), snippet),
                "evidence": snippet,
            })
    counts: dict[str, int] = {}
    for doc in docs:
        counts[doc["suggestion"]] = counts.get(doc["suggestion"], 0) + 1
    mel = [d for d in docs if "melatonin" in d["interventions"]]
    pool = [d for d in docs if d["sol_poolable"] > 0]
    both = [d for d in mel if d["sol_poolable"] > 0]
    befund = {"melatonin": len(mel), "poolbar": len(pool),
              "beides": len(both), "pmcs": [d["pmc"] for d in both]}
    return {
        "befund": befund,
        "generated": datetime.now().replace(microsecond=0).isoformat(),
        "documents": sorted(docs, key=lambda d: (SUGGESTIONS.index(d["suggestion"]), d["pmc"])),
        "counts": counts,
        "with_xml": sum(1 for d in docs if d["xml"]),
    }


def write_markdown(result: dict, path: Path) -> None:
    lines = [
        "# Zensus-Vorurteil: 57 Dokumente der SOL-Sichtung",
        "",
        f"Stand: {result['generated']}. Erzeugt von `scripts/prejudge_sol_census.py`. "
        f"XML vorhanden: {result['with_xml']} von {len(result['documents'])}.",
        "",
        "**Das ist ein Vorurteil, kein Urteil.** Die Spalte *Vorschlag* entsteht aus "
        "Mustern in Titel, Abstract und Methodenteil (ohne Referenzliste) plus den "
        "gespeicherten Zeilen. Melatonin zaehlt nur als Intervention, wenn eine "
        "Interventionsformulierung steht (\"melatonin group\", \"3 mg melatonin\", "
        "\"received melatonin\"), nicht als Outcome oder Zitat. Die Spalte *Urteil* "
        "bleibt leer und wird von Hand gefuellt.",
        "",
        "## Verteilung",
        "",
        "| Vorschlag | Dokumente |",
        "|---|---:|",
    ]
    for name in SUGGESTIONS:
        if result["counts"].get(name):
            lines.append(f"| {name} | {result['counts'][name]} |")
    b = result["befund"]
    befund = [
        "## Befund der Vorsichtung",
        "",
        f"Von {len(result['documents'])} Zensus-Dokumenten nennen {b['melatonin']} "
        f"Melatonin in einer Interventionsformulierung, {b['poolbar']} haben eine "
        f"poolbare SOL-Zeile, beides zusammen trifft auf {b['beides']} zu"
        + (f" ({', '.join(b['pmcs'])})." if b["pmcs"] else "."),
        "",
    ]
    if b["beides"]:
        befund += [
            "Der Zensus stuetzt damit **nicht** die fruehere Aussage k = 1: der einzige "
            "Melatonin-Treffer mit poolbarer SOL-Zeile ist eine Beobachtungsstudie ohne "
            "Randomisierung, und seine SOL-Zeile ist ein modellbasierter Koeffizient "
            "(0,07; KI -0,04 bis 0,17), kein Arm-Mittelwert in Minuten. Die uebrigen "
            "poolbaren SOL-Zeilen stammen aus rTMS, Mikrobiom-Transplantation, "
            "Ernaehrungsberatung, Krankenhauslicht und einem Katarakt-Vergleich.",
            "",
        ]
    lines += [
        "",
        *befund,
        "## Arbeitsliste",
        "",
        "| # | PMC | Stratum | Jahr | Intervention | Design | SOL-Zeilen | Vorschlag | Beleg | Urteil |",
        "|---:|---|---|---:|---|---|---:|---|---|---|",
    ]
    for n, doc in enumerate(result["documents"], 1):
        interventions = ", ".join(doc["interventions"]) or "-"
        designs = ", ".join(doc["designs"]) or "-"
        evidence = doc["evidence"].replace("|", "/")[:120] or "-"
        lines.append(
            f"| {n} | {doc['pmc']} | {doc['stratum']} | {doc['year']} | {interventions} | "
            f"{designs} | {doc['sol_rows']} | {doc['suggestion']} | {evidence} | |"
        )
    lines += [
        "",
        "## Wie weiter",
        "",
        "1. Zeilen mit Vorschlag *Melatonin: poolbare SOL-Zeile gespeichert* zuerst "
        "pruefen - dort entscheidet sich, ob der Zensus eine Melatonin-Studie enthaelt.",
        "2. *andere Intervention (kein Melatonin)* und *Melatonin-Agonist* koennen als "
        "Ausschluss bestaetigt werden; sie zaehlen nicht zur Melatonin-Obergrenze.",
        "3. *Melatonin: SOL erwaehnt, keine poolbare Zeile* ist die einzige Gruppe, die "
        "echte Lesearbeit braucht: Tabelle suchen, Armwerte pruefen.",
        "4. Urteile in die Spalte eintragen; die Treffer erhoehen den Zensus und "
        "senken den unsicheren Rest der Hochrechnung.",
        "",
        "## Belege",
        "",
        "- `sichtung_obergrenze_20261108.json` - Auswahl der 57 Dokumente.",
        "- `zensus_vorurteil_20261108.json` - dieselben Zeilen maschinenlesbar.",
        "- XML unter `data/bench/sol/xml/`, `xml_q1/`, `xml_fetch_ncbi/`.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sighting", default="data/bench/sol/sichtung_obergrenze_20261108.json")
    ap.add_argument("--xml-dirs", default="data/bench/sol/xml,data/bench/sol/xml_q1,"
                                         "data/bench/sol/xml_fetch_ncbi")
    ap.add_argument("--out", default="data/bench/sol/zensus_vorurteil_20261108")
    args = ap.parse_args(argv[1:])

    sighting = json.loads(Path(args.sighting).read_text(encoding="utf-8"))
    xml_index: dict[str, Path] = {}
    for directory in [Path(p) for p in args.xml_dirs.split(",") if p.strip()]:
        if directory.is_dir():
            for path in directory.glob("*.xml"):
                xml_index.setdefault(path.stem.upper(), path)

    result = build(sighting, xml_index)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(result, out.with_suffix(".md"))

    print(f"Dokumente: {len(result['documents'])} | XML: {result['with_xml']}")
    for name in SUGGESTIONS:
        if result["counts"].get(name):
            print(f"  {name}: {result['counts'][name]}")
    print(f"geschrieben: {out.with_suffix('.md')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
