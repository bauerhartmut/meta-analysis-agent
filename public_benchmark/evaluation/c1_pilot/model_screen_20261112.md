# C1-Modell-Screening 2026-11-12

Stand: 2026-11-12
Status: **ABGESCHLOSSEN - kein Modell schlägt Qwen auf Dev; GLM 5.3 technisch unbrauchbar**
Daten: **26 Dev-Records, 140 erwartete Felder; Testsplit unberührt**
Prompt: **c1-dev-extract-v6**, Temperatur 0, max_tokens 900, Concurrency 3

## 1. Ziel

Geprüft wurde, ob die HRZ-Modelle

- `gwdg/deepseek-v4.1-flash-1017`
- `gwdg/glm-5.3`

auf dem C1-Dev-Set besserperformen als der bisherige Kandidat
`gwdg/qwen3.5-397b-a17b`.

Wichtig: Qwen erreicht auf Dev **140/140**. Auf diesem Set kann kein Modell
„besser“ werden; der Test misst höchstens Gleichstand, Abdeckung, Fehlerart
und Latenz. Der 249er-Test wurde nicht verwendet.

## 2. Ergebnisse

| Modell | Records | exakt | Abdeckung | fehlend | falsch | halluziniert | Parse-Fehler | vollständig exakt | mittlere Latenz |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gwdg/qwen3.5-397b-a17b` (Baseline) | 26/26 | **140/140 (100 %)** | 100 % | 0 | 0 | 0 | 0 | 26/26 | 6,67 s |
| `gwdg/deepseek-v4.1-flash-1017` | 26/26 | **134/140 (95,7 %)** | 95,7 % | 6 | 0 | 0 | 0 | 24/26 | 2,83 s |
| `gwdg/glm-5.3` | 26/26 | **34/140 (24,3 %)** | 24,3 % | 106 | 0 | 0 | 20 | 6/26 | 5,46 s |

Die Qwen-Zeile ist der eingefrorene Baseline-Lauf
`c1_dev_20261111_v6c`; Qwen wurde nicht erneut ausgeführt.

## 3. DeepSeek V4.1 Flash 1017

**Ergebnis:** 134/140 exakt, 6 fehlend, 0 falsch, 0 halluziniert,
0 Parse-Fehler, 24/26 Records vollständig exakt, MAE 0,0.

Fehlende Felder:

| Record | Typ | fehlende Felder | Anzahl |
|---:|---|---|---:|
| 191 | binary | `intervention_n`, `comparator_n`, `intervention_events`, `comparator_events` | 4 |
| 233 | continuous | `intervention_n`, `comparator_n` | 2 |

Feldbild:

- `intervention_n`: 24/26 exakt, 2 fehlend.
- `comparator_n`: 24/26 exakt, 2 fehlend.
- `intervention_events`: 7/8 exakt, 1 fehlend.
- `comparator_events`: 7/8 exakt, 1 fehlend.
- Means/SDs: jeweils 18/18 exakt.

Damit ist DeepSeek **näher an Qwen als GLM**, aber nicht gleichwertig:
Die Record-Vollständigkeit liegt bei 24/26 (92,3 %) und damit unter G2
(≥ 95 %). G3 gesamt ist mit 95,7 % knapp über 95 %, aber die kritischen
N- und Event-Felder liegen darunter. G4 wäre mit 24/26 (92,3 %) erfüllt.
G5 bleibt unabhängig davon offen.

## 4. GLM 5.3

**Ergebnis:** 34/140 exakt, 106 fehlend, 0 falsch, 0 halluziniert,
20/26 Records ohne verwertbare Antwort, 6/26 vollständig exakt.

Die 20 Fehler sind:

- 19 leere Antworten,
- 1 abgeschnittene JSON-Antwort (Record 233).

Die sechs erfolgreichen Records (225, 226, 234, 236, 237, 261) waren
vollständig exakt. Das Modell ist in diesem Setup jedoch nicht zuverlässig
evaluierbar: Es liefert die meiste Zeit keinen Content zurück. Das ist
primär ein technisches Endpoint-/Antwortproblem, keine belastbare Aussage
über die Extraktionsqualität des Modells.

## 5. Einordnung

- **Kein Modell ist besser als Qwen.** Qwen ist auf Dev am Ceiling.
- **DeepSeek** ist der einzige brauchbare Alternativkandidat: keine falschen
  oder halluzinierten Werte, aber 6 fehlende Felder in 2 Records. Die
  Latenz ist deutlich niedriger als bei Qwen, aber ein einzelner Lauf mit
  Rate-Limits ist kein belastbarer Kosten-/Geschwindigkeitsvergleich.
- **GLM 5.3** ist mit dem aktuellen Runner nicht einsetzbar. Die leeren
  Antworten müssen zuerst auf API-/Parameter-Ebene geklärt werden.
- **Kein Testsplit, keine Prompt-Änderung, keine Gate-Freigabe.** Der
  249er-Test bleibt verbraucht und unangetastet.

## 6. Empfehlung

1. **Qwen bleibt der Referenzkandidat.** Kein Wechsel allein aufgrund
   dieses Dev-Screenings.
2. **DeepSeek nur als Zweitkandidat weiterverfolgen**, wenn die zwei
   fehlenden N-/Event-Records (191, 233) auf Dev adressiert sind. Kein
   Prompt-Tuning auf dem Testsplit.
3. **GLM 5.3 nicht weiter testen**, solange 20/26 Antworten leer oder
   abgeschnitten sind. Zuerst Endpoint/Response-Format klären.
4. **Nächster belastbarer Schritt:** externen, artikeldisjunkten Holdout
   beschaffen. Ohne G5 bleibt jede Aussage „besser als Qwen“ auf Dev
   bedeutungslos, weil Qwen dort bereits 100 % erreicht.

## 7. Artefakte

- Qwen-Baseline: [`runs/c1_dev_20261111_v6c/`](runs/c1_dev_20261111_v6c/)
- DeepSeek: [`runs/c1_dev_20261112_deepseek_v41_flash/`](runs/c1_dev_20261112_deepseek_v41_flash/)
- GLM: [`runs/c1_dev_20261112_glm_5_3/`](runs/c1_dev_20261112_glm_5_3/)
- JSON-Zusammenfassung: [`model_screen_20261112.json`](model_screen_20261112.json)

**Kein Modelllauf auf dem Testsplit. Keine Prompt-Änderung. Keine
automatische Freigabe.**
