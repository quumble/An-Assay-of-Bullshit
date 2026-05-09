# An Assay of Bullshit

A series of exploratory studies comparing creative-writing defaults
across model families (Claude vs OpenAI) and tiers (small / medium /
full).

## Series

- **Series 1** (`Bullshit_Assay_1/`) — initial pass: 540 calls across
  6 models × 9 prompts (story / animal / poem × 3 length caps),
  10 iterations per cell. Exploratory; small per-cell n.
- **Series 2** (`Bullshit_Assay_2/`) — preregistered: 5,400 calls
  across 6 models × 9 prompts, narrowed to poetry, with 100
  iterations per cell. Includes a locked coding heuristic and a
  manual validation gate.
- A community re-analysis with Claude Opus 4.7 assistance lives in
  `Bullshit_Assay_2/Claude_Analysis/`. The original as-run analysis
  artifacts are preserved unchanged at
  `Bullshit_Assay_2/Results and Analysis/`.

## Methodological transparency

Series 2 is preregistered (`Bullshit_Assay_2/preregistration.md`)
with a locked coding heuristic
(`Bullshit_Assay_2/coding_heuristic.md`). All deviations are logged.

Deviation logs are layered:

- `deviations_md.md` (top-level, kept at this path for reference) —
  series 1 deviation log, written before the per-study directory
  convention was adopted.
- `Bullshit_Assay_2/deviations.md` — series 2 study-level deviations
  from the preregistration and coding heuristic.
- `Bullshit_Assay_2/Claude_Analysis/deviations.md` — re-analysis
  log, including a bug fix (5 of 13 preregistered Q2/Q3 features
  silently dropped from the original report).

[... existing series 1 content goes here unchanged ...]

## License

Code: Apache-2.0 (`LICENSE`). Documentation and analysis text:
CC-BY-4.0 (`LICENSE-CC-BY-4.0.txt`). Some derivative content may be
under CC-BY-NC-SA-4.0 (`LICENSE-CC-BY-NC-SA-4.0.txt`); see
individual files for specifics.
