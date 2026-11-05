"""
Repair the knowledge graph in the research database.

Problem: duplicated hypothesis claims were stored as separate knowledge_nodes and the
keyword-based edge builder connected every pair of near-identical claims (>30% overlap),
forming dense isolated cliques (e.g. 10 identical transhumanist hypotheses fully
interconnected, disconnected from the rest of the graph).

This script:
1. Groups hypothesis knowledge_nodes by keyword overlap (>80% = near-duplicate)
2. Keeps one canonical node per group (most edges, then longest label, then oldest)
3. Rewires all edges from duplicate nodes to the canonical node
4. Deletes duplicate nodes, self-loop edges, and duplicated edges

Usage:
    python repair_knowledge_graph.py [db_path]
"""

import sqlite3
import sys

DB_PATH = sys.argv[1] if len(sys.argv) > 1 else "data/research.db"
OVERLAP_THRESHOLD = 0.8

STOPWORDS = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
             'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
             'could', 'should', 'may', 'might', 'that', 'this', 'and', 'or',
             'not', 'but', 'for', 'with', 'from', 'in', 'of', 'to', 'by'}


def _label_keywords(label, stopwords=STOPWORDS):
    return {w for w in (label or "").lower().split() if len(w) > 3 and w not in stopwords}


def _keyword_overlap(label_a, label_b, stopwords=STOPWORDS):
    words_a = _label_keywords(label_a, stopwords)
    words_b = _label_keywords(label_b, stopwords)
    if not words_a or not words_b:
        return 0.0
    return len(words_a & words_b) / len(words_a | words_b)


def _edge_count(conn, node_id):
    row = conn.execute(
        "SELECT COUNT(*) c FROM knowledge_edges WHERE source_node_id=? OR target_node_id=?",
        (node_id, node_id),
    ).fetchone()
    return row["c"] if isinstance(row, sqlite3.Row) else row[0]


def downgrade_unevidenced_relations(conn) -> int:
    """Turn "supports"/"contradicts" edges without a backing row into "related_to".

    The old keyword linker labelled every overlap edge "supports" (146 of 164 on
    one corpus) although no evidence row connected the fact's source to the
    hypothesis. New edges are built correctly; this repairs the rows already on
    disk. Direction is only kept when an evidence row names one of the sources
    the fact came from.
    """
    import json

    fact_sources = {}
    for row in conn.execute("SELECT content, source_ids FROM facts"):
        try:
            ids = json.loads(row["source_ids"] or "[]")
        except (TypeError, ValueError):
            continue
        if isinstance(ids, list) and ids:
            fact_sources[row["content"]] = {str(i) for i in ids if i}

    hypothesis_ids = {
        row["claim"]: row["id"]
        for row in conn.execute("SELECT id, claim FROM hypotheses")
    }
    directional = {}
    for row in conn.execute(
        "SELECT hypothesis_id, source_id, evidence_type FROM evidence "
        "WHERE evidence_type IN ('supports','contradicts') AND source_id <> ''"
    ):
        directional.setdefault(row["hypothesis_id"], set()).add(row["source_id"])

    nodes = {
        row["id"]: row["content"]
        for row in conn.execute("SELECT id, content FROM knowledge_nodes")
    }
    downgraded = 0
    for edge in conn.execute(
        "SELECT id, source_node_id, target_node_id, relation FROM knowledge_edges "
        "WHERE relation IN ('supports','contradicts')"
    ).fetchall():
        fact_content = nodes.get(edge["source_node_id"], "")
        hypothesis_id = hypothesis_ids.get(nodes.get(edge["target_node_id"], ""))
        sources = fact_sources.get(fact_content, set())
        backed = bool(hypothesis_id) and bool(
            sources & directional.get(hypothesis_id, set())
        )
        if not backed:
            conn.execute(
                "UPDATE knowledge_edges SET relation='related_to' WHERE id=?",
                (edge["id"],),
            )
            downgraded += 1
    return downgraded


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # --- 1. Load all hypothesis nodes ---
    hyps = conn.execute(
        "SELECT * FROM knowledge_nodes WHERE node_type='hypothesis' ORDER BY date_added ASC"
    ).fetchall()
    print(f"DB: {DB_PATH}")
    print(f"hypothesis nodes: {len(hyps)}")

    # --- 2. Group near-duplicates (>80% keyword overlap) ---
    groups = []
    for h in hyps:
        label = h["label"]
        for g in groups:
            if _keyword_overlap(label, g[0]["label"]) > OVERLAP_THRESHOLD:
                g.append(h)
                break
        else:
            groups.append([h])

    multi_groups = [g for g in groups if len(g) > 1]
    print(f"groups: {len(groups)}, groups with duplicates: {len(multi_groups)}")

    total_removed = 0
    for g in multi_groups:
        # Canonical = most edges, then longest label, then oldest date_added
        canonical = sorted(
            g,
            key=lambda n: (
                -_edge_count(conn, n["id"]),        # most edges first
                -len(n["label"] or ""),            # then longest label
                n["date_added"] or "",             # then oldest date
            ),
        )[0]
        for dup in g:
            if dup["id"] == canonical["id"]:
                continue
            # Rewire edges: any edge touching the duplicate now points to the canonical node
            conn.execute(
                "UPDATE knowledge_edges SET source_node_id=? WHERE source_node_id=?",
                (canonical["id"], dup["id"]),
            )
            conn.execute(
                "UPDATE knowledge_edges SET target_node_id=? WHERE target_node_id=?",
                (canonical["id"], dup["id"]),
            )
            conn.execute("DELETE FROM knowledge_nodes WHERE id=?", (dup["id"],))
            total_removed += 1
            print(f"  merged {dup['id']} -> {canonical['id']}  |  {_safe_label(dup['label'])}")

    # --- 3. Remove self-loops created by rewiring ---
    self_loops = conn.execute(
        "DELETE FROM knowledge_edges WHERE source_node_id = target_node_id"
    ).rowcount

    # --- 4. Remove duplicated edges (same pair + relation, keep one) ---
    dup_edges = conn.execute(
        """DELETE FROM knowledge_edges WHERE id NOT IN (
               SELECT MIN(id) FROM knowledge_edges
               GROUP BY source_node_id, target_node_id, relation
           )"""
    ).rowcount

    conn.commit()

    # --- 4b. Direction is a claim: keep it only where evidence backs it ---
    downgraded = downgrade_unevidenced_relations(conn)
    conn.commit()

    # --- 5. Report ---
    nodes = conn.execute("SELECT COUNT(*) c FROM knowledge_nodes").fetchone()
    edges = conn.execute("SELECT COUNT(*) c FROM knowledge_edges").fetchone()
    print(f"\nmerged/removed nodes: {total_removed}")
    print(f"removed self-loops: {self_loops}")
    print(f"removed duplicate edges: {dup_edges}")
    print(f"downgraded unevidenced supports/contradicts edges: {downgraded}")
    print(f"remaining knowledge_nodes: {nodes['c']}, knowledge_edges: {edges['c']}")

    # Sanity: any self-loops or duplicate hyp-hyp cliques left?
    left_self = conn.execute(
        "SELECT COUNT(*) c FROM knowledge_edges WHERE source_node_id = target_node_id"
    ).fetchone()["c"]
    print(f"remaining self-loops: {left_self}")

    conn.close()
    print("repair complete.")


def _safe_label(label, maxlen=70):
    s = (label or "").replace("\n", " ")
    return s[:maxlen] + ("..." if len(s) > maxlen else "")


if __name__ == "__main__":
    main()
