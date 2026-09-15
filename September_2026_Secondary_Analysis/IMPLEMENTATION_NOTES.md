# September 2026 implementation notes

**Status:** Implementation of the already locked secondary-analysis plan and harmonized coding specification. This document does not add scientific hypotheses or inspect September outcomes.

## Fixed implementation choices made before outcome analysis

1. **Lexical tokenization.** Body word, per-line word, opening-token, and deterministic pronoun features use the English lexical regex defined in `scripts/harmonizer_core.py`: alphabetic tokens may contain internal apostrophes or hyphens. This choice is applied identically to both May datasets.
2. **POS tagger.** The September pipeline uses spaCy `en_core_web_trf`, consistent with the higher-accuracy model used in the May Study 2 feature extractor. The exact installed package versions are written to `results/environment_manifest.json` at execution time.
3. **Validation sample allocation.** The locked 15 responses per model per study are allocated as evenly as possible across that model's available prompt IDs. With nine prompt cells and 15 target responses, every cell receives at least one sampled response and six cells receive a second response; which six receive the extra response is determined deterministically from seed `20260915`, study, and model.
4. **Validation row order.** After sampling, the 180 rows are shuffled deterministically using seed `20260915`. Model and provider identity are omitted from the public review packet and local review HTML. A separate `validation_key_PRIVATE.csv` is generated for later provenance/rejoining.
5. **Primary-outcome gate.** `scripts/harmonize.py` refuses to run unless `validation/validation_scores.json` exists and records `overall_pass: true`. It derives features only; it does not fit the locked classifiers.
6. **No May artifact is modified.** All September files are written under `September_2026_Secondary_Analysis/`.

## Validation workflow

Run the synthetic unit tests first. Then generate the locked validation packet with `build_validation_packet.py`. Complete `validation_review.html` in a browser, export the judgments JSON, and score it using `score_validation.py`.

If any applicable validation field is below 0.90, do not run `harmonize.py`. Revise the parser only under the deviation procedure already specified in the locked plan.
