#!/usr/bin/env python3
"""Run locked September 2026 P1-P5 analyses on the frozen harmonized feature table."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

BASE_SEED = 20260915
BOOTSTRAP_N = 10_000
RAREFACTION_N = 10_000

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


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def classifier() -> Pipeline:
    return Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
        ("clf", LogisticRegression()),
    ])


def metric_bundle(y_true, y_pred, labels):
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    return {
        "n": int(len(y_true)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "per_label_recall": {
            str(label): float(val)
            for label, val in zip(labels, recall_score(y_true, y_pred, labels=labels, average=None, zero_division=0))
        },
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=labels).astype(int).tolist(),
        "labels": list(labels),
    }


def percentile_ci(values):
    lo, hi = np.percentile(np.asarray(values, dtype=float), [2.5, 97.5])
    return [float(lo), float(hi)]


def stratified_bootstrap_metrics(df_pred: pd.DataFrame, strata_cols, n_boot=BOOTSTRAP_N, seed=BASE_SEED):
    rng = np.random.default_rng(seed)
    work = df_pred.reset_index(drop=True)
    groups = [g.index.to_numpy() for _, g in work.groupby(strata_cols, sort=True, dropna=False)]
    yt = work["y_true"].to_numpy()
    yp = work["y_pred"].to_numpy()
    labels = np.unique(yt)
    acc = np.empty(n_boot, dtype=float)
    bacc = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        idx = np.concatenate([rng.choice(g, size=len(g), replace=True) for g in groups])
        a = yt[idx]; b = yp[idx]
        acc[i] = np.mean(a == b)
        recalls = [np.mean(b[a == label] == label) for label in labels]
        bacc[i] = np.mean(recalls)
    return {
        "n_resamples": n_boot,
        "seed": seed,
        "strata": list(strata_cols),
        "accuracy_95pct": percentile_ci(acc),
        "balanced_accuracy_95pct": percentile_ci(bacc),
    }


def fit_predict(train, test, target):
    pipe = classifier()
    pipe.fit(train[BODY_FEATURES], train[target])
    pred = pipe.predict(test[BODY_FEATURES])
    return pred, pipe


def write_cm(out_dir: Path, name: str, bundle: dict):
    cm = pd.DataFrame(bundle["confusion_matrix"], index=bundle["labels"], columns=bundle["labels"])
    cm.index.name = "true"
    cm.columns.name = "predicted"
    cm.to_csv(out_dir / f"{name}_confusion_matrix.csv")


def p1(df, out_dir):
    train = df[(df.study == "BA2") & (df.genre == "poem")].copy()
    test = df[(df.study == "BA1") & (df.genre == "poem")].copy()
    pred, _ = fit_predict(train, test, "model")
    b = metric_bundle(test.model, pred, MODELS)
    pred_df = test[["model", "prompt_id"]].copy()
    pred_df["y_true"] = test.model.to_numpy()
    pred_df["y_pred"] = pred
    b["bootstrap"] = stratified_bootstrap_metrics(pred_df, ["model", "prompt_id"], seed=BASE_SEED + 1)
    b["train_n"] = int(len(train))
    b["test_n"] = int(len(test))
    write_cm(out_dir, "P1_six_way_cross_study", b)
    return b


def p2(df, out_dir):
    train = df[(df.study == "BA2") & (df.genre == "poem")].copy()
    test = df[(df.study == "BA1") & (df.genre == "poem")].copy()
    labels = sorted(x for x in df.provider.dropna().unique())
    pred, _ = fit_predict(train, test, "provider")
    b = metric_bundle(test.provider, pred, labels)
    pred_df = test[["model", "prompt_id"]].copy()
    pred_df["y_true"] = test.provider.to_numpy()
    pred_df["y_pred"] = pred
    b["bootstrap"] = stratified_bootstrap_metrics(pred_df, ["model", "prompt_id"], seed=BASE_SEED + 2)
    b["train_n"] = int(len(train))
    b["test_n"] = int(len(test))
    write_cm(out_dir, "P2_provider_cross_study", b)
    return b


def p3(df, out_dir):
    d = df[df.study == "BA1"].copy()
    genres = ["story", "animal", "poem"]
    folds = {}
    pooled = []
    for genre in genres:
        train = d[d.genre != genre]
        test = d[d.genre == genre]
        pred, _ = fit_predict(train, test, "model")
        b = metric_bundle(test.model, pred, MODELS)
        b["train_n"] = int(len(train)); b["test_n"] = int(len(test))
        folds[genre] = b
        write_cm(out_dir, f"P3_holdout_{genre}", b)
        t = test[["model"]].copy(); t["y_true"] = test.model.to_numpy(); t["y_pred"] = pred
        pooled.append(t)
    pp = pd.concat(pooled, ignore_index=True)
    pooled_b = metric_bundle(pp.y_true, pp.y_pred, MODELS)
    write_cm(out_dir, "P3_pooled", pooled_b)
    return {"folds": folds, "pooled": pooled_b}


def transfer_family(d, column, groups, prefix, out_dir):
    folds = {}
    pooled = []
    for group in groups:
        train = d[d[column] != group]
        test = d[d[column] == group]
        pred, _ = fit_predict(train, test, "model")
        b = metric_bundle(test.model, pred, MODELS)
        b["train_n"] = int(len(train)); b["test_n"] = int(len(test))
        folds[str(group)] = b
        write_cm(out_dir, f"{prefix}_holdout_{group}", b)
        t = test[["model"]].copy(); t["y_true"] = test.model.to_numpy(); t["y_pred"] = pred
        pooled.append(t)
    pp = pd.concat(pooled, ignore_index=True)
    pooled_b = metric_bundle(pp.y_true, pp.y_pred, MODELS)
    write_cm(out_dir, f"{prefix}_pooled", pooled_b)
    return {"folds": folds, "pooled": pooled_b}


def p4(df, out_dir):
    d = df[(df.study == "BA2") & (df.genre == "poem")].copy()
    phrasing = transfer_family(d, "phrasing", ["write", "compose", "gimme"], "P4_phrasing", out_dir)
    length = transfer_family(d, "length_cap", [5, 10, 20], "P4_length", out_dir)
    return {"phrasing": phrasing, "length_cap": length}


def shannon_bits(tokens):
    n = len(tokens)
    if n == 0:
        return float("nan")
    c = Counter(tokens)
    return float(-sum((v/n) * math.log2(v/n) for v in c.values()))


def stable_model_seed(model: str) -> int:
    raw = hashlib.sha256(f"{BASE_SEED}:{model}".encode()).digest()[:8]
    return int.from_bytes(raw, "big") % (2**32 - 1)


def p5(df, out_dir):
    ba1 = df[(df.study == "BA1") & (df.genre == "poem")].copy()
    ba2 = df[(df.study == "BA2") & (df.genre == "poem")].copy()
    rows = []
    for model in MODELS:
        t1 = ba1.loc[ba1.model == model, "first_lexical_token"].fillna("").astype(str).tolist()
        t2 = ba2.loc[ba2.model == model, "first_lexical_token"].fillna("").astype(str).to_numpy()
        if any(not x for x in t1) or any(not x for x in t2):
            raise ValueError(f"P5 found missing/empty first lexical token for {model}")
        if len(t1) != 30:
            raise ValueError(f"P5 expected 30 BA1 poems for {model}, found {len(t1)}")
        if len(t2) < 30:
            raise ValueError(f"P5 requires at least 30 BA2 poems for {model}, found {len(t2)}")
        h1 = shannon_bits(t1)
        rng = np.random.default_rng(stable_model_seed(model))
        hs = np.empty(RAREFACTION_N, dtype=float)
        for i in range(RAREFACTION_N):
            sample = rng.choice(t2, size=30, replace=False)
            hs[i] = shannon_bits(sample.tolist())
        lo, hi = percentile_ci(hs)
        rows.append({
            "model": model,
            "ba1_n": len(t1),
            "ba1_entropy_bits": h1,
            "ba2_n": int(len(t2)),
            "ba2_rarefaction_n": 30,
            "ba2_rarefaction_resamples": RAREFACTION_N,
            "ba2_rarefaction_seed": stable_model_seed(model),
            "ba2_rarefaction_mean_entropy_bits": float(np.mean(hs)),
            "ba2_rarefaction_median_entropy_bits": float(np.median(hs)),
            "ba2_rarefaction_95pct_low": lo,
            "ba2_rarefaction_95pct_high": hi,
            "ba1_inside_ba2_95pct": bool(lo <= h1 <= hi),
        })
    tab = pd.DataFrame(rows)
    tab.to_csv(out_dir / "P5_opening_entropy.csv", index=False)
    rank1 = tab.sort_values("ba1_entropy_bits", ascending=False).model.tolist()
    rank2 = tab.sort_values("ba2_rarefaction_mean_entropy_bits", ascending=False).model.tolist()
    tab["provider"] = np.where(tab.model.str.startswith("claude"), "anthropic", "openai")
    provider_means = tab.groupby("provider")[["ba1_entropy_bits", "ba2_rarefaction_mean_entropy_bits"]].mean().to_dict(orient="index")
    gap = {
        "ba1_anthropic_minus_openai_bits": float(provider_means["anthropic"]["ba1_entropy_bits"] - provider_means["openai"]["ba1_entropy_bits"]),
        "ba2_rarefaction_mean_anthropic_minus_openai_bits": float(provider_means["anthropic"]["ba2_rarefaction_mean_entropy_bits"] - provider_means["openai"]["ba2_rarefaction_mean_entropy_bits"]),
    }
    return {
        "models": rows,
        "ba1_rank_high_to_low": rank1,
        "ba2_rarefaction_mean_rank_high_to_low": rank2,
        "provider_descriptive_means": provider_means,
        "provider_descriptive_gap": gap,
    }


def validate_input(df):
    required = set(BODY_FEATURES + ["study", "provider", "model", "prompt_id", "genre", "phrasing", "length_cap", "first_lexical_token"])
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    unknown_models = sorted(set(df.model.dropna()) - set(MODELS))
    if unknown_models:
        raise ValueError(f"Unexpected model labels: {unknown_models}")
    counts = df.groupby("study").size().to_dict()
    if counts.get("BA1") != 540 or counts.get("BA2") != 5398 or len(df) != 5938:
        raise ValueError(f"Frozen-count check failed: {counts}, total={len(df)}")
    if len(df[(df.study == "BA1") & (df.genre == "poem")]) != 180:
        raise ValueError("Expected 180 BA1 poetry rows for P1/P2/P5")
    return counts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=Path("September_2026_Secondary_Analysis/derived_data/harmonized_features.jsonl"))
    ap.add_argument("--out-dir", type=Path, default=Path("September_2026_Secondary_Analysis/results/primary_analysis"))
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_json(args.input, lines=True)
    counts = validate_input(df)

    results = {
        "analysis": "September 2026 locked primary P1-P5",
        "base_seed": BASE_SEED,
        "body_features": BODY_FEATURES,
        "source": {"path": str(args.input), "sha256": sha256_file(args.input), "counts": counts},
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__,
        },
    }
    results["P1"] = p1(df, args.out_dir)
    results["P2"] = p2(df, args.out_dir)
    results["P3"] = p3(df, args.out_dir)
    results["P4"] = p4(df, args.out_dir)
    results["P5"] = p5(df, args.out_dir)

    path = args.out_dir / "primary_analysis_results.json"
    path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(path)

if __name__ == "__main__":
    main()
