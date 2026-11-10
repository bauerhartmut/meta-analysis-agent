# Kappa-Probelauf: Konflikte fuer die dritte Stimme (2026-11-10)

Grundlage: nur die drei Probelauf-Dokumente, Toleranz 1 %. Schwelle Zeilen-Kappa: 0.80.

- Dokumente: 3
- Schluessel: 0
- Treffer: 0 (n/a)
- Kappa Dokumentebene: n/a
- Kappa Zeilenebene: n/a
- Konflikte: 0

**Keine Konflikte, weil keine Annotation vorliegt.** Beide Dateien
enthalten keine Effektzeilen. Die Liste fuellt sich, sobald A und B
abgegeben haben; sie ist kein Beleg fuer Uebereinstimmung.

Der Schluessel ist (Dokument, Outcome, Vergleich, Zeitpunkt). Zwei
Zeilen mit demselben Schluessel, aber anderem Typ oder Wert sind ein
Konflikt; zwei Zeilen mit verschiedenen Schluesseln sind `nur_a`/`nur_b`.

## Entscheidungsregeln

- `nur_a` / `nur_b`: Volltext pruefen. Belegt -> in den Konsens;
  nicht belegt -> verwerfen und Grund notieren.
- `typ`: Anleitung 5.2-5.5. `other` nur, wenn keine Kategorie passt.
- `wert`: berichteten Wert uebernehmen; verschiedene Zeitpunkte oder
  Adjustierungen sind getrennte Schluessel, keine Wertabweichung.
- `ki`: berichtetes KI uebernehmen, nicht umrechnen.
- Dokument ohne Zeile bei einem Annotator: pruefen, ob die Zeilen des
  anderen belegt sind; wenn nicht, der Begruendung folgen.

## Nur A (in B nicht vorhanden)

Keine.

## Nur B (in A nicht vorhanden)

Keine.

## Typabweichung

Keine.

## Wertabweichung

Keine.

## KI-Abweichung

Keine.

Volle Zeilen und Schluessel: `data/golden_effects/kappa_konflikte.json`.

