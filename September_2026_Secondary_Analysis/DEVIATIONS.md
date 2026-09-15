# September 2026 deviations log

No deviations recorded at implementation start.

Add dated entries here if the locked secondary-analysis plan or harmonized coding specification must be changed. Parser revisions triggered by the validation gate must record the before/after validation score and rationale.

## 2026-09-15 — S2 boolean-dtype runtime compatibility correction

- Frozen S1-S5 implementation boundary: `af645e834d05a5116a04c8ffa924b2532482bf5d`.
- The first real S1-S5 invocation aborted during S2 before the first full-surface classifier fit completed. `scikit-learn==1.9.1` raised `ValueError: SimpleImputer does not support data with dtype bool` for the locked binary surface indicators `preamble_present` and `title_present`.
- The failure report exposed no S1-S5 outcome values. The correction below was specified solely from the traceback and the frozen implementation.
- Correction: immediately before S2 fitting/prediction, cast the two locked binary surface indicators from Boolean values to numeric `0.0` / `1.0`. Their substantive values are unchanged.
- No feature definition, sample, split, target, imputation rule, scaling rule, classifier, hyperparameter, random seed, bootstrap rule, effect-size definition, or interpretation rule is changed.
- This is an implementation/runtime compatibility correction rather than a scientific-plan deviation.
- The aborted run may have written incomplete S1 files before the S2 exception. Those partial outputs are not treated as results; the `results/secondary_analysis/` directory is cleared and the complete S1-S5 suite is rerun from scratch after this correction is frozen.