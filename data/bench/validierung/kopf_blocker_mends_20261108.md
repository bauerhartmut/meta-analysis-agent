# Kopfzeilen-Blocker: abgelehnte Zeilen mit lesbarem Effekt

Stand: 2026-11-08T19:40:28+00:00. Read-only: kein Modell, kein Netz, keine Aenderung an der Pipeline.

## Kennzahlen

| Kennzahl | Wert |
|---|---:|
| untersuchte Dateien | 1 |
| erkannte Tabellenbloecke | 48 |
| von `effects_from_row` abgelehnte Zeilen | 724 |
| davon mit lesbarem Effekt samt Intervall | **23** (3.18 %) |
| betroffene Bloecke | 2 |
| davon mit Effektwort im Zeilenlabel | 0 |
| davon mit Effektwort in der Caption | 0 |

## Kategorien

| Kategorie | Bedeutung | Zeilen |
|---|---|---:|
| `nur_kopf` | Zelle lesbar, Spaltenzahl passt, aber keine Effektspalte an ihrer Position | 3 |
| `position_daneben` | Effektspalte existiert, aber an anderer Stelle | 0 |
| `kopf_und_spalten` | Zelle lesbar, aber Kopf und Zeile haben verschieden viele Zellen | 20 |

## Beispiele

### `data/bench/sol2/volltext/23098680.txt`

48 Bloecke, 724 abgelehnte Zeilen, 23 mit lesbarem Effekt.

- Block 3 (nur_kopf): `106 (34.8), 44 to 181` -> [106.0, 44.0, 181.0]; Spalten 4/4; Kopf-Effektspalten -; Label-Effektwort -
- Block 3 (nur_kopf): `50.8 (9.9), 40 to 73` -> [50.8, 40.0, 73.0]; Spalten 4/4; Kopf-Effektspalten -; Label-Effektwort -
- Block 6 (kopf_und_spalten): `27.91 (4.35 to 51.48)` -> [27.91, 4.35, 51.48]; Spalten 7/8; Kopf-Effektspalten -; Label-Effektwort -
- Block 6 (kopf_und_spalten): `-37.44 (-58.77 to -16.11)` -> [-37.44, -58.77, -16.11]; Spalten 4/8; Kopf-Effektspalten -; Label-Effektwort -
- Block 6 (kopf_und_spalten): `7.37 (-22.97 to 37.71)` -> [7.37, -22.97, 37.71]; Spalten 9/8; Kopf-Effektspalten -; Label-Effektwort -

## Was die Zahl bedeutet

23 von 724 abgelehnten Zeilen tragen einen lesbaren Effekt samt Intervall (3.18 %). Davon haetten 3 bei stimmiger Spaltenzuordnung nur am Kopf gescheitert; die uebrigen scheitern zusaetzlich an der Spaltenzuordnung oder an der Position der Effektspalte. Ein Kopfzeilen-Fix allein rettet also hoechstens 3 Zeile(n).

## Grenzen

- Gemessen wird nur, was `parse_effect_cell` lesen kann; andere Schreibweisen zaehlen als nicht lesbar.
- Eine lesbare Zelle belegt nicht die richtige Zuordnung zu Endpunkt, Arm und Zeitpunkt. Die Messung sagt nur, ob die Zahl maschinenlesbar vorliegt.
- Die Stichprobe ist der lokale Textbestand, keine Aussage ueber den gesamten Korpus.
- `parse_effect_cell` liest auch Baseline-Zeilen wie `106 (34.8), 44 to 181` als Effekt mit Intervall. Die Kategorie `nur_kopf` ist deshalb eine OBERGRENZE, keine Trefferzahl: bei MENDS sind ihre drei Zeilen Baseline-Mittelwerte, keine Effekte.

## Reproduktion

```bash
export PYTHONIOENCODING=utf-8
.venv/bin/python.exe scripts/messe_kopf_blocker.py \
  --file data/bench/sol2/volltext/23098680.txt
```

Laufzeit: 0.446 s.
