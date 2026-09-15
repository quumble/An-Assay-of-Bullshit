#!/usr/bin/env python3
"""Derive the September harmonized feature table from frozen raw May responses.

IMPORTANT: Run only after the parser-validation gate passes.
This script does not fit classifiers or compute cross-study outcome summaries.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import platform
import sys
from pathlib import Path
from typing import Any

from harmonizer_core import (
    basic_body_features,
    harmonized_metadata,
    load_spacy_model,
    opening_features,
    parse_surface,
    pos_features,
    pronoun_features,
    punctuation_features,
    surface_dict,
)

DEFAULT_BA1 = Path("Bullshit_Assay_1/Results and Heuristics/results.jsonl")
DEFAULT_BA2 = Path("Bullshit_Assay_2/Results and Analysis/results_final_raw_5400.jsonl")
DEFAULT_OUT = Path("September_2026_Secondary_Analysis/derived_data/harmonized_features.jsonl")
DEFAULT_AUDIT = Path("September_2026_Secondary_Analysis/results/input_audit.json")
DEFAULT_ENV = Path("September_2026_Secondary_Analysis/results/environment_manifest.json")
DEFAULT_VALIDATION_SCORE = Path("September_2026_Secondary_Analysis/validation/validation_scores.json")

SPACY_MODEL = "en_core_web_trf"


def require_validation_pass(path: Path) -> None:
    if not path.exists():
        raise RuntimeError(
            f"Validation score file not found: {path}\n"
            "Complete and score the locked parser validation before harmonizing."
        )
    score = json.loads(path.read_text(encoding="utf-8"))
    if not score.get("overall_pass"):
        raise RuntimeError(
            f"Parser validation gate has not passed: {path}\n"
            "Do not run the outcome pipeline until the gate passes."
        )


def iter_source(path: Path):
    with path.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                yield "malformed", lineno, None
                continue

            if rec.get("error"):
                yield "error", lineno, rec
                continue
            response = rec.get("response")
            if response is None or not str(response).strip():
                yield "empty", lineno, rec
                continue
            yield "include", lineno, rec


def excluded_descriptor(study: str, lineno: int, rec: dict[str, Any] | None, reason: str) -> dict[str, Any]:
    rec = rec or {}
    return {
        "study": study,
        "source_line": lineno,
        "reason": reason,
        "provider": rec.get("provider"),
        "model": rec.get("model"),
        "prompt_id": rec.get("prompt_id"),
        "iteration": rec.get("iteration"),
        "source_run_id": rec.get("run_id") or rec.get("output_id") or rec.get("id"),
        "error": rec.get("error"),
    }


def package_version(name: str):
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--ba1", type=Path, default=None)
    ap.add_argument("--ba2", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--audit", type=Path, default=None)
    ap.add_argument("--environment", type=Path, default=None)
    ap.add_argument("--validation-score", type=Path, default=None)
    args = ap.parse_args()

    repo = args.repo_root.resolve()
    ba1 = (args.ba1 or (repo / DEFAULT_BA1)).resolve()
    ba2 = (args.ba2 or (repo / DEFAULT_BA2)).resolve()
    out = (args.out or (repo / DEFAULT_OUT)).resolve()
    audit_path = (args.audit or (repo / DEFAULT_AUDIT)).resolve()
    env_path = (args.environment or (repo / DEFAULT_ENV)).resolve()
    validation_score = (args.validation_score or (repo / DEFAULT_VALIDATION_SCORE)).resolve()

    require_validation_pass(validation_score)
    nlp = load_spacy_model(SPACY_MODEL)

    out.parent.mkdir(parents=True, exist_ok=True)
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    env_path.parent.mkdir(parents=True, exist_ok=True)

    counts = {
        "BA1": {"raw_nonblank": 0, "included": 0, "error": 0, "empty": 0, "malformed": 0},
        "BA2": {"raw_nonblank": 0, "included": 0, "error": 0, "empty": 0, "malformed": 0},
    }
    excluded = []

    with out.open("w", encoding="utf-8") as fout:
        for study, path in (("BA1", ba1), ("BA2", ba2)):
            for status, lineno, rec in iter_source(path):
                counts[study]["raw_nonblank"] += 1
                if status != "include":
                    counts[study][status] += 1
                    excluded.append(excluded_descriptor(study, lineno, rec, status))
                    continue

                assert rec is not None
                parsed = parse_surface(rec.get("response"))
                body = parsed.creative_body
                basic = basic_body_features(body)

                row = {
                    **harmonized_metadata(rec, study),
                    **surface_dict(parsed),
                    **basic,
                    **pronoun_features(body),
                    **punctuation_features(body, basic["body_word_count"]),
                    **opening_features(body),
                    **pos_features(body, nlp),
                    "source_line": lineno,
                }
                fout.write(json.dumps(row, ensure_ascii=False) + "\n")
                counts[study]["included"] += 1

    audit = {
        "schema": "ba_sep2026_harmonized_input_audit_v1",
        "sources": {"BA1": str(ba1), "BA2": str(ba2)},
        "counts": counts,
        "excluded_records": excluded,
        "validation_score_file": str(validation_score),
    }
    audit_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")

    env = {
        "schema": "ba_sep2026_environment_v1",
        "python": sys.version,
        "platform": platform.platform(),
        "spacy_model": SPACY_MODEL,
        "packages": {
            "spacy": package_version("spacy"),
            "spacy-transformers": package_version("spacy-transformers"),
            "numpy": package_version("numpy"),
            "scikit-learn": package_version("scikit-learn"),
        },
        "tokenization_note": (
            "September body word/line/opening features use the fixed English lexical regex "
            "in scripts/harmonizer_core.py; POS ratios use en_core_web_trf."
        ),
    }
    env_path.write_text(json.dumps(env, indent=2), encoding="utf-8")

    print(f"Harmonized feature table: {out}")
    print(f"Input audit: {audit_path}")
    print(f"Environment manifest: {env_path}")
    print("No classifier or cross-study outcome analysis has been run by this script.")


if __name__ == "__main__":
    main()
