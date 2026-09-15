# September 2026 parser validation score

Threshold: **0.90**
Packet rows: **180**
Overall gate: **PASS**

| Field | n scored | n N/A | n missing | agreement | pass |
|---|---:|---:|---:|---:|---|
| preamble_present | 180 | 0 | 0 | 0.989 | yes |
| title_present | 180 | 0 | 0 | 0.994 | yes |
| preamble_boundary_correct | 25 | 155 | 0 | 0.920 | yes |
| title_boundary_correct | 73 | 107 | 0 | 0.986 | yes |
| creative_body_start_correct | 180 | 0 | 0 | 0.989 | yes |

If any applicable field is below 0.90, the locked plan permits parser revision before primary outcome analysis, with the change documented in the September deviations log.
