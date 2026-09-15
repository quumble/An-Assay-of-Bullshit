# Post-primary I&A access summary

**Status:** outcome-informed exploratory diagnostics.

This file is generated mechanically from the I&A outputs. It reports values without upgrading their evidentiary status.

## IA1 — matched-size cross-study transfer

- Resamples: 1000
- Training size per resample: 360
- Frozen BA1-poetry test size: 180
- Median accuracy: 0.4611
- 95% resample interval: [0.4056, 0.5222]
- Frozen full-training P1 accuracy: 0.4889
- Frozen P3 holdout accuracies: story=0.2444, animal=0.2500, poem=0.1778

## IA2 — feature-family decomposition (headline pooled conditions)

| Feature family | P1 cross-study | P3 pooled | P4 phrasing pooled | P4 length pooled |
|---|---:|---:|---:|---:|
| form_structure | 0.3444 | 0.2352 | 0.3101 | 0.2742 |
| grammar_person | 0.3167 | 0.1833 | 0.4533 | 0.4014 |
| punctuation | 0.3389 | 0.2389 | 0.4087 | 0.3579 |
| nonstructural_style | 0.4333 | 0.2037 | 0.5584 | 0.4961 |
| full_body | 0.4889 | 0.2241 | 0.6193 | 0.4843 |

## Model heterogeneity — frozen full-body references

| Model | P1 recall | P3 pooled recall | P4 phrasing pooled recall | P4 length pooled recall |
|---|---:|---:|---:|---:|
| claude-haiku-4-5-20251001 | 0.7333 | 0.2222 | 0.4233 | 0.3144 |
| claude-sonnet-4-6 | 0.4333 | 0.3444 | 0.6678 | 0.4700 |
| claude-opus-4-7 | 0.1000 | 0.1889 | 0.6733 | 0.4200 |
| gpt-5.4-nano | 0.6333 | 0.1444 | 0.8298 | 0.6263 |
| gpt-5.4-mini | 0.5667 | 0.1667 | 0.6233 | 0.6589 |
| gpt-5.4 | 0.4667 | 0.2778 | 0.4983 | 0.4160 |

## Concrete behavioral example — opening-token entropy

| Model | BA1 entropy | BA2 rarefaction mean | BA2 95% interval | BA1 inside interval |
|---|---:|---:|---:|:---:|
| claude-haiku-4-5-20251001 | 2.7811 | 2.1395 | [1.3722, 2.8497] | True |
| claude-sonnet-4-6 | 0.2108 | 0.0482 | [-0.0000, 0.2108] | True |
| claude-opus-4-7 | 1.2580 | 0.9573 | [0.7219, 1.2310] | False |
| gpt-5.4-nano | 1.2976 | 2.0430 | [1.4834, 2.5716] | False |
| gpt-5.4-mini | 1.2656 | 1.4634 | [0.8118, 2.0988] | True |
| gpt-5.4 | 2.1671 | 2.3944 | [1.9722, 2.7777] | True |

## Interpretation boundary

Classifier recognition, stability of a particular observable behavior, and a context-independent model trait are distinct claims.
This exploratory layer is intended to help separate them, not collapse them.
