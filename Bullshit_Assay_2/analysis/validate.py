"""
Validation harness for the manual coding step.

Locked in `coding_heuristic.md`: a stratified sample of poems is hand-tagged
to validate the automated feature extractors. Features failing 85%
agreement are downgraded to exploratory.

This module provides:
- `draw_sample`: stratified random sample → JSON for the HTML tool
- `score_results`: load human tags from HTML tool export → compute agreement
"""

from __future__ import annotations

import json
import random
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional

# Locked agreement threshold from coding_heuristic.md
AGREEMENT_THRESHOLD = 0.85


def parse_phrasing_and_cap(prompt_id: str) -> tuple[Optional[str], Optional[int]]:
    m = re.match(r"poem_([a-z]+)_(\d+)$", prompt_id)
    if not m:
        return None, None
    return m.group(1), int(m.group(2))


def stratified_sample(features: list[dict], n: int, seed: int) -> list[dict]:
    """
    Proportional stratified sampling across (model × length_cap × phrasing) cells.
    Returns a list of feature records, length n.
    """
    rng = random.Random(seed)

    # Bucket by cell
    cells: dict[tuple[str, int, str], list[dict]] = defaultdict(list)
    for f in features:
        phr, cap = parse_phrasing_and_cap(f["prompt_id"])
        if phr is None or cap is None:
            continue
        if not f.get("poem_body"):
            continue
        cells[(f["model"], cap, phr)].append(f)

    if not cells:
        return []

    n_cells = len(cells)
    base_per_cell = n // n_cells
    remainder = n - base_per_cell * n_cells

    # Random order over cells for the remainder allocation
    cell_keys = list(cells.keys())
    rng.shuffle(cell_keys)

    sample = []
    for i, key in enumerate(cell_keys):
        take = base_per_cell + (1 if i < remainder else 0)
        bucket = cells[key]
        rng.shuffle(bucket)
        sample.extend(bucket[:take])

    rng.shuffle(sample)
    return sample


def build_validation_json(features: list[dict], n: int, seed: int) -> dict:
    """
    Build the JSON payload that the HTML tool consumes.

    Each item is blinded: model and phrasing are stripped from the visible
    payload; only length_cap is shown. The full record is included under
    a `_blinded` field with shuffle order so we can join back later.
    """
    sample = stratified_sample(features, n, seed)
    items = []
    for f in sample:
        phr, cap = parse_phrasing_and_cap(f["prompt_id"])
        person = f.get("person")
        items.append({
            "run_id": f["run_id"],
            "length_cap": cap,
            "poem_body": f["poem_body"],
            "preamble_text": f.get("preamble_text"),
            "auto": {
                "rhyme_scheme": f.get("rhyme_scheme"),
                "rhyme_scheme_known_only": f.get("rhyme_scheme_known_only"),
                "rhyme_participation_rate": f.get("rhyme_participation_rate"),
                "person": person,
                "has_preamble": f.get("has_preamble"),
            },
        })
    return {
        "version": 1,
        "n_items": len(items),
        "seed": seed,
        "agreement_threshold": AGREEMENT_THRESHOLD,
        "items": items,
    }


def draw_sample(features_path: Path, out_path: Path, n: int, seed: int) -> None:
    print(f"Loading features from {features_path}...", file=sys.stderr)
    features = []
    with features_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                features.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    print(f"  {len(features)} feature records loaded.", file=sys.stderr)

    payload = build_validation_json(features, n, seed)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote validation sample ({payload['n_items']} items, seed={seed}) "
          f"to {out_path.resolve()}", file=sys.stderr)
    print(f"\nNext step: open analysis/validation_tool.html in a browser, "
          f"load this file, and tag.", file=sys.stderr)


def score_results(results_path: Path, out_md: Path, out_json: Path) -> None:
    """
    Read human tags exported by the HTML tool and compute agreement
    rates per feature. Flag features below threshold.
    """
    payload = json.loads(results_path.read_text(encoding="utf-8"))
    items = payload.get("items", [])
    if not items:
        sys.exit("No items in validation results file.")

    # Aggregate
    counts = {
        "pos_ok": {"yes": 0, "mostly": 0, "no": 0, "untagged": 0},
        "rhyme_ok": {"yes": 0, "partial": 0, "no": 0, "untagged": 0},
        "person_ok": {"yes": 0, "no": 0, "untagged": 0},
        "preamble_ok": {"yes": 0, "no": 0, "untagged": 0},
    }
    notes: list[str] = []
    for item in items:
        tags = item.get("tags") or {}
        for feat, default_buckets in counts.items():
            v = tags.get(feat)
            if v is None:
                counts[feat]["untagged"] += 1
            elif v in counts[feat]:
                counts[feat][v] += 1
            else:
                counts[feat]["untagged"] += 1
        if item.get("notes"):
            notes.append(f"- [{item['run_id']}] {item['notes']}")

    # Agreement: yes counts as agreement; "mostly"/"partial" are partial credit (0.5)
    n_total = len(items)
    agreement = {}
    for feat, buckets in counts.items():
        if feat == "pos_ok":
            yes_score = buckets["yes"] + 0.5 * buckets["mostly"]
            tagged_n = buckets["yes"] + buckets["mostly"] + buckets["no"]
        elif feat == "rhyme_ok":
            yes_score = buckets["yes"] + 0.5 * buckets["partial"]
            tagged_n = buckets["yes"] + buckets["partial"] + buckets["no"]
        else:
            yes_score = buckets["yes"]
            tagged_n = buckets["yes"] + buckets["no"]
        rate = yes_score / tagged_n if tagged_n > 0 else None
        agreement[feat] = {
            "rate": rate,
            "tagged_n": tagged_n,
            "untagged_n": buckets["untagged"],
            "buckets": buckets,
            "passes_threshold": rate is not None and rate >= AGREEMENT_THRESHOLD,
        }

    out_data = {
        "n_total": n_total,
        "threshold": AGREEMENT_THRESHOLD,
        "agreement": agreement,
        "notes": notes,
    }
    out_json.write_text(json.dumps(out_data, indent=2), encoding="utf-8")

    # Markdown report
    lines = []
    lines.append("# Validation Results")
    lines.append("")
    lines.append(f"Total items in sample: {n_total}")
    lines.append(f"Agreement threshold (locked): {AGREEMENT_THRESHOLD}")
    lines.append("")
    lines.append("| Feature | Agreement | Tagged n | Untagged | Passes 85% |")
    lines.append("|---|---|---|---|---|")
    for feat, r in agreement.items():
        rate_str = f"{r['rate']:.3f}" if r["rate"] is not None else "—"
        lines.append(f"| {feat} | {rate_str} | {r['tagged_n']} | {r['untagged_n']} | "
                     f"{r['passes_threshold']} |")
    lines.append("")
    failed = [f for f, r in agreement.items() if not r["passes_threshold"]]
    if failed:
        lines.append("**Features below threshold (downgrade to exploratory):**")
        for f in failed:
            lines.append(f"- `{f}`")
        lines.append("")
    if notes:
        lines.append("## Notes")
        lines.append("")
        for note in notes:
            lines.append(note)
        lines.append("")

    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote scoring report to {out_md.resolve()}", file=sys.stderr)
    print(f"Wrote scoring JSON to {out_json.resolve()}", file=sys.stderr)
    if failed:
        print("\nFEATURES FAILING THRESHOLD:", file=sys.stderr)
        for f in failed:
            print(f"  - {f}", file=sys.stderr)
