# C1-Testprojektion: Prüfbericht

Stand: 2026-11-11T23:16:37
Status: **PASSED**

| Prüfung | Ergebnis |
|---|---|
| `freeze_sha256` | OK |
| `projection_records` | OK |
| `reference_records` | OK |
| `source_records` | OK |
| `projection_input_sha256` | OK |
| `projection_reference_sha256` | OK |
| `projection_frozen_sha256` | OK |
| `input_ids_unique` | OK |
| `reference_ids_unique` | OK |
| `input_reference_same_ids` | OK |
| `no_dev_test_id_overlap` | OK |
| `input_schema` | OK |
| `reference_schema` | OK |
| `input_split_test` | OK |
| `reference_split_test` | OK |
| `input_ico_schema` | OK |
| `no_reference_fields_in_input` | OK |
| `article_count` | OK |
| `type_counts` | OK |
| `expected_fields_1308` | OK |
| `input_matches_freeze` | OK (0 Abweichungen) |
| `reference_matches_freeze` | OK (0 Abweichungen) |
| `source_paths_exist` | OK (0 fehlend) |
| `test_policy_locked` | OK |
| `reference_not_loaded_by_runner` | OK |
| `no_prompt_optimization` | OK |

## Zählungen

- Records: 249
- Artikel: 64
- Typen: {'continuous': 156, 'binary': 93}
- Erwartete Felder: 1308

## Hashes

- Freeze: `567d54b81ca07163979684e43ab333a740812909614b7215c2de5edd200bf13c`
- Test-Input: `b8a2f3d17c2ee4a41473811ccb72632175f1d786b05b9e16e2d8c18d64204368`
- Test-Referenz: `84b5c925340af82eb72717b36b2e4c5a2fa04760d6a6d01e63b742d0689e0629`

Der Testsplit wurde für die Projektion gelesen, aber nicht für Prompt-Optimierung oder einen Modelllauf verwendet.
