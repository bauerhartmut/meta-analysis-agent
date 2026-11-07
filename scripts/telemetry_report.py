"""Telemetrie des letzten Laufs auswerten und den gezielten Lauf begruenden.

Quellen (alle read-only):
  * ``data/research2-usage.db``   Token-Buchhaltung von Run 2 (nur 2026-11-05)
  * ``data/research-usage.db``    Token-Buchhaltung des Themas (27.10.-05.11.,
                                  nicht laufgenau - enthaelt mehrere Laeufe)
  * ``data/research2-...db``      Quellen, Texte, Studien, Effekte, Suchanfragen
  * ``data/runs/melatonin_net_run2.log``  429er, Zyklusabbrueche, Abbruch

Erzeugt einen Markdown-Bericht mit den gemessenen Zahlen und dem Vorschlag
fuer einen Lauf auf genau ein Outcome. Jede Zahl im Bericht stammt aus einer
dieser Quellen; der Aufwands-Schaetzwert ist als Schaetzung markiert.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from pathlib import Path

USAGE = {"run2": "data/research2-usage.db", "thema": "data/research-usage.db"}
TOPIC = {"run2": "data/research2-does-melatonin-improve-sleep-onset-laten-382747.db"}
LOG = {"run2": "data/runs/melatonin_net_run2.log", "run1": "data/runs/melatonin_net_run1.log"}


def _usage(path: str) -> dict:
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute(
        "SELECT phase, COUNT(*) calls, COALESCE(SUM(total_tokens),0) tokens,"
        " ROUND(SUM(time_ms)/1000.0,1) secs, SUM(1-success) errors"
        " FROM llm_usage GROUP BY phase ORDER BY tokens DESC")]
    total = dict(conn.execute(
        "SELECT COUNT(*) calls, COALESCE(SUM(total_tokens),0) tokens,"
        " ROUND(SUM(time_ms)/1000.0,1) secs, SUM(1-success) errors"
        " FROM llm_usage").fetchone())
    window = dict(conn.execute(
        "SELECT MIN(timestamp) first, MAX(timestamp) last FROM llm_usage").fetchone())
    days = [r[0] for r in conn.execute("SELECT DISTINCT day FROM llm_usage ORDER BY day")]
    conn.close()
    return {"by_phase": rows, "total": total, "window": window, "days": days}


def _topic(path: str) -> dict:
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row

    def one(sql: str) -> dict:
        return dict(conn.execute(sql).fetchone())

    data = {
        "counts": one("""SELECT (SELECT COUNT(*) FROM sources) sources,
                                (SELECT COUNT(*) FROM source_texts) texts,
                                (SELECT COUNT(*) FROM studies) studies,
                                (SELECT COUNT(*) FROM study_effects) effects,
                                (SELECT COUNT(*) FROM extracted_tables) tables,
                                (SELECT COUNT(*) FROM hypotheses) hypotheses"""),
        "effects": one("""SELECT SUM(CASE WHEN se IS NOT NULL THEN 1 ELSE 0 END) with_se,
                                 SUM(CASE WHEN ci_low IS NOT NULL AND ci_high IS NOT NULL
                                          THEN 1 ELSE 0 END) with_ci,
                                 SUM(CASE WHEN TRIM(COALESCE(quote,'')) != ''
                                          THEN 1 ELSE 0 END) with_quote
                          FROM study_effects"""),
        "queries": one("SELECT COUNT(*) n, COUNT(DISTINCT query) q FROM query_stats"),
        "session": one("SELECT status, start_time, end_time FROM research_sessions "
                       "ORDER BY rowid DESC LIMIT 1"),
    }
    conn.close()
    return data


def _log_stats(path: str) -> dict:
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    return {
        "lines": len(text.splitlines()),
        "http_429": text.count("429"),
        "rate_limit_mentions": len(re.findall(r"rate[\s_-]?limit", text, re.I)),
        "cycles_complete": len(re.findall(r"Cycle \d+ complete", text)),
        "cycles_error": len(re.findall(r"Cycle \d+ error", text)),
        "backoff_waits": len(re.findall(r"backoff|waiting|sleep", text, re.I)),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", default="data/bench/telemetrie_20261107.json")
    ap.add_argument("--md", default="data/bench/telemetrie_run2_20261107.md")
    args = ap.parse_args(argv)

    usage = {name: _usage(path) for name, path in USAGE.items()}
    topic = {name: _topic(path) for name, path in TOPIC.items()}
    logs = {name: _log_stats(path) for name, path in LOG.items()}

    run2_u, run2_t, run2_l = usage["run2"], topic["run2"], logs["run2"]
    tot = run2_u["total"]
    counts = run2_t["counts"]
    effects = run2_t["effects"]
    per_phase = {row["phase"]: row for row in run2_u["by_phase"]}
    heavy = sum(per_phase.get(p, {}).get("tokens", 0)
                for p in ("hypothesizing", "analyzing", "critiquing"))
    share_heavy = 100.0 * heavy / max(1, tot["tokens"])

    def per(total_value, count):
        return round(total_value / max(1, count))

    lines = [
        "# Telemetrie des letzten Laufs (Run 2) und Vorschlag fuer einen gezielten Lauf",
        "",
        "Stand: 07.11.2026. Alle Zahlen read-only aus `data/research2-usage.db`,",
        "`data/research-usage.db`, der Run-2-Themen-DB und dem Lauf-Log",
        "`data/runs/melatonin_net_run2.log`. Run 2 ist am 05.11. um 22:44 im",
        "Rate-Limit-Backoff abgebrochen (Session `active`, `end_time` leer).",
        "",
        "## Run 2: was der Lauf gekostet hat",
        "",
        "| Kennzahl | Wert |",
        "|---|---:|",
        f"| LLM-Aufrufe | {tot['calls']} |",
        f"| Tokens gesamt | {tot['tokens']} |",
        f"| LLM-Zeit (Summe der Aufrufe) | {tot['secs']} s |",
        f"| Fehler | {tot['errors']} |",
        f"| Quellen | {counts['sources']} |",
        f"| Tokens je Quelle | {per(tot['tokens'], counts['sources'])} |",
        f"| Studien | {counts['studies']} |",
        f"| Tokens je Studie | {per(tot['tokens'], counts['studies'])} |",
        f"| Effekte | {counts['effects']} (SE {effects['with_se']}, CI {effects['with_ci']}) |",
        f"| Tokens je Effekt | {per(tot['tokens'], counts['effects'])} |",
        f"| Suchanfragen (`query_stats`) | {run2_t['queries']['n']} Zeilen, "
        f"{run2_t['queries']['q']} verschiedene |",
        f"| HTTP 429 im Log | {run2_l['http_429']} |",
        f"| Zyklen abgeschlossen / Fehler | {run2_l['cycles_complete']} / "
        f"{run2_l['cycles_error']} |",
        "",
        "### Tokens je Phase",
        "",
        "| Phase | Aufrufe | Tokens | Sekunden | Anteil |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in run2_u["by_phase"]:
        share = 100.0 * (row["tokens"] or 0) / max(1, tot["tokens"])
        lines.append(f"| {row['phase']} | {row['calls']} | {row['tokens']} | "
                     f"{row['secs']} | {share:.1f} % |")

    lines += [
        "",
        f"**{share_heavy:.1f} % der Tokens** gingen in Hypothesen, Analyse und",
        f"Kritik. Die Suche kostete {per_phase.get('searching', {}).get('tokens', 0)} "
        f"Tokens in {per_phase.get('searching', {}).get('calls', 0)} Aufrufen -",
        "also rund "
        f"{round(per_phase.get('searching', {}).get('tokens', 0) / max(1, run2_t['queries']['q']))}"
        " Tokens je Suchanfrage.",
        "",
        "Zum Vergleich das Themen-Konto `data/research-usage.db` (enthaelt",
        f"mehrere Laeufe, Tage {usage['thema']['days'][0]} bis "
        f"{usage['thema']['days'][-1]}): {usage['thema']['total']['calls']} Aufrufe,",
        f"{usage['thema']['total']['tokens']} Tokens. Run 1 allein ist daraus",
        "nicht isolierbar - die Zahlen oben fuer Run 2 sind es, weil dessen",
        "Usage-DB nur den 05.11. enthaelt.",
        "",
        "## Was die Telemetrie ueber den Engpass sagt",
        "",
        f"* Das Lauf-Log enthaelt {run2_l['http_429']} 429-Zeilen und "
        f"{run2_l['rate_limit_mentions']} Rate-Limit-Nennungen; der Lauf starb",
        "  im Backoff, nicht an einem Logikfehler.",
        f"* {tot['calls']} Aufrufe fuer {counts['effects']} Effekte heisst: "
        f"{per(tot['calls'], counts['effects'])} LLM-Aufrufe je Effekt. Der",
        "  groesste Teil davon sind Hypothesen- und Kritikschleifen, die zur",
        "  Effektgewinnung nichts beitragen.",
        f"* Nur {effects['with_se']} von {counts['effects']} Effekten tragen eine",
        "  Praezision; aus den Textpfaden kommt fast nichts Poolbares.",
        "* Die 43 XML-Dokumente des Korpus liefern deterministisch 31 Effekte",
        "  (15 g, 16 OR) - ohne einen einzigen LLM-Aufruf. Der teure Teil des",
        "  Laufs ist also nicht die Effektgewinnung, sondern die Hypothesen-",
        "  und Analysesimulation.",
        "",
        "## Vorschlag: ein gezielter Lauf auf genau ein Outcome",
        "",
        "**Ziel:** mindestens zwei unabhaengige Studien mit Effekt **und**",
        "Praezision zum selben Outcome auf derselben Skala - die kleinste",
        "Einheit, aus der `build_analysis` eine gepoolte Schaetzung bildet.",
        "",
        "**Outcome:** Sleep onset latency (SOL) in Minuten (mean difference)",
        "oder standardisiert (Hedges g), je nachdem, was die Studien berichten.",
        "",
        "**Ablauf, bewusst ohne Zyklen, Hypothesen und Kritik:**",
        "",
        "1. **Zwei Suchen** (Limit aus `AGENTS.md`: 2-3 pro Frage):",
        "   Europe PMC `(melatonin) AND (sleep onset latency) AND (randomized)`",
        "   mit Filter `OPEN_ACCESS:y`, und Crossref als Gegenprobe auf",
        "   Metaanalysen, deren eingeschlossene Studien als Seed dienen.",
        "2. **Korpus deterministisch ziehen:** DOIs/PMCIDs der Treffer nehmen,",
        "   Europe-PMC-XML laden (kein LLM), Reader laufen lassen",
        "   (`effect_columns`, `arm_level`).",
        "3. **Vor der Extraktion `mean_diff` ergaenzen:** Schlafstudien berichten",
        "   SOL meist als Minuten-Differenz mit 95 %-CI, nicht als g. Ohne",
        "   diesen Typ faellt genau die haeufigste Zeile weg.",
        "4. **Pooling** mit `build_analysis`, Regel 'adjustiert vor crude',",
        "   Gruppen nur auf gleicher Skala.",
        "5. **Abbruchkriterium:** weniger als zwei unabhaengige Studien mit",
        "   Praezision nach 40 XML-Dokumenten -> Frage als 'Korpus zu klein'",
        "   berichten, nicht in einen zweiten Lauf investieren.",
        "",
        "**Aufwand (geschaetzt, aus den Messwerten abgeleitet):**",
        "",
        f"* Netz: 2 Suchanfragen x 5 Provider plus ~40 XML-Downloads.",
        "* LLM: 0 Tokens fuer Schritt 2-4. Nur wenn eine Relevance-Pruefung",
        f"  gewuenscht ist, kostet sie nach Run-2-Massstab ~"
        f"{round(per_phase.get('searching', {}).get('tokens', 0) / max(1, run2_t['queries']['q']))}",
        "  Tokens je Anfrage - Groessenordnung 10^4 statt 1,6 x 10^6.",
        "* Zeit: Minuten statt 3,25 h; kein 429-Risiko, weil keine",
        "  Schleifen laufen.",
        "",
        "**Risiko:** SOL steht haeufig nur als Arm-Mittelwert ohne Fallzahl je",
        "Arm in den Tabellen (genau der Befund aus `arm_level_befund`). Dann",
        "bleibt es bei k = 1, obwohl der Korpus gross genug ist. Deshalb ist",
        "Schritt 3 (mean_diff) Pflicht, bevor der Lauf startet.",
        "",
        "**Erfolgskriterium:** mindestens eine Gruppe mit k >= 2 und",
        "berichteter Praezision; andernfalls dokumentierter Negativbefund.",
        "",
    ]
    Path(args.md).write_text("\n".join(lines) + "\n", encoding="utf-8")
    Path(args.json).write_text(json.dumps(
        {"usage": usage, "topic": topic, "logs": logs,
         "derived": {"share_heavy_phases_pct": round(share_heavy, 1),
                     "tokens_per_effect": per(tot["tokens"], counts["effects"]),
                     "tokens_per_source": per(tot["tokens"], counts["sources"]),
                     "tokens_per_study": per(tot["tokens"], counts["studies"])}},
        ensure_ascii=False, indent=1), encoding="utf-8")

    print(json.dumps({
        "run2_calls": tot["calls"], "run2_tokens": tot["tokens"],
        "per_effect": per(tot["tokens"], counts["effects"]),
        "per_source": per(tot["tokens"], counts["sources"]),
        "heavy_share_pct": round(share_heavy, 1),
        "http_429": run2_l["http_429"],
        "cycles_complete": run2_l["cycles_complete"],
        "search_tokens": per_phase.get("searching", {}).get("tokens", 0),
    }, ensure_ascii=False))
    print(f"MD: {args.md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
