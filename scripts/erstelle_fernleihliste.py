"""Erzeugt die druckfertige Fernleih-Bestellliste fuer die 5 A- und 20 B-Titel.

Quellen, alle lokal, kein Netz:
  data/bench/sol2/zugangsliste_20261108.csv   Prioritaet, PMID, DOI, Jahr, Zeitschrift, Titel
  data/bench/sol2/zitationen_a.json           Autoren und Kollation der 5 A-Titel
  data/bench/sol2/abstracts_b_20261108.xml    Autoren und Kollation der 20 B-Titel
  data/bench/sol2/triage_b_20261108.md        Triage-Klassen (hier als Tabelle gespiegelt)

Ausgabe:
  data/bench/sol2/fernleihliste_20261109.md
  data/bench/sol2/fernleihliste_20261109.txt
"""

from __future__ import annotations

import csv
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = Path("data/bench/sol2")
OUT_MD = BASE / "fernleihliste_20261109.md"
OUT_TXT = BASE / "fernleihliste_20261109.txt"

# Triage-Klassen aus triage_b_20261108.md, Abschnitt "Auszählung".
TRIAGE = {
    "41369870": "A", "39437460": "A", "34181143": "A", "20535539": "A",
    "19299778": "A", "16919138": "A", "9566656": "A",
    "30160043": "B", "20025642": "B", "18078449": "B", "15275698": "B",
    "11211063": "B", "26569624": "B", "17404779": "B",
    "42533530": "C",
    "40791136": "D", "34293628": "D", "29619605": "D", "23098680": "D",
    "9737496": "D",
}

# Begruendung fuer die fuenf D-Faelle, aus triage_b_20261108.md.
D_GRUND = {
    "40791136": "Walnuss-Intervention, kein Melatonin",
    "34293628": "Melatonin gegen Triclofos (EEG-Sedierung), kein Placebo",
    "29619605": "Melatonin gegen Meloxicam, kein Placebo",
    "23098680": "HTA-Bericht der MENDS-Studie, Duplikat von S1, liegt lokal vor",
    "9737496": "Notaerzte nach Nachtschicht, kein SOL-Endpunkt berichtet",
}

# Hinweise, die beim Lesen des Volltexts zu beachten sind (aus Triage und Dedup-Register).
HINWEIS = {
    "16919138": "Dedup-Verdacht gegen S1 (MENDS): Register-ID im Volltext pruefen, bevor extrahiert wird.",
    "23098680": "Zeichengleiche SOL-Werte wie PMC3489506; max. Ergaenzung fuer S1, keine neue Zeile.",
    "19299778": "Berichtet Endwerte der ersten postoperativen Nacht, keine Veraenderung; Baseline-Ausgleich pruefen.",
    "20535539": "Crossover: gepaarte Streuung noetig.",
    "9566656": "Crossover: gepaarte Streuung noetig.",
    "18078449": "Crossover: gepaarte Streuung noetig.",
    "15275698": "Crossover: gepaarte Streuung noetig.",
    "11211063": "Crossover, PSG: gepaarte Streuung noetig.",
    "26569624": "Crossover: gepaarte Streuung noetig.",
    "39437460": "SOL per PSG berichtet, Differenz 8,36 min.",
    "28364493": "Andere Intervention (Melatonin plus Licht), keine Doppelpublikation.",
    "11292231": "Von S3 zitiert, externe Arbeit; mit 14566165 auf gleiche Kohorte pruefen.",
    "14566165": "Von S3 zitiert, externe Arbeit; mit 11292231 auf gleiche Kohorte pruefen.",
}


def norm_title(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").replace("\u2019", "'")).strip()


def xpath_text(node, path: str) -> str:
    found = node.find(path)
    if found is None or found.text is None:
        return ""
    return norm_title(found.text)


def parse_b_xml() -> dict[str, dict]:
    tree = ET.parse(BASE / "abstracts_b_20261108.xml")
    out: dict[str, dict] = {}
    for art in tree.iter("PubmedArticle"):
        pmid = xpath_text(art, "./MedlineCitation/PMID")
        article = art.find("./MedlineCitation/Article")
        if article is None:
            continue
        names = []
        for author in article.findall("./AuthorList/Author"):
            last = xpath_text(author, "./LastName")
            initials = xpath_text(author, "./Initials")
            collective = xpath_text(author, "./CollectiveName")
            if last:
                names.append(f"{last} {initials}".strip())
            elif collective:
                names.append(collective)
        journal = article.find("./Journal")
        iso = ""
        year = ""
        volume = ""
        issue = ""
        pages = ""
        if journal is not None:
            iso = xpath_text(journal, "./ISOAbbreviation") or xpath_text(journal, "./Title")
            volume = xpath_text(journal, "./JournalIssue/Volume")
            issue = xpath_text(journal, "./JournalIssue/Issue")
            jyear = journal.find("./JournalIssue/PubDate/Year")
            if jyear is not None:
                year = norm_title(jyear.text)
            else:
                medline_date = xpath_text(journal, "./JournalIssue/PubDate/MedlineDate")
                year = medline_date[:4]
        pages = xpath_text(article, "./Pagination/MedlinePgn") or xpath_text(
            article, "./Pagination/StartPage"
        )
        out[pmid] = {
            "pmid": pmid,
            "authors": names,
            "title": xpath_text(article, "./ArticleTitle").rstrip("."),
            "journal": iso,
            "year": year,
            "volume": volume,
            "issue": issue,
            "pages": pages,
        }
    return out


def format_authors(names: list[str]) -> str:
    if not names:
        return ""
    if len(names) <= 6:
        return ", ".join(names)
    return ", ".join(names[:6]) + " et al."


def kollation(journal: str, year: str, volume: str, issue: str, pages: str) -> str:
    text = f"{journal}. {year}" if journal else f"{year}"
    if volume:
        text += f";{volume}"
        if issue:
            text += f"({issue})"
    if pages:
        text += f":{pages}"
    return text


def main() -> None:
    rows = list(csv.DictReader((BASE / "zugangsliste_20261108.csv").open(encoding="utf-8")))
    zitationen = {z["pmid"]: z for z in json.loads((BASE / "zitationen_a.json").read_text("utf-8"))}
    b_meta = parse_b_xml()

    entries: list[dict] = []
    for prio in ("A", "B"):
        for row in (r for r in rows if r["prioritaet"] == prio):
            pmid = row["pmid"].strip()
            doi = row["doi"].strip()
            if prio == "A":
                z = zitationen[pmid]
                authors = [
                    part.strip()
                    for part in re.split(r",\s*", z.get("author", ""))
                    if part.strip() and part.strip().lower() != "et al."
                ]
                loc = z.get("loc", "")
                # loc hat die Form "2026;62(1):16-22" - Band, Heft und Seiten daraus.
                m = re.match(r"(?P<year>\d{4})(?:;(?P<vol>[^(:]+))?(?:\((?P<iss>[^)]+)\))?(?::(?P<pages>.+))?", loc)
                vol = (m.group("vol") or "").strip() if m else ""
                iss = (m.group("iss") or "").strip() if m else ""
                pages = (m.group("pages") or "").strip() if m else ""
                entries.append({
                    "prio": prio,
                    "pmid": pmid,
                    "doi": doi,
                    "authors": format_authors(authors),
                    "title": norm_title(z.get("title", row["titel"])).rstrip("."),
                    "source": kollation(z.get("journal", row["zeitschrift"]), z.get("year", row["jahr"]), vol, iss, pages),
                    "year": z.get("year", row["jahr"]),
                    "triage": "",
                })
            else:
                meta = b_meta.get(pmid, {})
                entries.append({
                    "prio": prio,
                    "pmid": pmid,
                    "doi": doi,
                    "authors": format_authors(meta.get("authors", [])),
                    "title": norm_title(meta.get("title") or row["titel"]).rstrip("."),
                    "source": kollation(
                        meta.get("journal") or row["zeitschrift"],
                        meta.get("year") or row["jahr"],
                        meta.get("volume", ""),
                        meta.get("issue", ""),
                        meta.get("pages", ""),
                    ),
                    "year": meta.get("year") or row["jahr"],
                    "triage": TRIAGE.get(pmid, ""),
                })

    assert len(entries) == 25, len(entries)
    assert len({e["pmid"] for e in entries}) == 25
    assert all(e["doi"] for e in entries)
    assert all(e["authors"] for e in entries), [e["pmid"] for e in entries if not e["authors"]]
    assert all(e["title"] for e in entries)

    streichen = [e for e in entries if e["triage"] == "D"]
    behalten = [e for e in entries if e["triage"] != "D"]
    assert len(streichen) == 5 and len(behalten) == 20

    md: list[str] = []
    md.append("# Fernleih-Bestellliste: 5 A- und 20 B-Titel\n")
    md.append(
        "Stand: 2026-11-09. Grundlage ist die Zugangsliste der 83 Dokumente ohne "
        "PMC-Volltext (`zugangsliste_20261108.csv`, Prioritaeten A 5, B 20, C 39, "
        "D 19). Je Eintrag stehen die Felder, die ein Fernleihformular verlangt: "
        "Autor, Titel, Quelle, DOI, PMID.\n"
    )
    md.append(
        "Alle Angaben sind maschinell aus lokalen Dateien uebernommen, nichts ist "
        "abgetippt oder ergaenzt: A aus `zitationen_a.json` (PubMed-Metadaten), "
        "B aus `abstracts_b_20261108.xml` (PubMed-efetch). Erzeugt von "
        "`scripts/erstelle_fernleihliste.py`.\n"
    )
    md.append(
        "**Fuenf der zwanzig B-Titel sind nach der Abstract-Triage nicht zu "
        "bestellen** (Klasse D: kein Placebo, kein Melatonin, Duplikat oder kein "
        "SOL-Endpunkt). Sie stehen in Teil 2 mit dem Vermerk `entfaellt` und sind "
        "in Abschnitt 4 begruendet. Die bestellfaehige Menge sind 5 + 15 = 20 "
        "Titel.\n"
    )

    md.append("## 1. Uebersicht\n")
    md.append("| Nr | Teil | PMID | DOI | Jahr | Triage |")
    md.append("|---:|---|---|---|---:|---|")
    for i, e in enumerate(entries, start=1):
        md.append(
            f"| {i} | {e['prio']} | {e['pmid']} | {e['doi']} | "
            f"{e['year']} | {e['triage'] or '-'} |"
        )
    md.append("")

    for part, label, prio in ((1, "2. Prioritaet A: fuenf Titel mit Einschaflatenz im Titel", "A"),
                              (2, "3. Prioritaet B: zwanzig Titel, Endpunkt offen", "B")):
        md.append(f"## {label}\n")
        for e in entries:
            if e["prio"] != prio:
                continue
            nr = entries.index(e) + 1
            md.append(f"### {nr}) {e['title']}\n")
            md.append("```text")
            md.append(f"Autor: {e['authors']}")
            md.append(f"Titel: {e['title']}")
            md.append(f"Quelle: {e['source']}")
            md.append(f"DOI: {e['doi']}")
            md.append(f"PMID: {e['pmid']}")
            if e["triage"]:
                md.append(f"Triage: Klasse {e['triage']}" + (" - entfaellt" if e["triage"] == "D" else ""))
            if e["pmid"] in HINWEIS:
                md.append(f"Hinweis: {HINWEIS[e['pmid']]}")
            md.append("```\n")

    md.append("## 4. Vor dem Absenden zu streichen\n")
    md.append("Diese fuenf B-Titel sind nach `triage_b_20261108.md` Klasse D. "
              "Sie kosten fuenf Fernleihen ohne Aussicht auf eine poolbare Zeile.\n")
    md.append("| PMID | DOI | Grund |")
    md.append("|---|---|---|")
    for e in streichen:
        md.append(f"| {e['pmid']} | {e['doi']} | {D_GRUND[e['pmid']]} |")
    md.append("")
    md.append("Bleiben 15 B-Titel. Zusammen mit den fuenf A-Titeln sind es "
              "**20 Bestellungen**.\n")

    md.append("## 5. Freitextfassung fuer ein einzelnes Bestellfeld\n")
    md.append("Fassung ohne die fuenf D-Titel (20 Bestellungen):\n")
    md.append("```text")
    md.append(
        "Bitte beschaffen Sie zwanzig Aufsaetze zu Melatonin und Einschaflatenz; alle "
        "sind ueber die DOI aufloesbar: "
    )
    dois = [e["doi"] for e in behalten]
    lines = []
    current = ""
    for doi in dois:
        piece = doi + (", " if doi != dois[-1] else ".")
        if len(current) + len(piece) > 72:
            lines.append(current.rstrip())
            current = ""
        current += piece
    lines.append(current.rstrip())
    md.extend(lines)
    md.append(
        "Bitte als PDF mit Textebene bereitstellen; ein reiner Scan ohne Textebene "
        "ist fuer die Auswertung nicht verwendbar."
    )
    md.append("```\n")
    md.append("Falls auch die fuenf gestrichenen Titel bestellt werden sollen, "
              "kommen diese DOIs hinzu: " + ", ".join(e["doi"] for e in streichen) + ".\n")

    md.append("## 6. Pruefung\n")
    md.append("| Pruefung | Ergebnis |")
    md.append("|---|---|")
    md.append("| Eintraege gesamt | 25 (5 A, 20 B) |")
    md.append("| eindeutige PMIDs | 25 |")
    md.append("| Eintraege mit DOI | 25 |")
    md.append("| Eintraege mit Autor und Titel | 25 |")
    md.append("| bestellfaehig nach Triage | 20 (5 A, 15 B) |")
    md.append("| gestrichen | 5 (Klasse D) |")
    md.append("")
    md.append(
        "Das Skript bricht bei Abweichung ab (`assert`). Es liest nur lokale "
        "Dateien, kein Netzaufruf, kein Modellaufruf.\n"
    )

    md.append("## 7. Grenzen\n")
    md.append(
        "- Die Einordnung A/B stammt aus dem Titel allein, die Triage aus den "
        "Abstracts. Beides ersetzt kein Screening am Volltext.\n"
        "- Bei Crossover-Studien (20535539, 9566656, 18078449, 15275698, "
        "11211063, 26569624) fehlt im Abstract fast immer die gepaarte Streuung. "
        "Ob eine Zeile entsteht, entscheidet der Volltext.\n"
        "- 16919138 und 23098680 sind vor der Extraktion gegen S1 zu pruefen; "
        "das Dedup-Register nennt die Merkmale.\n"
        "- Keine Angaben zu Gebuehren, Lieferart oder Bibliothekskonto: Das "
        "Formular erhebt sie selbst, sie lassen sich nicht aus dem Projekt "
        "ableiten.\n"
    )

    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")

    txt: list[str] = []
    txt.append("FERNLEIH-BESTELLLISTE - Melatonin, 20 Aufsaetze")
    txt.append("Stand 2026-11-09. Bitte als PDF mit Textebene.")
    txt.append("")
    for i, e in enumerate(behalten, start=1):
        txt.append(f"{i})")
        txt.append(f"Autor: {e['authors']}")
        txt.append(f"Titel: {e['title']}")
        txt.append(f"Quelle: {e['source']}")
        txt.append(f"DOI: {e['doi']}")
        txt.append(f"PMID: {e['pmid']}")
        txt.append("")
    txt.append("Nicht bestellen (Triage Klasse D):")
    for e in streichen:
        txt.append(f"- {e['pmid']} ({e['doi']}): {D_GRUND[e['pmid']]}")
    OUT_TXT.write_text("\n".join(txt) + "\n", encoding="utf-8")

    print(f"{OUT_MD}: {len(md)} Zeilen")
    print(f"{OUT_TXT}: bestellfaehig {len(behalten)}, gestrichen {len(streichen)}")


if __name__ == "__main__":
    main()
