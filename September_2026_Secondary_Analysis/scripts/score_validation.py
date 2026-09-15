#!/usr/bin/env python3
"""Score the locked human parser-validation gate.

Expected input is the JSON exported by validation_review.html.
No model identities or scientific outcome variables are used.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

THRESHOLD = 0.90

PRESENCE_FIELDS = {
    "preamble_present": ("parser_preamble_present", "human_preamble_present"),
    "title_present": ("parser_title_present", "human_title_present"),
}

CORRECTNESS_FIELDS = {
    "preamble_boundary_correct": "human_preamble_boundary_correct",
    "title_boundary_correct": "human_title_boundary_correct",
    "creative_body_start_correct": "human_creative_body_start_correct",
}


def load_packet(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def load_judgments(path: Path) -> dict[str, dict[str, str]]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if obj.get("schema") != "ba_sep2026_parser_validation_v1":
        raise RuntimeError("Unexpected validation judgments schema.")
    return obj.get("judgments", {})


def score(packet: list[dict[str, str]], judgments: dict[str, dict[str, str]]) -> dict[str, Any]:
    missing_items = []
    details: dict[str, Any] = {}

    for row in packet:
        vid = row["validation_id"]
        if vid not in judgments:
            missing_items.append(vid)

    for out_name, (parser_col, human_col) in PRESENCE_FIELDS.items():
        vals = []
        missing = []
        for row in packet:
            vid = row["validation_id"]
            h = judgments.get(vid, {}).get(human_col, "")
            if h not in {"yes", "no"}:
                missing.append(vid)
                continue
            vals.append(1 if h == row[parser_col] else 0)
        rate = sum(vals) / len(vals) if vals else None
        details[out_name] = {
            "n_scored": len(vals),
            "n_missing": len(missing),
            "agreement": rate,
            "passes_0.90": bool(rate is not None and rate >= THRESHOLD and not missing),
        }

    for out_name, human_col in CORRECTNESS_FIELDS.items():
        vals = []
        missing = []
        n_na = 0
        for row in packet:
            vid = row["validation_id"]
            h = judgments.get(vid, {}).get(human_col, "")
            if h == "not_applicable":
                n_na += 1
                continue
            if h not in {"yes", "no"}:
                missing.append(vid)
                continue
            vals.append(1 if h == "yes" else 0)
        rate = sum(vals) / len(vals) if vals else None
        details[out_name] = {
            "n_scored": len(vals),
            "n_not_applicable": n_na,
            "n_missing": len(missing),
            "agreement": rate,
            "passes_0.90": bool(rate is not None and rate >= THRESHOLD and not missing),
        }

    overall_pass = (not missing_items) and all(v["passes_0.90"] for v in details.values())
    return {
        "threshold": THRESHOLD,
        "packet_n": len(packet),
        "judgment_items_present": len(judgments),
        "missing_item_records": missing_items,
        "fields": details,
        "overall_pass": overall_pass,
    }


def markdown_report(results: dict[str, Any]) -> str:
    lines = [
        "# September 2026 parser validation score",
        "",
        f"Threshold: **{results['threshold']:.2f}**",
        f"Packet rows: **{results['packet_n']}**",
        f"Overall gate: **{'PASS' if results['overall_pass'] else 'FAIL / INCOMPLETE'}**",
        "",
        "| Field | n scored | n N/A | n missing | agreement | pass |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for name, v in results["fields"].items():
        agr = "NA" if v["agreement"] is None else f"{v['agreement']:.3f}"
        lines.append(
            f"| {name} | {v['n_scored']} | {v.get('n_not_applicable', 0)} | "
            f"{v['n_missing']} | {agr} | {'yes' if v['passes_0.90'] else 'no'} |"
        )
    lines += [
        "",
        "If any applicable field is below 0.90, the locked plan permits parser revision "
        "before primary outcome analysis, with the change documented in the September deviations log.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--packet", type=Path, required=True)
    ap.add_argument("--judgments", type=Path, required=True)
    ap.add_argument("--outdir", type=Path, default=None)
    args = ap.parse_args()

    outdir = (args.outdir or args.packet.parent).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    packet = load_packet(args.packet)
    judgments = load_judgments(args.judgments)
    results = score(packet, judgments)

    (outdir / "validation_scores.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
    (outdir / "validation_scores.md").write_text(
        markdown_report(results), encoding="utf-8"
    )

    print(markdown_report(results))
    raise SystemExit(0 if results["overall_pass"] else 2)


if __name__ == "__main__":
    main()
