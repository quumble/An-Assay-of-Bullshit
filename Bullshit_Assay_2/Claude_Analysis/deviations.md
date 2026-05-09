# Claude_Analysis — Re-analysis deviations

This directory contains a re-analysis of Bullshit Assay 2 conducted
with Claude Opus 4.7 assistance. The original as-run analysis
artifacts under `../Results and Analysis/` are preserved unchanged.
Outputs in this directory supersede them where they differ.

This log records every change to the analyzer and resulting outputs.

---

## 2026-05-09 — Bug fix: 5 of 13 preregistered Q2/Q3 features were silently dropped

**Type:** Correction to the as-run analyzer. Not a deviation from
the preregistration — the fix brings the analyzer into compliance
with the preregistered feature list.

**What the preregistration specifies:** `preregistration.md` §"Coding
plan" and §"Q2 — feature comparison across models" name 13 primary
features, including five POS ratios: `noun_ratio`, `verb_ratio`,
`adj_ratio`, `adv_ratio`, `pronoun_ratio`.

**What the as-run analyzer did:** `analysis/analyze.py` looked up the
five POS features by their bare names (`noun_ratio`, etc.). The
feature serializer in `analysis/features.py` (line 587, the
`("pos_", pf.pos)` entry in the prefix table) writes the POS keys to
disk with a `pos_` prefix (`pos_noun_ratio`, etc.). The lookup
silently failed for all five POS features and they were reported as
"no data" in the original `Results and Analysis/analysis_report.md`
Q2 and Q3 tables. Q1 (embeddings) and Q4 (compliance) do not use
these features and were unaffected.

**What was changed:** `analysis/analyze.py` `PRIMARY_FEATURES` list
updated to use the on-disk names (`pos_noun_ratio`, etc.). Inline
comment added pointing at the serializer.

**Reason:** The five POS features were specified in the
preregistration and extracted correctly into `features.jsonl`. The
defect was purely a key-name mismatch in the analyzer.

**Effect on conclusions:** Q1 unchanged (verified: silhouettes,
permutation nulls, and p-values are byte-identical to the original
report). Q4 unchanged. Q2 and Q3 now report all 13 preregistered
features. Effect sizes for the 8 previously-present features are
byte-identical to the original report; only the table is enlarged.

The largest substantive change: `pos_pronoun_ratio` enters with
η² = 0.229, the largest effect in the study by ~6 points. The other
four POS features all clear Bonferroni significance and the η² > 0.01
threshold; ranks: `pos_noun_ratio` (0.114), `pos_adv_ratio` (0.089),
`pos_adj_ratio` (0.078), `pos_verb_ratio` (0.045). Q3 phrasing main
effects and model × phrasing interactions on the new features are
included in the corrected report.

**Status:** Implemented. Corrected outputs in this directory:
`analysis_report.md`, `analysis_results.json`. Original outputs at
`../Results and Analysis/` retained as the as-run record.

---

## 2026-05-09 — Numerical correctness: cosine distance matrix clamped to non-negative

**Type:** Implementation correction. Not a deviation from the
preregistration.

**What the preregistration specifies:** Q1 silhouette score over a
cosine-distance matrix on poem embeddings.

**What the as-run analyzer did:** `cosine_distance_matrix` in
`analysis/analyze.py` computed `1 - normed @ normed.T`. Floating-point
roundoff on the matrix diagonal (and a small number of near-duplicate
embedding pairs) produces values around -7e-16 — well below machine
epsilon, but non-zero. The original report apparently ran against an
sklearn version that did not reject these; current sklearn (≥1.6)
raises `ValueError: Negative values in data passed to
pairwise_distances`.

**What was changed:** Added `np.maximum(d, 0.0, out=d)` after the
distance computation. Identical to the standard cosine-distance
implementation.

**Reason:** Allows the analysis to run on current sklearn. The clamp
operates only on values within machine epsilon of zero; the
mathematical operation is equivalent.

**Effect on conclusions:** None measurable. Q1 silhouette scores,
permutation nulls, and p-values match the original report to all four
reported decimal places.

**Status:** Implemented in `analyze.py`.

---

## 2026-05-09 — Validation tags not joined back to model identity

**Type:** Limitation note, not a correction.

**Observation:** `validation_results.json` carries `run_id` and human
tags but does not include the corresponding model identifier (the
HTML tagging tool blinded models, correctly, but the export does not
re-attach them). As a result, `validation_report.md` reports overall
agreement rates per feature but cannot break disagreements down by
model.

A non-trivial fraction of the disagreement notes ("title included as
first line", n ≈ 20 of 25 noted items) suggest the title-as-first-line
behavior may be concentrated in particular models, which would
inflate `line_count`, `stanza_count`, and `total_words` for those
models specifically. Without the join, this can only be flagged.

**Status:** Not corrected in this re-analysis (the joinable record
was not regenerated). Flagged for future work: `validate.py` could be
extended to write a `validation_report_by_model.json` after rejoining
on `run_id` from `features.jsonl`. Mentioned in the final write-up as
a caveat on family-level Q1/Q2 interpretation.

---

## 2026-05-09 — Sensitivity: strict-yes-only validation scoring

**Type:** Sensitivity analysis tied to the partial-credit scoring
deviation logged in `../deviations.md` (2026-05-08).

**What was tested:** Under strict yes-only scoring (no partial
credit for "mostly" or "partial"), `pos_ok` rates 0.78 and `rhyme_ok`
rates 0.775, both below the 0.85 threshold. Under the locked
decision rule, this would downgrade the five POS ratio features
(gated by `pos_ok`) and `rhyme_participation_rate` (gated by
`rhyme_ok`) to exploratory, leaving 7 of 13 preregistered features
in the primary battery.

**What was done:** Re-ran Q1, Q2, Q3, Q4 with the reduced 7-feature
battery (`line_count`, `stanza_count`, `words_per_line_mean`,
`words_per_line_sd`, `total_words`, `mean_word_length`,
`concreteness_mean`).

**Result:** Every one of the 7 retained features remains
Bonferroni-significant (under the looser α=0.05/7=0.0071) and η² > 0.01.
The minimum F-statistic across the seven is 18.1
(`line_count`); the maximum is 218.9 (`words_per_line_sd`). Q1
silhouettes and permutation nulls are byte-identical to the main
analysis. Q3 phrasing main effect remains significant. Q4 remains
degenerate.

**Conclusion:** Q1, Q2, and Q3 conclusions hold under strict
validation scoring. The headline finding ("models differ on every
preregistered structural feature") survives the strictest
interpretation of the validation gate.

**Effect on conclusions:** Strengthens the writeup's claim of
robustness. The `pos_pronoun_ratio` finding (η² = 0.229, the
largest in the study) is gated on partial-credit `pos_ok` scoring
and should be reported with the validation caveat; the other large
effects (`words_per_line_sd`, `words_per_line_mean`,
`concreteness_mean`, `mean_word_length`) are all in the
non-gated 7-feature battery and unconditional.

**Status:** Implemented. Sensitivity outputs in
`Claude_Analysis/sensitivity_strict_validation/`:
`analysis_report.md`, `analysis_results.json`.

<!-- Template for future entries:

## YYYY-MM-DD — Short description

**Type:** Deviation / clarification / correction / limitation note

**What the preregistration specifies:**

**What the as-run analyzer did / What was observed:**

**What was changed:**

**Reason:**

**Effect on conclusions:**

**Status:**

-->