"""E2: Pooling-Engine offline gegen dokumentierte Referenzwerte pruefen.

Ruft ``research_agent.meta.pooling.pool()`` direkt auf - ohne LLM, ohne Netz -
und vergleicht sechs Kennzahlen gegen die in
``data/bench/sol2/pooling_sol3_20261108.json`` dokumentierte Hauptanalyse.

Dazu sieben Verhaltensfaelle (identische Varianzen, stark unterschiedliche
Standardfehler, eine Studie mit sehr grossem SE, keine Heterogenitaet, k = 1,
ungueltige Eingaben, fehlende Streuung).

Grenze, bewusst: Die Unit-Faelle pruefen Verhalten gegen von Hand gerechnete
Werte, nicht gegen einen externen Datensatz. Ein Abgleich mit R metafor oder
statsmodels ist in dieser Umgebung nicht moeglich.

Schreibt ``data/bench/validierung/e2_pooling_20261108.{json,md}``. Aendert
keine Implementierung und keine Analysedaten. Exit 1, sobald ein Vergleich
ausserhalb der Toleranz liegt.
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research_agent.meta.pooling import pool  # noqa: E402

REFERENZ = ROOT / "data/bench/sol2/pooling_sol3_20261108.json"
OUT_DIR = ROOT / "data/bench/validierung"
ANALYSE = "Hauptanalyse"
TOLERANZ = 0.01          # TODO: dokumentierte numerische Toleranz
TOL_EXAKT = 1e-9

KENNZAHLEN = (
    ("pooled", "Gepoolter Effekt (min)"),
    ("ci_low", "Untere 95%-KI-Grenze (min)"),
    ("ci_high", "Obere 95%-KI-Grenze (min)"),
    ("tau2", "tau^2 (min^2)"),
    ("q", "Cochran Q"),
    ("i2", "I^2 (%)"),
)


def klassifiziere(abweichung: float) -> tuple[str, bool]:
    """Rundung von echtem Rechenfehler unterscheiden."""
    if abweichung <= TOL_EXAKT:
        return "exakt", True
    if abweichung <= TOLERANZ:
        return "rundung", True
    return "abweichung", False


def lade_referenz() -> dict:
    daten = json.loads(REFERENZ.read_text(encoding="utf-8"))
    for analyse in daten.get("analysen", []):
        if analyse.get("analyse") == ANALYSE:
            return {"kopf": daten, "analyse": analyse}
    raise SystemExit(f"Analyse '{ANALYSE}' fehlt in {REFERENZ}")


def vergleiche(soll: dict, ist: dict) -> tuple[list[dict], dict]:
    zeilen: list[dict] = []
    for key, name in KENNZAHLEN:
        sollwert = soll.get(key)
        istwert = ist.get(key)
        if sollwert is None or istwert is None:
            zeilen.append({
                "kennzahl": key, "name": name, "soll": sollwert, "ist": istwert,
                "abweichung": None, "art": "fehlt",
                "toleranz": TOLERANZ, "status": "FAIL",
            })
            continue
        abweichung = abs(float(istwert) - float(sollwert))
        art, ok = klassifiziere(abweichung)
        zeilen.append({
            "kennzahl": key, "name": name,
            "soll": float(sollwert), "ist": float(istwert),
            "abweichung": abweichung, "art": art,
            "toleranz": TOLERANZ, "status": "PASS" if ok else "FAIL",
        })
    return zeilen, {
        "k": ist.get("k"),
        "method": ist.get("method"),
        "weight_type": ist.get("weight_type"),
        "se_hksj": ist.get("se_hksj"),
        "pi_low": ist.get("pi_low"),
        "pi_high": ist.get("pi_high"),
        "small_k_note": ist.get("small_k_note"),
        "fixed": ist.get("fixed"),
    }


# Korrektur am eigenen Testentwurf - nicht am Harness. Wird im Bericht
# ausgewiesen, damit ein roter Erstlauf nicht still verschwindet.
KORREKTUREN = (
    {
        "fall": "U3-sehr-grosser-se",
        "text": (
            "Erste Fassung erwartete pooled = -10.0 und lief mit Abweichung "
            "3,33e-02 auf FAIL. Der Sollwert war falsch, nicht die Engine: "
            "die Studie mit SE 60 traegt 0,11 % Gewicht, also "
            "fe = (-10/4 - 40/3600)/(1/4 + 1/3600) = -10,0333; Q = 0,2497 "
            "< df = 1, damit tau^2 = 0 und der RE-Pool gleich dem FE-Wert. "
            "Der Fall prueft jetzt den nachgerechneten Wert und tau^2 = 0."
        ),
    },
)

# --- Verhaltensfaelle -------------------------------------------------------
# Erwartungswerte von Hand gerechnet, nicht aus der Engine abgeschrieben.
# U1: v = 25 fuer alle, w = 0.04, fe = -20;
#     Q = 0.04 * (100 + 0 + 100) = 8; df = 2 -> I^2 = 6/8 = 75 %;
#     Basis = 0.12 - 0.0048/0.12 = 0.08 -> tau^2 = 6/0.08 = 75.
UNIT_FAELLE = (
    {
        "id": "U1-gleiche-varianzen",
        "zweck": "identische SE: Q, tau^2 und I^2 muessen den Handwerten folgen",
        "rows": [
            {"label": "A", "est": -10.0, "se": 5.0},
            {"label": "B", "est": -20.0, "se": 5.0},
            {"label": "C", "est": -30.0, "se": 5.0},
        ],
        "erwartet": {"q": 8.0, "tau2": 75.0, "i2": 75.0, "pooled": -20.0},
        "toleranz": 1e-9,
    },
    {
        "id": "U2-stark-unterschiedliche-se",
        "zweck": "gleicher Effekt, SE 1 gegen 20: keine Heterogenitaet, Pool bleibt beim Effekt",
        "rows": [
            {"label": "A", "est": -10.0, "se": 1.0},
            {"label": "B", "est": -10.0, "se": 20.0},
        ],
        "erwartet": {"q": 0.0, "tau2": 0.0, "i2": 0.0, "pooled": -10.0},
        "toleranz": 1e-9,
    },
    {
        "id": "U3-sehr-grosser-se",
        # Korrektur am Testentwurf, im Bericht ausgewiesen: die erste Fassung
        # erwartete pooled = -10.0 und lag damit falsch. Die zweite Studie
        # traegt auch bei SE 60 Gewicht (1/3600 gegen 1/4):
        #   fe = (-10/4 - 40/3600) / (1/4 + 1/3600) = -10.0332963...
        #   Q  = 0.25*(-10-fe)^2 + (1/3600)*(-40-fe)^2 = 0.2497 < df = 1
        #   -> tau^2 = 0 -> der RE-Pool faellt auf den FE-Wert zusammen.
        "zweck": "eine Studie mit SE 60 verschiebt den Pool nur um 0,033 min; "
                 "ohne Heterogenitaet faellt RE auf FE zusammen",
        "rows": [
            {"label": "A", "est": -10.0, "se": 2.0},
            {"label": "B", "est": -40.0, "se": 60.0},
        ],
        "erwartet": {"pooled": -10.033296337402886, "tau2": 0.0, "k": 2},
        "toleranz": 1e-9,
    },
    {
        "id": "U4-keine-heterogenitaet",
        "zweck": "drei identische Effekte: Q = 0, tau^2 = 0, I^2 = 0",
        "rows": [
            {"label": "A", "est": -12.0, "se": 2.0},
            {"label": "B", "est": -12.0, "se": 3.0},
            {"label": "C", "est": -12.0, "se": 4.0},
        ],
        "erwartet": {"q": 0.0, "tau2": 0.0, "i2": 0.0, "pooled": -12.0},
        "toleranz": 1e-9,
    },
    {
        "id": "U5-nur-eine-studie",
        "zweck": "k = 1 darf kein gepooltes Ergebnis behaupten",
        "rows": [{"label": "A", "est": -5.0, "se": 2.0}],
        "erwartet": {"k": 1, "pooled": None},
    },
    {
        "id": "U6-ungueltige-eingaben",
        "zweck": "fehlender Effekt, fehlende SE, SE = 0: k = 0 statt Absturz",
        "rows": [
            {"label": "A", "est": None, "se": 2.0},
            {"label": "B", "est": -10.0, "se": None},
            {"label": "C", "est": -10.0, "se": 0.0},
        ],
        "erwartet": {"k": 0, "pooled": None},
    },
    {
        "id": "U7-fehlende-streuung",
        "zweck": "eine Zeile ohne SE faellt still heraus - k sinkt auf 2",
        "rows": [
            {"label": "A", "est": -10.0, "se": 2.0},
            {"label": "B", "est": -20.0, "se": None},
            {"label": "C", "est": -30.0, "se": 6.0},
        ],
        "erwartet": {"k": 2},
    },
)


def pruefe_unit_fall(fall: dict) -> dict:
    ist = pool(fall["rows"], method="hksj")
    zeilen = []
    for key, soll in fall["erwartet"].items():
        istwert = ist.get(key)
        if soll is None:
            ok = istwert is None
            zeilen.append({"feld": key, "soll": None, "ist": istwert,
                           "status": "PASS" if ok else "FAIL"})
            continue
        if istwert is None:
            zeilen.append({"feld": key, "soll": soll, "ist": None,
                           "status": "FAIL"})
            continue
        abweichung = abs(float(istwert) - float(soll))
        ok = abweichung <= fall.get("toleranz", 1e-9)
        zeilen.append({"feld": key, "soll": soll, "ist": float(istwert),
                       "abweichung": abweichung,
                       "status": "PASS" if ok else "FAIL"})
    return {
        "id": fall["id"],
        "zweck": fall["zweck"],
        "eingabe": fall["rows"],
        "pruefungen": zeilen,
        "ergebnis": "PASS" if all(z["status"] == "PASS" for z in zeilen) else "FAIL",
        "beobachtung": (
            f"excluded-Liste nach dem Filtern: {len(ist.get('excluded') or [])} "
            f"Eintraege, k = {ist.get('k')}"
        ),
    }


def schreibe_bericht(ergebnis: dict) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "e2_pooling_20261108.json").write_text(
        json.dumps(ergebnis, ensure_ascii=False, indent=2),
        encoding="utf-8", newline="\n")

    zeilen = [
        "# E2 - Pooling-Engine offline validiert",
        "",
        f"Stand: {ergebnis['stand']}. Test-ID `{ergebnis['test_id']}`.",
        f"Engine: `{ergebnis['engine']}`. Modellaufrufe: keine. "
        "Netz: keines.",
        f"Referenz: `{ergebnis['referenz']}`, Analyse "
        f"'{ergebnis['analyse']}'. Toleranz: {TOLERANZ}.",
        "",
        "## Kennzahlen gegen die Referenz",
        "",
        "| Kennzahl | Soll | Ist | Abweichung | Art | Ergebnis |",
        "|---|---:|---:|---:|---|---|",
    ]
    for z in ergebnis["kennzahlen"]:
        soll = "-" if z["soll"] is None else f"{z['soll']:.6f}"
        ist = "-" if z["ist"] is None else f"{z['ist']:.6f}"
        abw = "-" if z["abweichung"] is None else f"{z['abweichung']:.2e}"
        zeilen.append(f"| {z['name']} | {soll} | {ist} | {abw} | {z['art']} | "
                      f"**{z['status']}** |")
    zusatz = ergebnis["zusatz"]
    zeilen += [
        "",
        "## Verfahren und Zustand",
        "",
        f"- k = {zusatz['k']}, Methode `{zusatz['method']}`, "
        f"Gewichtung `{zusatz['weight_type']}`",
        f"- SE (HKSJ) = {zusatz['se_hksj']:.6f}",
        f"- Prediction Interval = [{zusatz['pi_low']:.3f}; "
        f"{zusatz['pi_high']:.3f}]",
        f"- Fixed-Effect-Vergleich = {zusatz['fixed']:.4f}",
        f"- Hinweis: {zusatz['small_k_note']}",
        "",
        "## Verhaltensfaelle",
        "",
        "| Fall | Zweck | Ergebnis |",
        "|---|---|---|",
    ]
    for fall in ergebnis["unit_tests"]:
        zeilen.append(f"| `{fall['id']}` | {fall['zweck']} | **{fall['ergebnis']}** |")
    if ergebnis.get("korrekturen"):
        zeilen += ["", "## Korrektur am Testentwurf", "",
                   "Kein Harness-Ergebnis wurde angepasst; korrigiert wurde ein "
                   "falscher Sollwert in diesem Skript.", ""]
        for k in ergebnis["korrekturen"]:
            zeilen.append(f"- **{k['fall']}**: {k['text']}")

    zeilen += ["", "### Einzelpruefungen", ""]
    for fall in ergebnis["unit_tests"]:
        zeilen.append(f"**{fall['id']}** - {fall['beobachtung']}")
        for p in fall["pruefungen"]:
            abw = "" if "abweichung" not in p else f", Abweichung {p['abweichung']:.2e}"
            zeilen.append(f"- `{p['feld']}`: soll {p['soll']} / ist {p['ist']} "
                          f"-> {p['status']}{abw}")
        zeilen.append("")
    zeilen += [
        "## Grenzen",
        "",
        "- Die Verhaltensfaelle pruefen gegen von Hand gerechnete Werte, nicht "
        "gegen R metafor oder statsmodels; ein externer Abgleich bleibt offen.",
        "- Ein gruener Lauf zeigt, dass die Engine die dokumentierten Zahlen "
        "reproduziert. Er zeigt nicht, dass die Eingabewerte korrekt aus den "
        "Studien gelesen wurden - das ist E1.",
        "",
        "## Reproduktion",
        "",
        "```bash",
        "export PYTHONIOENCODING=utf-8",
        ".venv/bin/python.exe scripts/validate_pooling_e2.py",
        "```",
        "",
        f"Laufzeit: {ergebnis['laufzeit_s']:.3f} s. "
        f"Gesamtergebnis: **{ergebnis['gesamt']}**.",
        "",
    ]
    (OUT_DIR / "e2_pooling_20261108.md").write_text(
        "\n".join(zeilen), encoding="utf-8", newline="\n")


def main() -> int:
    start = time.perf_counter()
    referenz = lade_referenz()
    analyse = referenz["analyse"]
    rows = [
        {"label": str(i.get("label")), "est": float(i["est"]), "se": float(i["se"])}
        for i in analyse["inputs"]
    ]

    ist = pool(rows, method="hksj")
    kennzahlen, zusatz = vergleiche(analyse, ist)
    unit = [pruefe_unit_fall(fall) for fall in UNIT_FAELLE]

    alles_ok = (all(z["status"] == "PASS" for z in kennzahlen)
                and all(u["ergebnis"] == "PASS" for u in unit))
    ergebnis = {
        "test_id": "E2-pooling-20261108",
        "stand": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "engine": "research_agent.meta.pooling.pool",
        "referenz": str(REFERENZ.relative_to(ROOT)),
        "analyse": ANALYSE,
        "eingabe": rows,
        "modell": "keiner",
        "netz": "keines",
        "toleranz": TOLERANZ,
        "kennzahlen": kennzahlen,
        "zusatz": zusatz,            "unit_tests": unit,
            "korrekturen": KORREKTUREN,
        "gesamt": "PASS" if alles_ok else "FAIL",
        "laufzeit_s": time.perf_counter() - start,
    }
    schreibe_bericht(ergebnis)

    for z in kennzahlen:
        abw = "-" if z["abweichung"] is None else f"{z['abweichung']:.2e}"
        print(f"{z['kennzahl']:<8} soll {z['soll']!s:>12}  ist {z['ist']!s:>18}  "
              f"abw {abw:>9}  {z['status']}")
    print(f"\nk={zusatz['k']} method={zusatz['method']} "
          f"weight={zusatz['weight_type']}")
    for u in unit:
        print(f"  {u['id']:<30} {u['ergebnis']}")
    print(f"\nGESAMT: {ergebnis['gesamt']}  "
          f"({ergebnis['laufzeit_s']:.3f} s)")
    print(f"Bericht: {OUT_DIR.relative_to(ROOT)}/e2_pooling_20261108.md")
    return 0 if alles_ok else 1


if __name__ == "__main__":
    sys.exit(main())
