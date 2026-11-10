"""Erzeugt die Abgabe-Checkliste fuer den Probelauf.

Read-only. Die Hashes sind der aktuelle Stand der Gerueste; nach dem
Ausfuellen aendern sie sich. Der Abgabe-Hash wird vom Pruefer ausgegeben und
in der Checkliste eingetragen. Die Designfaelle nennen nur Pruefpunkte,
keine Effektwerte.
"""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / "data" / "golden_effects" / "goldstandard_A.json"
B = ROOT / "data" / "golden_effects" / "goldstandard_B.json"
DOCS = ROOT / "data" / "golden_effects" / "documents.json"


def _hash(pfad: Path) -> str:
    return hashlib.sha256(pfad.read_bytes()).hexdigest()


def _stand(pfad: Path) -> dict:
    daten = json.loads(pfad.read_text(encoding="utf-8"))
    docs = [d for d in daten["documents"] if d.get("probelauf")]
    zeilen = sum(len(d.get("effects") or []) for d in docs)
    begr = sum(1 for d in docs if str(d.get("no_effect_reason") or "").strip())
    offen = sum(1 for d in docs
                if not (d.get("effects") or [])
                and not str(d.get("no_effect_reason") or "").strip())
    return {"zeilen": zeilen, "begruendungen": begr, "offen": offen,
            "hash": _hash(pfad), "dokumente": len(docs)}


def _pruefpunkt(meta: dict) -> str:
    design = meta.get("design_category")
    verbatim = str(meta.get("design_verbatim") or "").lower()
    if design == "aggregate" and "narrative" in verbatim:
        return ("5.8: Hat das Dokument einen eigenen gepoolten Schaetzer? "
                "Wenn nein, keine Zeile und no_effect_reason; Einzelstudien "
                "nicht uebernehmen.")
    if design == "aggregate":
        return ("5.8: gepoolte Schaetzer als je eine Zeile mit "
                "is_primary: false; Einzelstudien nicht uebernehmen.")
    if design == "parallel_rct":
        return ("5.7: p-Wert ohne Effektgroesse ist keine Zeile; nur "
                "berichtete Effekte mit Unsicherheit.")
    return "Design nach 5.1 pruefen; nur Effekte mit Unsicherheit."


def main() -> int:
    a, b = _stand(A), _stand(B)
    daten = json.loads(A.read_text(encoding="utf-8"))
    probelauf = [d for d in daten["documents"] if d.get("probelauf")]
    meta = {d["document_id"]: d for d in
            json.loads(DOCS.read_text(encoding="utf-8"))["documents"]}

    zeilen = [
        "# Abgabe-Checkliste Probelauf (2026-11-10)",
        "",
        "Format- und Ablauftest für A und B, getrennt auszufüllen. Während",
        "der Annotation kein Austausch; nur Volltext, Anleitung und Schema.",
        "Eine Kappa-Zahl entsteht hier nicht; sie folgt nach der Vollannotation.",
        "",
        "## Stand",
        "",
        "| Datei | Zeilen | Begründungen | offen | Probelauf-Dokumente |",
        "|---|---|---|---|---|",
        f"| `goldstandard_A.json` | {a['zeilen']} | {a['begruendungen']} | "
        f"{a['offen']} | {a['dokumente']} |",
        f"| `goldstandard_B.json` | {b['zeilen']} | {b['begruendungen']} | "
        f"{b['offen']} | {b['dokumente']} |",
        "",
        "Aktuelle Hashes (Stand nach der Designkorrektur):",
        "",
        f"- A: `{a['hash']}`",
        f"- B: `{b['hash']}`",
        "",
        "Die Hashes sind **Startwerte**. Nach dem Ausfüllen ändern sie sich;",
        "der Abgabe-Hash wird vom Prüfer ausgegeben und unten eingetragen.",
        "",
        "## Die drei Designfälle",
        "",
    ]
    for doc in probelauf:
        m = meta.get(doc["document_id"], {})
        zeilen += [
            f"### {doc['document_id'][:10]}",
            "",
            f"- Design: `{doc.get('design_category')}` / "
            f"`{doc.get('design_verbatim')}`",
            f"- Schicht: `{doc.get('stratum')}`",
            f"- Prüfpunkt: {_pruefpunkt({**m, **doc})}",
            "",
        ]
    zeilen += [
        "## Vor der Abgabe (je Annotator)",
        "",
        "- [ ] Nur die drei Probelauf-Dokumente bearbeitet; die übrigen 27",
        "      bleiben unberührt.",
        "- [ ] Jedes der drei Dokumente hat Zeilen oder `no_effect_reason`.",
        "- [ ] Alle 14 Pflichtfelder je Zeile und 9 Dokumentpflichtfelder sind",
        "      gesetzt.",
        "- [ ] Jede `quote` ist exakt; `quote_start`/`quote_end` passen.",
        "- [ ] Kein Effekt umgerechnet, keine Zahl gerundet.",
        "- [ ] Ratio-Werte positiv; Effekt liegt im KI.",
        "- [ ] `is_primary: false` nur bei gepoolten Schätzern.",
        "- [ ] `design_category` nach 5.1; 5.11 bei Spannweiten über Zeitpunkte.",
        "- [ ] 5.7 geprüft: p-Wert ohne Effektgröße ist keine Zeile.",
        "- [ ] 5.8 geprüft: Einzelstudien aus Übersichten nicht übernehmen.",
        "",
        "## Abgabe",
        "",
        "1. `python scripts/pruefe_probelauf_abgabe.py` ausführen; Exit 0.",
        "2. Den ausgegebenen SHA-256 unten eintragen.",
        "3. Datei committen und nicht mehr ändern.",
        "4. Erst danach vergleichen.",
        "",
        "## Nach der Abgabe: Format auswerten",
        "",
        "- Zeilen und Begründungen je Dokument zählen; jedes Dokument hat",
        "  Zeilen oder eine Begründung.",
        "- Die drei Designfälle prüfen: 7111ea ohne Zeile, bb921 ohne Zeile,",
        "  203c mit zwei gepoolten Zeilen.",
        "- Keine Kappa-Zahl in diesem Schritt.",
        "",
        "## Kappa nach der Vollannotation",
        "",
        "- `python scripts/werte_kappa_probe.py` (ohne `--probelauf`)",
        "- `python scripts/berichte_kappa_konflikte.py` (ohne `--probelauf`)",
        "- `python scripts/priorisiere_kappa_konflikte.py`",
        "- Konflikte für die dritte Stimme; Schwelle Zeilen-Kappa 0,80.",
        "",
        "## Abgabe-Hashes",
        "",
        "- A: ______________________________",
        "- B: ______________________________",
        "",
    ]
    text = "\n".join(zeilen)
    ziel = ROOT / "docs" / "internal" / "probelauf_abgabe_checkliste_20261110.md"
    ziel.write_text(text + "\n", encoding="utf-8")
    print(text)
    print(f"Checkliste: {ziel.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
