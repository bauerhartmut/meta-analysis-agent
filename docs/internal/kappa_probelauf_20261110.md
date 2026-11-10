# Kappa-Probelauf: drei Dokumente (2026-11-10)

Ziel: Prüfen, ob die Anleitung an den Grenzfällen trägt, **bevor** alle 30
Dokumente annotiert werden. Drei Dokumente kosten drei Dokumente; dreißig
kosten dreißig.

## Die drei Dokumente

| Schicht | ID | Titel (gekürzt) | Warum |
|---|---|---|---|
| RCT | `bb9218735f` | Multicenter, placebo-controlled trial of melatonin | Ratio-Maß plus KI, mehrere Endpunkte |
| Kohorte | `7111ea9787` | Mediterranean diet in preeclampsia prevention | adjustiert/unadjustiert, OR und RR gemischt |
| Aggregat | `203c831dbe` | Post-diagnosis Mediterranean diet and cancer outcomes | gepoolter Schätzer, `is_primary: false` |

Die Markierung steht als `probelauf: true` in beiden Gerüsten. Die Auswertung
filtert darüber, ohne dass jemand IDs abtippen muss.

## Ablauf

1. Gerüste erzeugen (einmalig):
   `python scripts/erzeuge_annotationsgeruest.py`
2. A und B füllen die drei Dokumente **unabhängig** aus — nur Volltext,
   Anleitung, Schema. Kein Blick in die andere Datei, keine DB.
3. Jede Datei prüfen:
   `python scripts/pruefe_goldstandard.py --entwurf data/golden_effects/goldstandard_A.json`
   (im Entwurfsmodus sind noch nicht bearbeitete Dokumente „offen", kein Fehler).
4. Erst wenn beide abgegeben haben, auswerten:
   `python scripts/werte_kappa_probe.py --probelauf --out data/golden_effects/kappa_probe.json`

## Was ausgewertet wird

- **Kappa Dokumentebene:** hat ein Dokument in beiden Dateien mindestens eine
  Zeile (ja/nein)?
- **Kappa Zeilenebene:** kommt derselbe Schlüssel aus Dokument, Outcome,
  Vergleich und Zeitpunkt in beiden Dateien vor? Die Item-Menge ist die
  Vereinigung; eine Zeile, die nur einer sieht, zählt als Nicht-Übereinstimmung.
- **Übereinstimmungsquote** und **Konflikte**: `nur_a`, `nur_b`,
  Typ-Abweichung, Wert-Abweichung (Toleranz 1 %), KI-Abweichung.

Das Skript rechnet Cohens Kappa selbst (kein sklearn), `--selbsttest` prüft
die Formel an vier konstruierten Fällen.

## Schwelle und Konsequenz

- Zeilen-Kappa **≥ 0,80**: Anleitung trägt, alle 30 annotieren.
- **< 0,80**: Anleitung an den häufigsten Konfliktarten schärfen (nicht die
  Auswahl ändern) und die betroffene Schicht neu annotieren.

Ein niedriger Wert ist ein Befund über die Anleitung, nicht über die
Annotatoren. Deshalb wird er dokumentiert und nicht geglättet.

## Stand

Gerüste erzeugt, beide Dateien enthalten 30 Dokumente und **0 Effektzeilen**.
Der Nullbericht liegt in `data/golden_effects/kappa_probe.json`; Kappa ist
dort bewusst `null`, weil ohne eine einzige Zeile keine Übereinstimmung
gemessen werden kann.
