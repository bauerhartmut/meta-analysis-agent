"""Kappa und Konfliktvergleich fuer den Goldstandard-Probelauf.

Verglichen werden zwei Annotationsdateien (A und B). Gemessen wird:
- Dokumentebene: hat ein Dokument mindestens eine Zeile (ja/nein)?
- Zeilenebene: kommt ein Schluessel aus Dokument, Outcome, Vergleich und
  Zeitpunkt in beiden Dateien vor (ja/nein)?
- Je gemeinsamem Schluessel: Typ, Effekt und KI innerhalb einer Toleranz.

Die Kappa-Werte sind Cohens Kappa auf binaeren Ratings; die Item-Menge ist
die Vereinigung der Schluessel beider Dateien. Das ist bewusst konservativ:
eine Zeile, die nur einer sieht, zaehlt als Nicht-Uebereinstimmung.
"""

from __future__ import annotations

import re


def _norm(text) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip().lower()


def schluessel(doc_id: str, effekt: dict) -> tuple:
    return (doc_id, _norm(effekt.get("outcome_normalized")),
            _norm(effekt.get("comparison_verbatim")),
            _norm(effekt.get("time_point")))


def cohens_kappa(a: list, b: list):
    """Cohens Kappa fuer zwei gleich lange binaere Listen; None bei n = 0."""
    if len(a) != len(b):
        raise ValueError("Listen unterschiedlich lang")
    n = len(a)
    if n == 0:
        return None
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    pa1 = sum(a) / n
    pb1 = sum(b) / n
    pe = pa1 * pb1 + (1 - pa1) * (1 - pb1)
    if pe >= 1.0:
        return 1.0 if po == 1.0 else 0.0
    return (po - pe) / (1 - pe)


def _zahl(effekt: dict, feld: str):
    wert = effekt.get(feld)
    return wert if isinstance(wert, (int, float)) and not isinstance(wert, bool) else None


def _nah(x, y, toleranz: float) -> bool:
    if x is None or y is None:
        return x is None and y is None
    return abs(x - y) <= max(1e-9, toleranz * max(abs(x), abs(y)))


def _index(docs: dict) -> dict:
    index = {}
    for doc_id, effekte in docs.items():
        for effekt in effekte or []:
            index[schluessel(doc_id, effekt)] = effekt
    return index


def vergleiche(docs_a: dict, docs_b: dict, toleranz: float = 0.01) -> dict:
    """docs_a/docs_b: {document_id: [effekt, ...]}."""
    ids = sorted(set(docs_a) | set(docs_b))
    dok_kappa = cohens_kappa([1 if docs_a.get(i) else 0 for i in ids],
                             [1 if docs_b.get(i) else 0 for i in ids])

    ia, ib = _index(docs_a), _index(docs_b)
    keys = sorted(set(ia) | set(ib))
    if not keys:
        # Ohne eine einzige Zeile ist "keine Zeile" trivial uebereinstimmend;
        # ein Kappa waere hier eine Scheinzahl, keine Messung.
        dok_kappa = None
    zeilen_kappa = (cohens_kappa([1 if k in ia else 0 for k in keys],
                                 [1 if k in ib else 0 for k in keys])
                    if keys else None)

    treffer, nur_a, nur_b = 0, [], []
    typ_abw, wert_abw, ki_abw = [], [], []
    for key in keys:
        if key in ia and key in ib:
            ea, eb = ia[key], ib[key]
            if ea.get("effect_type") != eb.get("effect_type"):
                typ_abw.append({"key": key, "a": ea.get("effect_type"), "b": eb.get("effect_type")})
            elif not _nah(_zahl(ea, "effect"), _zahl(eb, "effect"), toleranz):
                wert_abw.append({"key": key, "a": _zahl(ea, "effect"), "b": _zahl(eb, "effect")})
            elif not (_nah(_zahl(ea, "ci_low"), _zahl(eb, "ci_low"), toleranz)
                      and _nah(_zahl(ea, "ci_high"), _zahl(eb, "ci_high"), toleranz)):
                ki_abw.append({"key": key,
                               "a": [_zahl(ea, "ci_low"), _zahl(ea, "ci_high")],
                               "b": [_zahl(eb, "ci_low"), _zahl(eb, "ci_high")]})
            else:
                treffer += 1
        elif key in ia:
            nur_a.append(key)
        else:
            nur_b.append(key)

    n = len(keys)
    return {
        "n_dokumente": len(ids),
        "n_keys": n,
        "treffer": treffer,
        "quote": (treffer / n) if n else None,
        "kappa_dokument": dok_kappa,
        "kappa_zeile": zeilen_kappa,
        "nur_a": nur_a,
        "nur_b": nur_b,
        "typ_abweichung": typ_abw,
        "wert_abweichung": wert_abw,
        "ki_abweichung": ki_abw,
    }


def als_text(ergebnis: dict, schwelle: float = 0.80) -> str:
    def k(wert):
        return "n/a" if wert is None else f"{wert:.3f}"

    def q(wert):
        return "n/a" if wert is None else f"{100 * wert:.1f} %"

    zeilen = [
        f"Dokumente: {ergebnis['n_dokumente']} | Schluessel: {ergebnis['n_keys']} | Treffer: {ergebnis['treffer']}",
        f"Kappa Dokumentebene: {k(ergebnis['kappa_dokument'])}",
        f"Kappa Zeilenebene:   {k(ergebnis['kappa_zeile'])}",
        f"Uebereinstimmung:    {q(ergebnis['quote'])}",
        f"Konflikte: nur_a {len(ergebnis['nur_a'])}, nur_b {len(ergebnis['nur_b'])}, "
        f"typ {len(ergebnis['typ_abweichung'])}, wert {len(ergebnis['wert_abweichung'])}, "
        f"ki {len(ergebnis['ki_abweichung'])}",
    ]
    if ergebnis["n_keys"] == 0:
        zeilen.append("Noch keine Annotation: beide Dateien enthalten keine Effektzeilen.")
    else:
        bestanden = (ergebnis["kappa_zeile"] is not None
                     and ergebnis["kappa_zeile"] >= schwelle)
        zeilen.append(f"Schwelle {schwelle:.2f} (Zeilen-Kappa): "
                      f"{'bestanden' if bestanden else 'nicht bestanden'}")
    return "\n".join(zeilen)
