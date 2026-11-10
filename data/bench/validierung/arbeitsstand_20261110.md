# Arbeitsstand 2026-11-10 — Lesepass-Dedup bis SE-Audit

Zeitraum: seit Commit `f5eb24b` (Dedup-Messung, „nur echte Zwillinge fallen aus
dem Pool"). Danach vier Commits, alle gepusht:

| Commit | Inhalt |
|---|---|
| `325a9c3` | Bericht weist die Prüfspur der Doppellesung aus |
| `3660d2c` | 45 Pass-B-Zeilen ohne Zwilling klassifiziert, beleglose Schlüssel gehärtet |
| `6c6d37d` | Einzige poolbare `nur_pass_b`-Zeile geprüft: Review-Aggregat, Gate greift |
| `8e3f21e` | SE-gegen-KI-Audit: wo die SE im Pool zählt, passt sie |

Alle Läufe offline, read-only auf Kopien, **0 Modellaufrufe**.

---

## 1. Prüfspur im Bericht (`325a9c3`)

**Problem:** Die Dedup-Regel verhinderte Doppelzählungen, aber der Bericht
zeigte sie nicht. Verworfene Kopien fielen nur in die allgemeine Liste „Warum
Zeilen nicht gepoolt wurden"; poolbare Zeilen aus Pass B sahen aus wie jede
andere Zeile.

**Lösung:** In `report.py` die Funktion `_pruefspur_counts(analysis)` und der
Abschnitt „Prüfspur: zweite Lesungen". Er nennt zwei Zahlen getrennt:

- verworfene Kopien (`excluded` mit Grund „zweite Lesung …") — ein verhinderter
  Fehler;
- poolbare Zeilen mit `extraction_pass > 1` — im Pool, aber ohne Gegenlesung,
  also eine offene Prüfung.

`pooling.py` reicht dafür `extraction_pass` bis in die Gruppenzeilen durch.
Der Abschnitt erscheint nur, wenn mindestens eine Zahl > 0 ist.

**Beleg:** Rendert im echten Bericht (`data/harness_local.db`, Topic
`melatonin`). Vor der Schlüssel-Härtung: **9** verworfene Kopien; danach
**5** — die Differenz waren vier beleglose Zeilen, die fälschlich als Kopien
zählten (siehe Abschnitt 2).

**Tests:** 4 neue in `test_meta_pruefspur.py`; Report-Nachbarschaft 79 bzw. 70
grün; Prüfskript Exit 0 (report.py 7 Marker).

---

## 2. 45 Pass-B-Zeilen ohne Zwilling (`3660d2c`)

**Frage:** Sind die 45 poolbaren Zweitlesungen echte Funde oder fehlende
Gegenlesungen?

**Ergebnis** (8 Themen-DBs, dieselbe Grundgesamtheit wie Teil D der Messung):

| Klasse | Zeilen | mit Zahl + SE | Bedeutung |
|---|---:|---:|---|
| `anderes_outcome` | 30 | 15 | Pass 1 las dieselbe Quelle für ein anderes Maß |
| `nur_pass_b` | 7 | 1 | Pass 1 hat die Quelle gar nicht gelesen |
| `andere_aussage` | 7 | 4 | Pass 1 las dieselbe Quelle, anderen Kontrast |
| `gleiche_stelle` | 1 | 0 | Grenzfall: Quote teilt den Anfang, Text weicht ab |

**Keine einzige Zeile ist eine übersehene Kopie.** 37 sind eigenständige
Aussagen derselben Quelle, 7 stammen aus Quellen ohne Erstlesung, 1 ist ein
Grenzfall. Poolbar (im Sinne von `standardize`) sind **16**, in einer
Gruppe landen **4**.

**Dabei gefundener Bug:** `_wert_zwilling` gab für Zeilen ohne Effekt
`("", None, None)` zurück, `_zitat_zwilling` für Zeilen ohne Quote `("", "")` —
beides für alle solchen Zeilen identisch. Damit galt eine Zweitlesung ohne
Beleg als Kopie jeder anderen beleglosen Zeile. Behoben: Beide Schlüssel tragen
ohne Beleg die Zeilen-ID. Hauptpfad unverändert (Exercise k 24 → 21, abgelehnt
105 → 108). Zwei neue Tests; 11 im Modul, 181 in der Nachbarschaft.

**Artefakte:** `scripts/klassifiziere_pass_b_20261110.py`,
`data/bench/validierung/pass_b_ohne_zwilling_20261110.{md,json}`, Nachtrag in
`research_agent/patches/pooling_lesepass_dedup_20261110.md`.

---

## 3. Review-Aggregat-Zeile geprüft (`6c6d37d`)

**Zeile:** `e8ba18ca3525`, Quelle `85a47de24314` (Papamichael et al. 2026),
Outcome Krebsrezidiv, HR 0,83 (95 %-KI 0,70–0,99, I² = 49 %), n = 6697.

**Volltextbeleg:** Zitat wortgleich, Zahl korrekt übertragen — kein Lesefehler.

**Entscheidung: darf nicht in den Pool.** Es ist der gepoolte Schätzer einer
Übersichtsarbeit über sechs Kohorten. Das bestehende Gate
(`aggregate_design`) weist die Zeile bereits ab; sie steht in `excluded` mit
„Übersichtsarbeit …, keine Primärstudie" und in keiner Gruppe. Keine Änderung
nötig.

**Korrekturen an meiner eigenen Darstellung:**

- `85a47de24314` ist die **source_id**, nicht die Zeilen-ID.
- Die Zeile war nie im Pool; die frühere Formulierung „einzige ungegelesene
  Zahl im Pool" war falsch.
- Die „SE 16,3 % zu klein"-Diagnose war falsch (siehe Abschnitt 4).

**Artefakt:** `data/bench/validierung/pruefung_pass_b_zeile_20261110.md`.

---

## 4. SE-gegen-KI-Audit (`8e3f21e`)

**Code-Befund, entscheidend für die Bewertung:** `standardize` rechnet bei
Ratio-Typen (`or`, `rr`, `hr`) **mit vorhandenem KI** die log-SE aus dem KI und
ignoriert die gespeicherte `se`. Nur ohne KI liest es `se` als log-SE. Lineare
Typen (`beta`, `mean_diff`, `g`, `smd`, `z`, `heritability`) nutzen `se` direkt.

**A. Skala der SE bei Ratio-Typen** (2 636 Zeilen mit KI): 2 632 liegen auf der
Ratio-Skala (±5 %) — `hr` 40/40, `rr` 80/80, `or` 2 512/2 516. Das ist die
Extraktionskonvention und unschädlich, weil **jede** Ratio-Zeile ein KI hat
(0 Zeilen ohne KI).

**B. Abweichung dort, wo die SE gelesen wird** (3 947 lineare Zeilen):
Median 0,0 %, **2 Zeilen** über 10 % (beide dieselbe smd-Zeile `0d6b1b995a0c`,
+12,0 %), 0 über 20 %. Nach Design und Lesepass kein Muster.

**Nicht prüfbar:** 709 lineare Zeilen ohne KI, 464 mit Typ `r`/`other`/leer,
89 ohne SE, 52 ohne Effekt.

**Zurückgenommene Aussage:** Die Mediterran-SE 0,073981 ist exakt
(0,99 − 0,70)/3,92, also die SE auf der HR-Skala. „16,3 % zu klein" beruhte auf
einem falschen Skalenvergleich. Für den Pool gilt ohnehin die aus dem KI
gerechnete SE 0,0884.

**Artefakte:** `scripts/messe_se_ki_konsistenz_20261110.py`,
`data/bench/validierung/se_ki_konsistenz_20261110.{md,json}`, korrigierter
Prüfbericht aus Abschnitt 3.

---

## Prüfstand

| Prüfung | Ergebnis |
|---|---|
| Lesepass-Modul | 11 Tests grün |
| Nachbarschaft (Pooling, Extraction, Gates, Targets, Cohort, RVE, Reference, Report, Prüfskript) | 181 passed |
| `scripts/pruefe_report_patch.py` | Exit 0 |
| Alle Messskripte | Exit 0, 0 Modellaufrufe |
| Produktionscode geändert in `8e3f21e` | nein (nur Skript und Berichte) |

Geschützte Dateien (`report.py`, `pooling.py`) sind gitignored und **nicht**
committet; die Änderungen sind über `research_agent/patches/` (Eintrag,
Marker im Prüfskript, Sicherung in `local_patches/`) belegt.

---

## Grenzen

1. **709 lineare Zeilen ohne KI** — dort geht die SE ungeprüft in Gewichte und
   Intervall ein; der einzige verbliebene blinde Fleck.
2. **Ratio-SE ist toter Ballast**, solange ein KI da ist: eine falsch
   gespeicherte Ratio-SE fiele nicht auf.
3. **`anderes_outcome` heißt nicht unabhängig** — dieselbe Quelle kann dieselbe
   Stichprobe unter anderem Label berichten; für RVE bleiben das abhängige
   Zeilen.
4. **7 `nur_pass_b`-Zeilen** sind ohne Ursache: Volltext fehlte, Gate, oder
   Quelle kam später dazu — das Skript sagt es nicht.
5. Der Arbeitsbaum enthält weiterhin untracked Altlasten (`data/runs/`,
   `data/bench/backfill/run*.db`, modifizierte `search_*.json`) — bewusst nicht
   committet.

---

## Nächste Schritte (priorisiert)

1. **709 lineare Zeilen ohne KI auf SE-Plausibilität prüfen** — offline,
   arithmetisch gegen `n` und Design (z. B. se ≈ sqrt(1/n₁+1/n₂) für
   standardisierte Mittelwerte, Ausreißer nach oben und unten markieren).
   Wirkung: schließt den letzten blinden Fleck der SE-Prüfung. Kosten: 0
   Guthaben, ~1 Stunde. Risiko: gering.
2. **Die 2 Ausreißer (smd +12 %) am Volltext prüfen** — klein, aber billig;
   klärt, ob es ein Übertragungsfehler oder eine andere KI-Berechnung ist.
3. **Ursachen der 7 `nur_pass_b`-Zeilen sortieren** — Volltext vorhanden? Gate?
   Später hinzugekommen? Entscheidet, ob dort eine Gegenlesung fehlt.
4. **Optional:** Die Ratio-SE-Spalte als „nur bei fehlendem KI relevant"
   dokumentieren oder ein Skalen-Gate für den Fall ergänzen, dass künftig eine
   Ratio-Zeile ohne KI entsteht (heute 0 Fälle).

**Empfehlung:** Schritt 1 zuerst. Er ist der einzige Punkt, an dem eine falsche
Zahl noch unbemerkt in ein gepooltes Ergebnis eingehen könnte, kostet kein
Guthaben und liefert eine belastbare Quote statt einer Vermutung.

---

## Dateien dieses Zeitraums

**Neu:** `research_agent/tests/test_meta_pruefspur.py`,
`research_agent/patches/report_pruefspur_20261110.md`,
`scripts/klassifiziere_pass_b_20261110.py`,
`scripts/messe_se_ki_konsistenz_20261110.py`,
`data/bench/validierung/pass_b_ohne_zwilling_20261110.{md,json}`,
`data/bench/validierung/pruefung_pass_b_zeile_20261110.md`,
`data/bench/validierung/se_ki_konsistenz_20261110.{md,json}`.

**Geändert (committet):** `research_agent/tests/test_meta_lesepass_dedup.py`,
`scripts/pruefe_report_patch.py`, `research_agent/patches/README.md`,
`research_agent/patches/pooling_lesepass_dedup_20261110.md`,
`data/bench/validierung/lesepass_filter_20261110.{md,json}`.

**Geändert (geschützt, lokal):** `research_agent/report.py`,
`research_agent/meta/pooling.py` — Sicherungen in
`local_patches/report_20261110.py`, `local_patches/pooling_20261110_lesepass.py`.
