"""Abgleich Goldstandard gegen Pipeline-Extraktion.

Verglichen werden Effektzeilen je Dokument. Der Goldstandard liefert
outcome_normalized, comparison_verbatim, effect_type und effect; die
Pipeline liefert outcome, comparison, effect_type und effect.

Matching ist eine nachvollziehbare Heuristik, kein Modell:
- Aehnlichkeit der Outcomes (Token-Jaccard ohne Stoppwoerter),
- Aehnlichkeit des Vergleichs, wenn beide Seiten ihn nennen,
- gleicher Effekttyp,
- Effekt innerhalb einer relativen Toleranz.
Paare werden absteigend nach Aehnlichkeit greedy zugewiesen, jede Zeile
hoechstens einmal. Die Schwelle ist konfigurierbar und wird im Bericht
ausgewiesen.

Wichtig: Ein Dokument ohne Zeilen und ohne no_effect_reason ist *nicht
annotiert*, nicht "keine Effekte". Solche Dokumente werden ausgelassen,
sonst waere die Precision systematisch falsch.
"""

from __future__ import annotations

import re
from collections import defaultdict

STOPP = frozenset("""
the a an of and or in on for with to vs versus by at from after before during
among between patients participants patient participant group groups effect
effects risk odds hazard ratio mean difference change changes compared
comparison intervention control controls study studies results outcome
outcomes significant significantly
""".split())


def token(text) -> set:
    woerter = re.findall(r"[a-z0-9]+", str(text or "").lower())
    return {w for w in woerter if w not in STOPP and len(w) > 1}


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _zahl(effekt: dict, feld: str):
    wert = effekt.get(feld)
    return wert if isinstance(wert, (int, float)) and not isinstance(wert, bool) else None


def _nah(x, y, toleranz: float) -> bool:
    if x is None or y is None:
        return False
    return abs(x - y) <= max(1e-9, toleranz * max(abs(x), abs(y)))


def aehnlichkeit(gold: dict, pipe: dict, toleranz: float = 0.01) -> float:
    s_out = jaccard(token(gold.get("outcome_normalized") or gold.get("outcome")),
                    token(pipe.get("outcome")))
    g_cmp = token(gold.get("comparison_verbatim"))
    p_cmp = token(pipe.get("comparison"))
    s_cmp = jaccard(g_cmp, p_cmp) if g_cmp and p_cmp else None
    s_typ = 1.0 if (gold.get("effect_type")
                    and gold.get("effect_type") == pipe.get("effect_type")) else 0.0
    s_wert = 1.0 if _nah(_zahl(gold, "effect"), _zahl(pipe, "effect"), toleranz) else 0.0
    if s_cmp is None:
        return 0.65 * s_out + 0.2 * s_typ + 0.15 * s_wert
    return 0.5 * s_out + 0.25 * s_cmp + 0.15 * s_typ + 0.1 * s_wert


def matche(gold: list, pipe: list, schwelle: float = 0.55,
           toleranz: float = 0.01):
    """Greedy-Paarung; Rueckgabe (paare, ungenutzt_gold, ungenutzt_pipeline)."""
    kandidaten = []
    for i, g in enumerate(gold):
        for j, p in enumerate(pipe):
            score = aehnlichkeit(g, p, toleranz)
            if score >= schwelle:
                kandidaten.append((score, i, j))
    kandidaten.sort(reverse=True)

    gi, pj = set(), set()
    paare = []
    for score, i, j in kandidaten:
        if i in gi or j in pj:
            continue
        gi.add(i)
        pj.add(j)
        paare.append((score, gold[i], pipe[j]))
    return (paare,
            [g for i, g in enumerate(gold) if i not in gi],
            [p for j, p in enumerate(pipe) if j not in pj])


def ist_poolbar(zeile: dict) -> bool:
    """Dieselbe Definition wie ``Database.POOLABLE``.

    Nicht strittig, nicht verworfen, mit verifiziertem Zitatbereich und
    einer Praezision (SE oder KI). Eine zweite Definition hier waere eine
    zweite Wahrheit; der Abgleich muss zaehlen, was das Pooling zaehlt.
    """
    if zeile.get("disputed"):
        return False
    if str(zeile.get("rejection_reason") or "").strip():
        return False
    try:
        start = zeile.get("quote_start")
        if start is None or int(start) < 0:
            return False
    except (TypeError, ValueError):
        return False
    return (zeile.get("se") is not None
            or (zeile.get("ci_low") is not None
                and zeile.get("ci_high") is not None))


def _wert_zwilling(zeile: dict):
    effekt = _zahl(zeile, "effect")
    if effekt is None:
        return None
    se = _zahl(zeile, "se")
    return (round(effekt, 9), None if se is None else round(se, 9))


def _zitat_zwilling(zeile: dict):
    text = " ".join(str(zeile.get("quote") or "").split()).lower()[:200]
    return text or None


def dedupe(zeilen: list):
    """Entfernt Wert- und Zitat-Zwillinge, die erste Zeile bleibt.

    Dieselbe Semantik wie ``_drop_zweitlesungen`` in ``meta/pooling.py``:
    Zwilling ist gleiche Quelle plus gleicher Effekt (9 Stellen, SE) oder
    gleicher normalisierter Zitattext (erste 200 Zeichen). Hier ohne
    Pass-Filter, weil der Abgleich die gespeicherte Ausgabe bewertet, nicht
    den Lesepass. Eine Zeile ohne Wert und ohne Quote wird nie verworfen.
    """
    gesehen_wert, gesehen_zitat = set(), set()
    behalten, duplikate = [], 0
    for zeile in zeilen:
        wert = _wert_zwilling(zeile)
        zitat = _zitat_zwilling(zeile)
        if (wert is not None and wert in gesehen_wert) or (
                zitat is not None and zitat in gesehen_zitat):
            duplikate += 1
            continue
        if wert is not None:
            gesehen_wert.add(wert)
        if zitat is not None:
            gesehen_zitat.add(zitat)
        behalten.append(zeile)
    return behalten, duplikate


def _leer() -> dict:
    return {"tp": 0, "fp": 0, "fn": 0, "typ_ok": 0, "wert_ok": 0,
            "pipeline_zeilen": 0, "pipeline_zeilen_annotiert": 0,
            "pipeline_unique": 0, "pipeline_duplikate": 0,
            "unique": 0, "duplikate": 0,
            "poolbar": 0, "poolbar_unique": 0, "poolbar_tp": 0,
            "n_annotiert": 0, "n_offen": 0}


def _abschluss(d: dict) -> dict:
    tp, fp, fn = d["tp"], d["fp"], d["fn"]
    d["precision"] = (tp / (tp + fp)) if (tp + fp) else None
    d["recall"] = (tp / (tp + fn)) if (tp + fn) else None
    d["typquote"] = (d["typ_ok"] / tp) if tp else None
    d["wertquote"] = (d["wert_ok"] / tp) if tp else None
    n = d["pipeline_zeilen_annotiert"]
    d["poolbare_quote"] = (d["poolbar"] / n) if n else None
    d["poolbare_quote_tp"] = (d["poolbar_tp"] / tp) if tp else None
    d["zeilen_pro_dokument"] = (n / d["n_annotiert"]) if d["n_annotiert"] else None
    d["ausbeute_poolbar"] = ((d["poolbar"] / d["n_annotiert"])
                             if d["n_annotiert"] else None)
    d["poolbare_quote_unique"] = ((d["poolbar_unique"] / d["unique"])
                                  if d["unique"] else None)
    d["ausbeute_poolbar_unique"] = ((d["poolbar_unique"] / d["n_annotiert"])
                                    if d["n_annotiert"] else None)
    d["duplikatquote"] = ((d["duplikate"] / n) if n else None)
    d["baseline_duplikatquote"] = ((d["pipeline_duplikate"] / d["pipeline_zeilen"])
                                    if d["pipeline_zeilen"] else None)
    return d


def werte(gold_docs: dict, pipe_docs: dict, docs: list, annotiert: set,
          schwelle: float = 0.55, toleranz: float = 0.01) -> dict:
    gesamt = _leer()
    schichten = defaultdict(_leer)
    details = []

    for doc in docs:
        fid = doc["document_id"]
        schicht = doc["stratum"]
        p = pipe_docs.get(fid, [])
        p_unique, duplikate = dedupe(p)
        for ziel in (gesamt, schichten[schicht]):
            ziel["pipeline_zeilen"] += len(p)
            ziel["pipeline_unique"] += len(p_unique)
            ziel["pipeline_duplikate"] += duplikate

        if fid not in annotiert:
            gesamt["n_offen"] += 1
            schichten[schicht]["n_offen"] += 1
            details.append({"document_id": fid, "stratum": schicht,
                            "status": "offen", "gold": 0, "pipeline": len(p)})
            continue

        g = gold_docs.get(fid, [])
        paare, rest_g, rest_p = matche(g, p, schwelle, toleranz)
        zahlen = {"tp": len(paare), "fp": len(rest_p), "fn": len(rest_g),
                  "typ_ok": sum(1 for _, ga, pa in paare
                                if ga.get("effect_type") == pa.get("effect_type")),
                  "wert_ok": sum(1 for _, ga, pa in paare
                                 if _nah(_zahl(ga, "effect"), _zahl(pa, "effect"), toleranz)),
                  "pipeline_zeilen_annotiert": len(p),
                  "unique": len(p_unique), "duplikate": duplikate,
                  "poolbar": sum(1 for x in p if ist_poolbar(x)),
                  "poolbar_unique": sum(1 for x in p_unique if ist_poolbar(x)),
                  "poolbar_tp": sum(1 for _, _, pa in paare if ist_poolbar(pa))}
        for ziel in (gesamt, schichten[schicht]):
            for k, v in zahlen.items():
                ziel[k] += v
        for ziel in (gesamt, schichten[schicht]):
            ziel["n_annotiert"] += 1
        details.append({"document_id": fid, "stratum": schicht, "status": "annotiert",
                        "gold": len(g), "pipeline": len(p), **zahlen,
                        "paare": [{"score": round(s, 3),
                                   "gold_outcome": ga.get("outcome_normalized"),
                                   "pipe_outcome": pa.get("outcome"),
                                   "gold_effect": _zahl(ga, "effect"),
                                   "pipe_effect": _zahl(pa, "effect"),
                                   "typ_gleich": ga.get("effect_type") == pa.get("effect_type")}
                                  for s, ga, pa in paare],
                        "nur_gold": [x.get("outcome_normalized") for x in rest_g],
                        "nur_pipeline": [x.get("outcome") for x in rest_p],
                        "poolbar": zahlen["poolbar"],
                        "poolbar_unique": zahlen["poolbar_unique"],
                        "duplikate": zahlen["duplikate"],
                        "poolbar_tp": zahlen["poolbar_tp"]})

    return {"stufen": {"schwelle": schwelle, "toleranz": toleranz},
            "gesamt": _abschluss(gesamt),
            "schichten": {k: _abschluss(v) for k, v in sorted(schichten.items())},
            "dokumente": details}
