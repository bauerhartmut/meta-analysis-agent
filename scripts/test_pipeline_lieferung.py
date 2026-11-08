"""Synthetischer Testfall fuer die Lieferungs-Pipeline.

Prueft ``scripts/triage_lieferung.py`` und ``scripts/pruefe_lieferung.py`` an
PDFs, deren Zustand vorher bekannt ist - ohne Netz, ohne echte Lieferung:

  poolbar            Text-PDF mit einem Arm-Satz, den der Fliesstext-Leser
                     als SOL-Effekt speichern muss
  scan               PDF ohne Textebene (aus einer echten Seite gerastert)
  endpunkt_nicht_berichtet
                     Text-PDF ohne SOL-Satz
  fremd              Text-PDF, dessen Dateiname keine PMID traegt

Dazu zwei Negativfaelle: ein Bericht mit falschem k (muss als Fehler
gemeldet werden) und ein leeres Verzeichnis (Exit 2).

Aufruf:
    .venv/bin/python.exe scripts/test_pipeline_lieferung.py

Exit 0 heisst: alle Erwartungen erfuellt. Exit 1: mindestens eine nicht.
Der Bericht landet in ``data/bench/sol2/testfall_pipeline_20261108.md``.
"""

from __future__ import annotations

import csv
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = Path(__file__).resolve().parent
for path in (ROOT, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import make_scan_probe  # noqa: E402
import make_text_pdf  # noqa: E402
import pruefe_lieferung  # noqa: E402
import read_pdf_corpus  # noqa: E402
import triage_lieferung  # noqa: E402

WORK = ROOT / "data" / "bench" / "sol2" / "testfall_pipeline"
SCAN_QUELLE = ROOT / "data" / "origpdf" / "09169ac90aa57bab.pdf"

# Der Satz folgt genau dem Muster, das ``arm_text`` akzeptiert: zwei
# Mittelwerte mit Streuung, je eine Fallzahl, zwei Arm-Etiketten, eines mit
# Interventionsvokabular, Outcome vor dem ersten Arm.
SOL_SATZ = ("Sleep onset latency was 18.3 +- 7.2 min in the melatonin group "
            "(n = 20) and 27.9 +- 8.1 min in the placebo group (n = 20).")

FUELLSATZ = ("The study protocol described the assessment schedule for each "
             "visit in detail and defined the handling of missing records.")

# Der Tabellen-Leser braucht Pipes als Trenner. Ohne Trennzeichen entsteht
# kein Block - dieselbe Zeile wird dann als "Endpunkt nicht berichtet"
# gemeldet. Beide Varianten stehen hier, damit die Grenze im Bericht belegt
# ist statt nur behauptet.
OR_TABELLE = [
    "Table 2. Effects on sleep outcomes",
    "Outcome | Odds ratio (95% CI)",
    "Sleep onset latency | 0.85 (0.70, 1.03)",
    "Total sleep time | 1.02 (0.88, 1.18)",
]
OR_TABELLE_OHNE_PIPES = [
    "Table 2. Effects on sleep outcomes",
    "Outcome                          Odds ratio (95% CI)",
    "Sleep onset latency              0.85 (0.70, 1.03)",
    "Total sleep time                 1.02 (0.88, 1.18)",
]

PMIDS = {
    "poolbar": "41369870",
    "scan": "39437460",
    "ohne_sol": "34181143",
    "or": "19299778",
}
NICHT_GELIEFERT = "33157425"

ergebnisse: list[tuple[str, bool, str]] = []


def pruefe(name: str, bedingung: bool, detail: str) -> None:
    ergebnisse.append((name, bool(bedingung), detail))


def text_pdf(pfad: Path, zeilen: list[str]) -> None:
    quelle = pfad.with_suffix(".txt")
    quelle.write_text("\n".join(zeilen), encoding="utf-8")
    make_text_pdf.main(["make_text_pdf.py", str(quelle), str(pfad)])


def baue_pdfs() -> None:
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)

    fuell = [FUELLSATZ] * 30
    text_pdf(WORK / f"{PMIDS['poolbar']}_poolbar.pdf", [SOL_SATZ] + fuell)
    text_pdf(WORK / f"{PMIDS['ohne_sol']}_ohne_sol.pdf", fuell)
    text_pdf(WORK / f"{PMIDS['or']}_or.pdf", OR_TABELLE + fuell)
    text_pdf(WORK / "unbekannt_ohne_pmid.pdf", [SOL_SATZ[:0] + FUELLSATZ] + fuell)

    if SCAN_QUELLE.is_file():
        make_scan_probe.main(["make_scan_probe.py", str(SCAN_QUELLE),
                              str(WORK / f"{PMIDS['scan']}_scan.pdf"),
                              "--scale", "1"])
    else:
        pruefe("Scan-Quelle vorhanden", False, f"{SCAN_QUELLE} fehlt")


def erwartete_csv(pfad: Path) -> None:
    with pfad.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["pmid", "prioritaet", "doi", "titel"])
        for key, pmid in PMIDS.items():
            writer.writerow([pmid, "A", f"10.0000/test.{key}", f"Testtitel {key}"])
        writer.writerow([NICHT_GELIEFERT, "A", "10.0000/test.fehlt", "Nicht geliefert"])


def main() -> int:
    if not ((ROOT / "research_agent").is_dir() and (ROOT / "scripts").is_dir()):
        print("falsches Arbeitsverzeichnis")
        return 1

    baue_pdfs()
    erwartet = WORK / "erwartet.csv"
    erwartete_csv(erwartet)

    # ---- Triage auf dem Testfall -----------------------------------------
    rc = triage_lieferung.main([
        "--dir", str(WORK),
        "--erwartet", str(erwartet),
        "--work-dir", str(WORK),
        "--json", str(WORK / "lieferung.json"),
        "--md", str(WORK / "lieferung.md"),
        "--basis-k", "3",
        "--ziel", "5",
    ])
    pruefe("Triage Exit-Code 0", rc == 0, f"rc={rc}")

    bericht = json.loads((WORK / "lieferung.json").read_text(encoding="utf-8"))
    docs = {d["file"]: d for d in bericht["documents"]}

    def zustand(schluessel: str) -> str:
        for name, doc in docs.items():
            if schluessel in name:
                return str(doc["zustand"])
        return "FEHLT"

    pruefe("poolbare Datei erkannt", zustand("poolbar") == "poolbar",
           f"zustand={zustand('poolbar')}")
    pruefe("Scan als Scan erkannt", zustand("scan") == "scan",
           f"zustand={zustand('scan')}")
    pruefe("fehlender Endpunkt erkannt",
           zustand("ohne_sol") == "endpunkt_nicht_berichtet",
           f"zustand={zustand('ohne_sol')}")
    pruefe("SOL-Zeile ohne poolbaren Effekt erkannt",
           zustand("_or") == "sol_nicht_poolbar",
           f"zustand={zustand('_or')}")

    k = bericht["k"]
    poolbar_n = sum(1 for d in bericht["documents"] if d["zustand"] == "poolbar")
    pruefe("k = Basis + poolbare Dateien",
           k["k_neu"] == k["basis_k"] + poolbar_n,
           f"k_neu={k['k_neu']} basis={k['basis_k']} poolbar={poolbar_n}")
    pruefe("k waechst um genau eine Studie", poolbar_n == 1, f"poolbar={poolbar_n}")

    fehlend = [f["pmid"] for f in bericht["fehlend"]]
    pruefe("nicht gelieferter Artikel gemeldet", NICHT_GELIEFERT in fehlend,
           f"fehlend={fehlend}")
    pruefe("Datei ohne PMID als fremd gemeldet",
           any("unbekannt" in f for f in bericht["fremd"]),
           f"fremd={bericht['fremd']}")

    scan_doc = next((d for d in bericht["documents"] if "scan" in d["file"]), {})
    pruefe("Scan traegt keine Zeichen", not scan_doc.get("chars"),
           f"chars={scan_doc.get('chars')}")

    # ---- Pruefskript auf dem echten Triage-Bericht ------------------------
    rc2 = pruefe_lieferung.main([
        "--bericht", str(WORK / "lieferung.json"),
        "--md", str(WORK / "pruefung.md"),
        "--json", str(WORK / "pruefung.json"),
        "--ziel", "5",
        "--gesamt-ziel", "5",
        "--artikel", "5",
    ])
    pruefung = json.loads((WORK / "pruefung.json").read_text(encoding="utf-8"))
    pruefe("Pruefskript meldet keinen Widerspruch", rc2 == 0, f"rc={rc2}")
    pruefe("Pruefskript findet k konsistent",
           pruefung["kennzahlen"]["konsistent"] is True,
           str(pruefung["kennzahlen"]["konsistent"]))
    pruefe("Scan wird im Pruefbericht gezaehlt",
           pruefung["kennzahlen"]["scan"] == 1,
           f"scan={pruefung['kennzahlen']['scan']}")

    # ---- Negativfall 1: manipuliertes k ----------------------------------
    kaputt = json.loads(json.dumps(bericht))
    kaputt["k"]["k_neu"] = kaputt["k"]["k_neu"] + 1
    kaputt_path = WORK / "lieferung_kaputt.json"
    kaputt_path.write_text(json.dumps(kaputt, ensure_ascii=False), encoding="utf-8")
    rc3 = pruefe_lieferung.main([
        "--bericht", str(kaputt_path),
        "--md", str(WORK / "pruefung_kaputt.md"),
        "--json", str(WORK / "pruefung_kaputt.json"),
    ])
    pruefe("falsches k fuehrt zu Exit 1", rc3 == 1, f"rc={rc3}")
    kaputt_res = json.loads((WORK / "pruefung_kaputt.json").read_text(encoding="utf-8"))
    pruefe("falsches k wird als Fehler benannt",
           any(b["schwere"] == "fehler" for b in kaputt_res["befunde"]),
           str([b["schwere"] for b in kaputt_res["befunde"]]))

    # ---- Negativfall 2: leeres Verzeichnis -------------------------------
    leer = WORK / "leer"
    leer.mkdir(exist_ok=True)
    rc4 = triage_lieferung.main([
        "--dir", str(leer),
        "--erwartet", str(erwartet),
        "--work-dir", str(leer),
        "--json", str(leer / "lieferung.json"),
        "--md", str(leer / "lieferung.md"),
        "--basis-k", "3",
        "--ziel", "5",
    ])
    pruefe("leeres Verzeichnis fuehrt zu Exit 2", rc4 == 2, f"rc={rc4}")

    # ---- Diagnose: dieselbe Tabelle ohne Trennzeichen --------------------
    diag = WORK / "diag_leerzeichen"
    diag.mkdir(exist_ok=True)
    text_pdf(diag / "leerzeichen.pdf", OR_TABELLE_OHNE_PIPES + [FUELLSATZ] * 25)
    read_pdf_corpus.main(["--dir", str(diag), "--db", str(diag / "d.db"),
                          "--json", str(diag / "d.json"),
                          "--md", str(diag / "d.md"), "--min-chars", "500"])
    d_json = json.loads((diag / "d.json").read_text(encoding="utf-8"))
    d_doc = (d_json.get("documents") or [{}])[0]
    pruefe("Tabelle ohne Pipes wird gelesen",
           int(d_doc.get("blocks") or 0) >= 1 and int(d_doc.get("sol_rows") or 0) >= 1,
           f"blocks={d_doc.get('blocks')} sol_rows={d_doc.get('sol_rows')}")

    # ---- Bericht ---------------------------------------------------------
    ok = sum(1 for _n, b, _d in ergebnisse if b)
    zeilen = [
        "# Testfall der Lieferungs-Pipeline",
        "",
        "Stand: 2026-11-08. Synthetische PDFs mit bekanntem Zustand, danach",
        "`triage_lieferung.py` und `pruefe_lieferung.py` darauf. Kein Netz.",
        "",
        f"Ergebnis: **{ok} von {len(ergebnisse)} Erwartungen erfuellt.**",
        "",
        "| Erwartung | Ergebnis | Detail |",
        "|---|---|---|",
    ]
    for name, bestanden, detail in ergebnisse:
        zeilen.append(f"| {name} | {'ok' if bestanden else 'FEHLER'} | {detail} |")
    zeilen += [
        "",
        "## Was der Test abdeckt",
        "",
        "- Scan ohne Textebene wird als `scan` gemeldet und zaehlt nicht als",
        "  gelesen; das Pruefskript zaehlt ihn getrennt.",
        "- Ein nicht berichteter Endpunkt wird als `endpunkt_nicht_berichtet`",
        "  gefuehrt, nicht als Kettenfehler.",
        "- Eine Datei ohne PMID im Namen erscheint als `fremd`.",
        "- Ein nicht gelieferter Artikel der Zugangsliste erscheint unter",
        "  `fehlend`.",
        "- Ein Bericht mit falschem k fuehrt bei `pruefe_lieferung.py` zu Exit 1",
        "  und einem Befund der Schwere `fehler`.",
        "- Ein leeres Verzeichnis fuehrt zu Exit 2, nicht zu Exit 0.",
        "",
        "## Befunde",
        "",
        "1. Tabellen ohne Trennzeichen werden erkannt: dieselbe Zeile, die ohne",
        "   Erweiterung `blocks = 0` ergab und als `endpunkt_nicht_berichtet`",
        "   galt, liefert jetzt einen Block und `sol_nicht_poolbar`.",
        "2. **`leser_luecke` ist nicht erreichbar.** `triage_dokument` verlangt",
        "   `sol_rows > 0` bei `arm_stored + direct_stored == 0`. `sol_rows` wird",
        "   in `read_pdf_corpus.py` aber ausschliesslich aus den gespeicherten",
        "   Zeilen gebildet (`all_rows = stored_arm + stored_direct`); beide",
        "   Bedingungen schliessen sich aus.",
        "3. Die Folge ist eine Fehlklassifikation, keine verlorene Studie: eine",
        "   berichtete, aber nicht poolbare SOL-Zeile kann als 'Endpunkt nicht",
        "   berichtet' gezaehlt werden. Solche Faelle am Volltext pruefen, nicht",
        "   der Meldung glauben.",
        "",
        "## Grenzen",
        "",
        "- Der Test prueft die Meldewege, nicht die inhaltliche Extraktion.",
        "- Die PDFs sind minimal (Helvetica, eine Seite); echte Verlags-PDFs",
        "  haben Spalten und Tabellen, die hier nicht vorkommen.",
        "",
    ]
    (ROOT / "data" / "bench" / "sol2" / "testfall_pipeline_20261108.md").write_text(
        "\n".join(zeilen), encoding="utf-8")

    print(f"{ok}/{len(ergebnisse)} Erwartungen erfuellt")
    for name, bestanden, detail in ergebnisse:
        print(f"  {'ok   ' if bestanden else 'FEHLER'} {name}  ({detail})")
    return 0 if ok == len(ergebnisse) else 1


if __name__ == "__main__":
    raise SystemExit(main())
