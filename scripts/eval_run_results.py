"""Kennzahlen aus einer Topic-DB des Metaanalyse-Agenten auslesen.

Nimmt einen DB-Pfad und schreibt einen Markdown-Report auf stdout.
Verwendet am Ende der Benchaerder-Laeufe (runs a/b/c), um zu beantworten:
„Wie gut ist der Agent ohne Volltextzugriff auf alle Studien?" -
anhand von Abstracts-only vs. Volltext-Quellen, Screening-Entscheidungen,
extrahierten Effekten und Risiko-of-Bias-Urteilen.

Usage:
    python scripts/eval_run_results.py data/research-<slug>-<hash>.db
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from collections import Counter
from pathlib import Path


def q(conn: sqlite3.Connection, sql: str, args: tuple = ()) -> list:
    return conn.execute(sql, args).fetchall()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("db", help="Pfad zur Topic-DB (sqlite)")
    ap.add_argument("--out", default="", help="Pfad für den Report (default: stdout)")
    args = ap.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"DB nicht gefunden: {db_path}", file=sys.stderr)
        return 1
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)

    lines = [f"# Lauf-Auswertung: {db_path.name}"]
    n = lambda sql, a=(): conn.execute(sql, a).fetchone()[0]  # noqa: E731

    # Quellen
    lines.append("## Quellen")
    lines.append(f"- sources gesamt: {n('SELECT COUNT(*) FROM sources')}")
    counts = Counter(kind for (kind,) in q(conn, "SELECT kind FROM source_texts"))
    for kind, cnt in sorted(counts.items()):
        lines.append(f"- source_texts kind={kind}: {cnt}")
    total_chars = n("SELECT COALESCE(SUM(chars),0) FROM source_texts")
    lines.append(f"- source_texts Zeichen gesamt: {total_chars}")

    # Studien / Volltext
    lines.append("## Studienregister")
    lines.append(f"- studies gesamt: {n('SELECT COUNT(*) FROM studies')}")
    lines.append(f"- studies has_fulltext=1: {n('SELECT COUNT(*) FROM studies WHERE has_fulltext=1')}")
    for s, c in sorted(q(conn, "SELECT status, COUNT(*) FROM studies GROUP BY status")):
        lines.append(f"- status={s!r}: {c}")
    for r, c in sorted(q(conn, "SELECT excluded_reason, COUNT(*) FROM studies WHERE excluded_reason IS NOT NULL GROUP BY excluded_reason")):
        lines.append(f"- excluded_reason={r!r}: {c}")

    # Screening
    lines.append("## Screening")
    for d, c in sorted(q(conn, "SELECT decision, COUNT(*) FROM screening GROUP BY decision")):
        lines.append(f"- decision={d!r}: {c}")
    for b, c in sorted(q(conn, "SELECT decided_by, COUNT(*) FROM screening GROUP BY decided_by")):
        lines.append(f"- decided_by={b!r}: {c}")

    # Effekte & Evidenz
    lines.append("## Effekt-Extraktion")
    lines.append(f"- study_effects gesamt: {n('SELECT COUNT(*) FROM study_effects')}")
    for et, c in sorted(q(conn, "SELECT effect_type, COUNT(*) FROM study_effects GROUP BY effect_type")):
        lines.append(f"- effect_type={et!r}: {c}")
    lines.append(f"- study_effects mit CI: {n('SELECT COUNT(*) FROM study_effects WHERE ci_low IS NOT NULL AND ci_high IS NOT NULL')}")
    lines.append(f"- study_effects mit SE: {n('SELECT COUNT(*) FROM study_effects WHERE se IS NOT NULL')}")
    with_quote = n("SELECT COUNT(*) FROM study_effects WHERE quote IS NOT NULL AND length(quote) > 0")
    lines.append(f"- study_effects mit Zitat: {with_quote}")
    lines.append(f"- hypotheses erzeugt: {n('SELECT COUNT(*) FROM hypotheses')}")

    # RoB
    lines.append("## Risiko of Bias")
    for o, c in sorted(q(conn, "SELECT overall, COUNT(*) FROM risk_of_bias GROUP BY overall")):
        lines.append(f"- overall={o!r}: {c}")
    lines.append(f"- dispositioned: {n('SELECT COUNT(*) FROM risk_of_bias WHERE disputed=1')}")

    # Diagnostik
    lines.append("## Historie/Diagnostik")
    rows = q(conn, "SELECT started_at, ended_at, status FROM research_sessions ORDER BY rowid DESC LIMIT 3") \
        if any(r[0] == "research_sessions" for r in q(conn, "PRAGMA table_info(research_sessions)")) else []
    for r in rows:
        lines.append(f"- session: {r}")

    text = "\n".join(lines) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"Report geschrieben: {args.out}")
    else:
        print(text)
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
