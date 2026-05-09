# Deviations from Preregistration

This file logs any departure from the locked design, coding heuristic,
or analysis plan during the run or analysis phase. Each entry includes
a date and a reason.

If this file is empty, no deviations have occurred.

---

## 2026-05-08 — Validation sample size scaled to 200

**Type:** Deviation from `coding_heuristic.md` §"Manual validation step"

**What was specified:** "a 50-poem random sample is hand-validated"
with stratification ≥5 per model and ≥5 per length cap.

**What was done instead:** A 200-poem stratified sample was drawn
(seed=42) and fully tagged. Stratification was proportional across
all (model × length_cap × phrasing) cells, which subsumes the
preregistered minimums.

**Reason:** Larger sample tightens the agreement-rate confidence
interval and reduces the chance that a feature passes or fails the
85% threshold by chance. The threshold itself is unchanged.

**Effect on conclusions:** Strengthens the validation step;
agreement rates are estimated more precisely. No effect on which
features pass.

**Status:** Implemented. Reported in final write-up.

---

## 2026-05-08 — Validation agreement scoring uses partial credit

**Type:** Clarification + deviation. The locked document specified
the tag levels (yes/mostly/no for `pos_ok`; yes/partial/no for
`rhyme_ok`) but did not specify how non-binary tags map to a 0–1
agreement rate.

**What was specified:** `coding_heuristic.md` §"Manual validation
step" lists the tag levels and locks an 85% agreement threshold, but
does not define the mapping from {yes, mostly/partial, no} to a
numeric agreement score.

**What was done instead:** `analysis/validate.py` (`score_results`)
implements partial credit: yes = 1.0, mostly/partial = 0.5, no = 0.0.
Under this scoring, `pos_ok` and `rhyme_ok` both rate 0.860, just
above the 0.85 threshold.

**Reason:** Some tagger output is genuinely partially correct
(spaCy POS on enjambed lines; near-rhymes that the CMU dict misses).
Treating "mostly" and "partial" as full disagreement throws away
information; treating them as full agreement overstates accuracy.
0.5 is the standard split.

**Effect on conclusions:** The two POS-validated and rhyme-validated
features both pass the threshold under partial-credit scoring. Under
strict yes-only scoring they would fail (`pos_ok` 0.78, `rhyme_ok`
0.775) and be downgraded to exploratory. A sensitivity re-run of the
primary analyses excluding these features is reported in the final
write-up; if conclusions change, this is disclosed.

**Status:** Implemented. Sensitivity rerun completed (see
`Claude_Analysis/deviations.md` 2026-05-09 entry "Sensitivity:
strict-yes-only validation scoring"). Conclusions unchanged under
the stricter scoring; the seven non-validation-gated features all
remain Bonferroni-significant with η² > 0.01.

---

## 2026-05-08 — Q4 compliance regression is degenerate

**Type:** Anticipated by preregistration §"What would change our minds"

**What was specified:** Q4 compliance regression with model,
length_cap, and phrasing as predictors, with a decision rule based on
p-values and odds ratios.

**What occurred:** Overall compliance is 0.998 (5,387 of 5,397). All
four GPT cells are at 1.000; the only sub-1.000 cells are Claude at
the 5-line cap (lowest is 0.980). The logistic regression fails to
converge cleanly and produces large coefficients (≈15–22) with
p-values ≈ 0.99 — a classic separation artifact, not a meaningful
result.

**Reason:** The variance in compliance across cells is too small
relative to within-cell binary noise for the regression to identify
stable effects.

**Effect on conclusions:** Q4 is reported as degenerate, exactly as
preregistered: "If compliance rates are uniformly near-perfect or
uniformly low across all cells, the compliance question loses its
variance and Q4 becomes degenerate; this is reported as such." The
per-cell compliance table is reported descriptively. The logistic
regression coefficients are not interpreted.

**Status:** Implemented. Reported in final write-up as a degenerate
Q4 per the preregistered fallback.

<!-- Template for entries:

## YYYY-MM-DD — Short description

**What was specified:** [from preregistration.md or coding_heuristic.md, with section reference]

**What was done instead:**

**Reason:**

**Effect on conclusions:**

-->
