#!/usr/bin/env python3
"""Run the September 2026 post-primary Interpretability & Access diagnostics.

These analyses are explicitly outcome-informed and exploratory. They are
specified in POST_PRIMARY_IA_PLAN.md and operate downstream of the frozen
harmonized dataset and frozen P1-P5 results. They do not modify P1-P5 or S1-S5.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
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
IA1_RESAMPLES = 1000
CHANCE_SIX_WAY = 1.0 / 6.0

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

FEATURE_FAMILIES = {
    "form_structure": [
        "body_word_count",
        "body_line_count_nonempty",
        "body_stanza_count",
        "words_per_line_mean",
        "words_per_line_sd",
        "mean_word_length",
    ],
    "grammar_person": [
        "pos_noun_ratio",
        "pos_verb_ratio",
        "pos_adj_ratio",
        "pos_adv_ratio",
        "pos_pronoun_ratio",
        "pronoun_1s_share",
        "pronoun_1p_share",
        "pronoun_2_share",
        "pronoun_3_share",
    ],
    "punctuation": [
        "em_dash_per_100_words",
        "semicolon_per_100_words",
        "colon_per_100_words",
        "comma_per_100_words",
        "exclamation_per_100_words",
        "question_per_100_words",
        "ellipsis_per_100_words",
    ],
}
FEATURE_FAMILIES["nonstructural_style"] = FEATURE_FAMILIES["grammar_person"] + FEATURE_FAMILIES["punctuation"]
FEATURE_FAMILIES["full_body"] = BODY_FEATURES.copy()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def percentile_ci(values) -> list[float]:
    lo, hi = np.percentile(np.asarray(values, dtype=float), [2.5, 97.5])
    return [float(lo), float(hi)]


def classifier() -> Pipeline:
    # Exact frozen P1/P3/P4 classifier specification.
    return Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
        ("clf", LogisticRegression()),
    ])


def fit_predict_features(train: pd.DataFrame, test: pd.DataFrame, features: list[str]):
    pipe = classifier()
    with warnings.catch_warnings():
        # Fail closed rather than silently accepting a non-converged exploratory fit.
        warnings.filterwarnings("error", category=ConvergenceWarning)
        pipe.fit(train[features], train["model"])
    pred = pipe.predict(test[features])
    return pred, pipe


def metric_bundle(y_true, y_pred, labels=MODELS) -> dict[str, Any]:
    yt = np.asarray(y_true)
    yp = np.asarray(y_pred)
    return {
        "n": int(len(yt)),
        "accuracy": float(accuracy_score(yt, yp)),
        "balanced_accuracy": float(balanced_accuracy_score(yt, yp)),
        "per_label_recall": {
            str(label): float(v)
            for label, v in zip(labels, recall_score(yt, yp, labels=labels, average=None, zero_division=0))
        },
        "confusion_matrix": confusion_matrix(yt, yp, labels=labels).astype(int).tolist(),
        "labels": list(labels),
    }


def validate_input(df: pd.DataFrame) -> dict[str, int]:
    required = set(BODY_FEATURES + ["study", "model", "prompt_id", "genre", "phrasing", "length_cap"])
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    unknown = sorted(set(df.model.dropna()) - set(MODELS))
    if unknown:
        raise ValueError(f"Unexpected model labels: {unknown}")
    counts = df.groupby("study").size().to_dict()
    if counts.get("BA1") != 540 or counts.get("BA2") != 5398 or len(df) != 5938:
        raise ValueError(f"Frozen-count check failed: {counts}, total={len(df)}")
    if len(df[(df.study == "BA1") & (df.genre == "poem")]) != 180:
        raise ValueError("Expected 180 BA1 poetry rows")
    for model in MODELS:
        n = len(df[(df.study == "BA1") & (df.genre == "poem") & (df.model == model)])
        if n != 30:
            raise ValueError(f"Expected 30 BA1 poems for {model}, found {n}")
    return {str(k): int(v) for k, v in counts.items()}


def _ia1_model_rng(resample_index: int, model_index: int):
    # Independent deterministic stream from base seed + analysis id + resample + model.
    ss = np.random.SeedSequence([BASE_SEED, 1, int(resample_index), int(model_index)])
    return np.random.default_rng(ss)


def draw_ia1_training_sample(ba2: pd.DataFrame, resample_index: int) -> pd.DataFrame:
    pieces = []
    for model_index, model in enumerate(MODELS):
        m = ba2[ba2.model == model]
        cells = sorted(m.prompt_id.astype(str).unique().tolist())
        if len(cells) != 9:
            raise ValueError(f"IA1 expected 9 BA2 prompt cells for {model}, found {len(cells)}")
        rng = _ia1_model_rng(resample_index, model_index)
        extra_cells = set(rng.choice(np.arange(9), size=6, replace=False).tolist())
        for j, cell in enumerate(cells):
            g = m[m.prompt_id.astype(str) == cell]
            take = 7 if j in extra_cells else 6
            if len(g) < take:
                raise ValueError(f"IA1 cell {model}/{cell} has only {len(g)} rows; need {take}")
            chosen = rng.choice(g.index.to_numpy(), size=take, replace=False)
            pieces.append(g.loc[chosen])
    sample = pd.concat(pieces, ignore_index=True)
    if len(sample) != 360:
        raise AssertionError(f"IA1 sample size is {len(sample)}, expected 360")
    model_counts = sample.groupby("model").size().reindex(MODELS)
    if not (model_counts == 60).all():
        raise AssertionError(f"IA1 model balance failed: {model_counts.to_dict()}")
    return sample


def ia1_size_matched(df: pd.DataFrame, primary: dict, out_dir: Path) -> dict:
    ba2 = df[(df.study == "BA2") & (df.genre == "poem")].copy()
    test = df[(df.study == "BA1") & (df.genre == "poem")].copy()
    rows = []
    recall_rows = []
    for i in range(IA1_RESAMPLES):
        train = draw_ia1_training_sample(ba2, i)
        pred, _ = fit_predict_features(train, test, BODY_FEATURES)
        b = metric_bundle(test.model, pred)
        rows.append({
            "resample_index": i,
            "train_n": 360,
            "test_n": 180,
            "accuracy": b["accuracy"],
            "balanced_accuracy": b["balanced_accuracy"],
        })
        for model in MODELS:
            recall_rows.append({
                "resample_index": i,
                "model": model,
                "recall": b["per_label_recall"][model],
            })

    res = pd.DataFrame(rows)
    recalls = pd.DataFrame(recall_rows)
    res.to_csv(out_dir / "IA1_size_matched_resamples.csv", index=False)
    recalls.to_csv(out_dir / "IA1_model_recall_resamples.csv", index=False)

    recall_summary = []
    for model in MODELS:
        vals = recalls.loc[recalls.model == model, "recall"].to_numpy(dtype=float)
        lo, hi = percentile_ci(vals)
        recall_summary.append({
            "model": model,
            "median_recall": float(np.median(vals)),
            "mean_recall": float(np.mean(vals)),
            "recall_95pct_low": lo,
            "recall_95pct_high": hi,
        })
    pd.DataFrame(recall_summary).to_csv(out_dir / "IA1_model_recall_summary.csv", index=False)

    a_lo, a_hi = percentile_ci(res.accuracy)
    b_lo, b_hi = percentile_ci(res.balanced_accuracy)
    p3_refs = {genre: float(primary["P3"]["folds"][genre]["accuracy"]) for genre in ["story", "animal", "poem"]}
    summary = {
        "n_resamples": IA1_RESAMPLES,
        "base_seed": BASE_SEED,
        "train_n_per_resample": 360,
        "test_n": 180,
        "sampling": "60/model; per model 6 from all nine BA2 prompt cells plus one extra from six cells selected by deterministic model-specific RNG; no replacement",
        "accuracy_median": float(np.median(res.accuracy)),
        "accuracy_mean": float(np.mean(res.accuracy)),
        "accuracy_95pct": [a_lo, a_hi],
        "balanced_accuracy_median": float(np.median(res.balanced_accuracy)),
        "balanced_accuracy_mean": float(np.mean(res.balanced_accuracy)),
        "balanced_accuracy_95pct": [b_lo, b_hi],
        "per_model_recall_summary": recall_summary,
        "frozen_full_training_P1_accuracy": float(primary["P1"]["accuracy"]),
        "frozen_P3_holdout_accuracy_references": p3_refs,
    }
    return summary


def run_p1_for_features(df: pd.DataFrame, features: list[str]) -> dict:
    train = df[(df.study == "BA2") & (df.genre == "poem")]
    test = df[(df.study == "BA1") & (df.genre == "poem")]
    pred, _ = fit_predict_features(train, test, features)
    b = metric_bundle(test.model, pred)
    b["train_n"] = int(len(train)); b["test_n"] = int(len(test))
    return b


def run_p3_for_features(df: pd.DataFrame, features: list[str]) -> dict:
    d = df[df.study == "BA1"]
    folds = {}
    pooled_true = []
    pooled_pred = []
    for genre in ["story", "animal", "poem"]:
        train = d[d.genre != genre]
        test = d[d.genre == genre]
        pred, _ = fit_predict_features(train, test, features)
        b = metric_bundle(test.model, pred)
        b["train_n"] = int(len(train)); b["test_n"] = int(len(test))
        folds[genre] = b
        pooled_true.extend(test.model.tolist())
        pooled_pred.extend(pred.tolist())
    return {"folds": folds, "pooled": metric_bundle(pooled_true, pooled_pred)}


def run_transfer_family_for_features(d: pd.DataFrame, column: str, groups, features: list[str]) -> dict:
    folds = {}
    pooled_true = []
    pooled_pred = []
    for group in groups:
        train = d[d[column] != group]
        test = d[d[column] == group]
        pred, _ = fit_predict_features(train, test, features)
        b = metric_bundle(test.model, pred)
        b["train_n"] = int(len(train)); b["test_n"] = int(len(test))
        folds[str(group)] = b
        pooled_true.extend(test.model.tolist())
        pooled_pred.extend(pred.tolist())
    return {"folds": folds, "pooled": metric_bundle(pooled_true, pooled_pred)}


def run_p4_for_features(df: pd.DataFrame, features: list[str]) -> dict:
    d = df[(df.study == "BA2") & (df.genre == "poem")]
    return {
        "phrasing": run_transfer_family_for_features(d, "phrasing", ["write", "compose", "gimme"], features),
        "length_cap": run_transfer_family_for_features(d, "length_cap", [5, 10, 20], features),
    }


def assert_metric_equal(name: str, observed: dict, frozen: dict) -> None:
    # Exact confusion equality plus tight floating equality for scalar metrics/recalls.
    if observed["confusion_matrix"] != frozen["confusion_matrix"]:
        raise RuntimeError(f"IA2 full-body reproducibility gate failed for {name}: confusion matrix mismatch")
    for key in ["accuracy", "balanced_accuracy"]:
        if not np.isclose(float(observed[key]), float(frozen[key]), rtol=0.0, atol=1e-15):
            raise RuntimeError(f"IA2 full-body reproducibility gate failed for {name}: {key} mismatch")
    for model in MODELS:
        if not np.isclose(
            float(observed["per_label_recall"][model]),
            float(frozen["per_label_recall"][model]),
            rtol=0.0,
            atol=1e-15,
        ):
            raise RuntimeError(f"IA2 full-body reproducibility gate failed for {name}: recall mismatch for {model}")


def verify_full_body_reproduction(result: dict, primary: dict) -> None:
    assert_metric_equal("P1", result["P1"], primary["P1"])
    for genre in ["story", "animal", "poem"]:
        assert_metric_equal(f"P3/{genre}", result["P3"]["folds"][genre], primary["P3"]["folds"][genre])
    assert_metric_equal("P3/pooled", result["P3"]["pooled"], primary["P3"]["pooled"])
    for family, key in [("phrasing", "phrasing"), ("length_cap", "length_cap")]:
        groups = ["write", "compose", "gimme"] if family == "phrasing" else ["5", "10", "20"]
        for group in groups:
            assert_metric_equal(
                f"P4/{family}/{group}",
                result["P4"][key]["folds"][group],
                primary["P4"][key]["folds"][group],
            )
        assert_metric_equal(f"P4/{family}/pooled", result["P4"][key]["pooled"], primary["P4"][key]["pooled"])


def _frozen_reference(primary: dict, analysis: str, family: str | None = None, holdout: str | None = None) -> dict:
    if analysis == "P1":
        return primary["P1"]
    if analysis == "P3":
        return primary["P3"]["pooled"] if holdout == "pooled" else primary["P3"]["folds"][holdout]
    if analysis == "P4":
        branch = primary["P4"][family]
        return branch["pooled"] if holdout == "pooled" else branch["folds"][holdout]
    raise KeyError((analysis, family, holdout))


def ia2_feature_families(df: pd.DataFrame, primary: dict, out_dir: Path) -> dict:
    results = {}
    summary_rows = []
    recall_rows = []
    confusion_store = {}

    for family_name, features in FEATURE_FAMILIES.items():
        fam = {
            "features": features,
            "P1": run_p1_for_features(df, features),
            "P3": run_p3_for_features(df, features),
            "P4": run_p4_for_features(df, features),
        }
        results[family_name] = fam
        if family_name == "full_body":
            verify_full_body_reproduction(fam, primary)

        conditions = [("P1", None, None, fam["P1"])]
        for genre in ["story", "animal", "poem"]:
            conditions.append(("P3", None, genre, fam["P3"]["folds"][genre]))
        conditions.append(("P3", None, "pooled", fam["P3"]["pooled"]))
        for transfer_family, groups in [("phrasing", ["write", "compose", "gimme"]), ("length_cap", ["5", "10", "20"])]:
            for group in groups:
                conditions.append(("P4", transfer_family, group, fam["P4"][transfer_family]["folds"][group]))
            conditions.append(("P4", transfer_family, "pooled", fam["P4"][transfer_family]["pooled"]))

        for analysis, transfer_family, holdout, b in conditions:
            ref = _frozen_reference(primary, analysis, transfer_family, holdout)
            key = "/".join(x for x in [analysis, transfer_family, holdout] if x is not None)
            summary_rows.append({
                "feature_family": family_name,
                "analysis": analysis,
                "transfer_family": transfer_family or "",
                "holdout": holdout or "",
                "train_n": int(b.get("train_n", ref.get("train_n", 0) or 0)),
                "test_n": int(b.get("test_n", b.get("n", 0))),
                "accuracy": b["accuracy"],
                "balanced_accuracy": b["balanced_accuracy"],
                "accuracy_delta_vs_frozen_full": float(b["accuracy"] - ref["accuracy"]),
                "balanced_accuracy_delta_vs_frozen_full": float(b["balanced_accuracy"] - ref["balanced_accuracy"]),
            })
            for model in MODELS:
                recall_rows.append({
                    "feature_family": family_name,
                    "analysis": analysis,
                    "transfer_family": transfer_family or "",
                    "holdout": holdout or "",
                    "model": model,
                    "recall": b["per_label_recall"][model],
                    "recall_delta_vs_frozen_full": float(b["per_label_recall"][model] - ref["per_label_recall"][model]),
                })
            confusion_store[f"{family_name}/{key}"] = {
                "labels": b["labels"],
                "confusion_matrix": b["confusion_matrix"],
            }

    summary = pd.DataFrame(summary_rows)
    recalls = pd.DataFrame(recall_rows)
    summary.to_csv(out_dir / "IA2_feature_family_summary.csv", index=False)
    recalls.to_csv(out_dir / "IA2_feature_family_model_recalls.csv", index=False)
    (out_dir / "IA2_confusion_matrices.json").write_text(
        json.dumps(confusion_store, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return {
        "feature_families": FEATURE_FAMILIES,
        "full_body_reproduction_gate_passed": True,
        "results": results,
    }


def chance_adjusted(accuracy: float) -> float:
    return float((accuracy - CHANCE_SIX_WAY) / (1.0 - CHANCE_SIX_WAY))


def _primary_map_rows(primary: dict) -> list[dict]:
    rows = []
    def add(analysis, transfer_family, holdout, train_env, test_env, b):
        rows.append({
            "source_layer": "frozen_primary",
            "analysis": analysis,
            "transfer_family": transfer_family,
            "holdout": holdout,
            "train_environment": train_env,
            "test_environment": test_env,
            "train_n": int(b.get("train_n", 0)),
            "test_n": int(b.get("test_n", b.get("n", 0))),
            "feature_family": "full_body",
            "accuracy": float(b["accuracy"]),
            "balanced_accuracy": float(b["balanced_accuracy"]),
            "chance_reference": CHANCE_SIX_WAY,
            "chance_adjusted_accuracy": chance_adjusted(float(b["accuracy"])),
            "accuracy_95pct_low": np.nan,
            "accuracy_95pct_high": np.nan,
        })
    add("P1", "cross_study", "BA1_poetry", "BA2_poetry", "BA1_poetry", primary["P1"])
    for genre in ["story", "animal", "poem"]:
        other = "+".join(g for g in ["story", "animal", "poem"] if g != genre)
        add("P3", "genre", genre, f"BA1_{other}", f"BA1_{genre}", primary["P3"]["folds"][genre])
    for group in ["write", "compose", "gimme"]:
        train_groups = "+".join(g for g in ["write", "compose", "gimme"] if g != group)
        add("P4", "phrasing", group, f"BA2_{train_groups}", f"BA2_{group}", primary["P4"]["phrasing"]["folds"][group])
    for group in ["5", "10", "20"]:
        train_groups = "+".join(g for g in ["5", "10", "20"] if g != group)
        add("P4", "length_cap", group, f"BA2_cap_{train_groups}", f"BA2_cap_{group}", primary["P4"]["length_cap"]["folds"][group])
    return rows


def _ia2_map_rows(ia2: dict) -> list[dict]:
    rows = []
    # Full-body is represented by frozen-primary rows in the transfer map; IA2 full rerun is QA only.
    for family_name, fam in ia2["results"].items():
        if family_name == "full_body":
            continue
        def add(analysis, transfer_family, holdout, train_env, test_env, b):
            rows.append({
                "source_layer": "IA2",
                "analysis": analysis,
                "transfer_family": transfer_family,
                "holdout": holdout,
                "train_environment": train_env,
                "test_environment": test_env,
                "train_n": int(b.get("train_n", 0)),
                "test_n": int(b.get("test_n", b.get("n", 0))),
                "feature_family": family_name,
                "accuracy": float(b["accuracy"]),
                "balanced_accuracy": float(b["balanced_accuracy"]),
                "chance_reference": CHANCE_SIX_WAY,
                "chance_adjusted_accuracy": chance_adjusted(float(b["accuracy"])),
                "accuracy_95pct_low": np.nan,
                "accuracy_95pct_high": np.nan,
            })
        add("P1", "cross_study", "BA1_poetry", "BA2_poetry", "BA1_poetry", fam["P1"])
        for genre in ["story", "animal", "poem"]:
            other = "+".join(g for g in ["story", "animal", "poem"] if g != genre)
            add("P3", "genre", genre, f"BA1_{other}", f"BA1_{genre}", fam["P3"]["folds"][genre])
        for group in ["write", "compose", "gimme"]:
            train_groups = "+".join(g for g in ["write", "compose", "gimme"] if g != group)
            add("P4", "phrasing", group, f"BA2_{train_groups}", f"BA2_{group}", fam["P4"]["phrasing"]["folds"][group])
        for group in ["5", "10", "20"]:
            train_groups = "+".join(g for g in ["5", "10", "20"] if g != group)
            add("P4", "length_cap", group, f"BA2_cap_{train_groups}", f"BA2_cap_{group}", fam["P4"]["length_cap"]["folds"][group])
    return rows


def ia3_transfer_map(primary: dict, ia1: dict, ia2: dict, out_dir: Path) -> dict:
    rows = _primary_map_rows(primary) + _ia2_map_rows(ia2)
    rows.append({
        "source_layer": "IA1_summary",
        "analysis": "IA1",
        "transfer_family": "cross_study_size_matched",
        "holdout": "BA1_poetry",
        "train_environment": "BA2_poetry_balanced_360",
        "test_environment": "BA1_poetry",
        "train_n": 360,
        "test_n": 180,
        "feature_family": "full_body",
        "accuracy": ia1["accuracy_median"],
        "balanced_accuracy": ia1["balanced_accuracy_median"],
        "chance_reference": CHANCE_SIX_WAY,
        "chance_adjusted_accuracy": chance_adjusted(ia1["accuracy_median"]),
        "accuracy_95pct_low": ia1["accuracy_95pct"][0],
        "accuracy_95pct_high": ia1["accuracy_95pct"][1],
    })
    tab = pd.DataFrame(rows)
    tab.to_csv(out_dir / "IA3_transfer_map.csv", index=False)
    return {"rows": rows, "note": "Descriptive, non-reciprocal transfer map; not a fully crossed invariance matrix."}


def write_opening_entropy_reference(primary: dict, out_dir: Path) -> list[dict]:
    rows = []
    for r in primary["P5"]["models"]:
        rows.append({
            "model": r["model"],
            "ba1_entropy_bits": r["ba1_entropy_bits"],
            "ba2_rarefaction_mean_entropy_bits": r["ba2_rarefaction_mean_entropy_bits"],
            "ba2_rarefaction_95pct_low": r["ba2_rarefaction_95pct_low"],
            "ba2_rarefaction_95pct_high": r["ba2_rarefaction_95pct_high"],
            "ba1_inside_ba2_95pct": r["ba1_inside_ba2_95pct"],
        })
    pd.DataFrame(rows).to_csv(out_dir / "IA_opening_entropy_reference.csv", index=False)
    return rows


def write_access_summary(primary: dict, ia1: dict, ia2: dict, opening_rows: list[dict], out_dir: Path) -> None:
    lines = [
        "# Post-primary I&A access summary",
        "",
        "**Status:** outcome-informed exploratory diagnostics.",
        "",
        "This file is generated mechanically from the I&A outputs. It reports values without upgrading their evidentiary status.",
        "",
        "## IA1 — matched-size cross-study transfer",
        "",
        f"- Resamples: {ia1['n_resamples']}",
        f"- Training size per resample: {ia1['train_n_per_resample']}",
        f"- Frozen BA1-poetry test size: {ia1['test_n']}",
        f"- Median accuracy: {ia1['accuracy_median']:.4f}",
        f"- 95% resample interval: [{ia1['accuracy_95pct'][0]:.4f}, {ia1['accuracy_95pct'][1]:.4f}]",
        f"- Frozen full-training P1 accuracy: {ia1['frozen_full_training_P1_accuracy']:.4f}",
        "- Frozen P3 holdout accuracies: " + ", ".join(f"{k}={v:.4f}" for k, v in ia1["frozen_P3_holdout_accuracy_references"].items()),
        "",
        "## IA2 — feature-family decomposition (headline pooled conditions)",
        "",
        "| Feature family | P1 cross-study | P3 pooled | P4 phrasing pooled | P4 length pooled |",
        "|---|---:|---:|---:|---:|",
    ]
    for fam_name in ["form_structure", "grammar_person", "punctuation", "nonstructural_style", "full_body"]:
        fam = ia2["results"][fam_name]
        lines.append(
            f"| {fam_name} | {fam['P1']['accuracy']:.4f} | {fam['P3']['pooled']['accuracy']:.4f} | "
            f"{fam['P4']['phrasing']['pooled']['accuracy']:.4f} | {fam['P4']['length_cap']['pooled']['accuracy']:.4f} |"
        )
    lines += [
        "",
        "## Model heterogeneity — frozen full-body references",
        "",
        "| Model | P1 recall | P3 pooled recall | P4 phrasing pooled recall | P4 length pooled recall |",
        "|---|---:|---:|---:|---:|",
    ]
    for model in MODELS:
        lines.append(
            f"| {model} | {primary['P1']['per_label_recall'][model]:.4f} | "
            f"{primary['P3']['pooled']['per_label_recall'][model]:.4f} | "
            f"{primary['P4']['phrasing']['pooled']['per_label_recall'][model]:.4f} | "
            f"{primary['P4']['length_cap']['pooled']['per_label_recall'][model]:.4f} |"
        )
    lines += [
        "",
        "## Concrete behavioral example — opening-token entropy",
        "",
        "| Model | BA1 entropy | BA2 rarefaction mean | BA2 95% interval | BA1 inside interval |",
        "|---|---:|---:|---:|:---:|",
    ]
    for r in opening_rows:
        lines.append(
            f"| {r['model']} | {r['ba1_entropy_bits']:.4f} | {r['ba2_rarefaction_mean_entropy_bits']:.4f} | "
            f"[{r['ba2_rarefaction_95pct_low']:.4f}, {r['ba2_rarefaction_95pct_high']:.4f}] | "
            f"{str(bool(r['ba1_inside_ba2_95pct']))} |"
        )
    lines += [
        "",
        "## Interpretation boundary",
        "",
        "Classifier recognition, stability of a particular observable behavior, and a context-independent model trait are distinct claims.",
        "This exploratory layer is intended to help separate them, not collapse them.",
        "",
    ]
    (out_dir / "IA_ACCESS_SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=Path("September_2026_Secondary_Analysis/derived_data/harmonized_features.jsonl"))
    ap.add_argument("--primary-results", type=Path, default=Path("September_2026_Secondary_Analysis/results/primary_analysis/primary_analysis_results.json"))
    ap.add_argument("--out-dir", type=Path, default=Path("September_2026_Secondary_Analysis/results/post_primary_ia"))
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_json(args.input, lines=True)
    counts = validate_input(df)
    primary = json.loads(args.primary_results.read_text(encoding="utf-8"))

    results = {
        "analysis": "September 2026 post-primary Interpretability & Access",
        "evidentiary_status": "outcome-informed exploratory follow-up specified in POST_PRIMARY_IA_PLAN.md after P1-P5 inspection",
        "base_seed": BASE_SEED,
        "source": {
            "harmonized_path": str(args.input),
            "harmonized_sha256": sha256_file(args.input),
            "primary_results_path": str(args.primary_results),
            "primary_results_sha256": sha256_file(args.primary_results),
            "counts": counts,
        },
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__,
        },
        "feature_families": FEATURE_FAMILIES,
    }

    results["IA1"] = ia1_size_matched(df, primary, args.out_dir)
    results["IA2"] = ia2_feature_families(df, primary, args.out_dir)
    results["IA3"] = ia3_transfer_map(primary, results["IA1"], results["IA2"], args.out_dir)
    opening_rows = write_opening_entropy_reference(primary, args.out_dir)
    results["opening_entropy_reference"] = opening_rows
    write_access_summary(primary, results["IA1"], results["IA2"], opening_rows, args.out_dir)

    out = args.out_dir / "post_primary_ia_results.json"
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
