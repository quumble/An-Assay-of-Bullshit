"""
Single entrypoint for the Bullshit Assay 2 analysis pipeline.

Usage (from the repo root, in PowerShell or any shell):

  python run_analysis.py features --input results.jsonl --output features.jsonl
  python run_analysis.py embed --input features.jsonl --output embeddings.jsonl
  python run_analysis.py validate --draw --input features.jsonl --output validation_sample.json --n 200 --seed 42
  python run_analysis.py validate --score --input validation_results.json --report-md validation_report.md --report-json validation_report.json
  python run_analysis.py analyze --features features.jsonl --embeddings embeddings.jsonl --report-md analysis_report.md --report-json analysis_results.json
  python run_analysis.py test
"""

from __future__ import annotations

import argparse
import json
import sys
import unittest
from pathlib import Path


def cmd_features(args) -> None:
    from analysis.features import extract_features, features_to_flat_dict

    in_path = Path(args.input)
    out_path = Path(args.output)
    if not in_path.exists():
        sys.exit(f"Input not found: {in_path}")

    out_path.parent.mkdir(parents=True, exist_ok=True)

    n_in = 0
    n_out = 0
    n_err = 0
    with in_path.open("r", encoding="utf-8") as f_in, \
         out_path.open("w", encoding="utf-8") as f_out:
        for line in f_in:
            line = line.strip()
            if not line:
                continue
            n_in += 1
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                n_err += 1
                continue
            if rec.get("error"):
                # Skip errored runs from the experiment
                continue
            try:
                feats = extract_features(rec)
                flat = features_to_flat_dict(feats)
                f_out.write(json.dumps(flat, ensure_ascii=False) + "\n")
                n_out += 1
            except Exception as e:
                print(f"Feature extraction failed for run_id "
                      f"{rec.get('run_id')}: {type(e).__name__}: {e}",
                      file=sys.stderr)
                n_err += 1
            if n_in % 100 == 0:
                print(f"  processed {n_in} records...", file=sys.stderr)

    print(f"Processed {n_in} input records.", file=sys.stderr)
    print(f"Wrote {n_out} feature records to {out_path.resolve()}.", file=sys.stderr)
    if n_err:
        print(f"{n_err} errors during processing.", file=sys.stderr)


def cmd_embed(args) -> None:
    from analysis.embed import run_embed
    run_embed(Path(args.input), Path(args.output))


def cmd_validate(args) -> None:
    if args.draw and args.score:
        sys.exit("Cannot pass both --draw and --score.")
    if not args.draw and not args.score:
        sys.exit("Must pass either --draw or --score.")

    if args.draw:
        from analysis.validate import draw_sample
        draw_sample(
            Path(args.input),
            Path(args.output),
            n=args.n,
            seed=args.seed,
        )
    else:
        from analysis.validate import score_results
        score_results(
            Path(args.input),
            out_md=Path(args.report_md),
            out_json=Path(args.report_json),
        )


def cmd_analyze(args) -> None:
    from analysis.analyze import run_analyze
    embeddings_path = Path(args.embeddings) if args.embeddings else None
    run_analyze(
        features_path=Path(args.features),
        embeddings_path=embeddings_path,
        report_md=Path(args.report_md),
        report_json=Path(args.report_json),
    )


def cmd_test(args) -> None:
    # Ensure the repo root is on sys.path so `analysis.tests.*` imports work
    # regardless of where Python is invoked from.
    repo_root = Path(__file__).resolve().parent
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    loader = unittest.TestLoader()
    # Load by module name explicitly. More robust than discover() across
    # Python versions (3.14 tightened discover()'s import rules).
    suite = loader.loadTestsFromName("analysis.tests.test_features")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    p_feat = sub.add_parser("features", help="Extract per-poem features from results.jsonl")
    p_feat.add_argument("--input", default="results.jsonl",
                        help="Input JSONL from run_experiment.py (default: results.jsonl)")
    p_feat.add_argument("--output", default="features.jsonl",
                        help="Output JSONL of features (default: features.jsonl)")
    p_feat.set_defaults(func=cmd_features)

    p_emb = sub.add_parser("embed", help="Compute poem embeddings via OpenAI")
    p_emb.add_argument("--input", default="features.jsonl",
                       help="Input features JSONL (default: features.jsonl)")
    p_emb.add_argument("--output", default="embeddings.jsonl",
                       help="Output embeddings JSONL (default: embeddings.jsonl)")
    p_emb.set_defaults(func=cmd_embed)

    p_val = sub.add_parser("validate", help="Draw validation sample or score results")
    p_val.add_argument("--draw", action="store_true",
                       help="Draw a stratified sample for validation.")
    p_val.add_argument("--score", action="store_true",
                       help="Score validation results against automated tags.")
    p_val.add_argument("--input", default="features.jsonl",
                       help="For --draw: features JSONL. For --score: validation_results.json.")
    p_val.add_argument("--output", default="validation_sample.json",
                       help="(--draw) Output sample JSON for the HTML tool.")
    p_val.add_argument("--n", type=int, default=200, help="(--draw) Number of poems to sample.")
    p_val.add_argument("--seed", type=int, default=42,
                       help="(--draw) Random seed for stratified sampling.")
    p_val.add_argument("--report-md", default="validation_report.md",
                       help="(--score) Markdown report path.")
    p_val.add_argument("--report-json", default="validation_report.json",
                       help="(--score) JSON report path.")
    p_val.set_defaults(func=cmd_validate)

    p_an = sub.add_parser("analyze", help="Run primary statistical analyses")
    p_an.add_argument("--features", default="features.jsonl")
    p_an.add_argument("--embeddings", default="embeddings.jsonl",
                      help="Embeddings JSONL. Pass empty string to skip Q1.")
    p_an.add_argument("--report-md", default="analysis_report.md")
    p_an.add_argument("--report-json", default="analysis_results.json")
    p_an.set_defaults(func=cmd_analyze)

    p_test = sub.add_parser("test", help="Run unit tests on feature extractors")
    p_test.set_defaults(func=cmd_test)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
