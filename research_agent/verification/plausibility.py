"""Deterministic plausibility checks with hard errors and warnings.

Hard errors make verification impossible.  Warnings are shown to the reviewer
but do not silently alter a value.  No rule subtracts, rounds or imputes a
number.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from .schema import parse_number, required_fields


def _entry(rule: str, severity: str, field: str, message: str) -> Dict[str, str]:
    return {"rule": rule, "severity": severity, "field": field, "message": message}


def check_fields(record: Dict[str, Any],
                 values: Dict[str, Any]) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    outcome_type = str(record.get("outcome_type") or "continuous")
    for field in required_fields(outcome_type):
        value = values.get(field)
        number = parse_number(value)
        if value in (None, ""):
            out.append(_entry("required_field_missing", "error", field,
                              "Pflichtfeld fehlt; keine automatische Freigabe."))
            continue
        if number is None:
            out.append(_entry("not_numeric", "error", field,
                              "Der Wert ist keine endliche Zahl."))
            continue
        if field.endswith("_n"):
            if not float(number).is_integer() or number <= 0:
                out.append(_entry("n_not_positive_integer", "error", field,
                                  "Stichprobengroesse muss eine positive ganze Zahl sein."))
        if field.endswith("_sd") and number <= 0:
            out.append(_entry("sd_not_positive", "error", field,
                              "Standardabweichung muss positiv sein."))
        if field.endswith("_events"):
            if not float(number).is_integer() or number < 0:
                out.append(_entry("events_not_nonnegative_integer", "error", field,
                                  "Ereigniszahl muss eine nichtnegative ganze Zahl sein."))
            n = parse_number(values.get(field.replace("_events", "_n")))
            if n is not None and number > n:
                out.append(_entry("events_exceed_n", "error", field,
                                  "Ereigniszahl ist groesser als die zugehoerige Stichprobe."))

    if outcome_type == "continuous":
        for arm in ("intervention", "comparator"):
            mean = parse_number(values.get(f"{arm}_mean"))
            sd = parse_number(values.get(f"{arm}_sd"))
            n = parse_number(values.get(f"{arm}_n"))
            if mean is None or sd is None or n is None:
                continue
            if sd > 0 and n > 0 and sd > 10 * max(abs(mean), 1):
                out.append(_entry("sd_large_relative_to_mean", "warning",
                                  f"{arm}_sd",
                                  "SD ist sehr gross relativ zum Mittelwert; pruefen, "
                                  "ob eine andere Skala oder Streuung gelesen wurde."))
            if n == 0:
                out.append(_entry("n_zero", "error", f"{arm}_n",
                                  "Stichprobengroesse null ist fuer ein Arm-Paar unzulaessig."))

    left_n = parse_number(values.get("intervention_n"))
    right_n = parse_number(values.get("comparator_n"))
    if left_n is not None and right_n is not None and left_n == right_n == 1:
        out.append(_entry("single_participant_arms", "warning", "intervention_n",
                          "Beide Arme haben N=1; die Zuordnung ist fachlich zu pruefen."))

    if record.get("time_point") in (None, "") and values.get("time_point") in (None, ""):
        out.append(_entry("timepoint_not_documented", "warning", "time_point",
                          "Kein Messzeitpunkt dokumentiert; keine stille Umrechnung."))

    units = {str(values.get("unit") or "").strip().lower()}
    if len(units) > 1:
        out.append(_entry("unit_inconsistent", "error", "unit",
                          "Mehrere Einheiten im selben Record."))
    return out


def hard_errors(validations: Iterable[Dict[str, str]]) -> List[Dict[str, str]]:
    return [item for item in validations if item.get("severity") == "error"]
