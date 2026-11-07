"""Gates gegen Zeilen, die kein Behandlungseffekt einer Primaerstudie sind.

Zwei Faelle, die der Baseline-Filter nicht abdeckt:

* **Gepoolte Zeile:** ``MD [95%CI]`` neben ``I 2 (%)`` ist eine Schaetzung
  ueber mehrere Studien, keine Studienzeile. Wer sie als Studie zaehlt,
  gewichtet dieselben Daten doppelt.
* **Praediktortabelle:** Die verglichenen Gruppen sind nach dem **Ergebnis**
  gebildet ("A Better Outcome" gegen "Not"), nicht nach der Intervention. Ein
  OR aus einer solchen Tabelle beschreibt einen praediktiven Zusammenhang,
  keinen Behandlungseffekt.

Beide Gates arbeiten auf Caption und Kopf. Sie sind bewusst eng: das Wort
"multivariate" allein reicht nicht, es muss eine Gruppierung nach Ergebnis
oder ein Heterogenitaetsmass dazukommen. Eine Zeile "Overall" in einer
Studientabelle wird **nicht** verworfen - dort fehlt der zweite Beleg.
"""

from __future__ import annotations

import re
from typing import Sequence

POOLED_CAPTION = re.compile(
    r"meta[-\s]?analys|pooled\s+(?:estimate|effect|analysis)"
    r"|random[-\s]effects?\s+model|fixed[-\s]effects?\s+model",
    re.IGNORECASE)

# Ein Heterogenitaetsmass im Kopf beweist eine Metaanalyse-Tabelle: I-Quadrat,
# Tau-Quadrat oder ein Q-Test stehen nur dort.
HETEROGENEITY = re.compile(
    r"\bI\s*2\b|\bI\u00b2\b|heterogen|\btau\s*2\b|\bQ\s*-?\s*(?:statistic|test|value)\b",
    re.IGNORECASE)

# Gruppen, die nach dem Ergebnis benannt sind statt nach der Intervention.
OUTCOME_GROUP = re.compile(
    r"\b(?:better|worse|poor|good|favourable|favorable)\s+outcome\b"
    r"|\bresponders?\b|\bnon[-\s]?responders?\b"
    r"|\bimproved\b|\bnot\s+improved\b"
    r"|\bremitters?\b|\bnon[-\s]?remitters?\b",
    re.IGNORECASE)

PREDICTOR_CAPTION = re.compile(
    r"predictor|determinant|risk\s+factor|associated\s+with|correlat",
    re.IGNORECASE)

UNIVARIATE = re.compile(r"univariat|multivariat|crude\s+(?:or|hr|rr)|adjusted\s+(?:or|hr|rr)",
                        re.IGNORECASE)

POOLED_REASON = "gepoolte Schaetzung (Metaanalyse), keine Studienzeile"
PREDICTOR_REASON = "Praediktortabelle (Gruppen nach Ergebnis), kein Behandlungseffekt"


def _joined(header: Sequence[str]) -> str:
    return " ".join(str(item or "") for item in header or [])


def pooled_violation(caption: str, header: Sequence[str]) -> str:
    """Grund, warum die Zeile eine gepoolte Schaetzung ist - oder ""."""
    heads = _joined(header)
    if POOLED_CAPTION.search(str(caption or "")):
        return POOLED_REASON
    if HETEROGENEITY.search(heads):
        return POOLED_REASON
    return ""


def predictor_violation(caption: str, header: Sequence[str]) -> str:
    """Grund, warum die Zeile aus einer Praediktortabelle stammt - oder ""."""
    heads = _joined(header)
    if OUTCOME_GROUP.search(heads):
        return PREDICTOR_REASON
    if PREDICTOR_CAPTION.search(str(caption or "")) and UNIVARIATE.search(heads):
        return PREDICTOR_REASON
    return ""


def design_violation(caption: str, header: Sequence[str]) -> str:
    """Erster zutreffender Grund aus beiden Gates - oder ""."""
    return pooled_violation(caption, header) or predictor_violation(caption, header)
