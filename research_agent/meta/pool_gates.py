"""Gates fuer gepoolte Ergebnisse, die kein Intervall tragen duerfen.

Befund E4f: Der Kollaps-Schluessel mit Exposition behaelt mehrere Zeilen
derselben Quelle. Bei `preeclampsia` sind es fuenf Zeilen, aber nur **ein**
unabhaengiger Cluster. `pool_rve` liefert dann `M = 1` und kann kein
cluster-robustes Intervall bilden; das naive HKJ-Intervall ist trotzdem da
und wirkt praezise, obwohl es keine zweite unabhaengige Einheit gibt.

Das Gate entfernt in diesem Fall die Intervalle und laesst den Punktschaetzer
als Sichtung stehen. Es aendert keinen Effektwert und keine Zeile.
"""

from __future__ import annotations

from typing import Dict

NOTE = (
    "Nur ein unabhaengiger Cluster (M=1): Alle Zeilen stammen aus derselben "
    "Quelle. Ein Konfidenzintervall waere Scheinpraezision - der "
    "Punktschaetzer steht als Sichtung, nicht als Ergebnis."
)

_INTERVAL_FIELDS = (
    "ci_low", "ci_high",
    "fixed_ci_low", "fixed_ci_high",
    "pi_low", "pi_high",
)


def single_cluster_gate(analysis: Dict) -> Dict:
    """Entfernt die Intervalle eines Pools mit weniger als zwei Clustern.

    Voraussetzungen: `analysis` kommt aus `pool()` und traegt `rve` aus
    `pool_rve()`. Ein Pool mit k < 2 hat ohnehin kein Intervall und wird
    nicht markiert. Fehlt `rve` ganz, wird nichts angenommen (kein Gate).
    """

    if not isinstance(analysis, dict):
        return analysis
    if int(analysis.get("k") or 0) < 2:
        return analysis
    rve = analysis.get("rve")
    if not isinstance(rve, dict):
        return analysis
    if int(rve.get("M") or 0) >= 2:
        return analysis

    for field in _INTERVAL_FIELDS:
        analysis[field] = None
    analysis["single_cluster"] = True
    analysis["single_cluster_note"] = NOTE
    analysis["note"] = ((analysis.get("note") or "") + " " + NOTE).strip()
    return analysis
