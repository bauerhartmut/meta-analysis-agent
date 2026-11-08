"""Zugangsliste: Melatonin-Trials ohne PMC-Volltext.

Aus den 114 Treffern des Q2-Abzugs sind 83 ohne PMC-Volltext. Diese Liste
sortiert sie fuer die Bibliotheksbestellung: Prioritaet nach Titelsignalen,
DOI/PMID fuer die Bestellung, CSV fuer die Sammelanfrage.

Deterministisch, kein Netz. Die Prioritaet ist eine Lesehilfe, kein Urteil
ueber die Studie - entschieden wird am Volltext.
"""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime
from pathlib import Path

MEL = re.compile(r"melatonin", re.I)
FREMD = re.compile(
    r"ramelteon|tasimelteon|agomelatine|valerian|cherry|vitamin\b|exercise|"
    r"dexmedetomidine|temazepam|zolpidem|light\s+therapy", re.I)
RCT = re.compile(r"randomi|placebo|double[\s-]?blind|controlled\s+trial|\btrial\b", re.I)
SOL = re.compile(r"sleep[\s-]onset|sleep[\s-]latency|insomnia|einschlaf", re.I)
SLEEP = re.compile(r"sleep|circadian|jet\s*lag|shift\s*work", re.I)


def classify(title: str) -> tuple[str, str]:
    """(Prioritaet, Begruendung) aus dem Titel."""
    if not MEL.search(title):
        return "D", "Melatonin steht nicht im Titel - als Vergleich oder Hintergrund"
    if FREMD.search(title):
        return "C", "Titel nennt einen anderen Wirkstoff oder eine Co-Intervention"
    if not SLEEP.search(title):
        return "C", "Melatonin im Titel, aber kein Schlafendpunkt erkennbar"
    if RCT.search(title) and SOL.search(title):
        return "A", "Melatonin plus RCT-Signal plus Einschaflatenz oder Insomnie"
    if RCT.search(title):
        return "B", "Melatonin plus RCT-Signal, Endpunkt im Titel offen"
    return "C", "Melatonin im Titel, kein RCT-Signal"


def main() -> int:
    records = json.loads(Path("data/bench/sol2/manifest_q2.json").read_text(encoding="utf-8"))
    ohne = [r for r in records if not r.get("xml")]
    rows = []
    for rec in ohne:
        title = str(rec.get("title") or "")
        tier, why = classify(title)
        rows.append({
            "prioritaet": tier,
            "begruendung": why,
            "pmid": rec.get("pmid") or "",
            "doi": rec.get("doi") or "",
            "pmc": rec.get("pmc") or "",
            "jahr": rec.get("year") or "",
            "zeitschrift": rec.get("journal") or "",
            "titel": title,
            "hat_doi": bool(rec.get("doi")),
        })
    order = {"A": 0, "B": 1, "C": 2, "D": 3}
    rows.sort(key=lambda r: (order[r["prioritaet"]], -int(r["jahr"] or 0)))
    counts = {t: sum(1 for r in rows if r["prioritaet"] == t) for t in "ABCD"}

    Path("data/bench/sol2/zugangsliste_20261108.json").write_text(
        json.dumps({"generated": datetime.now().isoformat(timespec="seconds"),
                    "ohne_volltext": len(ohne), "counts": counts, "rows": rows},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    with open("data/bench/sol2/zugangsliste_20261108.csv", "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["prioritaet", "pmid", "doi", "jahr",
                                                "zeitschrift", "titel"])
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row[k] for k in writer.fieldnames})

    lines = [
        "# Zugangsliste: Melatonin-Trials ohne PMC-Volltext", "",
        f"Stand: {datetime.now().isoformat(timespec='seconds')}. Quelle: "
        "`data/bench/sol2/manifest_q2.json`, 114 Treffer, davon 83 ohne Volltext.",
        "Kein Netz. Die Prioritaet ist eine Lesehilfe, keine Bewertung.", "",
        "| Prioritaet | Anzahl | Bedeutung |", "|---|---:|---|",
        f"| A | {counts['A']} | Melatonin + RCT-Signal + Einschaflatenz/Insomnie im Titel |",
        f"| B | {counts['B']} | Melatonin + RCT-Signal, Endpunkt offen |",
        f"| C | {counts['C']} | Melatonin, aber anderer Wirkstoff oder kein Schlafendpunkt |",
        f"| D | {counts['D']} | Melatonin nicht im Titel - nicht anfordern |", "",
        f"Mit DOI bestellbar: {sum(1 for r in rows if r['hat_doi'])} von {len(rows)}.", "",
        "## Prioritaet A", "",
        "| PMID | DOI | Jahr | Zeitschrift | Titel |", "|---|---|---:|---|---|",
    ]
    for row in [r for r in rows if r["prioritaet"] == "A"]:
        lines.append(f"| {row['pmid']} | {row['doi'] or '-'} | {row['jahr']} | "
                     f"{row['zeitschrift'][:40]} | {row['titel'][:110]} |")
    lines += ["", "## Prioritaet B", "",
              "| PMID | DOI | Jahr | Titel |", "|---|---|---:|---|"]
    for row in [r for r in rows if r["prioritaet"] == "B"]:
        lines.append(f"| {row['pmid']} | {row['doi'] or '-'} | {row['jahr']} | {row['titel'][:110]} |")
    lines += ["", "## Prioritaet C und D (nur Zaehlung)", "",
              f"{counts['C']} Dokumente mit anderem Wirkstoff oder ohne Schlafendpunkt, "
              f"{counts['D']} ohne Melatonin im Titel. Beide Gruppen stehen vollstaendig "
              "in der JSON- und CSV-Datei, aber nicht in dieser Bestellliste.", "",
              "## Wie die Liste benutzt wird", "",
              "1. Prioritaet A zuerst bestellen (DOI ist angegeben, PMID als Rueckfall).",
              "2. B nachziehen, wenn A nicht reicht.",
              "3. Nach Erhalt: dieselbe Kette (`scripts/read_q2_extended.py`) auf die",
              "   neuen XML/PDF ansetzen; die Erfolgsschwelle bleibt k >= 5.",
              "",
              "Grenze: Die Einordnung liest nur den Titel. Ein Trial kann in A stehen",
              "und am Volltext scheitern (kein Arm-Mittelwert) oder in B stehen und",
              "die Einschaflatenz doch berichten. Die Liste ersetzt kein Screening."]
    Path("data/bench/sol2/zugangsliste_20261108.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"ohne_volltext={len(ohne)} A={counts['A']} B={counts['B']} "
          f"C={counts['C']} D={counts['D']} mit_doi={sum(1 for r in rows if r['hat_doi'])}")
    for row in [r for r in rows if r["prioritaet"] == "A"][:12]:
        print(f"  A {row['jahr']} {row['pmid']} {row['doi'][:38]:38} {row['titel'][:64]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
