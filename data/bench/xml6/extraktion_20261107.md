# Extraktion der sechs XML-Dokumente (offline)

Stand: 2026-11-07T13:13:51. Kette: `_xml_to_text` -> `save_source_text` -> `blocks_from_jats`/`augment_document_text` -> `EffectExtractor` (zwei unabhaengige Lesungen). Kein Netzlauf, nur die XML-Dateien aus `data/bench/xml6/`.

Poolbar = nicht strittig, kein Ablehnungsgrund, SE oder beide CI-Grenzen, Zitat per `locate_quote` im gespeicherten Text belegt.

| DOI | Zeichen | JATS-Blöcke | stat. Zeilen | Effektzeilen | poolbar | mit SE | mit CI |
|---|---:|---:|---:|---:|---:|---:|---:|
| 10.1001/jamanetworkopen.2026.26983 | 41790 | 3 | 15 | 3 | 1 | 3 | 3 |
| 10.3389/fnut.2026.1890075 | 54590 | 4 | 27 | 2 | 0 | 0 | 0 |
| 10.3390/healthcare13020180 | 35008 | 4 | 1 | 2 | 0 | 0 | 0 |
| 10.3390/ijms27146320 | 49047 | 4 | 3 | 2 | 0 | 0 | 0 |
| 10.3390/medicina62040662 | 64192 | 3 | 6 | 2 | 0 | 0 | 0 |
| 10.5888/pcd20.230198 | 28197 | 3 | 16 | 3 | 0 | 2 | 0 |
| **Summe** | | 21 | 68 | **14** | **1** | 5 | 3 |

Strittig: 4 | abgelehnt: 9 | Zitat nicht auffindbar: 0

## Einzelne Zeilen

### 10.1001/jamanetworkopen.2026.26983

| Outcome | Typ | Effekt | SE | CI | poolbar | Grund |
|---|---|---:|---:|---|---|---|
| Sleep onset latency | g | 0.07 | 0.053572412977088674 | -0.04–0.17 | nein | disputed |
| Sleep onset latency | g | 0.07 | 0.053572412977088674 | -0.04–0.17 | ja | poolable |
| sleep onset latency | g | 0.07 | 0.053572412977088674 | -0.04–0.17 | nein | disputed |

### 10.3389/fnut.2026.1890075

| Outcome | Typ | Effekt | SE | CI | poolbar | Grund |
|---|---|---:|---:|---|---|---|
| sleep quality | beta | None |  |  | nein | rejected |
| sleep quality (PSQI total score) | beta | None |  |  | nein | rejected |

### 10.3390/healthcare13020180

| Outcome | Typ | Effekt | SE | CI | poolbar | Grund |
|---|---|---:|---:|---|---|---|
| Sleep latency | mean_diff | None |  |  | nein | rejected |
| sleep latency | mean_diff | None |  |  | nein | rejected |

### 10.3390/ijms27146320

| Outcome | Typ | Effekt | SE | CI | poolbar | Grund |
|---|---|---:|---:|---|---|---|
| Sleep onset latency | other | None |  |  | nein | rejected |
| Sleep onset latency | other | None |  |  | nein | rejected |

### 10.3390/medicina62040662

| Outcome | Typ | Effekt | SE | CI | poolbar | Grund |
|---|---|---:|---:|---|---|---|
| sleep onset latency | other | None |  |  | nein | rejected |
| sleep onset latency | other | None |  |  | nein | rejected |

### 10.5888/pcd20.230198

| Outcome | Typ | Effekt | SE | CI | poolbar | Grund |
|---|---|---:|---:|---|---|---|
| sleep duration | beta | 0.08 | 0.003 |  | nein | disputed |
| sleep duration | beta | 0.008 | 0.003 |  | nein | disputed |
| sleep onset latency | other | None |  |  | nein | rejected |

