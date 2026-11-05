"""Referenz-Reports end-to-end erzeugen (Implementierungsplan T1).

Baut vollstaendige Closing-Reports aus den Referenz-DBs (Exercise /
Mediterrane / Kognition) auf BYTE-IDENTISCHEN KOPIEN der Datenbanken, damit
die Original-DBs garantiert unveraendert bleiben. Fuer jede DB wird
gespeichert: DB-Hash (vor/nach), Git-Commit, Zeitstempel und der gepoolte
Effekt aus dem Report. Der gepoolte Wert wird zusaetzlich mit einer
unabhaengigen DerSimonian-Laird-Nachrechnung aus `study_effects`
verglichen.

Usage:
    python scripts/build_reference_reports.py
"""

from __future__ import annotations

import hashlib
import json
import math
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT_DIR = ROOT / "data" / "reports"
REG_DIR = ROOT / "data" / "bench" / "regreports"

REFERENCE_DBS = {
    "exercise": "data/research-exercise-and-depressive-symptoms-in-adul-bbb324.db",
    "mediterran": "data/research-mediterrane-ernaehrung-und-kardiovaskula-475855.db",
    "kognition": "data/research-kognition-und-gesundheit-ist-der-zusamme-ec45a1.db",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT,
            capture_output=True, text=True, timeout=15,
        ).stdout.strip()
    except OSError:
        return "unknown"


def main_topic(conn: sqlite3.Connection) -> str:
    row = conn.execute(
        "SELECT topic FROM research_sessions ORDER BY start_time LIMIT 1"
    ).fetchone()
    return str(row[0]) if row else "topic"


def dl_recheck(db_path: Path) -> list[dict]:
    """Unabhaengige DL-Poolung je (effect_type, outcome, unit)-Gruppe.

    Nur Zeilen mit se>0, keinerlei RVE-Korrektur - bewusst simpel und
    unabhaengig von research_agent.meta.pooling.
    """
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    rows: list[dict] = []
    try:
        q = conn.execute(
            "SELECT effect_type, outcome, unit, effect, se, rejection_reason"
            " FROM study_effects"
        )
        groups: dict[tuple, list[tuple]] = {}
        for et, outcome, unit, eff, se, rej in q:
            if eff is None or se is None or float(se) <= 0:
                continue
            if rej:
                continue
            groups.setdefault((str(et), str(outcome or "?"), str(unit or "?")),
                              []).append((float(eff), float(se)))
        for (et, outcome, unit), vals in sorted(groups.items()):
            if len(vals) < 2:
                continue
            w = [1.0 / se**2 for _e, se in vals]
            fixed = sum(wi * e for wi, (e, _s) in zip(w, vals)) / sum(w)
            q_stat = sum(wi * (e - fixed) ** 2
                         for wi, (e, _s) in zip(w, vals))
            df = len(vals) - 1
            c = sum(w) - sum(wi * wi for wi in w) / sum(w)
            tau2 = max(0.0, (q_stat - df) / c) if c > 0 else 0.0
            w_rand = [1.0 / (se * se + tau2) for _e, se in vals]
            dl = sum(wi * e for wi, (e, _s) in zip(w_rand, vals)) / sum(w_rand)
            se_dl = math.sqrt(1.0 / sum(w_rand))
            rows.append({
                "outcome": outcome, "effect_type": et, "unit": unit,
                "k": len(vals), "q": round(q_stat, 4), "df": df,
                "tau2": round(tau2, 6),
                "dl_estimate": round(dl, 4), "dl_se": round(se_dl, 4),
                "dl_ci": [round(dl - 1.96 * se_dl, 4),
                          round(dl + 1.96 * se_dl, 4)],
            })
    finally:
        conn.close()
    return rows


def parse_report_meta(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    start = text.find("## Metaanalyse")
    stop = text.find("## Limitationen")
    section = text[start:stop] if 0 <= start < stop else ""
    info: dict = {}
    for pat, key in [
        ("Gepoolter Effekt", "gepoolter_effekt"),
    ]:
        idx = section.find(pat)
        info[key] = section[idx: idx + 400].split("\n")[0] if idx >= 0 else None
    for line in section.splitlines():
        s = line.strip()
        if s.startswith("| Effektzeilen gesamt"):
            info["effektzeilen_gesamt"] = s.split("|")[2].strip()
        if s.startswith("| Gepoolte Studien"):
            info["gepoolte_studien"] = s.split("|")[2].strip()
        if "estimate" in s.lower() and "[" in s:
            info.setdefault("pooling_verweis", []).append(s[:160])
    info["section_chars"] = len(section)
    return info


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REG_DIR.mkdir(parents=True, exist_ok=True)
    commit = git_commit()
    from research_agent.database import Database
    from research_agent.report import build_report

    summary = {"commit": commit, "started": datetime.now(timezone.utc).isoformat(),
               "reports": []}
    for name, src_rel in REFERENCE_DBS.items():
        src = ROOT / src_rel
        if not src.exists():
            print(f"[SKIP] {name}: {src} fehlt", file=sys.stderr)
            continue
        hash_before = sha256(src)
        copy = REG_DIR / src.name
        shutil.copy2(src, copy)

        rw_conn = sqlite3.connect(copy)
        topic = main_topic(rw_conn)
        rw_conn.close()

        db = Database(str(copy))
        reason = "T1 Referenz-Report (Byte-Kopie; Implementierungsplan 05.11.2026)"
        md_path = build_report(db, topic, reason=reason, out_dir=str(OUT_DIR))
        report_md = Path(md_path)
        pdf = report_md.with_suffix(".pdf")

        meta = {
            "name": name,
            "topic": topic,
            "db_source": src_rel,
            "db_copy": str(copy.relative_to(ROOT)),
            "db_sha256_before": hash_before,
            "db_sha256_after": sha256(copy),
            "db_identity_kept": sha256(copy) == hash_before,
            "db_sha256_source_now": sha256(src),
            "source_untouched": sha256(src) == hash_before,
            "commit": commit,
            "report_md": str(report_md.relative_to(ROOT)),
            "report_pdf": (str(pdf.relative_to(ROOT)) if pdf.exists()
                           else None),
            "created": datetime.now(timezone.utc).isoformat(),
            "report_meta": parse_report_meta(report_md),
            "dl_recheck": dl_recheck(copy),
        }
        out_json = REG_DIR / f"{name}_report_meta.json"
        out_json.write_text(json.dumps(meta, indent=2, ensure_ascii=False),
                            encoding="utf-8")
        meta["meta_json"] = str(out_json.relative_to(ROOT))
        summary["reports"].append(meta)
        print(f"[OK] {name}: {report_md.name} "
              f"(Source-DB unveraendert: {meta['source_untouched']})")

    summary["finished"] = datetime.now(timezone.utc).isoformat()
    (REG_DIR / "t1_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Zusammenfassung:", REG_DIR / "t1_summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
