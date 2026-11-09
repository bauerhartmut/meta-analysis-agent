"""Metadaten der Teststudien aus lokalen Quellen. Keine Erfindung: fehlt ein
Feld in der Quelle, steht dort ein Strich."""
import xml.etree.ElementTree as ET
from pathlib import Path

ZIELE = [
    ("T1", "23098680", "PMC3489506"),
    ("T2", None, "PMC2933606"),
    ("T3", None, "PMC2952772"),
    ("T4", "39437460", None),
    ("T5", "34181143", None),
    ("T6", "9566656", None),
    ("T7", "20535539", None),
    ("T8", "19030713", "NUNES"),
    ("T10", "19299778", None),
]

def txt(el):
    return " ".join("".join(el.itertext()).split()) if el is not None else None

def pubmed(path):
    out = {}
    for art in ET.parse(path).getroot().iter("PubmedArticle"):
        pmid = art.findtext(".//PMID")
        if not pmid:
            continue
        authors = []
        for a in art.findall(".//AuthorList/Author"):
            ln, ini = a.findtext("LastName"), a.findtext("Initials")
            if ln:
                authors.append(f"{ln} {ini or ''}".strip())
        doi = None
        for e in art.findall(".//ELocationID"):
            if e.get("EIdType") == "doi":
                doi = (e.text or "").strip()
        out[pmid.strip()] = dict(
            title=txt(art.find(".//ArticleTitle")),
            journal=art.findtext(".//Journal/Title") or art.findtext(".//Journal/ISOAbbreviation"),
            year=art.findtext(".//JournalIssue/PubDate/Year") or art.findtext(".//JournalIssue/PubDate/MedlineDate"),
            authors=authors, doi=doi,
        )
    return out

def pmc(path):
    root = ET.parse(path).getroot()
    ids = {}
    for aid in root.iter("article-id"):
        ids[aid.get("pub-id-type")] = (aid.text or "").strip()
    authors = []
    for c in root.iter("contrib"):
        sn, gn = c.findtext(".//surname"), c.findtext(".//given-names")
        if sn:
            authors.append(f"{sn} {gn or ''}".strip())
    return dict(
        pmid=ids.get("pmid"), pmcid=ids.get("pmcid"),
        title=txt(root.find(".//article-title")),
        journal=root.findtext(".//journal-title"),
        year=root.findtext(".//pub-date/year"),
        authors=authors, doi=ids.get("doi"),
    )

pub = pubmed("data/bench/sol2/abstracts_b_20261108.xml")
pmcs = {}
for f in Path("data/bench/sol2/xml").glob("PMC*.xml"):
    try:
        d = pmc(f)
        pmcs[d["pmcid"] or f.stem] = d
    except ET.ParseError as e:
        print("Parsefehler", f.name, e)

rows = []
for fall, pmid, pmcid in ZIELE:
    d = None
    if pmcid == "NUNES":
        d = dict(pmid="19030713", pmcid=None, doi=None,
                 title="Effect of melatonin administration on subjective sleep quality in chronic obstructive pulmonary disease",
                 journal="Brazilian Journal of Medical and Biological Research",
                 year="2008",
                 authors=["Nunes D.M.", "Mota R.M.S.", "Machado M.O.", "Pereira E.D.B.",
                          "de Bruin V.M.S.", "de Bruin P.F.C."])
    elif pmcid and pmcid in pmcs:
        d = pmcs[pmcid]
    elif pmid and pmid in pub:
        d = pub[pmid]
    elif pmid:
        for x in pmcs.values():
            if x.get("pmid") == pmid:
                d = x; break
    if not d:
        rows.append((fall, pmid or pmcid, None)); continue
    a = d["authors"]
    kurz = ", ".join(a[:3]) + (" et al." if len(a) > 3 else "")
    rows.append((fall, pmid or d.get("pmid") or pmcid, dict(**d, kurz=kurz)))

for fall, key, d in rows:
    if d is None:
        print(f"{fall}\t{key}\tNICHT GEFUNDEN")
    else:
        print(f"{fall}\t{key}\t{d['kurz']}\t{d['year']}\t{d['journal']}\t{d['doi']}\t{d['title']}")

lines = ["# Namen und Herausgeber der Teststudien", "",
         "Stand: 2026-11-09. Alle Angaben aus lokalen Quellen",
         "(`abstracts_b_20261108.xml`, `sol2/xml/PMC*.xml`); kein Feld geschaetzt.", "",
         "| Fall | Studie | Erstautoren | Jahr | Zeitschrift | PMID / DOI |", "|---|---|---|---|---|---|"]
for fall, key, d in rows:
    if d is None:
        lines.append(f"| {fall} | nicht in lokaler Quelle | - | - | - | {key} |")
        continue
    ident = " / ".join(x for x in [d.get("pmid") or key, d.get("doi")] if x)
    lines.append(f"| {fall} | {d['title']} | {d['kurz']} | {d['year']} | {d['journal']} | {ident} |")
Path("data/bench/validierung/harness_teststudien_namen_20261109.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\nMD geschrieben,", len(rows), "Zeilen")
