# Pass-B-Zeilen ohne Zwilling (2026-11-10)

Geprueft: 8 Datenbanken mit `study_effects`, 1 ohne Tabelle (siehe JSON).

Definition: `extraction_pass > 1` ohne Treffer in Textschluessel (Quelle, Outcome, Vergleich, Richtung), Wert (Quelle, Effekt, SE) oder Quote (Quelle, erste 200 Zeichen) gegen alle Zeilen aus Pass 1. Dieselbe Definition wie Teil D der E5-Messung.

**45 Zeilen ohne Zwilling**, davon 20 mit Zahl und SE und 4 nach `build_analysis` in einer Gruppe.

## Verteilung

| Klasse | Zeilen | Bedeutung |
|---|---:|---|
| `anderes_outcome_unpoolbar` | 15 | Pass 1 las dieselbe Quelle fuer ein anderes Mass - eigenstaendiger Fund |
| `anderes_outcome` | 15 | Pass 1 las dieselbe Quelle fuer ein anderes Mass - eigenstaendiger Fund |
| `nur_pass_b_unpoolbar` | 6 | Pass 1 hat die Quelle nicht gelesen - echter Fund |
| `andere_aussage` | 4 | Pass 1 las dieselbe Quelle, anderen Kontrast - eigenstaendiger Fund |
| `andere_aussage_unpoolbar` | 3 | Pass 1 las dieselbe Quelle, anderen Kontrast - eigenstaendiger Fund |
| `gleiche_stelle_unpoolbar` | 1 | Quote teilt den Anfang, Text weicht ab - Grenzfall der Zitatregel |
| `nur_pass_b` | 1 | Pass 1 hat die Quelle nicht gelesen - echter Fund |

## Beispiele

### `anderes_outcome_unpoolbar` (4 von 15 gezeigt)

- harness_local.db: `683bd1c26269` / 'total sleep time' / Effekt 3.0 / SE None / Pass-1-Zeilen der Quelle: 1 / dort: sleep onset latency
- research-exercise-and-depressive-symptoms-in-adul-bbb324.db: `182b05a12853` / '' / Effekt None / SE None / Pass-1-Zeilen der Quelle: 1 / dort: depressive symptoms
- research-exercise-and-depressive-symptoms-in-adul-bbb324.db: `b0e4bca955f2` / 'treatment resistance (TRD vs non-TRD)' / Effekt None / SE 0.005102135 / Pass-1-Zeilen der Quelle: 1 / dort: depressive symptoms
- research-exercise-and-depressive-symptoms-in-adul-bbb324.db: `4ed4d3592910` / 'depressive symptoms' / Effekt None / SE None / Pass-1-Zeilen der Quelle: 1 / dort: physical activity (moderate to vigorous, perceived intensity)

### `anderes_outcome` (4 von 15 gezeigt)

- research-exercise-and-depressive-symptoms-in-adul-bbb324.db: `4927a0818af5` / 'chronic disease incidence' / Effekt 0.005 / SE 0.001785747 / Pass-1-Zeilen der Quelle: 1 / dort: depressive symptoms
- research-exercise-and-depressive-symptoms-in-adul-bbb324.db: `9d341af7b02a` / 'depressive symptoms' / Effekt -0.18 / SE 0.079083086 / Pass-1-Zeilen der Quelle: 1 / dort: physical activity
- research-exercise-and-depressive-symptoms-in-adul-bbb324.db: `b181ec03741f` / 'physical activity at 2 years' / Effekt 1.87 / SE 0.303577007 / Pass-1-Zeilen der Quelle: 1 / dort: depressive symptoms
- research-kognition-und-gesundheit-ist-der-zusamme-ec45a1.db: `95f947ecfddd` / 'Frailty Index' / Effekt 0.15 / SE 0.031888341 / Pass-1-Zeilen der Quelle: 1 / dort: 

### `nur_pass_b_unpoolbar` (4 von 6 gezeigt)

- research-does-caffeine-intake-affect-short-term-m-783a51.db: `de5d50203d6e` / '' / Effekt None / SE None / Pass-1-Zeilen der Quelle: 0
- research-exercise-and-depressive-symptoms-in-adul-bbb324.db: `78724545a3f7` / '' / Effekt None / SE None / Pass-1-Zeilen der Quelle: 0
- research-kognition-und-gesundheit-ist-der-zusamme-ec45a1.db: `4ac5e3b8b1a7` / '' / Effekt None / SE None / Pass-1-Zeilen der Quelle: 0
- research-kognition-und-gesundheit-ist-der-zusamme-ec45a1.db: `febd6d28db9c` / '' / Effekt None / SE None / Pass-1-Zeilen der Quelle: 0

### `andere_aussage` (4 von 4 gezeigt)

- research-exercise-and-depressive-symptoms-in-adul-bbb324.db: `f9d8fbabbc39` / 'depressive symptoms' / Effekt -0.24 / SE 0.12 / Pass-1-Zeilen der Quelle: 1 / dort: depressive symptoms
- research-mediterrane-ernaehrung-und-kardiovaskula-475855.db: `bbd18327e2ae` / 'Incident cardiovascular disease' / Effekt 0.67 / SE 0.130104432 / Pass-1-Zeilen der Quelle: 1 / dort: Incident cardiovascular disease
- research-mediterrane-ernaehrung-und-kardiovaskula-475855.db: `ad7207a5e12f` / 'Incident cardiovascular disease' / Effekt 1.67 / SE 0.448987842 / Pass-1-Zeilen der Quelle: 1 / dort: Incident cardiovascular disease
- research-mediterrane-ernaehrung-und-kardiovaskula-475855.db: `be86f50d8f30` / 'Major adverse cardiovascular events' / Effekt 1.784 / SE 0.530111782 / Pass-1-Zeilen der Quelle: 1 / dort: Major adverse cardiovascular events

### `andere_aussage_unpoolbar` (3 von 3 gezeigt)

- harness_local.db: `eadc35037dca` / 'sleep onset latency' / Effekt None / SE None / Pass-1-Zeilen der Quelle: 1 / dort: sleep onset latency
- research-exercise-and-depressive-symptoms-in-adul-bbb324.db: `ad24b3f96a7e` / 'physical activity agreement' / Effekt 0.083 / SE None / Pass-1-Zeilen der Quelle: 1 / dort: physical activity agreement
- research-kognition-und-gesundheit-ist-der-zusamme-ec45a1.db: `df23352f42dd` / 'General cognitive ability' / Effekt None / SE None / Pass-1-Zeilen der Quelle: 1 / dort: General cognitive ability

### `gleiche_stelle_unpoolbar` (1 von 1 gezeigt)

- research-kognition-und-gesundheit-ist-der-zusamme-ec45a1.db: `ad44822de20b` / 'Psychological distress' / Effekt None / SE None / Pass-1-Zeilen der Quelle: 1 / dort: Psychological distress

### `nur_pass_b` (1 von 1 gezeigt)

- research-mediterrane-ernaehrung-und-kardiovaskula-475855.db: `85a47de24314` / 'Cancer recurrence or cancer-specific mortality' / Effekt 0.83 / SE 0.073980951 / Pass-1-Zeilen der Quelle: 0
