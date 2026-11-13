# GLM-5.3-Diagnose

Stand: 2026-11-13
Modell angefragt: `gwdg/glm-5.3`, Backend TUDaGPT, Daten: Dev-Records 120 und 233.

| Fall | HTTP | content | finish_reason | completion_tokens | reasoning |
|---|---:|---:|---|---:|---:|
| record120_baseline | 200 | 0 | length | 900 | 3414 |
| record120_repeat | 200 | 0 | length | 900 | 3414 |
| record120_no_reasoning_param | 200 | 0 | length | 900 | 3238 |
| record120_max_tokens_2000 | 200 | 0 | length | 2000 | 7551 |
| record120_stream | 200 | 3282 | length | None | 0 |
| record233_baseline | 200 | 0 | length | 900 | 3345 |
| record120_max_tokens_8000 | 200 | 385 | stop | 4035 | 14897 |
| record120_max_tokens_16000 | 200 | 386 | stop | 2544 | 9166 |
