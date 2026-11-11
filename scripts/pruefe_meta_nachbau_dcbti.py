"""Prüft den dCBT-I-Pilot gegen seinen Antwortschlüssel.

Berechnet den Random-Effects-Pool (DerSimonian-Laird) einmal aus den
berichteten SMDs und KIs und einmal aus N, Mittelwert und SD mit
Hedges-g-Korrektur. Zusätzlich werden die vier Studien-SMDs einzeln
gegen die publizierten Werte geprüft.

Exit 0 = alle Nachrechnungen liegen innerhalb der Toleranzen.
Exit 1 = mindestens eine Abweichung.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEY = ROOT / "data" / "meta_nachbau" / "pilot_dcbti" / "antwortschluessel.json"
Z = 1.959963984540054


def dl_pool(estimates: list[float], standard_errors: list[float]) -> dict:
    k = len(estimates)
    weights = [1.0 / (se * se) for se in standard_errors]
    fixed = sum(w * y for w, y in zip(weights, estimates)) / sum(weights)
    q = sum(w * (y - fixed) ** 2 for w, y in zip(weights, estimates))
    df = k - 1
    c = sum(weights) - sum(w * w for w in weights) / sum(weights)
    tau2 = max(0.0, (q - df) / c) if c > 0 else 0.0
    random_weights = [1.0 / (se * se + tau2) for se in standard_errors]
    pooled = sum(w * y for w, y in zip(random_weights, estimates)) / sum(random_weights)
    se_pooled = math.sqrt(1.0 / sum(random_weights))
    i2 = max(0.0, (q - df) / q) * 100.0 if q > 0 else 0.0
    return {
        "smd": pooled,
        "ci_low": pooled - Z * se_pooled,
        "ci_high": pooled + Z * se_pooled,
        "q": q,
        "df": df,
        "tau2": tau2,
        "i2_percent": i2,
        "k": k,
    }


def hedges_from_means(study: dict) -> tuple[float, float]:
    n1 = int(study["n_treatment"])
    n2 = int(study["n_control"])
    m1 = float(study["mean_treatment"])
    m2 = float(study["mean_control"])
    s1 = float(study["sd_treatment"])
    s2 = float(study["sd_control"])
    sp = math.sqrt(((n1 - 1) * s1 * s1 + (n2 - 1) * s2 * s2) / (n1 + n2 - 2))
    d = (m1 - m2) / sp
    j = 1.0 - 3.0 / (4.0 * (n1 + n2) - 9.0)
    g = d * j
    se = math.sqrt((n1 + n2) / (n1 * n2) + g * g / (2.0 * (n1 + n2)))
    return g, se


def close(actual: float, expected: float, tolerance: float) -> bool:
    return abs(actual - expected) <= tolerance


def main() -> int:
    data = json.loads(KEY.read_text(encoding="utf-8"))
    studies = data["studies"]
    tol = data["tolerances"]
    errors: list[str] = []

    smds = [float(s["smd_published"]) for s in studies]
    ses = [
        (float(s["ci_high"]) - float(s["ci_low"])) / (2.0 * Z)
        for s in studies
    ]
    from_smd = dl_pool(smds, ses)

    gs, gses = zip(*(hedges_from_means(s) for s in studies))
    from_means = dl_pool(list(gs), list(gses))

    if from_smd["k"] != int(tol["k_exact"]):
        errors.append(f"k={from_smd['k']} statt {tol['k_exact']}")

    for study, g in zip(studies, gs):
        published = float(study["smd_published"])
        if not close(g, published, float(tol["study_smd_abs"])):
            errors.append(
                f"{study['study_id']}: g={g:.4f} statt {published:.4f}"
            )

    published_pool = data["published_pooled"]
    for label, actual in (
        ("SMD", from_smd["smd"]),
        ("CI unten", from_smd["ci_low"]),
        ("CI oben", from_smd["ci_high"]),
    ):
        expected = published_pool[
            {"SMD": "smd", "CI unten": "ci_low", "CI oben": "ci_high"}[label]
        ]
        if not close(actual, expected, float(tol["pooled_smd_abs"])):
            errors.append(f"{label}: {actual:.4f} statt {expected:.4f}")
    if not close(
        from_smd["i2_percent"],
        published_pool["i2_percent"],
        float(tol["i2_abs"]),
    ):
        errors.append(
            f"I2: {from_smd['i2_percent']:.2f} statt {published_pool['i2_percent']:.2f}"
        )
    if not close(
        from_smd["tau2"],
        published_pool["tau2"],
        float(tol["tau2_abs"]),
    ):
        errors.append(
            f"tau2: {from_smd['tau2']:.4f} statt {published_pool['tau2']:.4f}"
        )

    print(f"k = {from_smd['k']}")
    print("Studien:")
    for study, g, se in zip(studies, gs, gses):
        print(
            "  %-16s g=% .4f (SE %.4f), publiziert % .2f"
            % (study["study_id"], g, se, study["smd_published"])
        )
    print(
        "aus SMD/KI:   %.4f [%.4f, %.4f], Q=%.4f, tau2=%.4f, I2=%.2f%%"
        % (
            from_smd["smd"],
            from_smd["ci_low"],
            from_smd["ci_high"],
            from_smd["q"],
            from_smd["tau2"],
            from_smd["i2_percent"],
        )
    )
    print(
        "aus N/M/SD:   %.4f [%.4f, %.4f], Q=%.4f, tau2=%.4f, I2=%.2f%%"
        % (
            from_means["smd"],
            from_means["ci_low"],
            from_means["ci_high"],
            from_means["q"],
            from_means["tau2"],
            from_means["i2_percent"],
        )
    )
    print(
        "publiziert:   %.4f [%.4f, %.4f], Q=%.2f, tau2=%.2f, I2=%.2f%%"
        % (
            published_pool["smd"],
            published_pool["ci_low"],
            published_pool["ci_high"],
            published_pool["q"],
            published_pool["tau2"],
            published_pool["i2_percent"],
        )
    )
    if errors:
        print("FEHLER:")
        for error in errors:
            print(" -", error)
        return 1
    print("OK: Publizierter Pool aus den Studienwerten reproduziert.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
