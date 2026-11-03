"""Auftrag v2 §6: Evidenz-Kategorien und Konfidenz aus Zeilen, nicht aus Tonfall.

Drei Trennlinien, die der Auftrag verlangt:

1. Eine Hypothese ohne richtungsweisende Evidenzzeile ist **spekulativ** -
   sie wird im Report nie als empirische Erkenntnis angezeigt, ihre
   Modell-Konfidenz erscheint ausdrücklich als Plausibilität, nicht als
   Evidenzsicherheit.
2. Die Kategorie folgt *deterministisch* aus den gespeicherten
   Evidenzzeilen (supports / contradicts), nie aus dem LLM-Tonfall.
3. Die Konfidenz ist eine Funktion der Zeilenzählung mit festgelegter
   Deckelung; widersprüchliche Evidenz kann nie eine hohe
   Schlussfolgerungssicherheit tragen.

Die Funktionen sind rein und ohne DB-Zugriff, damit Report und spätere
Prüf-schichten dieselbe Regel teilen (wie designs.py: ein Regelwerk,
nicht drei Regexe).
"""

from __future__ import annotations

from typing import Dict, Optional, Sequence

EVIDENCE_CATEGORIES = (
    "empirisch_belegt",
    "evidenzgestuetzt_unsicher",
    "widerspruechlich_ungeklaert",
    "spekulativ",
)

CATEGORY_LABELS = {
    "empirisch_belegt": "Empirisch belegt",
    "evidenzgestuetzt_unsicher": "Evidenzgestützt, unsicher",
    "widerspruechlich_ungeklaert": "Widersprüchlich / ungeklärt",
    "spekulativ": "Spekulativ / theoretisch",
}


def _counts(evidence_rows: Sequence[dict]):
    supports = 0
    contradicts = 0
    for row in evidence_rows or ():
        kind = str((row or {}).get("evidence_type") or "").strip().lower()
        if kind == "supports":
            supports += 1
        elif kind == "contradicts":
            contradicts += 1
    return supports, contradicts


def evidence_category(evidence_rows: Sequence[dict]) -> str:
    """Eine der vier Kategorien, deterministisch aus den Zeilen.

    - widersprüchlich: stützende UND widersprechende Zeilen - oder nur
      widersprechende: eine widersprechende Zeile ist negative Evidenz;
      sie zeichnet den Umstand, dass geprüft wurde und nicht bestätigt
      (Auftrag §6.1.3 'widersprüchlich oder ungeklärt');
    - empirisch belegt: mindestens 2 unabhängige stützende Zeilen und keine
      widersprechende (§6.1.1 - 'belegt' verlangt mehr als eine Quelle);
    - gestützt-unsicher: genau eine stützende Zeile, keine widersprechende
      (§6.1.2);
    - spekulativ: keine richtungsweisende Zeile (§6.1.4).
    """
    supports, contradicts = _counts(evidence_rows)
    if supports and contradicts:
        return "widerspruechlich_ungeklaert"
    if contradicts:
        return "widerspruechlich_ungeklaert"
    if supports >= 2:
        return "empirisch_belegt"
    if supports == 1:
        return "evidenzgestuetzt_unsicher"
    return "spekulativ"


def evidence_confidence(evidence_rows: Sequence[dict]) -> Optional[float]:
    """Konfidenz nur aus Evidenzzeilen; None heißt: keine Erkenntnisangabe.

    Deterministisch und konservativ:

    - Grundformel 0.5 + 0.45 * (s - c) / (s + c): die Balance zwischen
      stützenden und widersprechenden Zeilen (Konsistenz-Proxy);
    - jede widersprechende Zeile deckelt die Sicherheit auf 0.60: eine
      Schlussfolgerung über widersprüchlicher Evidenz trägt nie mehr als
      'unsicher' (§6.2);
    - eine einzige stützende Zeile läuft nie über 0.70, weil 'Anzahl
      unabhängiger Studien' ein §6.2-Bestandteil ist;
    - ohne Evidenzzeilen: None - ein LLM-Wert allein ist Plausibilität,
      keine Evidenzsicherheit (§6.2 Schluss).
    """
    supports, contradicts = _counts(evidence_rows)
    total = supports + contradicts
    if total == 0:
        return None
    confidence = 0.5 + 0.45 * ((supports - contradicts) / total)
    if contradicts:
        confidence = min(confidence, 0.60)
    if total == 1:
        confidence = min(confidence, 0.70)
    return round(min(max(confidence, 0.05), 0.95), 3)


def classify_hypothesis(hypothesis: dict, evidence_rows: Sequence[dict]) -> Dict:
    """Kategorie + Konfidenzstze für einen Hypothesen-Kopf (Report/Dashboard)."""
    category = evidence_category(evidence_rows)
    return {
        "category": category,
        "label": CATEGORY_LABELS[category],
        "evidence_confidence": evidence_confidence(evidence_rows),
        "model_confidence": hypothesis.get("confidence"),
    }
