#!/usr/bin/env python3
"""
Clean data-quality issues in data/research.db:
1. Deduplicate facts (identical content, merge source_ids)
1b. Delete facts with no resolvable source and facts on off-topic subjects
2. Deduplicate evidence (hypothesis+source+content)
3. Delete orphaned embeddings (entity no longer exists)
4. Deduplicate journal entries (session+cycle, keep richest)
5. Close stale 'active' sessions (no recent activity)
6. Rebuild knowledge graph: drop isolated nodes, dedupe near-identical labels,
   merge duplicate edges

Run with --dry-run to preview, and --only to run selected sections only.
NOT safe while agent is writing (WAL).
Usage: .venv/bin/python.exe clean_data_quality.py [--dry-run] [--only 1,2,4]
"""
import sqlite3, json, sys, re
from collections import defaultdict

DB = "data/research.db"

# Off-topic subjects that reached the facts table through search hits that only
# shared a keyword with the research topic. Kept next to the cleanup so the rule
# is reproducible; memory/store.py gates new facts at extraction time.
OFF_TOPIC_FACT_PATTERNS = [
    r"digital twin", r"cost accounting", r"tamil ?nadu",
    r"\bpsa\b", r"prostate", r"cancer-free",
    r"machine intelligence|turing test",
    r"artificial general intelligence|\bagi\b",
    r"telecom|cyber ?security|data protection act",
    r"muhasebe",
    r"volumetric controllability|laplacian dynamics|controllability score",
    r"wireless|multicast|antenna",
    r"artificial intelligence act|conformity assessment",
    r"expected exposure accuracy",
    r"published on \d{4}-|\bwas published in\b|\bwas accepted to\b",
]

STOP = {"the","a","an","is","are","was","were","be","been","have","has","had","do","does","did",
        "will","would","could","should","may","might","that","this","and","or","not","but","for",
        "with","from","in","of","to","by","wird","werden","der","die","das","und","oder",
        "für","mit","von","auf","bei","nicht"}


def _keywords(s):
    return {w for w in re.findall(r"[a-zA-Z]{4,}", (s or "").lower()) if w not in STOP}


def _overlap(a, b):
    A, B = _keywords(a), _keywords(b)
    if not A or not B:
        return 0.0
    return len(A & B) / len(A | B)


# ---------- 1. Deduplicate facts ----------
def dedup_facts(cur, dry, stats):
    print("[1] Facts dedup...")
    rows = cur.execute("SELECT id, content, source_ids, confidence, date_added FROM facts ORDER BY date_added ASC").fetchall()
    groups = defaultdict(list)
    for r in rows:
        groups[r["content"].strip().lower()].append(r)

    to_delete, merged_src = [], 0
    for key, g in groups.items():
        if len(g) <= 1:
            continue
        keep = g[0]  # oldest
        old_refs = []
        try:
            old_refs = json.loads(keep["source_ids"])
        except Exception:
            old_refs = []
        for dup in g[1:]:
            to_delete.append(dup["id"])
            try:
                old_refs.extend(json.loads(dup["source_ids"]))
            except Exception:
                pass
        # dedupe + keep only valid refs
        seen, valid = set(), []
        for i in old_refs:
            if i and i not in seen:
                seen.add(i)
                valid.append(i)
        merged_src += len(valid)
        if not dry:
            cur.execute("UPDATE facts SET source_ids = ? WHERE id = ?", (json.dumps(valid), keep["id"]))
    # drop refs to nonexistent sources
    src_ids = {r["id"] for r in cur.execute("SELECT id FROM sources").fetchall()}
    for r in cur.execute("SELECT id, source_ids FROM facts").fetchall():
        try:
            refs = json.loads(r["source_ids"])
        except Exception:
            continue
        valid = [i for i in refs if i in src_ids]
        if valid != refs:
            merged_src += 1
            if not dry:
                cur.execute("UPDATE facts SET source_ids = ? WHERE id = ?", (json.dumps(valid), r["id"]))
    stats["facts_deleted"] = len(to_delete)
    stats["facts_refs_fixed"] = merged_src
    if not dry:
        cur.executemany("DELETE FROM facts WHERE id = ?", [(i,) for i in to_delete])
    print(f"  delete {len(to_delete)} duplicate facts, fix {merged_src} source refs")


# ---------- 1b. Off-topic and sourceless facts ----------
def delete_offtopic_facts(cur, dry, stats):
    """Facts whose source row is gone cannot be checked against anything, and
    facts whose subject is a different field (accounting, telecoms law, oncology
    biomarkers, control theory, machine-intelligence tests) came in through
    search hits that only shared a keyword with the topic."""
    print("[1b] Off-topic and sourceless facts...")
    off_topic_re = re.compile("|".join(OFF_TOPIC_FACT_PATTERNS), re.IGNORECASE)
    valid_src = {r["id"] for r in cur.execute("SELECT id FROM sources").fetchall()}
    to_delete, reasons = [], {"sourceless": 0, "off_topic": 0}
    for r in cur.execute("SELECT id, content, source_ids FROM facts").fetchall():
        try:
            refs = json.loads(r["source_ids"] or "[]")
        except Exception:
            refs = []
        if not [i for i in refs if i in valid_src]:
            to_delete.append(r["id"])
            reasons["sourceless"] += 1
        elif off_topic_re.search(r["content"] or ""):
            to_delete.append(r["id"])
            reasons["off_topic"] += 1
    stats["facts_sourceless_deleted"] = reasons["sourceless"]
    stats["facts_offtopic_deleted"] = reasons["off_topic"]
    if not dry:
        cur.executemany("DELETE FROM facts WHERE id = ?", [(i,) for i in to_delete])
        cur.executemany("DELETE FROM embeddings WHERE entity_type = 'fact' AND entity_id = ?",
                        [(i,) for i in to_delete])
    print(f"  delete {len(to_delete)} facts ({reasons['sourceless']} sourceless, "
          f"{reasons['off_topic']} off-topic)")


# ---------- 2. Deduplicate evidence ----------
def dedup_evidence(cur, dry, stats):
    print("[2] Evidence dedup...")
    rows = cur.execute("""SELECT id, hypothesis_id, source_id, content, evidence_type, strength
                          FROM evidence WHERE content != '' ORDER BY date_added ASC""").fetchall()
    groups = defaultdict(list)
    for r in rows:
        key = (r["hypothesis_id"], r["source_id"], r["content"].strip()[:200])
        groups[key].append(r)
    to_delete = []
    for key, g in groups.items():
        if len(g) <= 1:
            continue
        keep = g[0]
        if keep["strength"] == 0:
            # keep highest-strength variant instead
            keep = max(g, key=lambda x: x["strength"])
        for dup in g:
            if dup["id"] != keep["id"]:
                to_delete.append(dup["id"])
    stats["evidence_deleted"] = len(to_delete)
    if not dry:
        cur.executemany("DELETE FROM evidence WHERE id = ?", [(i,) for i in to_delete])
    print(f"  delete {len(to_delete)} duplicate evidence rows")

    # Deleting rows leaves their ids in the hypotheses' evidence lists, where
    # they inflate the cumulative support/contradict counts used for status.
    # Prune ids that no longer resolve to a row.
    ev_ids = {r["id"] for r in cur.execute("SELECT id FROM evidence")} - set(to_delete)
    pruned = touched = 0
    for h in cur.execute("SELECT id, supporting_evidence, contradicting_evidence FROM hypotheses").fetchall():
        updates = {}
        for field in ("supporting_evidence", "contradicting_evidence"):
            try:
                refs = json.loads(h[field] or "[]")
            except Exception:
                refs = []
            valid = [i for i in refs if i in ev_ids]
            if len(valid) != len(refs):
                updates[field] = json.dumps(valid)
                pruned += len(refs) - len(valid)
        if updates:
            touched += 1
            if not dry:
                sets = ", ".join(f"{k} = ?" for k in updates)
                cur.execute(f"UPDATE hypotheses SET {sets} WHERE id = ?", list(updates.values()) + [h["id"]])
    stats["evidence_refs_pruned"] = pruned
    print(f"  prune {pruned} dangling evidence refs in {touched} hypotheses")


# ---------- 3. Delete orphaned embeddings ----------
def delete_orphan_embeddings(cur, dry, stats):
    print("[3] Orphaned embeddings...")
    map_type_tbl = {"source": "sources", "fact": "facts", "hypothesis": "hypotheses",
                    "claim": "claims", "question": "research_questions"}
    total_orphan = 0
    for et, tbl in map_type_tbl.items():
        n = cur.execute(
            f"SELECT COUNT(*) FROM embeddings WHERE entity_type = ? AND entity_id NOT IN (SELECT id FROM {tbl})",
            (et,)).fetchone()[0]
        total_orphan += n
        if not dry:
            cur.execute(f"DELETE FROM embeddings WHERE entity_type = ? AND entity_id NOT IN (SELECT id FROM {tbl})", (et,))
    stats["embeddings_deleted"] = total_orphan
    print(f"  delete {total_orphan} orphaned embeddings")


# ---------- 4. Deduplicate journal entries (session+cycle) ----------
def dedup_journal(cur, dry, stats):
    print("[4] Journal dedup...")
    rows = cur.execute("""SELECT id, session_id, cycle_number,
                          LENGTH(important_findings) + LENGTH(sources_investigated) AS richness
                          FROM journal_entries ORDER BY richness DESC""").fetchall()
    groups = defaultdict(list)
    for r in rows:
        groups[(r["session_id"], r["cycle_number"])].append(r)
    to_delete = []
    for key, g in groups.items():
        if len(g) <= 1:
            continue
        to_delete.extend(x["id"] for x in g[1:])
    stats["journal_deleted"] = len(to_delete)
    if not dry:
        cur.executemany("DELETE FROM journal_entries WHERE id = ?", [(i,) for i in to_delete])
    print(f"  delete {len(to_delete)} duplicate journal entries")


# ---------- 5. Close stale sessions ----------
def close_stale_sessions(cur, dry, stats):
    print("[5] Close stale sessions...")
    # Keep the most recent active session open (that is the one the agent would
    # resume) and close the rest. Picking the one with the most journal entries
    # kept the oldest crashed run and closed the current session.
    most_recent_active = cur.execute(
        "SELECT id FROM research_sessions WHERE status='active' ORDER BY start_time DESC LIMIT 1"
    ).fetchone()
    keep_id = most_recent_active["id"] if most_recent_active else ""
    to_close = [r["id"] for r in cur.execute("SELECT id FROM research_sessions WHERE status='active'").fetchall() if r["id"] != keep_id]
    stats["sessions_closed"] = len(to_close)
    if not dry:
        for sid in to_close:
            end = cur.execute("SELECT MAX(timestamp) FROM journal_entries WHERE session_id = ?", (sid,)).fetchone()[0] or ""
            cur.execute("""UPDATE research_sessions SET status='completed', end_time=?
                           WHERE id = ? AND end_time = ''""", (end, sid))
    print(f"  close {len(to_close)} stale sessions (keep current {keep_id[:8]}... open)")


# ---------- 6. Knowledge graph rebuild ----------
def rebuild_knowledge_graph(cur, dry, stats):
    print("[6] Knowledge graph...")
    # 6a. Dedupe near-identical hypothesis labels (keyword overlap > 0.8) FIRST
    hyp_nodes = cur.execute("SELECT id, label FROM knowledge_nodes WHERE node_type='hypothesis' ORDER BY date_added ASC").fetchall()
    groups = []
    for n in hyp_nodes:
        for g in groups:
            if _overlap(n["label"], g[0]["label"]) > 0.8:
                g.append(n)
                break
        else:
            groups.append([n])
    merge_map, removed_nodes = {}, 0
    for g in groups:
        if len(g) <= 1:
            continue
        canonical = g[0]
        for dup in g[1:]:
            merge_map[dup["id"]] = canonical["id"]
            removed_nodes += 1
    if not dry:
        for dup_id, can_id in merge_map.items():
            cur.execute("UPDATE knowledge_edges SET source_node_id = ? WHERE source_node_id = ?", (can_id, dup_id))
            cur.execute("UPDATE knowledge_edges SET target_node_id = ? WHERE target_node_id = ?", (can_id, dup_id))
            cur.execute("DELETE FROM knowledge_nodes WHERE id = ?", (dup_id,))
    # 6b. Drop zero-weight edges and merge duplicate edges.
    # Nodes are pruned by *provenance*, not connectivity: a node that still
    # describes a live fact or hypothesis is valid even while no edge points at
    # it (the keyword linker creates edges in batches, so freshly rebuilt nodes
    # are unconnected for a while). Deleting every isolated node removed the
    # whole graph the moment it was rebuilt.
    stale_nodes = cur.execute("""SELECT COUNT(*) FROM knowledge_nodes k
        WHERE NOT EXISTS (SELECT 1 FROM facts f WHERE f.content = k.content)
          AND NOT EXISTS (SELECT 1 FROM hypotheses h WHERE h.claim = k.content)""").fetchone()[0]
    if not dry:
        cur.execute("DELETE FROM knowledge_edges WHERE weight <= 0")
        cur.execute("DELETE FROM knowledge_edges WHERE source_node_id = target_node_id")
        cur.execute("""DELETE FROM knowledge_edges WHERE id NOT IN (
            SELECT MIN(id) FROM knowledge_edges GROUP BY source_node_id, target_node_id, relation)""")
        cur.execute("""DELETE FROM knowledge_nodes WHERE NOT EXISTS
            (SELECT 1 FROM facts f WHERE f.content = knowledge_nodes.content)
          AND NOT EXISTS (SELECT 1 FROM hypotheses h WHERE h.claim = knowledge_nodes.content)""")
        cur.execute("""DELETE FROM knowledge_edges WHERE source_node_id NOT IN (SELECT id FROM knowledge_nodes)
            OR target_node_id NOT IN (SELECT id FROM knowledge_nodes)""")
    nodes_before = cur.execute("SELECT COUNT(*) FROM knowledge_nodes").fetchone()[0]
    edges_after = cur.execute("SELECT COUNT(*) FROM knowledge_edges").fetchone()[0]
    nodes_after = cur.execute("SELECT COUNT(*) FROM knowledge_nodes").fetchone()[0]
    stats["kg_nodes_before"] = nodes_before
    stats["kg_nodes_merged"] = removed_nodes
    stats["kg_stale_nodes_deleted"] = stale_nodes
    stats["kg_nodes_after"] = nodes_after
    stats["kg_edges_after"] = edges_after
    print(f"  nodes: {nodes_before} -> {nodes_after} (merged {removed_nodes} duplicates, "
          f"{stale_nodes} stale without a live fact/hypothesis), edges now: {edges_after}")


SECTIONS = [
    ("1", dedup_facts),
    ("1b", delete_offtopic_facts),
    ("2", dedup_evidence),
    ("3", delete_orphan_embeddings),
    ("4", dedup_journal),
    ("5", close_stale_sessions),
    ("6", rebuild_knowledge_graph),
]


def main():
    dry = "--dry-run" in sys.argv
    only = set()
    if "--only" in sys.argv:
        raw = sys.argv[sys.argv.index("--only") + 1] if len(sys.argv) > sys.argv.index("--only") + 1 else ""
        only = {s.strip().lower() for s in re.split(r"[,\s]+", raw) if s.strip()}

    conn = sqlite3.connect(DB, timeout=30)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    stats = {}
    try:
        for name, fn in SECTIONS:
            if only and name not in only:
                continue
            fn(cur, dry, stats)
        if dry:
            conn.rollback()
            print("\nDRY RUN - no changes written.")
        else:
            conn.commit()
            cur.execute("VACUUM")
            print("\nCommitted + VACUUM.")
        print("\nSTATS:", json.dumps(stats, indent=2))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
