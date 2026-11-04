"""Goldstandard-Abgleich (Auftrag v2 §9.2/§9.3).

Liest ``data/goldstandard/goldstandard.csv`` und vergleicht gegen die
Run-DB:

- **Pool-Abweichung** — gepoolter Wert des Laufes vs. Referenzwert, mit
  den Toleranzen aus dem Pflegeblatt (PASS |Δ g| ≤ 0.15 UND
  CI-Überschneidung; grenzwertig ≤ 0.30; darüber Abweichung).
- **Studienauswahl (k)** — Decken-Warnung: publizierte Metaanalysen
  decken mehr ab als eine autonome Runde; informativ, kein Fehlerscore.
- **Zahlensextraktion** — Anteil der Zeilen mit Wert, die SE oder CI
  tragen (Lesbarkeitsquote für die Poolschicht).

Ehrlichkeit: Referenzen, die nicht mit „menschlich verifiziert"
einzelnen Abgang erzeugen keinen harten FAIL — ihr Wert wird ausgewertet,
aber als informativ markiert (Warnstempel). Nichts wird still geruhsam
angenommen.
"""

import csv
import logging
from pathlib import Path
from typing import Dict, List, Optional, Sequence

logger = logging.getLogger(__name__)

# Toleranzen aus dem Pflegeblatt (fest, nicht pro Lauf verhandelbar).
_PASS_DELTA = 0.15
_BORDERLAND_DELTA = 0.30

# Skalen des Fundus, die direkt auf die gepoolte Hedges'-g-Skala mappen.
_G_SCALES = {"hedges_g", "smd"}

# Aliase: Goldstandard-Ausgang -> Teile des gepoolten Gruppen-Outcomes
# (deterministische Substringsprüfung, keine Fuzzy-Hokuspokus).
_OUTCOME_ALIASES: Dict[str, Sequence[str]] = {
    "reaktionszeit": ("reaktion", "reaction", "rt"),
    "genauigkeit": ("genauigkeit", "accuracy", "antwortgenauigkeit"),
    "erfolgsrate": ("erfolgsrate", "success rate", "entscheidung", "decision"),
}

def _normalize_entry(raw: dict) -> dict:
    """Ein Fundus-Eintrag erhält seine Zahlenfelder; kaputte Werte werden
    zu None, nicht zu Definitionslosigkeit."""
    entry = {k: (v or "").strip() if isinstance(v, str) else v
             for k, v in raw.items()}
    try:
        entry["wert_num"] = float(str(entry.get("wert") or "").replace(",", "."))
    except (ValueError, TypeError):
        entry["wert_num"] = None
    try:
        entry["k_num"] = int(float(str(entry.get("k") or 0)))
    except (ValueError, TypeError):
        entry["k_num"] = 0
    return entry


def load_benchmark_entries(path) -> List[dict]:
    """Liest den Fundus tolerant; kaputte Zeilen zählen als Eintrag mit
    Grund, nicht als stiller Verlust."""
    rows: List[dict] = []
    try:
        with open(path, encoding="utf-8-sig", newline="") as fh:
            for raw in csv.DictReader(fh):
                entry = _normalize_entry(raw)
                if not entry.get("id"):
                    continue
                rows.append(entry)
    except OSError as e:
        logger.debug(f"Goldstandard-Fundus nicht lesbar: {e}")
    return rows


def resolve_benchmark_csv(db) -> Optional[Path]:
    """Der Fundus liegt neben der Run-DB: data/<name>.db ->
    data/goldstandard/goldstandard.csv. Bei einer In-Memory-DB keine
    Fundus-Suche."""
    db_path = str(getattr(db, "db_path", "") or "")
    if not db_path or getattr(db, "_is_memory", False):
        return None
    candidate = Path(db_path).parent / "goldstandard" / "goldstandard.csv"
    return candidate if candidate.exists() else None


def _match_group(entry: dict, group_name: str) -> bool:
    outcome = str(entry.get("outcome") or "").lower()
    for alias_set_key, aliases in _OUTCOME_ALIASES.items():
        if alias_set_key in outcome:
            group_lower = group_name.lower()
            return any(a in group_lower for a in aliases)
    return False


def run_benchmark(db, entries: Optional[List[dict]] = None,
                  csv_path=None) -> Dict:
    """Vergleicht die Fundus-Einträge gegen die Poolschicht der Run-DB.
    Es werden keine Daten verändert; alles ist Read-only."""
    if entries is not None:
        # Direkt übergebene Einträge (z. B. aus Tests) erhalten dieselben
        # Zahlenfelder wie die geladenen CSV-Zeilen.
        entries = [_normalize_entry(e) for e in entries]
    else:
        entries = []
        if csv_path is None:
            csv_path = resolve_benchmark_csv(db)
        if csv_path:
            entries = load_benchmark_entries(csv_path)
    if not entries:
        return {"available": False, "reason": "kein Fundus geladen"}

    from .pooling import build_analysis
    rows = db.get_study_effects()
    analysis = build_analysis(rows, outcomes=None)
    groups = analysis.get("groups") or {}

    # Zahlensextraktion: Anteil der Zeilen mit Wert, die SE oder CI tragen.
    with_value = 0
    with_precision = 0
    for r in rows:
        if r.get("effect") is None:
            continue
        with_value += 1
        if r.get("se") is not None or r.get("ci_low") is not None:
            with_precision += 1
    coverage = (with_precision / with_value) if with_value else None

    results: List[dict] = []
    counts = {"pass": 0, "grenzwertig": 0, "abweichung": 0,
              "kein_vergleich": 0, "kein_gepools": 0}
    hard_fails = 0
    for entry in entries:
        result = {
            "id": entry.get("id", ""),
            "outcome": entry.get("outcome", ""),
            "referenz": entry.get("wert_num"),
            "referenz_ci": (entry.get("ci_unten"), entry.get("ci_ober")),
            "k_fundus": entry.get("k_num"),
            "verified": "menschlich" in (entry.get("verifizierungszustand") or "").lower(),
            "lauf_wert": None, "lauf_ci": None, "lauf_k": None,
            "delta": None, "verdict": "kein_vergleich", "note": "",
        }

        scale_ok = (entry.get("skala") or "").lower() in _G_SCALES
        if entry.get("wert_num") is None or not scale_ok:
            result["note"] = ("Richtungsbedeutung ohne Vergleichszahlen "
                              "oder Skala ohne Hedges'-g-Abgleich")
            counts[result["verdict"]] += 1
            results.append(result)
            continue

        matched_group = None
        for group_name, group in sorted(groups.items()):
            if (group.get("scale") != "hedges_g"
                    or group.get("pooled") is None):
                continue
            if _match_group(entry, group_name):
                matched_group = group
                break
        if matched_group is None:
            result["verdict"] = "kein_gepools"
            result["note"] = ("kein gepoolter Hedges'-g-Wert für dieses "
                              "Outcome im Lauf")
            counts[result["verdict"]] += 1
            results.append(result)
            continue

        run_pooled = float(matched_group["pooled"])
        run_low = matched_group.get("ci_low")
        run_high = matched_group.get("ci_high")
        gs_low, gs_high = result["referenz_ci"]
        overlap = (
            run_low is not None and run_high is not None
            and gs_low is not None and gs_high is not None
            and float(run_low) <= float(gs_high)
            and float(run_high) >= float(gs_low)
        )
        delta = abs(run_pooled - result["referenz"])
        result.update({
            "lauf_wert": run_pooled,
            "lauf_ci": (run_low, run_high),
            "lauf_k": matched_group.get("k"),
            "delta": round(delta, 4),
        })
        if matched_group.get("k") is not None and result["k_fundus"]:
            if int(matched_group["k"]) < result["k_fundus"]:
                result["note"] = (f"Decken-Warnung: Lauf k = {matched_group['k']} "
                                  f"< Fundus k = {result['k_fundus']} (die publizierte "
                                  "Metaanalyse deckt mehr ab - informativ)")
        if delta <= _PASS_DELTA and overlap:
            result["verdict"] = "pass"
        elif delta <= _BORDERLAND_DELTA:
            result["verdict"] = "grenzwertig"
        else:
            result["verdict"] = "abweichung"
            if result["verified"]:
                hard_fails += 1
        counts[result["verdict"]] += 1
        results.append(result)

    exclude_full = len(analysis.get("excluded") or [])
    off_target = len(analysis.get("off_target") or [])
    return {
        "available": True,
        "total_refs": len(entries),
        "results": results,
        "counts": counts,
        "hard_fails": hard_fails,
        "n_with_value": with_value,
        "n_with_precision": with_precision,
        "extraction_coverage": coverage,
        "excluded": exclude_full,
        "off_target": off_target,
    }


def format_benchmark_lines(bench: Dict) -> List[str]:
    """Berichtstext für den Goldstandard-Abgleich — zählt, statt Tonfall."""
    lines: List[str] = []
    if not bench.get("available"):
        return lines
    counts = bench.get("counts") or {}
    lines.append(
        f"- Fundus: {bench.get('total_refs', 0)} Referenz-Einträge — "
        f"pass: {counts.get('pass', 0)}, grenzwertig: {counts.get('grenzwertig', 0)}, "
        f"Abweichung: {counts.get('abweichung', 0)}, "
        f"kein gepoolter Wert im Lauf: {counts.get('kein_gepools', 0)}, "
        "kein Zahlenvergleich möglich: "
        f"{counts.get('kein_vergleich', 0)}."
    )
    xs = bench.get("extraction_coverage")
    if xs is not None:
        lines.append(
            f"- Zahlensextraktion: {bench.get('n_with_precision', 0)} von "
            f"{bench.get('n_with_value', 0)} Zeilen mit Wert tragen SE oder CI "
            f"({xs:.0%}) — die Übrigen werden gezählt, nicht gepoolt."
        )
        lines.append(
            f"- Aus der Poolung ausgegliedert: {bench.get('excluded', 0)} Zeilen "
            f"(Gründe s. Tabelle); außerhalb des Zielmaßes: "
            f"{bench.get('off_target', 0)}."
        )
    if bench.get("hard_fails"):
        lines.append(
            f"- HARTE Abweichungen (Referenzwert als menschlich verifiziert "
            "gültig): "
            f"{bench['hard_fails']}"
        )
    for result in bench.get("results") or []:
        verdict = result.get("verdict", "?")
        stamp = "" if result.get("verified") else " (Referenz nicht menschlich verifiziert — informativ)"
        if verdict in ("pass", "grenzwertig", "abweichung"):
            lines.append(
                f"  - {result.get('id')} [{verdict}]: Referenz "
                f"{result.get('referenz')} vs. Lauf-Wert {result.get('lauf_wert')} "
                f"(Δ = {result.get('delta')}, Lauf k = {result.get('lauf_k')}, "
                f"Fundus k = {result.get('k_fundus')}){stamp}"
            )
        elif result.get("note"):
            lines.append(f"  - {result.get('id')} [{verdict}]: {result['note']}{stamp}")
    return lines
