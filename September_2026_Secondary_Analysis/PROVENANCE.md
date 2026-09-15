# Provenance — September 2026 Secondary Analysis

## Frozen source anchor

The repository state immediately before creation of the September analysis layer is:

`2d122305dafab5c89f1fbfc9f567069fed0b8d8f`

That commit is the frozen source anchor for both May studies as they stood when the September project began.

## Study 1

Directory: `Bullshit_Assay_1/`

Interpretation for September work:

- exploratory discovery study;
- 540 successful creative-writing outputs;
- six models;
- three genres × three length conditions × ten repetitions;
- temperature 1.0;
- no system message;
- 400-token output cap.

The May raw data and original analysis artifacts remain unchanged.

Known historical issue relevant to the September pass:

- the Series 1 structural title heuristic could classify a conversational preamble followed by a blank line as both `has_meta_preamble` and `has_title_line`; therefore old title-rate summaries are not treated as ground truth in September.

The September harmonized parser must derive title/preamble/body fields anew from the raw responses.

## Study 2

Directory: `Bullshit_Assay_2/`

Interpretation for September work:

- prospectively preregistered poetry follow-up;
- 5,400 planned calls, 5,397 analyzable in the May record;
- six models;
- three prompt phrasings × three line caps × 100 repetitions;
- temperature 1.0;
- no system message;
- 400-token output cap.

The preregistration was committed before the run start recorded in `Results and Analysis/run_metadata.json`.

Known historical issues relevant to the September pass:

1. The original Series 2 analyzer silently omitted five preregistered POS-ratio features because the analyzer expected unprefixed feature names while the serializer wrote `pos_`-prefixed names. A May re-analysis corrected this.
2. Later May review identified a title/body preprocessing issue in which a conversational preamble could be stripped while a following markdown title remained in the poem body. The public v3-1 paper reports corrected Sonnet structural summaries and retracts some artifact-driven findings, but the committed May re-analysis tables do not fully embody that later correction.
3. The September project therefore re-derives all harmonized features from raw Study 2 responses rather than treating `features_final_5397.jsonl` or any May summary table as authoritative input.

## Public paper lineage

The two frozen public antecedents are treated as historical reports:

- *The Average Bullshittings of Machines* — Study 1;
- *Six Ways to Write a Synthetic Poem* — Study 2.

The September journal manuscript, if completed, is a new synthesis and secondary-analysis product. It is not a silent replacement for either preprint.

## Separation rule

No file under `Bullshit_Assay_1/` or `Bullshit_Assay_2/` should be modified for September analysis.

All new scripts, validation records, derived data, results, figures, and manuscript files belong under:

`September_2026_Secondary_Analysis/`

## Reproducibility rule

Any result appearing in the September manuscript must be traceable to:

1. a frozen raw source file under one of the May study directories;
2. a September script/version;
3. the harmonized coding specification;
4. a machine-readable derived/result artifact;
5. any applicable deviation record.

If the September plan changes after this lock, the change must be logged prospectively where feasible and never back-edited into the original lock without an explicit amendment trail.

## September reconciliation of the Study 2 record count

The May analysis artifacts report 5,397 analyzable Study 2 records. A September 2026 raw-to-feature reconciliation found that the frozen 5,400-row raw file contains 5,398 successful, non-empty responses and two API-error rows.

Exactly one successful raw response is absent from the May `features_final_5397.jsonl` artifact:

- run_id: `dc984875-02cd-458c-a90c-68e3f2043596`
- model: `gpt-5.4-mini`
- prompt_id: `poem_write_20`
- iteration: `35`

The 5,397 shared run IDs contain no meaningful disagreements in model, prompt ID, or iteration metadata, and the May feature artifact contains no duplicate run IDs.

Accordingly, the September harmonized analysis includes 5,398 Study 2 records, following the locked rule to derive inclusion from the frozen raw responses rather than inheriting the May derived-table omission. The historical May 5,397 count remains unchanged in the frozen May record.

Machine-readable reconciliation: `results/ba2_may_reconciliation.json`.
