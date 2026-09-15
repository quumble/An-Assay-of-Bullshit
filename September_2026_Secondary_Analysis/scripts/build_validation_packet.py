#!/usr/bin/env python3
"""Build the fixed blinded 180-response parser-validation sample.

This script does not compute cross-study outcomes. It samples 15 responses per
model per study (90 + 90), balanced across prompt cells as evenly as possible,
using the locked seed 20260915. Model identity is omitted from the review packet.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from pathlib import Path
from typing import Any

from harmonizer_core import harmonized_metadata, parse_surface

LOCKED_SEED = 20260915
TARGET_PER_MODEL_STUDY = 15

DEFAULT_BA1 = Path("Bullshit_Assay_1/Results and Heuristics/results.jsonl")
DEFAULT_BA2 = Path("Bullshit_Assay_2/Results and Analysis/results_final_raw_5400.jsonl")
DEFAULT_OUTDIR = Path("September_2026_Secondary_Analysis/validation")


def stable_seed(*parts: object) -> int:
    raw = "|".join(str(x) for x in parts).encode("utf-8")
    return int.from_bytes(hashlib.sha256(raw).digest()[:8], "big")


def load_successes(path: Path, study: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"{path}:{lineno}: malformed JSON") from exc
            if rec.get("error"):
                continue
            response = rec.get("response")
            if response is None or not str(response).strip():
                continue
            rec = dict(rec)
            rec["_study"] = study
            rec["_source_line"] = lineno
            rows.append(rec)
    return rows


def allocate_across_prompt_cells(records: list[dict[str, Any]], target: int, seed: int) -> list[dict[str, Any]]:
    by_prompt: dict[str, list[dict[str, Any]]] = {}
    for rec in records:
        pid = str(rec.get("prompt_id") or "")
        by_prompt.setdefault(pid, []).append(rec)

    prompt_ids = sorted(by_prompt)
    if not prompt_ids:
        raise RuntimeError("No prompt cells available for sampling.")
    if len(records) < target:
        raise RuntimeError(f"Only {len(records)} records available; target is {target}.")

    base = target // len(prompt_ids)
    remainder = target % len(prompt_ids)
    allocation = {pid: min(base, len(by_prompt[pid])) for pid in prompt_ids}

    rng = random.Random(seed)
    shuffled = prompt_ids[:]
    rng.shuffle(shuffled)
    for pid in shuffled[:remainder]:
        if allocation[pid] < len(by_prompt[pid]):
            allocation[pid] += 1

    selected: list[dict[str, Any]] = []
    for pid in prompt_ids:
        cell = by_prompt[pid][:]
        rng.shuffle(cell)
        take = min(allocation[pid], len(cell))
        selected.extend(cell[:take])

    if len(selected) < target:
        selected_keys = {
            (r.get("run_id"), r.get("prompt_id"), r.get("iteration"), r.get("_source_line"))
            for r in selected
        }
        leftovers = [
            r for r in records
            if (r.get("run_id"), r.get("prompt_id"), r.get("iteration"), r.get("_source_line"))
            not in selected_keys
        ]
        rng.shuffle(leftovers)
        selected.extend(leftovers[: target - len(selected)])

    if len(selected) != target:
        raise RuntimeError(f"Sampling produced {len(selected)} rows, expected {target}.")
    return selected


def build_sample(ba1: list[dict[str, Any]], ba2: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for study, rows in (("BA1", ba1), ("BA2", ba2)):
        by_model: dict[str, list[dict[str, Any]]] = {}
        for rec in rows:
            model = str(rec.get("model") or "")
            by_model.setdefault(model, []).append(rec)

        if len(by_model) != 6:
            raise RuntimeError(f"{study}: expected 6 models, found {len(by_model)}: {sorted(by_model)}")

        for model in sorted(by_model):
            model_seed = stable_seed(LOCKED_SEED, study, model)
            selected.extend(allocate_across_prompt_cells(by_model[model], TARGET_PER_MODEL_STUDY, model_seed))

    if len(selected) != 180:
        raise RuntimeError(f"Expected 180 selected responses; got {len(selected)}.")

    rng = random.Random(LOCKED_SEED)
    rng.shuffle(selected)
    return selected


def review_row(validation_id: str, rec: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    study = rec["_study"]
    meta = harmonized_metadata(rec, study)
    parsed = parse_surface(rec.get("response"))

    public = {
        "validation_id": validation_id,
        "study": study,
        "prompt_id": meta["prompt_id"],
        "prompt_text": meta["prompt_text"],
        "genre": meta["genre"],
        "length_condition": meta["length_condition"],
        "phrasing": meta["phrasing"],
        "full_response": parsed.normalized_response,
        "parser_preamble_present": "yes" if parsed.preamble_present else "no",
        "parser_preamble_text": parsed.preamble_text,
        "parser_title_present": "yes" if parsed.title_present else "no",
        "parser_title_text": parsed.title_text,
        "parser_creative_body": parsed.creative_body,
    }
    private = {
        "validation_id": validation_id,
        "study": study,
        "provider": meta["provider"],
        "model": meta["model"],
        "prompt_id": meta["prompt_id"],
        "iteration": meta["iteration"],
        "source_run_id": meta["source_run_id"],
        "source_line": rec["_source_line"],
    }
    return public, private


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise RuntimeError(f"No rows to write: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def make_html(rows: list[dict[str, Any]], outpath: Path) -> None:
    data_json = json.dumps(rows, ensure_ascii=False).replace("</", "<\\/")
    doc = r"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>September 2026 Parser Validation</title>
<style>
body { font-family: system-ui, sans-serif; max-width: 1100px; margin: 24px auto; padding: 0 16px; }
pre { white-space: pre-wrap; border: 1px solid #bbb; padding: 12px; border-radius: 6px; max-height: 320px; overflow:auto; }
.segment { background: #f7f7f7; }
.grid { display:grid; grid-template-columns: 1fr 1fr; gap:16px; }
fieldset { margin: 10px 0; }
label { margin-right: 14px; }
button { padding: 8px 12px; margin-right: 8px; }
#progress { font-weight: 600; }
.meta { color:#555; }
textarea { width:100%; min-height:70px; }
</style>
</head>
<body>
<h1>September 2026 parser validation</h1>
<p>Model identity is not present in this file. Judge the full response and the parser's segmentation. Progress is saved in this browser's localStorage.</p>
<div id="progress"></div>
<div id="meta" class="meta"></div>
<h3>Full response</h3><pre id="full"></pre>
<div class="grid">
  <div><h3>Parser preamble</h3><pre id="pre" class="segment"></pre></div>
  <div><h3>Parser title</h3><pre id="title" class="segment"></pre></div>
</div>
<h3>Parser creative body</h3><pre id="body" class="segment"></pre>

<div id="questions"></div>
<label>Notes</label><textarea id="notes"></textarea>
<p>
<button onclick="prev()">Previous</button>
<button onclick="next()">Save & Next</button>
<button onclick="exportJSON()">Export judgments JSON</button>
</p>
<script>
const rows = __DATA__;
const KEY = "ba_sep2026_validation_v1";
let judgments = JSON.parse(localStorage.getItem(KEY) || "{}");
let idx = 0;

const fields = [
 ["human_preamble_present","Human: preamble present? ",["yes","no"]],
 ["human_title_present","Human: title present? ",["yes","no"]],
 ["human_preamble_boundary_correct","Parser preamble boundary correct? ",["yes","no","not_applicable"]],
 ["human_title_boundary_correct","Parser title boundary correct? ",["yes","no","not_applicable"]],
 ["human_creative_body_start_correct","Parser creative-body start correct? ",["yes","no"]]
];

function save() {
  const r = rows[idx];
  const j = judgments[r.validation_id] || {};
  for (const [name] of fields) {
    const el = document.querySelector(`input[name="${name}"]:checked`);
    j[name] = el ? el.value : "";
  }
  j.notes = document.getElementById("notes").value;
  judgments[r.validation_id] = j;
  localStorage.setItem(KEY, JSON.stringify(judgments));
}

function render() {
  const r = rows[idx];
  const j = judgments[r.validation_id] || {};
  const complete = Object.values(judgments).filter(x =>
    fields.every(([name]) => x[name])
  ).length;
  document.getElementById("progress").textContent = `Item ${idx+1} / ${rows.length} — fully coded ${complete} / ${rows.length}`;
  document.getElementById("meta").textContent =
    `${r.validation_id} | ${r.study} | ${r.prompt_id} | ${r.prompt_text}`;
  document.getElementById("full").textContent = r.full_response || "";
  document.getElementById("pre").textContent =
    `${r.parser_preamble_present}\n${r.parser_preamble_text || ""}`;
  document.getElementById("title").textContent =
    `${r.parser_title_present}\n${r.parser_title_text || ""}`;
  document.getElementById("body").textContent = r.parser_creative_body || "";

  const q = document.getElementById("questions");
  q.innerHTML = "";
  for (const [name, prompt, options] of fields) {
    const fs = document.createElement("fieldset");
    const legend = document.createElement("legend");
    legend.textContent = prompt;
    fs.appendChild(legend);
    for (const opt of options) {
      const lab = document.createElement("label");
      const inp = document.createElement("input");
      inp.type = "radio"; inp.name = name; inp.value = opt;
      inp.checked = j[name] === opt;
      lab.appendChild(inp);
      lab.appendChild(document.createTextNode(" " + opt));
      fs.appendChild(lab);
    }
    q.appendChild(fs);
  }
  document.getElementById("notes").value = j.notes || "";
  window.scrollTo(0,0);
}
function next() { save(); if (idx < rows.length-1) idx++; render(); }
function prev() { save(); if (idx > 0) idx--; render(); }

function exportJSON() {
  save();
  const payload = {
    schema: "ba_sep2026_parser_validation_v1",
    exported_at: new Date().toISOString(),
    judgments
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], {type:"application/json"});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "validation_judgments.json";
  a.click();
  URL.revokeObjectURL(a.href);
}
render();
</script>
</body>
</html>"""
    doc = doc.replace("__DATA__", data_json)
    outpath.write_text(doc, encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--ba1", type=Path, default=None)
    ap.add_argument("--ba2", type=Path, default=None)
    ap.add_argument("--outdir", type=Path, default=None)
    args = ap.parse_args()

    repo = args.repo_root.resolve()
    ba1_path = (args.ba1 or (repo / DEFAULT_BA1)).resolve()
    ba2_path = (args.ba2 or (repo / DEFAULT_BA2)).resolve()
    outdir = (args.outdir or (repo / DEFAULT_OUTDIR)).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    ba1 = load_successes(ba1_path, "BA1")
    ba2 = load_successes(ba2_path, "BA2")
    selected = build_sample(ba1, ba2)

    public_rows = []
    private_rows = []
    for i, rec in enumerate(selected, 1):
        vid = f"V{i:03d}"
        pub, priv = review_row(vid, rec)
        public_rows.append(pub)
        private_rows.append(priv)

    write_csv(outdir / "validation_packet.csv", public_rows)
    write_csv(outdir / "validation_key_PRIVATE.csv", private_rows)
    make_html(public_rows, outdir / "validation_review.html")

    manifest = {
        "schema": "ba_sep2026_parser_validation_v1",
        "seed": LOCKED_SEED,
        "target_total": 180,
        "target_per_study": 90,
        "target_per_model_per_study": TARGET_PER_MODEL_STUDY,
        "ba1_source": str(ba1_path),
        "ba2_source": str(ba2_path),
        "ba1_success_nonempty_available": len(ba1),
        "ba2_success_nonempty_available": len(ba2),
        "review_packet": "validation_packet.csv",
        "private_key": "validation_key_PRIVATE.csv",
        "review_html": "validation_review.html",
    }
    (outdir / "validation_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )

    print(f"Wrote {len(public_rows)} blinded validation items to {outdir}")
    print("STOP: complete and score parser validation before running harmonize.py.")


if __name__ == "__main__":
    main()
