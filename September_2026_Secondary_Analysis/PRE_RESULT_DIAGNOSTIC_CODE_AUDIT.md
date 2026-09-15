# Pre-Result Diagnostic Code Audit — September 2026

**Scope:** `run_post_review_diagnostics.py`  
**Status:** audited before any real D1/D2 diagnostic outcome is inspected

## Audit questions

### 1. Does D1 answer only the target-local separability question?

Yes.

- Input is restricted to frozen harmonized BA1 poetry rows.
- The script requires exactly 180 rows arranged as 18 model × prompt cells of n=10.
- Every resample splits each cell 5/5 without replacement.
- No row can occur in both train and test within a resample.
- The frozen 22 body features and exact primary classifier family are reused.
- Prompt conditions are intentionally represented in both train and test because D1 estimates within-target separability, not prompt-condition transfer.
- No feature selection or hyperparameter search is introduced.

### 2. Does D1 preserve evidentiary boundaries?

Yes.

The result bundle labels D1 outcome-informed exploratory. The script reports a separability distribution and does not relabel it as transfer, invariance, or a causal genre/category effect.

### 3. Does D2 distinguish direct termination evidence from token proximity?

Yes.

The code defines direct provider evidence narrowly:

- Anthropic `stop_reason == "max_tokens"`;
- OpenAI response `status == "incomplete"`.

`output_tokens >= max_tokens` and `output_tokens/max_tokens >= .95` are retained separately as proximity diagnostics and are not used as direct truncation evidence.

### 4. Is the conditional sensitivity outcome-independent once the plan is frozen?

Yes.

The branch is fixed in advance: rerun only P4 length-cap transfer if and only if at least one analyzed BA2 row has direct termination evidence. Near-cap counts alone do not trigger exclusions.

If triggered, the script removes only directly flagged BA2 rows and reruns the existing P4 length-cap transfer with the frozen body features and classifier.

### 5. Are frozen inputs protected?

Yes.

Production execution verifies:

- harmonized SHA-256 `cd6dfbb320e219241923a8a71a3f8cc2fb50d86c15226d73fb9c90653845750f`;
- primary-results SHA-256 `95f549bc125d137972fa863386886775503f353ec8e5ff9e0097fb98e9e112bb`;
- BA1/BA2 harmonized counts 540/5,398;
- exact six-model label set;
- presence of all 22 frozen body features.

Raw-source hashes are calculated and recorded in the result JSON.

### 6. Can a failed run be confused with completed diagnostics?

No under the normal workflow.

Real output is written to `post_review_diagnostics_STAGING`. The script refuses to overwrite an existing final or staging directory. Only after D1, D2, and all final result files complete successfully is the staging directory renamed to `post_review_diagnostics`.

### 7. Was the code tested without exposing real results?

Yes.

- `python -m py_compile run_post_review_diagnostics.py` passed.
- `python run_post_review_diagnostics.py --self-test` returned `SELF-TEST PASS`.
- The self-test uses synthetic in-memory data only.
- It checks balanced D1 split construction, no within-resample overlap, classifier execution, line-cap inference, and D2 direct/proximity flag logic.

The audit environment used Python with NumPy 2.3.5, pandas 2.2.3, and scikit-learn 1.8.0. This is a synthetic implementation test only; the real run will record the user's actual frozen-analysis environment, expected to be the existing September environment.

## Audit conclusion

The implementation matches the bounded post-review diagnostic plan and does not introduce an unplanned analysis family. It is suitable to freeze before the real D1/D2 run.
