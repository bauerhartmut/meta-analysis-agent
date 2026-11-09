"""Cluster-robuste Varianz mit Random-Effects-Gewichten (E4i).

E4f hat gezeigt, warum der Vergleich RVE (Fixed Effect) gegen HKJ (Random
Effects) nichts ueber Scheinpraezision beweist: Modellwechsel und
Cluster-Korrektur wirken gleichzeitig. Dieses Modul rechnet RVE mit
denselben Gewichten wie der Random-Effects-Punktschaetzer:

    w_i      = 1 / (v_i + tau2)
    theta    = sum(w_i y_i) / sum(w_i)
    D_m      = sum_{i in m} w_i (y_i - theta)
    Var      = [ sum_m D_m^2 / W^2 ] * M / (M - 1)
    Intervall= theta +/- t(0.975, M - 1) * sqrt(Var)

Punktschaetzer und Sandwich benutzen dieselben Gewichte; nur dann ist die
CR0-Identitaet erfuellt. Die frueher dokumentierte Sorge ("tau2-Gewichte in
einem Sandwich, das sie nie gesehen hat") betrifft den Mischfall: FE-Punkt
mit RE-Gewichten. Hier ist beides RE, tau2 steht in beiden.

Formeln: Hedges, Tipton & Johnson (2010), correlated effects, CR0 mit der
Korrektur M/(M-1) und t-Verteilung auf M-1 Freiheitsgraden. tau2 wird nicht
hier geschaetzt, sondern uebergeben - die Schätzung (DL/REML) bleibt bei
`pooling`, damit beide Modelle dieselbe Zahl benutzen.
"""

from __future__ import annotations

import math
from typing import Dict, List, Sequence


def random_effects_rve(y: Sequence[float], v: Sequence[float],
                       clusters: Sequence[Sequence[int]], tau2: float,
                       t_crit: float) -> Dict:
    """Random-Effects-Punkt mit cluster-robuster CR0-Varianz.

    ``clusters`` enthaelt je Cluster die Indizes der Zeilen (0-basiert).
    ``t_crit`` ist das 0.975-Quantil der t-Verteilung auf M-1 df; es wird
    uebergeben, damit dieses Modul keine Verteilungslogik braucht.
    """

    y = [float(x) for x in y]
    v = [float(x) for x in v]
    if len(y) != len(v):
        raise ValueError("y und v muessen gleich lang sein")
    if tau2 is None or float(tau2) < 0:
        raise ValueError("tau2 muss >= 0 sein")
    tau2 = float(tau2)

    M = len(clusters)
    w = [1.0 / (vi + tau2) for vi in v]
    W = sum(w)
    if W <= 0:
        return {"available": False, "reason": "keine positiven Gewichte",
                "pooled": None, "se": None, "ci_low": None, "ci_high": None,
                "M": M, "df": None, "clusters": M, "tau2": tau2,
                "weights": "random"}

    theta = sum(wi * yi for wi, yi in zip(w, y)) / W

    if M < 2:
        return {"available": False,
                "reason": ("nur 1 unabhaengiger Cluster - RVE braucht "
                           "mindestens 2"),
                "pooled": theta, "se": None, "ci_low": None,
                "ci_high": None, "M": M, "df": None, "clusters": M,
                "tau2": tau2, "weights": "random"}

    sandwich_sum = 0.0
    for indices in clusters:
        d_m = 0.0
        for index in indices:
            d_m += w[index] * (y[index] - theta)
        sandwich_sum += d_m * d_m

    var = (sandwich_sum / (W * W)) * M / (M - 1)
    if var <= 0 or var != var or math.isinf(var):
        return {"available": False, "reason": "degenerierte RVE-Varianz",
                "pooled": theta, "se": None, "ci_low": None, "ci_high": None,
                "M": M, "df": M - 1, "clusters": M, "tau2": tau2,
                "weights": "random"}

    se = math.sqrt(var)
    return {
        "available": True,
        "pooled": theta,
        "se": se,
        "ci_low": theta - t_crit * se,
        "ci_high": theta + t_crit * se,
        "M": M,
        "df": M - 1,
        "clusters": M,
        "tau2": tau2,
        "weights": "random",
        "note": ("cluster-robustes Intervall mit Random-Effects-Gewichten "
                 "(CR0, t auf M-1 df); tau2 steckt in Punkt und Sandwich."),
    }


def weight_share(y: Sequence[float], v: Sequence[float],
                 clusters: Sequence[Sequence[int]], tau2: float) -> List[float]:
    """Anteil jedes Clusters an der Gesamtinformation W (Diagnose)."""

    w = [1.0 / (float(vi) + float(tau2)) for vi in v]
    total = sum(w)
    if total <= 0:
        return []
    return [sum(w[i] for i in indices) / total for indices in clusters]
