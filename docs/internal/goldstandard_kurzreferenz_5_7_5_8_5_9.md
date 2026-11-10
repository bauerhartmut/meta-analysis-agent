# Kurzreferenz 5.7, 5.8, 5.9 — A/B (Anleitung v1.2)

Diese Referenz ist eine **Leshilfe**, keine neue Regel. Maßgeblich sind
`docs/internal/goldstandard_annotationsanleitung.md` (v1.2) und
`docs/internal/goldstandard_schema.json`. Sie gilt für die 12
Kalibrierungsdokumente, besonders für die drei Startdokumente `7111ea`,
`bb921` und `203c`.

## Schnellentscheidung

| Befund | Zeile? | Eintrag |
|---|---|---|
| p-Wert ohne Effektgröße | nein | `no_effect_reason`: „nur p-Wert, keine Effektgroesse“ |
| Mittelwert ± SD, kein Effekt/KI | nein | Begründung; keine Umrechnung |
| Effekt mit KI/SE | ja | `effect`, `ci_low`, `ci_high`, `quote` |
| gepoolter Schätzer einer Übersicht | ja, je Schätzer eine Zeile | `is_primary: false`, `design_category: aggregate` |
| Einzelstudie in einer Übersicht | nein | gehört zur Primärstudie |
| mehrere Arme, je Arm eigener Effekt | ja, je Arm eine Zeile | Arm in `comparison_verbatim` und/oder `notes` |
| nur gemeinsamer Effekt über Arme | eine Zeile | `notes`: „gepoolt über Arme“ |
| Dosis-Wirkungs-Peak | nein | Peak in `notes` (Wert, Dosis, CrI) |
| Sensitivitätsanalyse | nein | Wert in `notes` |

## 5.7 p-Wert ohne Effektgröße

- Ein p-Wert ist **kein Effekt** und **kein KI**. Er darf nicht in `effect`,
  `ci_low` oder `ci_high` stehen.
- Nur Mittelwerte ± SD sind ebenfalls keine Effektgröße mit Unsicherheit;
  nicht in eine Differenz oder SMD umrechnen.
- `no_effect_reason`: „nur p-Wert, keine Effektgroesse“ oder „nur
  Mittelwerte und SD, keine Effektgroesse mit KI/SE“.
- **Ausnahme:** Wird ein Effekt mit KI oder SE berichtet — auch wenn
  zusätzlich ein p-Wert dasteht — ist es eine Zeile.

**Prüffrage `bb921`:** Drei parallele Arme, Mittelwerte ± SD, p-Werte. Gibt es
irgendwo einen Effekt mit KI oder SE? Wenn nein: keine Zeile, Begründung.

## 5.8 Übersichtsarbeiten

- Der gepoolte Schätzer ist **eine** Zeile mit `is_primary: false` und
  `design_category: aggregate`.
- Einzelstudien-Ergebnisse, die die Übersicht zitiert, werden **nicht**
  übernommen. Sie gehören zur Primärstudie.
- Gibt es mehrere gepoolte Schätzer (z. B. HR und MD), ist **jeder** eine
  eigene Zeile; alle mit `is_primary: false`.
- Ein Aggregat, das selbst extrahiert wird, ist korrekt annotiert; das Gate
  im Code entscheidet über den Pool.

**Prüffrage `7111ea`:** Ist es ein narrativer Überblick ohne eigenen gepoolten
Schätzer? Wenn ja: keine Zeile und `no_effect_reason` nach 5.8.

**Prüffrage `203c`:** Welche gepoolten Schätzer sind berichtet? Jeder
gepoolte Schätzer ist eine Zeile mit `is_primary: false`; Einzelstudien aus
der Übersicht nicht übernehmen.

**Prüffrage `334f`:** Metaanalyse. Nur der gepoolte Schätzer zählt, keine
Einzelstudien.

**Prüffrage `fb484`:** Metaanalyse, kein RCT (Abstract: 15 RCTs, 12 in der
Metaanalyse). Der gepoolte SMD ist eine Zeile mit `is_primary: false`.

## 5.9 Mehrere Arme und Dosis

- **Je Arm eine Zeile**, wenn ein eigener Effekt mit Unsicherheit berichtet
  wird.
- Ist nur ein gemeinsamer Effekt über Arme berichtet, ist es **eine** Zeile
  mit `notes`: „gepoolt über Arme“.
- Ein **Dosis-Wirkungs-Peak** oder ein Punkt der Dosis-Wirkungs-Kurve ist
  **keine** eigene Zeile. Die Dosis ist kein Zeilenkriterium (Abschnitt 3);
  der Peak ist ein Punkt derselben Kurve, kein eigener Vergleich. Der
  gepoolte Hauptschätzer bleibt die Zeile; Peak, Dosis und Kurvenform stehen
  in `notes`.
- Eine **Sensitivitätsanalyse** ist **keine** eigene Zeile, wenn sie dieselbe
  Kombination aus Outcome, Vergleich, Zeitpunkt, Adjustierung und Population
  betrifft. Der Wert steht in `notes`.

**Beispiel `5cbf` (nicht in den 12, aber Regelbeispiel):**
- Hauptschätzer: Hedges’ g = -0.28 (95% CrI -0.43 bis -0.13) — **eine Zeile**
  mit `is_primary: false`.
- Peak bei ca. 740 METs-min/Woche: g = -0.44 (95% CrI -0.27 bis -0.73, wie
  berichtet) — **keine Zeile**, sondern `notes`. Die CrI-Reihenfolge nicht
  sortieren; sie steht so im Text.
- Sensitivitätsanalyse ohne 2 Hochrisikostudien: 0.29 (95% CI 0.21–0.38) —
  **keine Zeile**, sondern `notes`, „wie berichtet, nicht umgerechnet“.

## Vor der Abgabe je Dokument

- [ ] Jede Zeile hat `quote` exakt und `quote_start`/`quote_end` passend.
- [ ] `effect`, `ci_low`, `ci_high` aus dem Text; nichts umgerechnet oder
      gerundet.
- [ ] `is_primary: false` nur bei gepoolten Schätzern.
- [ ] `design_category: aggregate` bei Übersichten.
- [ ] `notes` für Peak, Sensitivität, Arme und Dosis.
- [ ] Dokument hat Zeilen oder `no_effect_reason`.
- [ ] `pruefe_goldstandard.py --entwurf` Exit 0.

## Drei Startdokumente: Prüffragen

| Dokument | Punkt | Prüffrage |
|---|---|---|
| `7111ea` | 5.8 | Gibt es einen eigenen gepoolten Schätzer? |
| `bb921` | 5.7 | Gibt es einen Effekt mit KI/SE oder nur Mittelwerte/p? |
| `203c` | 5.8 gepoolt | Welche gepoolten Schätzer sind berichtet? |

Die Prüffragen sind eine Orientierung, keine Annotation. Die Antwort steht
nur im Volltext, nicht in dieser Referenz.
