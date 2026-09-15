# Pre-I&A-Result Code Audit — September 2026

**Audit point:** before loading real I&A outcomes.

## Scope

Audited `scripts/run_post_primary_ia.py` against `POST_PRIMARY_IA_PLAN.md` and the frozen P1/P3/P4 classifier implementation.

## Checks

- [x] I&A layer is explicitly labeled outcome-informed and exploratory.
- [x] Frozen harmonized row-count checks are enforced: BA1=540, BA2=5,398, total=5,938.
- [x] Model labels are fixed to the six locked identifiers.
- [x] IA1 uses the unchanged 180-record BA1 poetry test set.
- [x] IA1 uses exactly 360 BA2 training poems per resample and 60 per model.
- [x] IA1 balances the nine BA2 prompt cells as 6/7 records per cell, with exactly six 7-record cells per model.
- [x] IA1 samples without replacement.
- [x] IA1 runs 1,000 deterministic resamples in the delivered implementation.
- [x] IA1 retains raw per-resample accuracy, balanced accuracy, and per-model recall.
- [x] IA2 feature-family membership exactly matches the plan.
- [x] IA2 reruns only P1, P3, and P4 six-way model attribution; P2/P5 are excluded as specified.
- [x] IA2 uses the frozen classifier pipeline without feature selection or hyperparameter tuning.
- [x] IA2 full-body rerun must reproduce frozen P1/P3/P4 results or abort.
- [x] Convergence warnings fail closed rather than being silently accepted.
- [x] IA3 reports raw accuracy alongside (optional) chance-adjusted accuracy.
- [x] IA3 does not imply reciprocal or fully crossed comparability.
- [x] P5 opening entropy is surfaced only as a frozen reference example; it is not recomputed or reinterpreted as IA2 evidence.
- [x] Outputs are isolated under `results/post_primary_ia/`.
- [x] No S1-S5 output is used as an I&A analysis input.

## Synthetic dry-run requirement

Before freezing the implementation, perform an end-to-end synthetic run with the exact 5,938-row study structure. The dry run may reduce `IA1_RESAMPLES` in-memory for speed, but the delivered script must retain `IA1_RESAMPLES = 1000`.

The dry run must verify:

- IA1 sampling invariants;
- all five IA2 feature families;
- P1/P3/P4 grouped splits;
- full-body reproducibility gate;
- IA3 transfer-map construction;
- all expected output files;
- JSON serialization.

No real I&A outcome should be loaded before the implementation is frozen.

## Synthetic dry-run result

Passed before delivery.

- Synthetic structure: BA1=540, BA2=5,398, total=5,938.
- IA1 dry-run resamples: 20 (reduced in-memory only for runtime testing; delivered script remains 1,000).
- IA2 full-body frozen-result reproduction gate: passed.
- IA3 transfer-map rows produced: 51.
- Expected output artifacts produced: 10/10.
- No real I&A outcomes were loaded or inspected during the dry run.
