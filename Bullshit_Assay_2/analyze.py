"""
Primary statistical analyses, locked in `preregistration.md`.

Implements:
- Q1: embedding clustering (silhouette + permutation null) at model, family, tier levels
- Q2: feature comparison across models (one-way ANOVA + effect sizes)
- Q3: phrasing × model 2-way ANOVA on each feature
- Q4: compliance regression

Reads:
- features.jsonl (output of `run_analysis.py features`)
- embeddings.jsonl (output of `run_analysis.py embed`)

Writes:
- analysis_report.md
- analysis_results.json
"""

from __future__ import annotations

import json
import math
import random
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Constants — locked in preregistration
# ---------------------------------------------------------------------------

PRIMARY_FEATURES = [
    "line_count",
    "stanza_count",
    "words_per_line_mean",
    "words_per_line_sd",
    "total_words",
    "mean_word_length",
    "noun_ratio",
    "verb_ratio",
    "adj_ratio",
    "adv_ratio",
    "pronoun_ratio",
    "concreteness_mean",
    "rhyme_participation_rate",
]

# Model → tier mapping. Tier collapses across families.
TIER_MAP = {
    "claude-haiku-4-5-20251001": "small",
    "claude-sonnet-4-6": "med",
    "claude-opus-4-7": "full",
    "gpt-5.4-nano": "small",
    "gpt-5.4-mini": "med",
    "gpt-5.4": "full",
}

FAMILY_MAP = {
    "claude-haiku-4-5-20251001": "claude",
    "claude-sonnet-4-6": "claude",
    "claude-opus-4-7": "claude",
    "gpt-5.4-nano": "gpt",
    "gpt-5.4-mini": "gpt",
    "gpt-5.4": "gpt",
}

PERMUTATION_N = 1000
PERMUTATION_SEED = 42  # locked

ALPHA = 0.05
EFFECT_SIZE_THRESHOLD = 0.01  # η² for "differs across models"


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_jsonl(path: Path) -> list[dict]:
    records = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def parse_phrasing(prompt_id: str) -> Optional[str]:
    """poem_write_10 → 'write'. Returns None if can't parse."""
    m = re.match(r"poem_([a-z]+)_\d+$", prompt_id)
    return m.group(1) if m else None


# ---------------------------------------------------------------------------
# Q1 — Embedding clustering
# ---------------------------------------------------------------------------

def cosine_distance_matrix(vectors: list[list[float]]):
    """Compute pairwise cosine distance. Returns numpy array."""
    import numpy as np
    arr = np.array(vectors, dtype=float)
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1, norms)
    normed = arr / norms
    sim = normed @ normed.T
    return 1.0 - sim


def silhouette_score(distances, labels) -> float:
    """Silhouette score using a precomputed distance matrix."""
    from sklearn.metrics import silhouette_score as sk_silhouette
    return float(sk_silhouette(distances, labels, metric="precomputed"))


def permutation_null(distances, labels, n_permutations: int, seed: int) -> list[float]:
    rng = random.Random(seed)
    labels = list(labels)
    null_scores = []
    for _ in range(n_permutations):
        permuted = labels.copy()
        rng.shuffle(permuted)
        null_scores.append(silhouette_score(distances, permuted))
    return null_scores


def q1_embedding_clustering(features: list[dict], embeddings: list[dict]) -> dict:
    # Index embeddings by run_id
    emb_by_id = {
        e["run_id"]: e["embedding"]
        for e in embeddings
        if e.get("embedding") is not None and e.get("error") is None
    }

    # Pair features and embeddings
    paired = []
    for f in features:
        emb = emb_by_id.get(f["run_id"])
        if emb is None:
            continue
        paired.append((f, emb))

    if not paired:
        return {"error": "no paired feature/embedding records"}

    feats = [p[0] for p in paired]
    vectors = [p[1] for p in paired]

    print(f"  Q1: {len(paired)} paired records, computing distance matrix...",
          file=sys.stderr)
    distances = cosine_distance_matrix(vectors)

    results = {"n_records": len(paired)}
    for label_name, label_fn in [
        ("model", lambda f: f["model"]),
        ("family", lambda f: FAMILY_MAP.get(f["model"], "unknown")),
        ("tier", lambda f: TIER_MAP.get(f["model"], "unknown")),
    ]:
        labels = [label_fn(f) for f in feats]
        observed = silhouette_score(distances, labels)
        print(f"  Q1: computing permutation null for {label_name} "
              f"({PERMUTATION_N} permutations)...", file=sys.stderr)
        null = permutation_null(distances, labels, PERMUTATION_N, PERMUTATION_SEED)
        null_sorted = sorted(null)
        p_value = sum(1 for n in null if n >= observed) / len(null)
        percentile_95 = null_sorted[int(0.95 * len(null_sorted))]
        results[label_name] = {
            "observed_silhouette": observed,
            "null_mean": sum(null) / len(null),
            "null_p95": percentile_95,
            "p_value_one_sided": p_value,
            "supported": observed > percentile_95,
        }
    return results


# ---------------------------------------------------------------------------
# Q2 — Feature comparison across models
# ---------------------------------------------------------------------------

def one_way_anova(groups: list[list[float]]) -> tuple[float, float, float]:
    """
    Returns (F, p, eta_squared).
    """
    from scipy.stats import f_oneway
    import numpy as np
    flat = [v for g in groups for v in g]
    if len(flat) < 2 or len(groups) < 2:
        return float("nan"), float("nan"), float("nan")
    grand_mean = sum(flat) / len(flat)
    ss_between = sum(
        len(g) * (sum(g) / len(g) - grand_mean) ** 2 for g in groups if g
    )
    ss_total = sum((v - grand_mean) ** 2 for v in flat)
    if ss_total == 0:
        return float("nan"), float("nan"), float("nan")
    eta_sq = ss_between / ss_total
    f_stat, p_val = f_oneway(*[g for g in groups if g])
    return float(f_stat), float(p_val), float(eta_sq)


def q2_feature_comparison(features: list[dict]) -> dict:
    n_features = len(PRIMARY_FEATURES)
    bonferroni_alpha = ALPHA / n_features

    results = {
        "n_features_tested": n_features,
        "bonferroni_alpha": bonferroni_alpha,
        "by_feature": {},
        "ranked_by_eta_squared": [],
    }

    for feat in PRIMARY_FEATURES:
        groups_by_model: dict[str, list[float]] = defaultdict(list)
        for f in features:
            v = f.get(feat)
            if v is None or (isinstance(v, float) and math.isnan(v)):
                continue
            groups_by_model[f["model"]].append(float(v))
        groups = list(groups_by_model.values())
        if not groups or all(len(g) == 0 for g in groups):
            results["by_feature"][feat] = {"error": "no data"}
            continue
        F, p, eta_sq = one_way_anova(groups)
        differs = (
            not math.isnan(p)
            and p < bonferroni_alpha
            and not math.isnan(eta_sq)
            and eta_sq > EFFECT_SIZE_THRESHOLD
        )
        per_model_means = {
            m: (sum(g) / len(g)) if g else None
            for m, g in groups_by_model.items()
        }
        per_model_n = {m: len(g) for m, g in groups_by_model.items()}
        results["by_feature"][feat] = {
            "F": F,
            "p": p,
            "p_bonferroni_corrected_alpha": bonferroni_alpha,
            "eta_squared": eta_sq,
            "differs_across_models": differs,
            "per_model_mean": per_model_means,
            "per_model_n": per_model_n,
        }

    # Rank by eta_squared
    ranked = sorted(
        [(feat, res["eta_squared"]) for feat, res in results["by_feature"].items()
         if "eta_squared" in res and not math.isnan(res["eta_squared"])],
        key=lambda x: x[1],
        reverse=True,
    )
    results["ranked_by_eta_squared"] = [{"feature": f, "eta_squared": e} for f, e in ranked]

    # For top-3 features, also compute family and tier effect sizes
    top3 = [r["feature"] for r in results["ranked_by_eta_squared"][:3]]
    results["top3_collapsed_factors"] = {}
    for feat in top3:
        family_groups: dict[str, list[float]] = defaultdict(list)
        tier_groups: dict[str, list[float]] = defaultdict(list)
        for f in features:
            v = f.get(feat)
            if v is None or (isinstance(v, float) and math.isnan(v)):
                continue
            family_groups[FAMILY_MAP.get(f["model"], "unknown")].append(float(v))
            tier_groups[TIER_MAP.get(f["model"], "unknown")].append(float(v))
        _, _, family_eta = one_way_anova(list(family_groups.values()))
        _, _, tier_eta = one_way_anova(list(tier_groups.values()))
        results["top3_collapsed_factors"][feat] = {
            "family_eta_squared": family_eta,
            "tier_eta_squared": tier_eta,
        }

    return results


# ---------------------------------------------------------------------------
# Q3 — Phrasing × model
# ---------------------------------------------------------------------------

def two_way_anova(features: list[dict], feat_name: str) -> Optional[dict]:
    """
    2-way ANOVA: model × phrasing on `feat_name`.
    """
    try:
        import pandas as pd
        import statsmodels.api as sm
        from statsmodels.formula.api import ols
    except ImportError:
        return {"error": "pandas/statsmodels not installed"}

    rows = []
    for f in features:
        v = f.get(feat_name)
        if v is None or (isinstance(v, float) and math.isnan(v)):
            continue
        phr = parse_phrasing(f["prompt_id"])
        if phr is None:
            continue
        rows.append({
            "value": float(v),
            "model": f["model"],
            "phrasing": phr,
        })
    if not rows:
        return {"error": "no data"}

    df = pd.DataFrame(rows)
    if df["phrasing"].nunique() < 2 or df["model"].nunique() < 2:
        return {"error": "insufficient factor levels"}

    try:
        model = ols("value ~ C(model) + C(phrasing) + C(model):C(phrasing)", data=df).fit()
        anova_table = sm.stats.anova_lm(model, typ=2)
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}

    # Compute partial eta-squared per term
    out: dict = {}
    ss_resid = float(anova_table.loc["Residual", "sum_sq"])
    for term in ["C(model)", "C(phrasing)", "C(model):C(phrasing)"]:
        if term not in anova_table.index:
            continue
        ss = float(anova_table.loc[term, "sum_sq"])
        F = float(anova_table.loc[term, "F"])
        p = float(anova_table.loc[term, "PR(>F)"])
        partial_eta_sq = ss / (ss + ss_resid) if (ss + ss_resid) > 0 else float("nan")
        key = {"C(model)": "model", "C(phrasing)": "phrasing",
               "C(model):C(phrasing)": "interaction"}[term]
        out[key] = {"F": F, "p": p, "partial_eta_squared": partial_eta_sq}
    return out


def q3_phrasing(features: list[dict]) -> dict:
    n_features = len(PRIMARY_FEATURES)
    bonferroni_alpha = ALPHA / n_features
    results = {
        "n_features_tested": n_features,
        "bonferroni_alpha": bonferroni_alpha,
        "by_feature": {},
        "any_phrasing_significant": False,
    }
    any_sig = False
    for feat in PRIMARY_FEATURES:
        res = two_way_anova(features, feat)
        results["by_feature"][feat] = res
        if isinstance(res, dict) and "phrasing" in res:
            if res["phrasing"]["p"] < bonferroni_alpha:
                any_sig = True
    results["any_phrasing_significant"] = any_sig
    return results


# ---------------------------------------------------------------------------
# Q4 — Compliance regression
# ---------------------------------------------------------------------------

def q4_compliance(features: list[dict]) -> dict:
    try:
        import pandas as pd
        import statsmodels.formula.api as smf
    except ImportError:
        return {"error": "pandas/statsmodels not installed"}

    rows = []
    for f in features:
        if f.get("compliant") is None:
            continue
        phr = parse_phrasing(f["prompt_id"])
        if phr is None or f.get("length_cap") is None:
            continue
        rows.append({
            "compliant": int(bool(f["compliant"])),
            "model": f["model"],
            "length_cap": int(f["length_cap"]),
            "phrasing": phr,
        })
    if not rows:
        return {"error": "no data"}

    df = pd.DataFrame(rows)

    per_cell = df.groupby(["model", "length_cap", "phrasing"])["compliant"].agg(
        ["mean", "count"]).reset_index()

    per_cell_records = per_cell.to_dict(orient="records")

    # Logistic regression
    try:
        m = smf.logit(
            "compliant ~ C(model) + C(length_cap) + C(phrasing)",
            data=df,
        ).fit(disp=0)
        coef_table = {
            "params": m.params.to_dict(),
            "pvalues": m.pvalues.to_dict(),
            "conf_int": m.conf_int().to_dict(orient="index"),
        }
    except Exception as e:
        coef_table = {"error": f"{type(e).__name__}: {e}"}

    return {
        "n_records": len(df),
        "overall_compliance_rate": float(df["compliant"].mean()),
        "per_cell_rates": per_cell_records,
        "logit": coef_table,
    }


# ---------------------------------------------------------------------------
# Report writing
# ---------------------------------------------------------------------------

def write_markdown_report(all_results: dict, out_path: Path) -> None:
    lines = []
    lines.append("# Bullshit Assay 2 — Analysis Report")
    lines.append("")
    lines.append("Auto-generated by `analyze.py`. Primary analyses are locked in")
    lines.append("`preregistration.md`. Any departure is recorded in `deviations.md`.")
    lines.append("")

    # Q1
    q1 = all_results.get("q1", {})
    lines.append("## Q1 — Embedding clustering")
    lines.append("")
    if "error" in q1:
        lines.append(f"**Error:** {q1['error']}")
    else:
        lines.append(f"Records included: {q1.get('n_records')}")
        lines.append("")
        lines.append("| Labeling | Observed silhouette | Null mean | Null 95th %ile | p (one-sided) | Supported |")
        lines.append("|---|---|---|---|---|---|")
        for label in ["model", "family", "tier"]:
            r = q1.get(label, {})
            lines.append(
                f"| {label} | {r.get('observed_silhouette', float('nan')):.4f} | "
                f"{r.get('null_mean', float('nan')):.4f} | "
                f"{r.get('null_p95', float('nan')):.4f} | "
                f"{r.get('p_value_one_sided', float('nan')):.4f} | "
                f"{r.get('supported')} |"
            )
    lines.append("")

    # Q2
    q2 = all_results.get("q2", {})
    lines.append("## Q2 — Feature comparison across models")
    lines.append("")
    lines.append(f"Features tested: {q2.get('n_features_tested')}")
    lines.append(f"Bonferroni-corrected α: {q2.get('bonferroni_alpha'):.6f}")
    lines.append("")
    lines.append("Features ranked by η² (effect size for model factor):")
    lines.append("")
    lines.append("| Feature | η² | F | p | Bonferroni-significant | η² > 0.01 | Differs |")
    lines.append("|---|---|---|---|---|---|---|")
    for entry in q2.get("ranked_by_eta_squared", []):
        feat = entry["feature"]
        r = q2["by_feature"].get(feat, {})
        lines.append(
            f"| {feat} | {r.get('eta_squared', float('nan')):.4f} | "
            f"{r.get('F', float('nan')):.2f} | "
            f"{r.get('p', float('nan')):.4g} | "
            f"{r.get('p', 1) < q2.get('bonferroni_alpha', 1)} | "
            f"{r.get('eta_squared', 0) > EFFECT_SIZE_THRESHOLD} | "
            f"{r.get('differs_across_models')} |"
        )
    lines.append("")
    if q2.get("top3_collapsed_factors"):
        lines.append("Top-3 features under collapsed factors:")
        lines.append("")
        lines.append("| Feature | family η² | tier η² |")
        lines.append("|---|---|---|")
        for feat, r in q2["top3_collapsed_factors"].items():
            lines.append(
                f"| {feat} | {r['family_eta_squared']:.4f} | "
                f"{r['tier_eta_squared']:.4f} |"
            )
        lines.append("")

    # Q3
    q3 = all_results.get("q3", {})
    lines.append("## Q3 — Phrasing × model interaction")
    lines.append("")
    lines.append(f"Any feature with significant phrasing main effect: "
                 f"**{q3.get('any_phrasing_significant')}**")
    lines.append("")
    lines.append("Per-feature 2-way ANOVA (partial η² and p-values):")
    lines.append("")
    lines.append("| Feature | model η² | model p | phrasing η² | phrasing p | interaction η² | interaction p |")
    lines.append("|---|---|---|---|---|---|---|")
    for feat in PRIMARY_FEATURES:
        r = q3.get("by_feature", {}).get(feat, {})
        if "error" in r:
            lines.append(f"| {feat} | — | — | — | — | — | error: {r['error']} |")
            continue
        m = r.get("model", {})
        ph = r.get("phrasing", {})
        ix = r.get("interaction", {})
        lines.append(
            f"| {feat} | "
            f"{m.get('partial_eta_squared', float('nan')):.4f} | "
            f"{m.get('p', float('nan')):.4g} | "
            f"{ph.get('partial_eta_squared', float('nan')):.4f} | "
            f"{ph.get('p', float('nan')):.4g} | "
            f"{ix.get('partial_eta_squared', float('nan')):.4f} | "
            f"{ix.get('p', float('nan')):.4g} |"
        )
    lines.append("")

    # Q4
    q4 = all_results.get("q4", {})
    lines.append("## Q4 — Compliance")
    lines.append("")
    if "error" in q4:
        lines.append(f"**Error:** {q4['error']}")
    else:
        lines.append(f"Overall compliance rate: "
                     f"{q4.get('overall_compliance_rate', float('nan')):.3f}")
        lines.append(f"Records: {q4.get('n_records')}")
        lines.append("")
        lines.append("Per-cell compliance rates:")
        lines.append("")
        lines.append("| Model | Length cap | Phrasing | n | Rate |")
        lines.append("|---|---|---|---|---|")
        for cell in q4.get("per_cell_rates", []):
            lines.append(
                f"| {cell['model']} | {cell['length_cap']} | {cell['phrasing']} | "
                f"{cell['count']} | {cell['mean']:.3f} |"
            )
        lines.append("")
        lines.append("Logistic regression (compliant ~ model + length_cap + phrasing):")
        lines.append("")
        logit = q4.get("logit", {})
        if "error" in logit:
            lines.append(f"Error: {logit['error']}")
        else:
            lines.append("| Term | Coefficient | p-value |")
            lines.append("|---|---|---|")
            params = logit.get("params", {})
            pvals = logit.get("pvalues", {})
            for term in params:
                lines.append(f"| {term} | {params[term]:.4f} | {pvals.get(term, float('nan')):.4g} |")
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def run_analyze(features_path: Path, embeddings_path: Optional[Path],
                report_md: Path, report_json: Path) -> None:
    print(f"Loading features from {features_path}...", file=sys.stderr)
    features = load_jsonl(features_path)
    print(f"  {len(features)} feature records loaded.", file=sys.stderr)

    embeddings: list[dict] = []
    if embeddings_path and embeddings_path.exists():
        print(f"Loading embeddings from {embeddings_path}...", file=sys.stderr)
        embeddings = load_jsonl(embeddings_path)
        print(f"  {len(embeddings)} embedding records loaded.", file=sys.stderr)

    all_results: dict = {}

    if embeddings:
        print("Running Q1 (embedding clustering)...", file=sys.stderr)
        all_results["q1"] = q1_embedding_clustering(features, embeddings)
    else:
        all_results["q1"] = {"error": "no embeddings provided"}

    print("Running Q2 (feature comparison)...", file=sys.stderr)
    all_results["q2"] = q2_feature_comparison(features)

    print("Running Q3 (phrasing × model)...", file=sys.stderr)
    all_results["q3"] = q3_phrasing(features)

    print("Running Q4 (compliance)...", file=sys.stderr)
    all_results["q4"] = q4_compliance(features)

    print(f"Writing JSON results to {report_json}...", file=sys.stderr)
    report_json.write_text(json.dumps(all_results, indent=2, default=str), encoding="utf-8")

    print(f"Writing Markdown report to {report_md}...", file=sys.stderr)
    write_markdown_report(all_results, report_md)

    print("Done.", file=sys.stderr)
