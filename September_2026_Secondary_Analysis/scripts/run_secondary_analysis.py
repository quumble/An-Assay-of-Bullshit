#!/usr/bin/env python3
"""Run the locked September 2026 secondary analyses S1-S5.

This script is downstream of the frozen P1-P5 results. It implements only the
secondary analyses prospectively specified in SECONDARY_ANALYSIS_PLAN.md. It
contains no post-primary Interpretability & Access diagnostics.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

BASE_SEED = 20260915
S1_BOOTSTRAP_N = 2000
S2_BOOTSTRAP_N = 10000
S5_SUBSTANTIAL_ETA2 = 0.06

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

SURFACE_CONTINUOUS = ["preamble_token_count", "title_token_count"]
SURFACE_BINARY = ["preamble_present", "title_present"]
FULL_SURFACE_FEATURES = BODY_FEATURES + SURFACE_CONTINUOUS + SURFACE_BINARY


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def finite_numeric_frame(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    x = df[cols].apply(pd.to_numeric, errors="coerce")
    arr = x.to_numpy(dtype=float)
    if np.isinf(arr).any():
        raise ValueError("Infinite values found in numeric feature columns")
    return x


def spearman_corr(a, b) -> float:
    a = pd.Series(np.asarray(a, dtype=float)).rank(method="average").to_numpy()
    b = pd.Series(np.asarray(b, dtype=float)).rank(method="average").to_numpy()
    if np.std(a) == 0 or np.std(b) == 0:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def percentile_ci(values, qs=(2.5, 97.5)):
    a = np.asarray([v for v in values if np.isfinite(v)], dtype=float)
    if len(a) == 0:
        return [None, None]
    return [float(x) for x in np.percentile(a, qs)]


def shannon_bits(tokens) -> float:
    vals = [str(t) for t in tokens if pd.notna(t) and str(t) != ""]
    if not vals:
        return float("nan")
    counts = np.asarray(list(Counter(vals).values()), dtype=float)
    p = counts / counts.sum()
    return float(-(p * np.log2(p)).sum())


def top_token_summary(tokens):
    vals = [str(t) for t in tokens if pd.notna(t) and str(t) != ""]
    if not vals:
        return {"top_token": "", "top_token_count": 0, "top_token_share": float("nan"), "n": 0}
    c = Counter(vals)
    top_token, n_top = sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[0]
    return {
        "top_token": top_token,
        "top_token_count": int(n_top),
        "top_token_share": float(n_top / len(vals)),
        "n": int(len(vals)),
    }


def validate_input(df: pd.DataFrame) -> dict:
    required = set(BODY_FEATURES + FULL_SURFACE_FEATURES + [
        "study", "provider", "model", "prompt_id", "genre", "phrasing",
        "length_cap", "first_lexical_token", "em_dash_count",
    ])
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
    ba1_cells = df[df.study == "BA1"].groupby(["model", "genre"]).size()
    expected_cells = {(m, g) for m in MODELS for g in ["story", "animal", "poem"]}
    if set(ba1_cells.index) != expected_cells or not (ba1_cells == 30).all():
        raise ValueError(f"Expected balanced BA1 model x genre cells of 30; got {ba1_cells.to_dict()}")
    finite_numeric_frame(df, BODY_FEATURES + SURFACE_CONTINUOUS)
    return counts


# ----------------------------- S1 -----------------------------------------

def model_feature_means(d: pd.DataFrame, feature: str) -> pd.Series:
    return d.groupby("model")[feature].mean().reindex(MODELS)


def standardize_six(s: pd.Series) -> pd.Series:
    vals = s.to_numpy(dtype=float)
    sd = vals.std(ddof=0)
    if sd == 0:
        return pd.Series(np.zeros(len(vals)), index=s.index)
    return pd.Series((vals - vals.mean()) / sd, index=s.index)


def resampled_model_means(d: pd.DataFrame, feature: str, rng: np.random.Generator) -> pd.Series:
    # Preserve model x prompt_id composition within a study.
    sums = {m: 0.0 for m in MODELS}
    ns = {m: 0 for m in MODELS}
    for (model, _prompt), g in d.groupby(["model", "prompt_id"], sort=True, dropna=False):
        arr = pd.to_numeric(g[feature], errors="coerce").to_numpy(dtype=float)
        arr = arr[np.isfinite(arr)]
        if len(arr) == 0:
            continue
        draw = rng.choice(arr, size=len(arr), replace=True)
        sums[model] += float(draw.sum())
        ns[model] += int(len(draw))
    return pd.Series([sums[m] / ns[m] if ns[m] else np.nan for m in MODELS], index=MODELS)


def s1_cross_study_feature_stability(df: pd.DataFrame, out_dir: Path) -> dict:
    ba1 = df[(df.study == "BA1") & (df.genre == "poem")].copy()
    ba2 = df[(df.study == "BA2") & (df.genre == "poem")].copy()
    rng = np.random.default_rng(BASE_SEED + 101)
    rows = []
    model_rows = []

    for feature in BODY_FEATURES:
        m1 = model_feature_means(ba1, feature)
        m2 = model_feature_means(ba2, feature)
        z1 = standardize_six(m1)
        z2 = standardize_six(m2)
        obs_rho = spearman_corr(z1, z2)
        obs_agree = np.sign(z1.to_numpy()) == np.sign(z2.to_numpy())

        boot_rho = []
        boot_agree = {m: [] for m in MODELS}
        for _ in range(S1_BOOTSTRAP_N):
            b1 = standardize_six(resampled_model_means(ba1, feature, rng))
            b2 = standardize_six(resampled_model_means(ba2, feature, rng))
            boot_rho.append(spearman_corr(b1, b2))
            agree = np.sign(b1.to_numpy()) == np.sign(b2.to_numpy())
            for model, val in zip(MODELS, agree):
                boot_agree[model].append(float(val))

        rows.append({
            "feature": feature,
            "spearman_rho": obs_rho,
            "spearman_bootstrap_95pct_low": percentile_ci(boot_rho)[0],
            "spearman_bootstrap_95pct_high": percentile_ci(boot_rho)[1],
            "direction_agreement_n": int(obs_agree.sum()),
            "direction_agreement_fraction": float(obs_agree.mean()),
            "bootstrap_resamples": S1_BOOTSTRAP_N,
            "bootstrap_seed": BASE_SEED + 101,
        })
        for i, model in enumerate(MODELS):
            model_rows.append({
                "feature": feature,
                "model": model,
                "ba1_poetry_mean": float(m1.loc[model]),
                "ba2_mean": float(m2.loc[model]),
                "ba1_within_study_z": float(z1.loc[model]),
                "ba2_within_study_z": float(z2.loc[model]),
                "observed_direction_agreement": bool(obs_agree[i]),
                "bootstrap_direction_agreement_probability": float(np.mean(boot_agree[model])),
            })

    summary = pd.DataFrame(rows)
    model_detail = pd.DataFrame(model_rows)
    summary.to_csv(out_dir / "S1_feature_stability.csv", index=False)
    model_detail.to_csv(out_dir / "S1_feature_stability_by_model.csv", index=False)
    return {
        "bootstrap_resamples": S1_BOOTSTRAP_N,
        "bootstrap_seed": BASE_SEED + 101,
        "features": summary.to_dict(orient="records"),
    }


# ----------------------------- S2 -----------------------------------------

def full_surface_classifier() -> Pipeline:
    continuous = BODY_FEATURES + SURFACE_CONTINUOUS
    binary = SURFACE_BINARY
    pre = ColumnTransformer([
        ("continuous", Pipeline([
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
        ]), continuous),
        ("binary", Pipeline([
            ("impute", SimpleImputer(strategy="most_frequent")),
        ]), binary),
    ], remainder="drop")
    return Pipeline([
        ("preprocess", pre),
        ("clf", LogisticRegression(max_iter=1000)),
    ])


def metric_bundle(y_true, y_pred, labels):
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


def write_cm(out_dir: Path, name: str, bundle: dict):
    cm = pd.DataFrame(bundle["confusion_matrix"], index=bundle["labels"], columns=bundle["labels"])
    cm.index.name = "true"
    cm.columns.name = "predicted"
    cm.to_csv(out_dir / f"{name}_confusion_matrix.csv")


def stratified_bootstrap_metrics(df_pred: pd.DataFrame, strata_cols, n_boot: int, seed: int):
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
        a = yt[idx]
        b = yp[idx]
        acc[i] = np.mean(a == b)
        bacc[i] = np.mean([np.mean(b[a == lab] == lab) for lab in labels])
    return {
        "n_resamples": n_boot,
        "seed": seed,
        "strata": list(strata_cols),
        "accuracy_95pct": percentile_ci(acc),
        "balanced_accuracy_95pct": percentile_ci(bacc),
    }


def full_fit_predict(train, test, target):
    train_x = train[FULL_SURFACE_FEATURES].copy()
    test_x = test[FULL_SURFACE_FEATURES].copy()

    # The harmonized parser stores the two locked surface indicators as bools.
    # scikit-learn 1.9.1 SimpleImputer does not accept dtype=bool, so encode the
    # same binary values numerically (False=0.0, True=1.0) before preprocessing.
    # This is representation-only: the binary features are still imputed with
    # most_frequent and are not standardized.
    for col in SURFACE_BINARY:
        train_x[col] = train_x[col].astype(float)
        test_x[col] = test_x[col].astype(float)

    pipe = full_surface_classifier()
    pipe.fit(train_x, train[target])
    return pipe.predict(test_x)


def s2_p1(df, out_dir):
    train = df[(df.study == "BA2") & (df.genre == "poem")].copy()
    test = df[(df.study == "BA1") & (df.genre == "poem")].copy()
    pred = full_fit_predict(train, test, "model")
    b = metric_bundle(test.model, pred, MODELS)
    p = test[["model", "prompt_id"]].copy()
    p["y_true"] = test.model.to_numpy(); p["y_pred"] = pred
    b["bootstrap"] = stratified_bootstrap_metrics(p, ["model", "prompt_id"], S2_BOOTSTRAP_N, BASE_SEED + 201)
    b["train_n"] = int(len(train)); b["test_n"] = int(len(test))
    write_cm(out_dir, "S2_P1_full_surface", b)
    return b


def s2_p2(df, out_dir):
    train = df[(df.study == "BA2") & (df.genre == "poem")].copy()
    test = df[(df.study == "BA1") & (df.genre == "poem")].copy()
    labels = sorted(df.provider.dropna().unique())
    pred = full_fit_predict(train, test, "provider")
    b = metric_bundle(test.provider, pred, labels)
    p = test[["model", "prompt_id"]].copy()
    p["y_true"] = test.provider.to_numpy(); p["y_pred"] = pred
    b["bootstrap"] = stratified_bootstrap_metrics(p, ["model", "prompt_id"], S2_BOOTSTRAP_N, BASE_SEED + 202)
    b["train_n"] = int(len(train)); b["test_n"] = int(len(test))
    write_cm(out_dir, "S2_P2_full_surface", b)
    return b


def s2_transfer_folds(d, column, groups, prefix, out_dir):
    folds = {}
    pooled = []
    for group in groups:
        train = d[d[column] != group]
        test = d[d[column] == group]
        pred = full_fit_predict(train, test, "model")
        b = metric_bundle(test.model, pred, MODELS)
        b["train_n"] = int(len(train)); b["test_n"] = int(len(test))
        folds[str(group)] = b
        write_cm(out_dir, f"{prefix}_holdout_{group}", b)
        t = pd.DataFrame({"y_true": test.model.to_numpy(), "y_pred": pred})
        pooled.append(t)
    pp = pd.concat(pooled, ignore_index=True)
    pooled_b = metric_bundle(pp.y_true, pp.y_pred, MODELS)
    write_cm(out_dir, f"{prefix}_pooled", pooled_b)
    return {"folds": folds, "pooled": pooled_b}


def s2_p3(df, out_dir):
    d = df[df.study == "BA1"].copy()
    return s2_transfer_folds(d, "genre", ["story", "animal", "poem"], "S2_P3_full_surface", out_dir)


def s2_p4(df, out_dir):
    d = df[(df.study == "BA2") & (df.genre == "poem")].copy()
    return {
        "phrasing": s2_transfer_folds(d, "phrasing", ["write", "compose", "gimme"], "S2_P4_phrasing_full_surface", out_dir),
        "length_cap": s2_transfer_folds(d, "length_cap", [5, 10, 20], "S2_P4_length_full_surface", out_dir),
    }


def metric_delta(full: dict, body: dict):
    return {
        "accuracy_delta_full_minus_body": float(full["accuracy"] - body["accuracy"]),
        "balanced_accuracy_delta_full_minus_body": float(full["balanced_accuracy"] - body["balanced_accuracy"]),
    }


def s2_surface_vs_body(df: pd.DataFrame, out_dir: Path, primary: dict) -> dict:
    p1 = s2_p1(df, out_dir)
    p2 = s2_p2(df, out_dir)
    p3 = s2_p3(df, out_dir)
    p4 = s2_p4(df, out_dir)
    deltas = {
        "P1": metric_delta(p1, primary["P1"]),
        "P2": metric_delta(p2, primary["P2"]),
        "P3": {
            "folds": {g: metric_delta(p3["folds"][g], primary["P3"]["folds"][g]) for g in p3["folds"]},
            "pooled": metric_delta(p3["pooled"], primary["P3"]["pooled"]),
        },
        "P4": {
            "phrasing": {
                "folds": {g: metric_delta(p4["phrasing"]["folds"][g], primary["P4"]["phrasing"]["folds"][g]) for g in p4["phrasing"]["folds"]},
                "pooled": metric_delta(p4["phrasing"]["pooled"], primary["P4"]["phrasing"]["pooled"]),
            },
            "length_cap": {
                "folds": {g: metric_delta(p4["length_cap"]["folds"][g], primary["P4"]["length_cap"]["folds"][g]) for g in p4["length_cap"]["folds"]},
                "pooled": metric_delta(p4["length_cap"]["pooled"], primary["P4"]["length_cap"]["pooled"]),
            },
        },
    }
    return {"full_surface_features": FULL_SURFACE_FEATURES, "P1": p1, "P2": p2, "P3": p3, "P4": p4, "deltas_vs_frozen_body_only": deltas}


# ----------------------------- S3 -----------------------------------------

def one_way_effect(x: np.ndarray, groups: np.ndarray) -> dict:
    x = np.asarray(x, dtype=float)
    groups = np.asarray(groups)
    mask = np.isfinite(x)
    x = x[mask]; groups = groups[mask]
    grand = float(np.mean(x))
    unique = list(dict.fromkeys(groups.tolist()))
    ss_between = 0.0
    ss_within = 0.0
    for g in unique:
        vals = x[groups == g]
        m = float(np.mean(vals))
        ss_between += len(vals) * (m - grand) ** 2
        ss_within += float(((vals - m) ** 2).sum())
    ss_total = ss_between + ss_within
    k = len(unique); n = len(x)
    eta2 = ss_between / ss_total if ss_total > 0 else 0.0
    df_between = k - 1; df_within = n - k
    ms_within = ss_within / df_within if df_within > 0 else 0.0
    omega2 = (ss_between - df_between * ms_within) / (ss_total + ms_within) if (ss_total + ms_within) > 0 else 0.0
    return {"eta_squared": float(eta2), "omega_squared": float(omega2)}


def hedges_g(a, b) -> float:
    a = np.asarray(a, dtype=float); b = np.asarray(b, dtype=float)
    a = a[np.isfinite(a)]; b = b[np.isfinite(b)]
    n1, n2 = len(a), len(b)
    if n1 < 2 or n2 < 2:
        return float("nan")
    s1 = a.std(ddof=1); s2 = b.std(ddof=1)
    df = n1 + n2 - 2
    pooled_var = ((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / df
    if pooled_var <= 0:
        return 0.0
    d = (a.mean() - b.mean()) / math.sqrt(pooled_var)
    j = 1 - 3 / (4 * df - 1)
    return float(j * d)


def s3_ba2_descriptive_effects(df: pd.DataFrame, out_dir: Path) -> dict:
    d = df[df.study == "BA2"].copy()
    model_rows = []
    effect_rows = []
    pair_rows = []
    for feature in BODY_FEATURES:
        vals = pd.to_numeric(d[feature], errors="coerce")
        eff = one_way_effect(vals.to_numpy(dtype=float), d.model.to_numpy())
        effect_rows.append({"feature": feature, **eff})
        for model in MODELS:
            x = pd.to_numeric(d.loc[d.model == model, feature], errors="coerce").to_numpy(dtype=float)
            x = x[np.isfinite(x)]
            model_rows.append({
                "feature": feature, "model": model, "n": int(len(x)),
                "mean": float(np.mean(x)), "sd": float(np.std(x, ddof=1)), "median": float(np.median(x)),
            })
        for a, b in combinations(MODELS, 2):
            xa = pd.to_numeric(d.loc[d.model == a, feature], errors="coerce").to_numpy(dtype=float)
            xb = pd.to_numeric(d.loc[d.model == b, feature], errors="coerce").to_numpy(dtype=float)
            pair_rows.append({
                "feature": feature, "model_a": a, "model_b": b,
                "hedges_g_a_minus_b": hedges_g(xa, xb),
            })
    desc = pd.DataFrame(model_rows)
    effects = pd.DataFrame(effect_rows)
    pairs = pd.DataFrame(pair_rows)
    desc.to_csv(out_dir / "S3_BA2_model_descriptives.csv", index=False)
    effects.to_csv(out_dir / "S3_BA2_global_model_effect_sizes.csv", index=False)
    pairs.to_csv(out_dir / "S3_BA2_pairwise_hedges_g.csv", index=False)
    return {"global_effect_sizes": effects.to_dict(orient="records")}


# ----------------------------- S4 -----------------------------------------

def scope_signature_rows(d: pd.DataFrame, scope: str) -> list[dict]:
    rows = []
    for model in MODELS:
        g = d[d.model == model].copy()
        top = top_token_summary(g.first_lexical_token)
        row = {
            "scope": scope, "model": model, "n": int(len(g)),
            "em_dash_mean_per_100_words": float(g.em_dash_per_100_words.mean()),
            "em_dash_prevalence": float((pd.to_numeric(g.em_dash_count, errors="coerce").fillna(0) > 0).mean()),
            "preamble_rate": float(pd.to_numeric(g.preamble_present, errors="coerce").mean()),
            "title_rate": float(pd.to_numeric(g.title_present, errors="coerce").mean()),
            "opening_entropy_bits": shannon_bits(g.first_lexical_token),
            "opening_top_token": top["top_token"],
            "opening_top_share": top["top_token_share"],
            "body_word_count_mean": float(g.body_word_count.mean()),
            "body_line_count_mean": float(g.body_line_count_nonempty.mean()),
            "body_stanza_count_mean": float(g.body_stanza_count.mean()),
            "words_per_line_mean_mean": float(g.words_per_line_mean.mean()),
            "words_per_line_sd_mean": float(g.words_per_line_sd.mean()),
            "pronoun_1s_share_mean": float(g.pronoun_1s_share.mean()),
            "pronoun_1p_share_mean": float(g.pronoun_1p_share.mean()),
            "pronoun_2_share_mean": float(g.pronoun_2_share.mean()),
            "pronoun_3_share_mean": float(g.pronoun_3_share.mean()),
        }
        rows.append(row)
    return rows


def s4_may_signatures(df: pd.DataFrame, out_dir: Path) -> dict:
    rows = []
    rows += scope_signature_rows(df[df.study == "BA1"], "BA1_all")
    rows += scope_signature_rows(df[(df.study == "BA1") & (df.genre == "poem")], "BA1_poetry")
    rows += scope_signature_rows(df[df.study == "BA2"], "BA2")
    tab = pd.DataFrame(rows)
    tab.to_csv(out_dir / "S4_harmonized_headline_signatures.csv", index=False)

    scalar_cols = [c for c in tab.columns if c not in {"scope", "model", "n", "opening_top_token"}]
    b1 = tab[tab.scope == "BA1_poetry"].set_index("model").reindex(MODELS)
    b2 = tab[tab.scope == "BA2"].set_index("model").reindex(MODELS)
    stability = []
    for col in scalar_cols:
        stability.append({
            "signature": col,
            "spearman_ba1_poetry_vs_ba2": spearman_corr(b1[col], b2[col]),
        })
    stab = pd.DataFrame(stability)
    stab.to_csv(out_dir / "S4_headline_signature_cross_study_stability.csv", index=False)
    return {"cross_study_stability": stab.to_dict(orient="records")}


# ----------------------------- S5 -----------------------------------------

def two_way_balanced_effects(d: pd.DataFrame, feature: str) -> dict:
    work = d[["model", "genre", feature]].copy()
    work[feature] = pd.to_numeric(work[feature], errors="coerce")
    if work[feature].isna().any():
        raise ValueError(f"S5 expects complete BA1 numeric feature {feature}")
    genres = ["story", "animal", "poem"]
    cell_counts = work.groupby(["model", "genre"]).size()
    if not (cell_counts == 30).all():
        raise ValueError(f"S5 requires 30 records per model x genre cell for {feature}")
    ncell = 30
    grand = float(work[feature].mean())
    model_means = work.groupby("model")[feature].mean().reindex(MODELS)
    genre_means = work.groupby("genre")[feature].mean().reindex(genres)
    cell_means = work.groupby(["model", "genre"])[feature].mean()

    ss_model = len(genres) * ncell * float(((model_means - grand) ** 2).sum())
    ss_genre = len(MODELS) * ncell * float(((genre_means - grand) ** 2).sum())
    ss_interaction = 0.0
    ss_error = 0.0
    for model in MODELS:
        for genre in genres:
            cm = float(cell_means.loc[(model, genre)])
            interaction = cm - float(model_means.loc[model]) - float(genre_means.loc[genre]) + grand
            ss_interaction += ncell * interaction**2
            vals = work.loc[(work.model == model) & (work.genre == genre), feature].to_numpy(dtype=float)
            ss_error += float(((vals - cm) ** 2).sum())
    ss_total = ss_model + ss_genre + ss_interaction + ss_error
    def eta(ss): return float(ss / ss_total) if ss_total > 0 else 0.0
    partial_int = float(ss_interaction / (ss_interaction + ss_error)) if (ss_interaction + ss_error) > 0 else 0.0
    return {
        "eta_squared_model": eta(ss_model),
        "eta_squared_genre": eta(ss_genre),
        "eta_squared_model_x_genre": eta(ss_interaction),
        "partial_eta_squared_model_x_genre": partial_int,
        "selected_substantial_model_separation": bool(eta(ss_model) >= S5_SUBSTANTIAL_ETA2),
    }


def s5_ba1_genre_interactions(df: pd.DataFrame, out_dir: Path) -> dict:
    d = df[df.study == "BA1"].copy()
    effect_rows = []
    for feature in BODY_FEATURES:
        effect_rows.append({"feature": feature, **two_way_balanced_effects(d, feature)})
    effects = pd.DataFrame(effect_rows)
    effects.to_csv(out_dir / "S5_BA1_model_genre_effect_sizes.csv", index=False)

    selected = effects.loc[effects.selected_substantial_model_separation, "feature"].tolist()
    cell_rows = []
    for feature in selected:
        means = d.groupby(["model", "genre"])[feature].mean()
        for model in MODELS:
            for genre in ["story", "animal", "poem"]:
                cell_rows.append({
                    "feature": feature, "model": model, "genre": genre,
                    "mean": float(means.loc[(model, genre)]),
                })
    cells = pd.DataFrame(cell_rows, columns=["feature", "model", "genre", "mean"])
    cells.to_csv(out_dir / "S5_BA1_selected_model_genre_cell_means.csv", index=False)
    return {
        "substantial_model_separation_eta2_threshold": S5_SUBSTANTIAL_ETA2,
        "selected_features": selected,
        "all_feature_effect_sizes": effects.to_dict(orient="records"),
    }


# ----------------------------- Main ---------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=Path("September_2026_Secondary_Analysis/derived_data/harmonized_features.jsonl"))
    ap.add_argument("--primary-results", type=Path, default=Path("September_2026_Secondary_Analysis/results/primary_analysis/primary_analysis_results.json"))
    ap.add_argument("--out-dir", type=Path, default=Path("September_2026_Secondary_Analysis/results/secondary_analysis"))
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_json(args.input, lines=True)
    counts = validate_input(df)
    primary = json.loads(args.primary_results.read_text(encoding="utf-8"))

    results = {
        "analysis": "September 2026 locked secondary S1-S5",
        "evidentiary_status": "S1-S5 specified in SECONDARY_ANALYSIS_PLAN.md before September harmonized outcomes; implementation details fixed after P1-P5 but before S1-S5 results",
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
    }

    results["S1"] = s1_cross_study_feature_stability(df, args.out_dir)
    results["S2"] = s2_surface_vs_body(df, args.out_dir, primary)
    results["S3"] = s3_ba2_descriptive_effects(df, args.out_dir)
    results["S4"] = s4_may_signatures(df, args.out_dir)
    results["S5"] = s5_ba1_genre_interactions(df, args.out_dir)

    out = args.out_dir / "secondary_analysis_results.json"
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
