# Post-review diagnostic access summary

**Status:** outcome-informed exploratory manuscript diagnostics.

## D1 — BA1-poetry target-local separability

- Resamples: 1000
- Train/test per resample: 90 / 90
- Accuracy median: 0.5778
- Accuracy mean: 0.5796
- 95% resample interval: [0.5000, 0.6667]
- Six-way chance reference: 0.1667

## D2 — 400-token ceiling audit

- Successful/non-empty BA1 records audited: 540
- Successful/non-empty BA2 records audited: 5398
- BA2 direct cap flags: 0
- Conditional P4-length sensitivity triggered: False

### BA2 by requested line cap

| line cap | n | direct cap | near 95% cap | token median | token p95 | token max |
|---:|---:|---:|---:|---:|---:|---:|
| 5.0 | 1799 | 0 | 0 | 39.0 | 55.0 | 68.0 |
| 10.0 | 1799 | 0 | 0 | 69.0 | 109.0 | 141.0 |
| 20.0 | 1800 | 0 | 0 | 115.0 | 187.0 | 255.0 |

## Interpretation boundary

D1 measures target-local separability, not transfer. D2 distinguishes direct provider termination evidence from token-count proximity. Neither diagnostic upgrades the evidentiary status of the September study.
