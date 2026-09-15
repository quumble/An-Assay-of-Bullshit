#!/usr/bin/env python3
"""Run bounded post-review diagnostics for the September 2026 manuscript.

D1: BA1-poetry target-local separability under the frozen 22-feature classifier.
D2: 400-token ceiling audit, with a conditional P4-length sensitivity only if
    direct BA2 cap termination is observed.

These diagnostics are outcome-informed exploratory follow-up. They do not alter
or overwrite any frozen May or September artifact.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import re
import sys
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import sklearn
from sklearn.exceptions import ConvergenceWarning
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

BASE_SEED = 20260915
D1_SEED = 20261215
D1_RESAMPLES = 1000

EXPECTED_HARMONIZED_SHA256 = "cd6dfbb320e219241923a8a71a3f8cc2fb50d86c15226d73fb9c90653845750f"
EXPECTED_PRIMARY_SHA256 = "95f549bc125d137972fa863386886775503f353ec8e5ff9e0097fb98e9e112bb"

MODELS = [
    "claude-haiku-4-5-20251001",
    "claude-sonnet-4-6",
    "claude-opus-4-7",
    "gpt-5.4-nano",
    "gpt-5.4-mini",
    "gpt-5.4",
]

BODY_FEATURES = [
    "body_word_count",
    "body_line_count_nonempty",
    "body_stanza_count",
    "words_per_line_mean",
    "words_per_line_sd",
    "mean_word_length",
    "pos_noun_ratio",
    "pos_verb_ratio",
    "pos_adj_ratio",
    "pos_adv_ratio",
    "pos_pronoun_ratio",
    "pronoun_1s_share",
    "pronoun_1p_share",
    "pronoun_2_share",
    "pronoun_3_share",
    "em_dash_per_100_words",
    "semicolon_per_100_words",
    "colon_per_100_words",
    "comma_per_100_words",
    "exclamation_per_100_words",
    "question_per_100_words",
    "ellipsis_per_100_words",
]

DEFAULT_HARMONIZED = Path("September_2026_Secondary_Analysis/derived_data/harmonized_features.jsonl")
DEFAULT_PRIMARY = Path("September_2026_Secondary_Analysis/results/primary_analysis/primary_analysis_results.json")
DEFAULT_BA1_RAW = Path("Bullshit_Assay_1/Results and Heuristics/results.jsonl")
DEFAULT_BA2_RAW = Path("Bullshit_Assay_2/Results and Analysis/results_final_raw_5400.jsonl")
DEFAULT_OUT = Path("September_2026_Secondary_Analysis/results/post_review_diagnostics")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"Malformed JSON at {path}:{lineno}") from exc
            rows.append(rec)
    return rows


def classifier() -> Pipeline:
    return Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
        ("clf", LogisticRegression()),
    ])


def fit_predict(train: pd.DataFrame, test: pd.DataFrame) -> np.ndarray:
    pipe = classifier()
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        pipe.fit(train[BODY_FEATURES], train["model"])
    return pipe.predict(test[BODY_FEATURES])


def metric_bundle(y_true, y_pred) -> dict[str, Any]:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    return {
        "n": int(len(y_true)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "per_model_recall": {
            model: float(val)
            for model, val in zip(
                MODELS,
                recall_score(y_true, y_pred, labels=MODELS, average=None, zero_division=0),
            )
        },
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=MODELS).astype(int).tolist(),
        "labels": MODELS,
    }


def q(values: np.ndarray | list[float], p: float) -> float:
    return float(np.percentile(np.asarray(values, dtype=float), p))


def summary_stats(values: np.ndarray | list[float]) -> dict[str, float]:
    arr = np.asarray(values, dtype=float)
    return {
        "mean": float(np.mean(arr)),
        "median": float(np.median(arr)),
        "pct_2_5": q(arr, 2.5),
        "pct_97_5": q(arr, 97.5),
    }


def integrity_checks(df: pd.DataFrame, harmonized_path: Path, primary_path: Path) -> None:
    hsha = sha256_file(harmonized_path)
    psha = sha256_file(primary_path)
    if hsha != EXPECTED_HARMONIZED_SHA256:
        raise RuntimeError(f"Harmonized SHA mismatch: {hsha}")
    if psha != EXPECTED_PRIMARY_SHA256:
        raise RuntimeError(f"Primary-results SHA mismatch: {psha}")

    counts = df["study"].value_counts().to_dict()
    if counts.get("BA1") != 540 or counts.get("BA2") != 5398:
        raise RuntimeError(f"Unexpected harmonized counts: {counts}")

    labels = sorted(df["model"].dropna().unique().tolist())
    if labels != sorted(MODELS):
        raise RuntimeError(f"Unexpected model labels: {labels}")

    missing_features = [c for c in BODY_FEATURES if c not in df.columns]
    if missing_features:
        raise RuntimeError(f"Missing frozen body features: {missing_features}")


def validate_d1_structure(poetry: pd.DataFrame) -> list[np.ndarray]:
    if len(poetry) != 180:
        raise RuntimeError(f"Expected 180 BA1 poetry rows, found {len(poetry)}")
    groups: list[np.ndarray] = []
    seen_models = sorted(poetry["model"].unique().tolist())
    if seen_models != sorted(MODELS):
        raise RuntimeError(f"Unexpected BA1 poetry models: {seen_models}")

    grouped = poetry.groupby(["model", "prompt_id"], sort=True, dropna=False)
    if len(grouped) != 18:
        raise RuntimeError(f"Expected 18 model x prompt cells, found {len(grouped)}")
    for key, g in grouped:
        if len(g) != 10:
            raise RuntimeError(f"D1 cell {key} has n={len(g)}, expected 10")
        groups.append(g.index.to_numpy())

    prompt_ids = sorted(poetry["prompt_id"].unique().tolist())
    if len(prompt_ids) != 3:
        raise RuntimeError(f"Expected 3 BA1 poetry prompt IDs, found {prompt_ids}")
    return groups


def run_d1(df: pd.DataFrame, out_dir: Path) -> dict[str, Any]:
    poetry = df[(df["study"] == "BA1") & (df["genre"] == "poem")].copy().reset_index(drop=True)
    groups = validate_d1_structure(poetry)
    rng = np.random.default_rng(D1_SEED)

    resample_rows: list[dict[str, Any]] = []
    recall_rows: list[dict[str, Any]] = []

    for r in range(D1_RESAMPLES):
        train_idx: list[int] = []
        test_idx: list[int] = []
        for g in groups:
            perm = rng.permutation(g)
            train_idx.extend(perm[:5].tolist())
            test_idx.extend(perm[5:].tolist())

        if set(train_idx) & set(test_idx):
            raise RuntimeError(f"D1 overlap detected in resample {r}")
        if len(train_idx) != 90 or len(test_idx) != 90:
            raise RuntimeError(f"D1 bad split sizes in resample {r}")

        train = poetry.loc[train_idx]
        test = poetry.loc[test_idx]
        pred = fit_predict(train, test)
        b = metric_bundle(test["model"], pred)
        resample_rows.append({
            "resample": r,
            "train_n": 90,
            "test_n": 90,
            "accuracy": b["accuracy"],
            "balanced_accuracy": b["balanced_accuracy"],
        })
        for model in MODELS:
            recall_rows.append({
                "resample": r,
                "model": model,
                "recall": b["per_model_recall"][model],
            })

    resamples = pd.DataFrame(resample_rows)
    recalls = pd.DataFrame(recall_rows)
    resamples.to_csv(out_dir / "D1_local_separability_resamples.csv", index=False)
    recalls.to_csv(out_dir / "D1_local_separability_model_recalls.csv", index=False)

    model_summary: dict[str, Any] = {}
    for model in MODELS:
        vals = recalls.loc[recalls.model == model, "recall"].to_numpy(dtype=float)
        model_summary[model] = summary_stats(vals)

    result = {
        "status": "outcome-informed exploratory",
        "question": "BA1 poetry target-local six-way separability",
        "seed": D1_SEED,
        "n_resamples": D1_RESAMPLES,
        "split_rule": "within each model x prompt cell, 5 train / 5 test without replacement",
        "train_n_per_resample": 90,
        "test_n_per_resample": 90,
        "chance_reference": 1.0 / 6.0,
        "accuracy": summary_stats(resamples["accuracy"].to_numpy()),
        "balanced_accuracy": summary_stats(resamples["balanced_accuracy"].to_numpy()),
        "per_model_recall": model_summary,
    }
    (out_dir / "D1_local_separability_summary.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    return result


def infer_length_cap(prompt_id: str, prompt_text: str) -> int | None:
    pid = (prompt_id or "").lower()
    text = (prompt_text or "").lower()
    m = re.search(r"(?:_|-)(5|10|20)$", pid)
    if m:
        return int(m.group(1))
    for cap in (5, 10, 20):
        if f"fewer than {cap}" in text or f"fewer then {cap}" in text or f"less than {cap}" in text:
            return cap
    return None


def successful_nonempty(rec: dict[str, Any]) -> bool:
    if rec.get("error"):
        return False
    response = rec.get("response")
    return response is not None and bool(str(response).strip())


def token_audit_rows(path: Path, study: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            if not line.strip():
                continue
            rec = json.loads(line)
            if not successful_nonempty(rec):
                continue

            raw = rec.get("raw_response") if isinstance(rec.get("raw_response"), dict) else {}
            provider = str(rec.get("provider") or "").lower()
            stop_reason = raw.get("stop_reason")
            status = raw.get("status")
            output_tokens = rec.get("output_tokens")
            max_tokens = rec.get("max_tokens")
            if max_tokens is None:
                max_tokens = rec.get("max_output_tokens")

            try:
                ot = float(output_tokens) if output_tokens is not None else math.nan
            except (TypeError, ValueError):
                ot = math.nan
            try:
                mt = float(max_tokens) if max_tokens is not None else math.nan
            except (TypeError, ValueError):
                mt = math.nan

            fraction = ot / mt if math.isfinite(ot) and math.isfinite(mt) and mt > 0 else math.nan
            direct = (provider == "anthropic" and stop_reason == "max_tokens") or (
                provider == "openai" and status == "incomplete"
            )
            at_cap = bool(math.isfinite(fraction) and fraction >= 1.0)
            near95 = bool(math.isfinite(fraction) and fraction >= 0.95)

            prompt_id = str(rec.get("prompt_id") or "")
            prompt_text = str(rec.get("prompt_text") or "")
            rows.append({
                "study": study,
                "source_line": lineno,
                "source_run_id": rec.get("run_id") or rec.get("output_id") or rec.get("id"),
                "provider": provider,
                "model": rec.get("model"),
                "prompt_id": prompt_id,
                "prompt_text": prompt_text,
                "length_cap": infer_length_cap(prompt_id, prompt_text),
                "iteration": rec.get("iteration"),
                "output_tokens": None if not math.isfinite(ot) else ot,
                "max_tokens": None if not math.isfinite(mt) else mt,
                "output_token_fraction": None if not math.isfinite(fraction) else fraction,
                "raw_stop_reason": stop_reason,
                "raw_status": status,
                "direct_cap_flag": bool(direct),
                "at_or_above_cap": bool(at_cap),
                "near_cap_95": bool(near95),
            })
    return rows


def grouped_token_summary(df: pd.DataFrame, by: list[str]) -> pd.DataFrame:
    def summarize(g: pd.DataFrame) -> pd.Series:
        tok = pd.to_numeric(g["output_tokens"], errors="coerce").dropna()
        return pd.Series({
            "n": len(g),
            "direct_cap_n": int(g["direct_cap_flag"].sum()),
            "direct_cap_fraction": float(g["direct_cap_flag"].mean()) if len(g) else math.nan,
            "at_or_above_cap_n": int(g["at_or_above_cap"].sum()),
            "at_or_above_cap_fraction": float(g["at_or_above_cap"].mean()) if len(g) else math.nan,
            "near_cap_95_n": int(g["near_cap_95"].sum()),
            "near_cap_95_fraction": float(g["near_cap_95"].mean()) if len(g) else math.nan,
            "output_tokens_median": float(tok.median()) if len(tok) else math.nan,
            "output_tokens_p95": float(tok.quantile(0.95)) if len(tok) else math.nan,
            "output_tokens_max": float(tok.max()) if len(tok) else math.nan,
        })

    return df.groupby(by, sort=True, dropna=False).apply(summarize, include_groups=False).reset_index()


def transfer_family_length(d: pd.DataFrame) -> dict[str, Any]:
    folds: dict[str, Any] = {}
    pooled_true: list[str] = []
    pooled_pred: list[str] = []
    for cap in (5, 10, 20):
        train = d[d["length_cap"] != cap]
        test = d[d["length_cap"] == cap]
        if train.empty or test.empty:
            raise RuntimeError(f"Conditional D2 sensitivity missing length-cap fold {cap}")
        if sorted(train["model"].unique().tolist()) != sorted(MODELS):
            raise RuntimeError(f"Conditional D2 train fold {cap} missing model labels")
        if sorted(test["model"].unique().tolist()) != sorted(MODELS):
            raise RuntimeError(f"Conditional D2 test fold {cap} missing model labels")
        pred = fit_predict(train, test)
        b = metric_bundle(test["model"], pred)
        b["train_n"] = int(len(train))
        b["test_n"] = int(len(test))
        folds[str(cap)] = b
        pooled_true.extend(test["model"].tolist())
        pooled_pred.extend(pred.tolist())
    return {"folds": folds, "pooled": metric_bundle(pooled_true, pooled_pred)}


def run_d2(
    df_harmonized: pd.DataFrame,
    ba1_raw: Path,
    ba2_raw: Path,
    primary_results: dict[str, Any],
    out_dir: Path,
) -> dict[str, Any]:
    rows = token_audit_rows(ba1_raw, "BA1") + token_audit_rows(ba2_raw, "BA2")
    audit = pd.DataFrame(rows)
    audit.to_csv(out_dir / "D2_token_cap_records.csv", index=False)

    by_study = grouped_token_summary(audit, ["study"])
    by_study.to_csv(out_dir / "D2_token_cap_by_study.csv", index=False)

    ba2 = audit[audit["study"] == "BA2"].copy()
    by_length = grouped_token_summary(ba2, ["length_cap"])
    by_model_length = grouped_token_summary(ba2, ["model", "length_cap"])
    by_prompt = grouped_token_summary(ba2, ["prompt_id"])
    by_length.to_csv(out_dir / "D2_token_cap_by_ba2_length.csv", index=False)
    by_model_length.to_csv(out_dir / "D2_token_cap_by_ba2_model_length.csv", index=False)
    by_prompt.to_csv(out_dir / "D2_token_cap_by_ba2_prompt.csv", index=False)

    direct_ba2 = ba2[ba2["direct_cap_flag"]].copy()
    sensitivity: dict[str, Any] | None = None
    sensitivity_triggered = len(direct_ba2) > 0

    if sensitivity_triggered:
        flagged_ids = direct_ba2["source_run_id"].dropna().astype(str).tolist()
        if len(flagged_ids) != len(set(flagged_ids)):
            raise RuntimeError("Duplicate directly flagged BA2 run IDs in raw audit")

        hba2 = df_harmonized[df_harmonized["study"] == "BA2"].copy()
        present = hba2["source_run_id"].astype(str).isin(flagged_ids)
        matched_ids = set(hba2.loc[present, "source_run_id"].astype(str))
        missing = sorted(set(flagged_ids) - matched_ids)
        if missing:
            raise RuntimeError(f"Directly flagged BA2 run IDs missing from harmonized table: {missing[:10]}")

        filtered = hba2.loc[~present].copy()
        rerun = transfer_family_length(filtered)
        frozen = primary_results["P4"]["length_cap"]
        sensitivity = {
            "triggered": True,
            "exclusion_rule": "exclude BA2 direct_cap_flag rows only",
            "excluded_n": int(present.sum()),
            "excluded_run_ids": flagged_ids,
            "frozen_original": frozen,
            "sensitivity_rerun": rerun,
        }
        (out_dir / "D2_conditional_length_sensitivity.json").write_text(
            json.dumps(sensitivity, indent=2), encoding="utf-8"
        )

    result = {
        "status": "outcome-informed exploratory",
        "successful_nonempty_records_audited": {
            "BA1": int((audit.study == "BA1").sum()),
            "BA2": int((audit.study == "BA2").sum()),
        },
        "direct_cap_ba2_n": int(len(direct_ba2)),
        "sensitivity_triggered": bool(sensitivity_triggered),
        "by_study": by_study.to_dict(orient="records"),
        "ba2_by_length": by_length.to_dict(orient="records"),
        "conditional_sensitivity": sensitivity,
        "interpretation_note": (
            "direct_cap_flag uses provider termination/status metadata; token-count proximity flags are diagnostics "
            "and are not automatically interpreted as proof of visible-text truncation"
        ),
    }
    return result


def render_access_summary(d1: dict[str, Any], d2: dict[str, Any]) -> str:
    a = d1["accuracy"]
    lines = [
        "# Post-review diagnostic access summary",
        "",
        "**Status:** outcome-informed exploratory manuscript diagnostics.",
        "",
        "## D1 — BA1-poetry target-local separability",
        "",
        f"- Resamples: {d1['n_resamples']}",
        f"- Train/test per resample: {d1['train_n_per_resample']} / {d1['test_n_per_resample']}",
        f"- Accuracy median: {a['median']:.4f}",
        f"- Accuracy mean: {a['mean']:.4f}",
        f"- 95% resample interval: [{a['pct_2_5']:.4f}, {a['pct_97_5']:.4f}]",
        f"- Six-way chance reference: {d1['chance_reference']:.4f}",
        "",
        "## D2 — 400-token ceiling audit",
        "",
        f"- Successful/non-empty BA1 records audited: {d2['successful_nonempty_records_audited']['BA1']}",
        f"- Successful/non-empty BA2 records audited: {d2['successful_nonempty_records_audited']['BA2']}",
        f"- BA2 direct cap flags: {d2['direct_cap_ba2_n']}",
        f"- Conditional P4-length sensitivity triggered: {d2['sensitivity_triggered']}",
        "",
        "### BA2 by requested line cap",
        "",
        "| line cap | n | direct cap | near 95% cap | token median | token p95 | token max |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in d2["ba2_by_length"]:
        cap = row.get("length_cap")
        lines.append(
            f"| {cap} | {int(row['n'])} | {int(row['direct_cap_n'])} | {int(row['near_cap_95_n'])} | "
            f"{row['output_tokens_median']:.1f} | {row['output_tokens_p95']:.1f} | {row['output_tokens_max']:.1f} |"
        )
    lines += [
        "",
        "## Interpretation boundary",
        "",
        "D1 measures target-local separability, not transfer. D2 distinguishes direct provider termination evidence from token-count proximity. Neither diagnostic upgrades the evidentiary status of the September study.",
        "",
    ]
    return "\n".join(lines)


def self_test() -> None:
    rng = np.random.default_rng(123)
    rows: list[dict[str, Any]] = []
    prompt_ids = ["poem_lt5", "poem_lt10", "poem_open"]
    for mi, model in enumerate(MODELS):
        for pi, pid in enumerate(prompt_ids):
            for it in range(10):
                row = {
                    "study": "BA1",
                    "genre": "poem",
                    "model": model,
                    "prompt_id": pid,
                    "source_run_id": f"{mi}-{pi}-{it}",
                }
                for fi, feat in enumerate(BODY_FEATURES):
                    row[feat] = mi * 2.0 + pi * 0.1 + rng.normal(0, 0.05) + fi * 0.001
                rows.append(row)
    d = pd.DataFrame(rows)
    groups = validate_d1_structure(d)
    srng = np.random.default_rng(D1_SEED)
    tr: list[int] = []
    te: list[int] = []
    for g in groups:
        p = srng.permutation(g)
        tr.extend(p[:5].tolist()); te.extend(p[5:].tolist())
    assert len(tr) == len(te) == 90
    assert not (set(tr) & set(te))
    pred = fit_predict(d.loc[tr], d.loc[te])
    b = metric_bundle(d.loc[te, "model"], pred)
    assert b["n"] == 90

    assert infer_length_cap("poem_write_20", "write a poem in fewer than 20 lines.") == 20
    sample_a = {
        "provider": "anthropic", "response": "x", "error": None,
        "prompt_id": "poem_write_20", "prompt_text": "write a poem in fewer than 20 lines.",
        "output_tokens": 400, "max_tokens": 400,
        "raw_response": {"stop_reason": "max_tokens"},
    }
    sample_o = {
        "provider": "openai", "response": "x", "error": None,
        "prompt_id": "poem_write_20", "prompt_text": "write a poem in fewer than 20 lines.",
        "output_tokens": 390, "max_tokens": 400,
        "raw_response": {"status": "completed"},
    }
    for rec in (sample_a, sample_o):
        assert successful_nonempty(rec)
    frac_a = sample_a["output_tokens"] / sample_a["max_tokens"]
    frac_o = sample_o["output_tokens"] / sample_o["max_tokens"]
    assert frac_a >= 1.0 and frac_o >= 0.95
    assert sample_a["raw_response"]["stop_reason"] == "max_tokens"
    assert sample_o["raw_response"]["status"] != "incomplete"
    print("SELF-TEST PASS")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--harmonized", type=Path, default=None)
    ap.add_argument("--primary-results", type=Path, default=None)
    ap.add_argument("--ba1-raw", type=Path, default=None)
    ap.add_argument("--ba2-raw", type=Path, default=None)
    ap.add_argument("--out-dir", type=Path, default=None)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        self_test()
        return

    repo = args.repo_root.resolve()
    harmonized = (args.harmonized or repo / DEFAULT_HARMONIZED).resolve()
    primary_path = (args.primary_results or repo / DEFAULT_PRIMARY).resolve()
    ba1_raw = (args.ba1_raw or repo / DEFAULT_BA1_RAW).resolve()
    ba2_raw = (args.ba2_raw or repo / DEFAULT_BA2_RAW).resolve()
    out_dir = (args.out_dir or repo / DEFAULT_OUT).resolve()
    staging_dir = out_dir.with_name(out_dir.name + "_STAGING")

    for p in (harmonized, primary_path, ba1_raw, ba2_raw):
        if not p.exists():
            raise FileNotFoundError(p)

    # Fail closed before creating result files.
    df = pd.read_json(harmonized, lines=True)
    integrity_checks(df, harmonized, primary_path)
    primary_results = json.loads(primary_path.read_text(encoding="utf-8"))

    if out_dir.exists():
        raise RuntimeError(f"Final output directory already exists; refusing to overwrite: {out_dir}")
    if staging_dir.exists():
        raise RuntimeError(f"Staging directory already exists from an earlier attempt: {staging_dir}")
    staging_dir.parent.mkdir(parents=True, exist_ok=True)
    staging_dir.mkdir()

    d1 = run_d1(df, staging_dir)
    d2 = run_d2(df, ba1_raw, ba2_raw, primary_results, staging_dir)

    result = {
        "analysis": "September 2026 post-review manuscript diagnostics",
        "evidentiary_status": "outcome-informed exploratory",
        "base_seed": BASE_SEED,
        "source": {
            "harmonized_path": str(harmonized),
            "harmonized_sha256": sha256_file(harmonized),
            "primary_results_path": str(primary_path),
            "primary_results_sha256": sha256_file(primary_path),
            "ba1_raw_path": str(ba1_raw),
            "ba1_raw_sha256": sha256_file(ba1_raw),
            "ba2_raw_path": str(ba2_raw),
            "ba2_raw_sha256": sha256_file(ba2_raw),
        },
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__,
        },
        "D1": d1,
        "D2": d2,
    }
    (staging_dir / "post_review_diagnostics_results.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    (staging_dir / "POST_REVIEW_DIAGNOSTIC_ACCESS_SUMMARY.md").write_text(
        render_access_summary(d1, d2), encoding="utf-8"
    )

    staging_dir.rename(out_dir)
    print(f"Post-review diagnostics complete: {out_dir}")
    print("D1 and D2 remain outcome-informed exploratory diagnostics.")


if __name__ == "__main__":
    main()
