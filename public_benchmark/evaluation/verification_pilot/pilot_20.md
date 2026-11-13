# Verifikationspilot: 20 C1-Records

**Art:** retrospektive technische Fehleranalyse auf dem verbrauchten 249er-Test; keine unabhaengige Validierung.

## Ergebnis

| Kennzahl | Wert |
|---|---:|
| Records | 20 |
| automatisch verifiziert | 9 |
| offen fuer menschliche Pruefung | 11 |
| abgelehnt | 0 |
| menschlich geprueft | 0 |
| Pflichtfelder | 104 |
| verifizierte Pflichtfelder | 56 |
| Feldabweichungen | 16 |
| fehlende Evidenz | 4 |

Die automatische Freigabe verlangt **zwei getrennte Lesungen plus eine exakte Quellzelle mit Zeilen-, Spalten- und Zeitpunktkontext**. Zwei Modelluebereinstimmungen allein reichen nicht.

## Einzelrecords

| Record | Typ | Status | A exakt | B exakt | Offene Felder |
|---|---|---|---:|---:|---|
| c1-12 | continuous | verified | 6/6 | 6/6 | - |
| c1-13 | binary | pending_review | 4/4 | 4/4 | intervention_n, comparator_n |
| c1-15 | binary | verified | 4/4 | 4/4 | - |
| c1-16 | binary | verified | 4/4 | 4/4 | - |
| c1-21 | continuous | pending_review | 6/6 | 2/6 | intervention_mean, intervention_sd, comparator_mean, comparator_sd |
| c1-22 | continuous | pending_review | 2/6 | 2/6 | intervention_mean, intervention_sd, comparator_mean, comparator_sd |
| c1-24 | continuous | verified | 6/6 | 6/6 | - |
| c1-25 | continuous | verified | 6/6 | 6/6 | - |
| c1-26 | continuous | verified | 6/6 | 6/6 | - |
| c1-27 | continuous | verified | 6/6 | 6/6 | - |
| c1-28 | continuous | verified | 6/6 | 6/6 | - |
| c1-29 | continuous | verified | 6/6 | 6/6 | - |
| c1-32 | continuous | pending_review | 0/6 | 2/6 | intervention_n, intervention_mean, intervention_sd, comparator_n, comparator_mean, comparator_sd |
| c1-36 | binary | pending_review | 4/4 | 0/4 | intervention_n, intervention_events, comparator_n, comparator_events |
| c1-45 | binary | pending_review | 4/4 | 0/4 | intervention_n, intervention_events, comparator_n, comparator_events |
| c1-48 | binary | pending_review | 4/4 | 0/4 | intervention_n, intervention_events, comparator_n, comparator_events |
| c1-50 | binary | pending_review | 4/4 | 0/4 | intervention_n, intervention_events, comparator_n, comparator_events |
| c1-95 | continuous | pending_review | 6/6 | 2/6 | intervention_n, intervention_mean, intervention_sd, comparator_n, comparator_mean, comparator_sd |
| c1-98 | continuous | pending_review | 6/6 | 0/6 | intervention_n, intervention_mean, intervention_sd, comparator_n, comparator_mean, comparator_sd |
| c1-194 | binary | pending_review | 2/4 | 0/4 | intervention_n, intervention_events, comparator_n, comparator_events |

## Grenzen

- Der 249er-Test ist verbraucht und darf nicht als unabhaengiger Nachweis fuer das neue System gelten.
- Pipeline B lief offline als Layout-Geometrie. Der vorhandene Vision-Adapter wurde **nicht** aufgerufen; es gab keinen Netzlauf.
- Ohne menschliche Entscheidung bleibt ein Record mit offenen Feldern `pending_review`; das ist kein Fehler, sondern die Freigaberegel.
- Die Referenzspalte dient nur der Diagnose und wurde nicht zur Extraktion oder Statusvergabe verwendet.
