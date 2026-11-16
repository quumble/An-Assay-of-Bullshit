"""
product_gap.py  --  bare API vs "chat app" conditions, quick run.

One file, no installs (Python 3.9+ standard library only).

    python product_gap.py            run everything, then print the summary
    python product_gap.py score      re-score what is already collected
    python product_gap.py --dry-run  fake responses, no keys, no spend (smoke test)

It asks for your API keys if ANTHROPIC_API_KEY / OPENAI_API_KEY are not set.
Keys are used in memory only and never written anywhere.

Everything lands in ./product_gap_run/ next to this file:
    results.jsonl   one line per call, written as it happens (safe to Ctrl-C)
    summary.md      the tables
    summary.csv     same numbers, flat

Run it again after a crash or Ctrl-C and it picks up where it stopped.

ARMS
    bare       no system prompt (what the published studies used)
    chatapp    the same short consumer-style system prompt for both families
    published  Claude models only, and only if you save Anthropic's published
               claude.ai system prompt as  claude_system_prompt.txt  next to
               this file. Skipped silently if the file is not there.

HAND ARM (optional, the only arm that is the real product)
    Paste replies from fresh temporary chats into
        product_gap_run/hand_claude.txt
        product_gap_run/hand_chatgpt.txt
    one reply after another, separated by a line containing only  ---
    These are scored as joke-prompt replies ("Tell me a joke.").
"""

from __future__ import annotations

import argparse
import csv
import getpass
import json
import math
import os
import random
import re
import sys
import threading
import time
import urllib.error
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "product_gap_run"
RESULTS = OUT / "results.jsonl"

# ---------------------------------------------------------------------------
# Design. Prompts are verbatim from the published studies, typo included.
# ---------------------------------------------------------------------------

PROMPTS = [
    ("joke", "Tell me a joke."),
    ("poem_lt5", "create a poem in fewer then 5 lines."),
    ("story_lt5", "create a short story in fewer than 5 sentences."),
]

ANTHROPIC_MODELS = ["claude-haiku-4-5-20251001", "claude-sonnet-4-6", "claude-opus-4-7"]
OPENAI_MODELS = ["gpt-5.4-nano", "gpt-5.4-mini", "gpt-5.4"]

TEMPERATURE = 1.0
MAX_TOKENS = 400

CHATAPP_TEMPLATE = (
    "You are {name}, an AI assistant made by {maker}. You are chatting with a "
    "user in the {app} app. The current date is {date}."
)
CHATAPP_FILL = {
    "anthropic": {"name": "Claude", "maker": "Anthropic", "app": "Claude"},
    "openai": {"name": "ChatGPT", "maker": "OpenAI", "app": "ChatGPT"},
}

# Rough list prices, US$ per million tokens (input, output), rounded up.
# Only used for the running estimate and the cap. Your provider dashboard
# is the real number.
PRICE = {
    "claude-haiku-4-5-20251001": (1.0, 5.0),
    "claude-sonnet-4-6": (3.0, 15.0),
    "claude-opus-4-7": (5.0, 25.0),
    "gpt-5.4-nano": (0.5, 2.0),
    "gpt-5.4-mini": (1.0, 5.0),
    "gpt-5.4": (3.0, 15.0),
}


def provider_of(model: str) -> str:
    return "anthropic" if model.startswith("claude") else "openai"


# ---------------------------------------------------------------------------
# Coder. The three functions below are copied from
# An-Assay-of-Bullshit / Bullshit_Assay_1 / structural_heuristics.py
# (Bo Chesterton, Apache-2.0) so the scoring matches the published coder.
# ---------------------------------------------------------------------------

META_FRAMING = (
    "here is", "here's", "title:", "story:", "poem:", "sure!", "sure,",
    "certainly!", "certainly,", "of course!", "absolutely!",
)


WORD_RE = re.compile(r"\b[a-zA-Z][a-zA-Z'\u2019-]*\b")


def clean_text(text):
    if not text:
        return ""
    return text.replace("\r\n", "\n").replace("\r", "\n").strip()


def tokenize(text: str):
    return [m.group(0).lower().replace("\u2019", "'") for m in WORD_RE.finditer(text)]


def nonempty_lines(text: str):
    return [ln.strip() for ln in clean_text(text).split("\n") if ln.strip()]


def title_or_preamble_flag(text: str):
    lines = nonempty_lines(text)
    if not lines:
        return {"has_title_line": False, "has_meta_preamble": False}
    first = lines[0].strip()
    text_lower = text.lower().lstrip()
    has_title_line = False
    if first and len(tokenize(first)) <= 10:
        if not first.endswith((".", "!", "?")):
            blank_after = bool(re.match(r"^[^\n]+\n\s*\n", text.strip()))
            title_case = first[0].isupper() and sum(
                1 for w in first.split() if w[:1].isupper()
            ) >= max(1, len(first.split()) // 2)
            if blank_after or title_case:
                has_title_line = True
    has_preamble = any(text_lower.startswith(p) for p in META_FRAMING)
    return {"has_title_line": has_title_line, "has_meta_preamble": has_preamble}


def code_response(text: str):
    text = clean_text(text)
    toks = tokenize(text)
    row = title_or_preamble_flag(text)
    row["em_dash_count"] = text.count("—")
    row["word_count"] = len(toks)
    row["first_word"] = toks[0] if toks else ""
    row["mentions_atoms"] = "atom" in text.lower()
    return row


# ---------------------------------------------------------------------------
# API calls (plain HTTPS, same request shapes as the original runner)
# ---------------------------------------------------------------------------

class ModelGone(Exception):
    pass


def _post(url: str, headers: dict, body: dict, timeout: int = 120) -> dict:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("content-type", "application/json")
    for k, v in headers.items():
        req.add_header(k, v)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def call_anthropic(key, model, prompt, system, send_temp=True):
    body = {
        "model": model,
        "max_tokens": MAX_TOKENS,
        "messages": [{"role": "user", "content": prompt}],
    }
    if send_temp:
        body["temperature"] = TEMPERATURE
    if system:
        body["system"] = system
    j = _post(
        "https://api.anthropic.com/v1/messages",
        {"x-api-key": key, "anthropic-version": "2023-06-01"},
        body,
    )
    text = "".join(b.get("text", "") for b in j.get("content", []) if b.get("type") == "text")
    u = j.get("usage", {})
    return text, u.get("input_tokens"), u.get("output_tokens")


def call_openai(key, model, prompt, system, send_temp=True):
    body = {"model": model, "input": prompt, "max_output_tokens": MAX_TOKENS}
    if send_temp:
        body["temperature"] = TEMPERATURE
    if system:
        body["instructions"] = system
    j = _post("https://api.openai.com/v1/responses", {"authorization": "Bearer " + key}, body)
    parts = []
    for item in j.get("output", []) or []:
        if item.get("type") == "message":
            for c in item.get("content", []) or []:
                if c.get("type") == "output_text":
                    parts.append(c.get("text", ""))
    u = j.get("usage", {}) or {}
    return "".join(parts), u.get("input_tokens"), u.get("output_tokens")


FAKE = [
    "Why don't scientists trust atoms?\n\nBecause they make up everything! \U0001F604",
    "Sure! Here is a short poem:\n\nThe rain — it falls,\nand so do I.",
    "# The Lighthouse\n\nThe keeper slept. The light went on.",
    "The fox waited by the gate until morning.",
]


def call_fake(key, model, prompt, system, send_temp=True):
    time.sleep(0.01)
    rng = random.Random(hash((model, prompt, system, time.perf_counter_ns())))
    return rng.choice(FAKE), 20 + (len(system or "") // 4), 30


def call_one(keys, model, prompt, system, dry):
    """Returns (record_fields). Raises ModelGone if the model id is not served."""
    prov = provider_of(model)
    fn = call_fake if dry else (call_anthropic if prov == "anthropic" else call_openai)
    send_temp = True
    last = None
    for attempt in range(6):
        try:
            t0 = time.perf_counter()
            text, tin, tout = fn(keys.get(prov), model, prompt, system, send_temp)
            return {
                "response": text,
                "input_tokens": tin,
                "output_tokens": tout,
                "latency_ms": int((time.perf_counter() - t0) * 1000),
                "temperature_sent": TEMPERATURE if send_temp else None,
                "error": None,
            }
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:600]
            last = "HTTP %s: %s" % (e.code, detail)
            low = detail.lower()
            if e.code in (401, 403):
                raise SystemExit("\nKey rejected by %s (HTTP %s). Nothing else was sent.\n%s" % (prov, e.code, detail))
            if e.code == 404 or (e.code == 400 and "model" in low and ("not found" in low or "does not exist" in low or "not_found" in low)):
                raise ModelGone(last)
            if e.code == 400 and "temperature" in low and send_temp:
                send_temp = False  # model only accepts its default; default is 1.0
                continue
            if e.code in (408, 409, 429) or e.code >= 500:
                time.sleep(min(60, 2 ** attempt + random.random()))
                continue
            break
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            last = "network: %r" % (e,)
            time.sleep(min(60, 2 ** attempt + random.random()))
    return {"response": None, "input_tokens": None, "output_tokens": None,
            "latency_ms": None, "temperature_sent": None, "error": last}


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

def read_results():
    rows = []
    if RESULTS.exists():
        with RESULTS.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        rows.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    return rows


def get_keys(models, dry):
    if dry:
        return {"anthropic": "dry", "openai": "dry"}
    keys = {}
    need = {provider_of(m) for m in models}
    for prov, env in (("anthropic", "ANTHROPIC_API_KEY"), ("openai", "OPENAI_API_KEY")):
        if prov not in need:
            continue
        k = os.environ.get(env, "").strip()
        if not k:
            k = getpass.getpass("Paste your %s (hidden, press Enter to skip that family): " % env).strip()
        if k:
            keys[prov] = k
        else:
            print("  no %s key, skipping those models" % prov)
    return keys


def run(args):
    OUT.mkdir(exist_ok=True)
    models = ANTHROPIC_MODELS + OPENAI_MODELS
    if args.models:
        models = [m.strip() for m in args.models.split(",") if m.strip()]
    keys = get_keys(models, args.dry_run)
    models = [m for m in models if provider_of(m) in keys]
    if not models:
        raise SystemExit("No keys, nothing to run.")

    today = datetime.now().strftime("%A, %B %d, %Y")
    pub_path = HERE / "claude_system_prompt.txt"
    published = pub_path.read_text(encoding="utf-8").strip() if pub_path.exists() else ""

    def system_for(model, arm):
        prov = provider_of(model)
        if arm == "bare":
            return ""
        if arm == "chatapp":
            return CHATAPP_TEMPLATE.format(date=today, **CHATAPP_FILL[prov])
        if arm == "published":
            return published
        raise ValueError(arm)

    done = {(r["model"], r["arm"], r["prompt_id"], r["iteration"])
            for r in read_results() if not r.get("error")}
    jobs = []
    for model in models:
        arms = ["bare", "chatapp"]
        if published and provider_of(model) == "anthropic":
            arms.append("published")
        for arm in arms:
            for pid, ptext in PROMPTS:
                for i in range(args.n):
                    if (model, arm, pid, i) not in done:
                        jobs.append((model, arm, pid, ptext, i))
    # Interleave so a crash or the cap leaves every cell partly filled, not some empty.
    random.Random(20261116).shuffle(jobs)

    total = len(jobs)
    print("\n%d calls to make (%d already done). Arms: bare, chatapp%s. n=%d per cell."
          % (total, len(done), ", published" if published else "", args.n))
    print("Output: %s\nCtrl-C is safe; run again to resume.\n" % RESULTS)
    if total == 0:
        return

    lock = threading.Lock()
    gone = {}
    state = {"k": 0, "usd": 0.0, "err": 0, "stop": False}
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    t_start = time.time()

    def work(job):
        model, arm, pid, ptext, i = job
        if state["stop"] or model in gone:
            return
        system = system_for(model, arm)
        try:
            res = call_one(keys, model, ptext, system, args.dry_run)
        except ModelGone as e:
            with lock:
                if model not in gone:
                    gone[model] = str(e)
                    print("  !! %s is not being served any more, skipping it." % model)
            return
        rec = {
            "run_id": run_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "provider": provider_of(model), "model": model, "arm": arm,
            "prompt_id": pid, "prompt_text": ptext, "iteration": i,
            "system_prompt": system, "max_tokens": MAX_TOKENS,
        }
        rec.update(res)
        pin, pout = PRICE.get(model, (5.0, 25.0))
        cost = ((res["input_tokens"] or 0) * pin + (res["output_tokens"] or 0) * pout) / 1e6
        with lock:
            with RESULTS.open("a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            state["k"] += 1
            state["usd"] += cost
            if res["error"]:
                state["err"] += 1
            el = time.time() - t_start
            eta = el / state["k"] * (total - state["k"])
            print("[%4d/%d] %-26s %-9s %-9s #%02d  %s   est $%.2f  ~%dm%02ds left"
                  % (state["k"], total, model, arm, pid, i,
                     "ERR" if res["error"] else "ok ", state["usd"],
                     int(eta // 60), int(eta % 60)), flush=True)
            if state["usd"] >= args.max_usd and not state["stop"]:
                state["stop"] = True
                print("\n  !! estimated spend reached the $%.2f cap. Stopping here." % args.max_usd)

    try:
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            futs = [ex.submit(work, j) for j in jobs]
            for f in as_completed(futs):
                f.result()
    except KeyboardInterrupt:
        state["stop"] = True
        print("\nStopped. Whatever finished is saved. Run again to resume.")

    print("\nDone: %d calls, %d errors, estimated $%.2f." % (state["k"], state["err"], state["usd"]))
    if gone:
        (OUT / "models_not_served.json").write_text(json.dumps(gone, indent=2), encoding="utf-8")
        print("Not served: " + ", ".join(gone))


# ---------------------------------------------------------------------------
# Score
# ---------------------------------------------------------------------------

def fisher_p(a, b, c, d):
    """Two-sided Fisher exact test for the table [[a, b], [c, d]]."""
    n1, n2, k = a + b, c + d, a + c
    n = n1 + n2
    if n == 0 or k == 0 or k == n:
        return 1.0
    denom = math.comb(n, k)
    def p(x):
        return math.comb(n1, x) * math.comb(n2, k - x) / denom
    p0 = p(a)
    lo, hi = max(0, k - n2), min(k, n1)
    return min(1.0, sum(p(x) for x in range(lo, hi + 1) if p(x) <= p0 * (1 + 1e-9)))


def summarize(texts):
    coded = [code_response(t) for t in texts]
    n = len(coded)
    if n == 0:
        return None
    words = sum(c["word_count"] for c in coded)
    modal_text, modal_n = Counter(t.strip() for t in texts).most_common(1)[0]
    fw, fw_n = Counter(c["first_word"] for c in coded).most_common(1)[0]
    return {
        "n": n,
        "preamble": sum(c["has_meta_preamble"] for c in coded),
        "title": sum(c["has_title_line"] for c in coded),
        "emdash_any": sum(1 for c in coded if c["em_dash_count"] > 0),
        "emdash_per100w": round(100.0 * sum(c["em_dash_count"] for c in coded) / words, 2) if words else 0.0,
        "atoms": sum(c["mentions_atoms"] for c in coded),
        "identical": modal_n,
        "distinct": len(set(t.strip() for t in texts)),
        "top_first_word": "%s (%d)" % (fw, fw_n),
        "modal_text": modal_text.replace("\n", " / ")[:90],
    }


def read_hand():
    out = {}
    for name in ("claude", "chatgpt"):
        p = OUT / ("hand_%s.txt" % name)
        if p.exists():
            chunks = re.split(r"(?m)^\s*---\s*$", p.read_text(encoding="utf-8"))
            texts = [c.strip() for c in chunks if c.strip()]
            if texts:
                out[name] = texts
    return out


def pct(k, n):
    return "%d/%d" % (k, n)


def score(_args=None):
    rows = [r for r in read_results() if not r.get("error") and r.get("response") is not None]
    if not rows:
        print("Nothing collected yet.")
        return
    cells = {}
    for r in rows:
        cells.setdefault((r["model"], r["prompt_id"], r["arm"]), []).append(r["response"])

    order_models = ANTHROPIC_MODELS + OPENAI_MODELS
    models = [m for m in order_models if any(k[0] == m for k in cells)] + \
             sorted({k[0] for k in cells} - set(order_models))
    arms_order = ["bare", "chatapp", "published"]

    md = ["# Product gap, quick run", "",
          "Scored %s. Settings: temperature 1.0, max 400 output tokens. Coder: the"
          " published structural heuristics (preamble, title line, em-dash)." % datetime.now().strftime("%Y-%m-%d %H:%M"),
          ""]
    flat = []
    for pid, ptext in PROMPTS:
        md += ["## `%s`" % ptext, "",
               "| model | arm | n | preamble | title line | any em-dash | em-dash /100w | atoms | identical | distinct | top first word |",
               "|---|---|---|---|---|---|---|---|---|---|---|"]
        for m in models:
            for arm in arms_order:
                s = summarize(cells.get((m, pid, arm), []))
                if not s:
                    continue
                md.append("| %s | %s | %d | %s | %s | %s | %.2f | %s | %s | %d | %s |" % (
                    m, arm, s["n"], pct(s["preamble"], s["n"]), pct(s["title"], s["n"]),
                    pct(s["emdash_any"], s["n"]), s["emdash_per100w"], pct(s["atoms"], s["n"]),
                    pct(s["identical"], s["n"]), s["distinct"], s["top_first_word"]))
                flat.append(dict(model=m, prompt_id=pid, arm=arm, **s))
        if pid == "joke":
            for name, texts in read_hand().items():
                s = summarize(texts)
                md.append("| %s app (by hand) | hand | %d | %s | %s | %s | %.2f | %s | %s | %d | %s |" % (
                    name, s["n"], pct(s["preamble"], s["n"]), pct(s["title"], s["n"]),
                    pct(s["emdash_any"], s["n"]), s["emdash_per100w"], pct(s["atoms"], s["n"]),
                    pct(s["identical"], s["n"]), s["distinct"], s["top_first_word"]))
                flat.append(dict(model=name + "_app", prompt_id=pid, arm="hand", **s))
        md.append("")

    md += ["## Does the system prompt move anything? (bare vs each other arm)", "",
           "Fisher exact p, two-sided, uncorrected. With six models, three prompts and four"
           " features, expect a few small p-values by chance; look for patterns, not single cells.", "",
           "| model | prompt | vs arm | feature | bare | other | p |", "|---|---|---|---|---|---|---|"]
    feats = [("preamble", "preamble"), ("title", "title line"), ("emdash_any", "any em-dash"), ("atoms", "atoms")]
    for m in models:
        for pid, _ in PROMPTS:
            b = summarize(cells.get((m, pid, "bare"), []))
            for arm in ("chatapp", "published"):
                o = summarize(cells.get((m, pid, arm), []))
                if not b or not o:
                    continue
                for key, label in feats:
                    if key == "atoms" and pid != "joke":
                        continue
                    if b[key] == 0 and o[key] == 0:
                        continue
                    p = fisher_p(b[key], b["n"] - b[key], o[key], o["n"] - o[key])
                    md.append("| %s | %s | %s | %s | %s | %s | %.4f%s |" % (
                        m, pid, arm, label, pct(b[key], b["n"]), pct(o[key], o["n"]), p,
                        " *" if p < 0.01 else ""))
    md.append("")

    OUT.mkdir(exist_ok=True)
    (OUT / "summary.md").write_text("\n".join(md), encoding="utf-8")
    if flat:
        with (OUT / "summary.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(flat[0].keys()))
            w.writeheader()
            w.writerows(flat)
    print("\n".join(md))
    print("\nSaved: %s and summary.csv" % (OUT / "summary.md"))


def main():
    ap = argparse.ArgumentParser(description="Bare API vs chat-app conditions, quick run.")
    ap.add_argument("command", nargs="?", default="run", choices=["run", "score"])
    ap.add_argument("--n", type=int, default=20, help="calls per cell (default 20)")
    ap.add_argument("--max-usd", type=float, default=5.0, help="stop when the estimate hits this (default 5)")
    ap.add_argument("--workers", type=int, default=4, help="parallel calls (default 4)")
    ap.add_argument("--models", default="", help="comma-separated model ids to override the default six")
    ap.add_argument("--dry-run", action="store_true", help="fake responses, no keys, no spend")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if args.command == "run":
        run(args)
    score(args)


if __name__ == "__main__":
    main()
