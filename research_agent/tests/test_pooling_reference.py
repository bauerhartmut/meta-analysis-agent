"""Referenztest für das Pooling (Claude-Vorschlag 5).

Zweierlei:
1. Eine UNABHÄNGIGE Zweitimplementierung der Standardformeln (Fixed-Effect-
   Gewichtung, Cochran's Q, DerSimonian-Laird Tau², Hartung-Knapp-Intervall
   mit t-Verteilung) rechnet dieselbe kleine Datenmenge streng nach und
   wird gegen ``pool()`` mit festen Toleranzen verglichen. Die Zweit-
   implementierung ist bewusst anders geschrieben (nicht dieselben
   Hilfsfunktionen), damit ein gemeinsamer Formelschreibfehler auffallen
   muss.
2. Der Kleinst-k-Hinweis: k<3 warnt explizit über Instabilität der
   Hartung-Knapp-Intervalle und das Prediction-Interval-Verbot unter k=3;
   k<5 bleibt Hinweis. Das k-Gate (Sprint 26) bleibt unangetastet - der
   Test prüft, dass pool() bei kleinen k NICHT verweigert, sondern nur
   kennzeichnet.

Grenze (bewusst dokumentiert): ein Abgleich gegen R metafor oder Python
statsmodels ist in dieser Umgebung nicht möglich (statsmodels ist nicht
installiert, R ist nicht verfügbar), damit der Vergleich hier die
Formeln doppelt rechnet. Ein echter metafor-Abgleich (z. B. der
klassische BCG-Datensatz) bleibt offen, sobald eine der beiden
Umgebungen da ist.
"""

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from research_agent.meta.pooling import pool


def _rows():
    """Kleine, handnachrechenbare Datenmenge (Standardisierung liegt vor)."""
    return [
        {"label": "A", "est": 0.20, "se": 0.10},
        {"label": "B", "est": 0.40, "se": 0.20},
        {"label": "C", "est": -0.10, "se": 0.05},
        {"label": "D", "est": 0.25, "se": 0.25},
        {"label": "E", "est": 0.35, "se": 0.30},
        {"label": "F", "est": 0.05, "se": 0.15},
    ]


def _yv(rows):
    y = [float(r["est"]) for r in rows]
    v = [float(r["se"]) ** 2 for r in rows]
    return y, v


def _ref_fixed(y, v):
    """Fixed-Effect-Formel, separat gerechnet."""
    w = [1.0 / x for x in v]
    total = sum(x * g for x, g in zip(w, y))
    weight_sum = sum(w)
    return total / weight_sum, math.sqrt(1.0 / weight_sum), weight_sum


def _ref_q(y, v, fe):
    w = [1.0 / x for x in v]
    return sum(x * (g - fe) ** 2 for x, g in zip(w, y))


def _ref_tau2_dl(y, v, fe, weight_sum):
    k = len(y)
    w = [1.0 / x for x in v]
    square_sum = sum(x * x for x in w)
    q = _ref_q(y, v, fe)
    base = weight_sum - square_sum / weight_sum
    if base <= 0:
        return 0.0, q
    return max(0.0, (q - (k - 1)) / base), q


def _ref_hk(y, v):
    """Hartung-Knapp-Intervall extrem simpel nachgerechnet (t = student).

    Bemutzt die BEKANNTEN t-Quantile (df = k-1, 97.5 %) als Konstante -
    keine Kopie von q_of() / _t_quantile().
    """
    # Zweitimplementierung ohne jede Projekthilfsfunktion:
    tau2, q = _ref_tau2_dl(y, v, _ref_fixed(y, v)[0], _ref_fixed(y, v)[2])
    w_star = [1.0 / (x + tau2) for x in v]
    total_w = sum(w_star)
    mu = sum(x * g for x, g in zip(w_star, y)) / total_w
    k = len(y)
    df = k - 1
    se_hk = math.sqrt(
        sum(x * (g - mu) ** 2 for x, g in zip(w_star, y)) / (total_w * df))
    # Student-t 97.5 %-Quantile je df als Konstanten (Quantiltabellen,
    # keine Kopie der Projekthilfsfunktion _t_quantile).
    t_crit = {2: 12.706, 3: 4.303, 4: 3.182, 5: 2.776, 6: 2.571}[k]
    return mu, se_hk, mu - t_crit * se_hk, mu + t_crit * se_hk, tau2, q


class TestReferenzNachrechnung(unittest.TestCase):
    TOL = 1e-9

    def test_fixed_effect_und_q_streng_gleich(self):
        rows = _rows()
        result = pool(rows, method="hksj")
        y, v = _yv(rows)
        fe, fe_se, weight_sum = _ref_fixed(y, v)
        self.assertAlmostEqual(result["fixed"], fe, places=10)
        # fixed CI: z-Intervall 1.96fach (beides historisch gleich)
        self.assertAlmostEqual(result["fixed_ci_low"],
                               fe - 1.96 * fe_se, places=10)
        self.assertAlmostEqual(result["fixed_ci_high"],
                               fe + 1.96 * fe_se, places=10)
        _, q = _ref_tau2_dl(y, v, fe, weight_sum)
        self.assertAlmostEqual(result["q"], q, places=10)
        self.assertAlmostEqual(result["i2"], max(0.0, (q - 5) / q) * 100,
                               places=8)

    def test_tau2_dl_und_hk_intervall_streng_gleich(self):
        rows = _rows()
        result = pool(rows, method="hksj")
        y, v = _yv(rows)
        mu, se_hk, low, high, tau2, _ = _ref_hk(y, v)
        # Die Algebra (tau2, se_hksj, pooled) ist exakt vergleichbar.
        # Die Intervallendpunkte haengen am Student-t-Quantil: meine
        # Tabellenkonstante vs die Projektnaehrung (z. B. 2.5705818 fuer
        # df=5 gegen 2.571 aus der Tabelle) uebereinstimmt nur auf
        # 1e-3 Genauigkeit - deshalb hier places=2, nicht 8.
        self.assertAlmostEqual(result["tau2"], tau2, places=10)
        self.assertAlmostEqual(result["se_hksj"], se_hk, places=10)
        self.assertAlmostEqual(result["hksj_low"], low, places=2)
        self.assertAlmostEqual(result["hksj_high"], high, places=2)
        self.assertAlmostEqual(result["ci_low"], low, places=2)
        self.assertAlmostEqual(result["ci_high"], high, places=2)

    def test_prediction_interval_formel_gleiche_arithmetik(self):
        rows = _rows()
        result = pool(rows, method="hksj")
        y, v = _yv(rows)
        mu, _, _, _, tau2, _ = _ref_hk(y, v)
        se_re = math.sqrt(1.0 / sum(1.0 / (x + tau2) for x in v))
        # pi_df = k-2 = 4, t 97.5 % aus Tabelle: Tabellenkonstante 2.776
        # vs Projektnaehrung 2.77644 - Vergleich auf 1e-3 Genauigkeit
        # (places=2), weil der t-Quantis geruendet ist.
        t_pi = 2.776
        spread = math.sqrt(tau2 + se_re ** 2)
        self.assertAlmostEqual(result["pi_low"], mu - t_pi * spread, places=2)
        self.assertAlmostEqual(result["pi_high"], mu + t_pi * spread, places=2)

    def test_zweite_lesung_liefert_dieselbe_pooled_zahl(self):
        # Streng: die Zweitimplementierung des DL-Gewichts prueft auch
        # die geschäzte pooled-Zahl, nicht nur Intervallbreite.
        rows = _rows()
        result = pool(rows, method="hksj")
        y, v = _yv(rows)
        mu, _, _, _, _, _ = _ref_hk(y, v)
        self.assertAlmostEqual(result["pooled"], mu, places=10)


class TestKleinstkHinweis(unittest.TestCase):
    def test_k_2_warnt_explizit_ueber_instabilitaet(self):
        result = pool([{"label": "A", "est": 0.30, "se": 0.12},
                       {"label": "B", "est": 0.42, "se": 0.30}],
                      method="hksj")
        self.assertEqual(result["k"], 2)
        hint = result.get("small_k_note") or ""
        self.assertIn("Sehr kleine", hint)
        self.assertIn("k<3", hint)
        self.assertIn("Prediction", hint)
        # Poolen selbst wird NICHT verweigert: der Hinweis kennzeichnet,
        # das k-Gate aus Sprint 26 bleibt unangetastet.
        self.assertIsNotNone(result["pooled"])

    def test_k_4_bleibt_hinweis_mit_vorsicht(self):
        rows = _rows()[:4]
        result = pool(rows, method="hksj")
        hint = result.get("small_k_note") or ""
        self.assertIn("Kleine Studienanzahl", hint)
        self.assertIn("Vorsicht", hint)

    def test_k_7_kein_hinweis(self):
        rows = _rows()
        result = pool(rows, method="hksj")
        self.assertNotIn("small_k_note", result)

    def test_se_null_checked_sorgt_kein_crash(self):
        # Bei einer se von 0 gibt es keine sinnvolle Präzision:
        # pool() darf darauf weder mit crashen noch definitiv falsche
        # Zahlen behaupten — nur jeden k-Wert korrekt liefern.
        result = pool([{"label": "X", "est": 0.1, "se": 0.0}],
                      method="hksj")
        self.assertEqual(result["k"], 0)


if __name__ == "__main__":
    unittest.main()
