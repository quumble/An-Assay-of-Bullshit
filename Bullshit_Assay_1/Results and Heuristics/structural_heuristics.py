#!/usr/bin/env python3
"""
structural_heuristics.py

Blind, deterministic structural-and-stylistic coder for the model-comparison JSONL.

Companion to (not replacement for) semantic_heuristics.py. Where that script codes
*what a response is about* (setting, mood, plot arc, imagery), this one codes
*how it is built* (punctuation, sentence rhythm, paragraph structure, repetition,
hedging, openings and endings). The two coders are intentionally different in
approach so agreement between them is more informative than either alone.

Design goals:
- Deterministic. Every code is a deterministic function of the response text.
- Auditable. No latent judgments hidden behind opaque scoring; lists and rules
  are visible at the top of the file.
- Blind. Model identities are masked with a seeded random map; the unblinding
  key is written to a file marked PRIVATE.
- Cross-check friendly. Recomputes word_count and sentence_count_alt with a
  different sentence splitter than semantic_heuristics.py, so disagreements
  between the two flag ambiguous cases rather than being silently averaged.

A note on bias:
The author of this script is `claude-opus-4-7`, which is one of the subjects
of the experiment. Structural/typographic features were chosen partly because
they are less vulnerable to my own priors than semantic-content features
would be, but they are not bias-free. Em-dash and smart-quote usage are
themselves model tells; choosing to measure them is itself a choice. Read
findings accordingly, especially any finding that flatters or disfavors the
author's own model family.

Example:
    python structural_heuristics.py results.jsonl \\
        --outdir analysis_structural \\
        --seed 20260507

Outputs:
    analysis_structural/coded_outputs.csv
    analysis_structural/summary_by_blind_model.csv
    analysis_structural/summary_by_blind_model_prompt.csv
    analysis_structural/cross_coder_join.csv  (only if --semantic-csv supplied)
    analysis_structural/blind_model_map_PRIVATE.json
    analysis_structural/manifest.json
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median, stdev
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# Lexicons and patterns
# Kept short and visible. These are weak signals, not ground truth.
# ---------------------------------------------------------------------------

HEDGES: Tuple[str, ...] = (
    "perhaps", "maybe", "might", "almost", "nearly", "seemed", "seems",
    "appeared", "as if", "as though", "kind of", "sort of", "somehow",
    "somewhat", "possibly", "probably",
)

INTENSIFIERS: Tuple[str, ...] = (
    "very", "really", "truly", "deeply", "utterly", "absolutely",
    "completely", "incredibly", "extraordinarily", "profoundly",
)

META_FRAMING: Tuple[str, ...] = (
    "here is", "here's", "title:", "story:", "poem:", "sure!", "sure,",
    "certainly!", "certainly,", "of course!", "absolutely!",
)

# Words used to open dramatic / flourish endings. Not a mood code; just
# checking whether the final sentence is doing a "twist" gesture.
ENDING_PIVOTS: Tuple[str, ...] = (
    "but", "yet", "still", "and yet", "however", "instead", "though",
    "until", "only", "except", "then", "finally",
)

# Sentence-initial repetition markers worth flagging when they cluster.
ANAPHORA_CANDIDATES: Tuple[str, ...] = (
    "i", "you", "we", "they", "she", "he", "it",
    "the", "and", "but", "in", "when", "where", "if",
)


# ---------------------------------------------------------------------------
# Core regex
# ---------------------------------------------------------------------------

WORD_RE = re.compile(r"\b[a-zA-Z][a-zA-Z'\u2019-]*\b")

# Sentence splitter: splits on terminal punctuation followed by whitespace,
# but tries to avoid splitting on common abbreviations. Deliberately different
# from semantic_heuristics.py's splitter so disagreements between the two
# flag ambiguous cases.
ABBREV = (
    "mr", "mrs", "ms", "dr", "st", "jr", "sr", "vs", "etc",
    "e.g", "i.e", "u.s", "u.k", "p.s",
)

def _split_sentences(text: str) -> List[str]:
    """Conservative sentence splitter aware of common abbreviations."""
    if not text:
        return []
    # Replace abbreviation-final periods with a placeholder so we don't split.
    placeholder = "\u0001"
    masked = text
    for abbr in ABBREV:
        masked = re.sub(
            rf"\b({re.escape(abbr)})\.",
            lambda m: m.group(1) + placeholder,
            masked,
            flags=re.IGNORECASE,
        )
    # Split on terminal . ! ? followed by whitespace and a capital/quote/dash.
    parts = re.split(r"(?<=[.!?])[\"'\u201d\u2019)]*\s+(?=[A-Z\"'\u201c\u2018(\-\u2014])", masked)
    # Final segment is also a sentence if it has terminal punctuation or content.
    out = []
    for p in parts:
        p = p.replace(placeholder, ".").strip()
        if p:
            out.append(p)
    return out


# ---------------------------------------------------------------------------
# Basic helpers
# ---------------------------------------------------------------------------

def clean_text(text: Optional[str]) -> str:
    if not text:
        return ""
    return text.replace("\r\n", "\n").replace("\r", "\n").strip()


def tokenize(text: str) -> List[str]:
    return [m.group(0).lower().replace("\u2019", "'") for m in WORD_RE.finditer(text)]


def nonempty_lines(text: str) -> List[str]:
    return [ln.strip() for ln in clean_text(text).split("\n") if ln.strip()]


def paragraph_blocks(text: str) -> List[str]:
    text = clean_text(text)
    if not text:
        return []
    return [p.strip() for p in re.split(r"\n\s*\n+", text) if p.strip()]


def stable_output_id(record: Dict[str, Any]) -> str:
    raw = "|".join(
        str(record.get(k, ""))
        for k in ["provider", "model", "prompt_id", "iteration", "timestamp"]
    )
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]


def build_blind_map(models: Sequence[str], seed: int) -> Dict[str, str]:
    """Independent blinding from semantic_heuristics.py.

    Uses different label prefix ('M1', 'M2', ...) so the two coders' blind
    labels do not accidentally collide if their CSVs are joined.
    """
    shuffled = list(sorted(set(models)))
    rng = random.Random(seed)
    rng.shuffle(shuffled)
    return {model: f"M{i+1}" for i, model in enumerate(shuffled)}


# ---------------------------------------------------------------------------
# Prompt parsing (kept consistent with semantic_heuristics.py)
# ---------------------------------------------------------------------------

def infer_prompt_category(prompt_id: str, prompt_text: str) -> str:
    s = f"{prompt_id} {prompt_text}".lower()
    if "poem" in s:
        return "poem"
    if "animal" in s:
        return "animal"
    if "story" in s:
        return "story"
    return "unknown"


def infer_length_condition(prompt_id: str, prompt_text: str) -> str:
    s = f"{prompt_id} {prompt_text}".lower()
    if "lt5" in s or "fewer than 5" in s or "fewer then 5" in s or "less than 5" in s:
        return "lt5"
    if "lt10" in s or "fewer than 10" in s or "fewer then 10" in s or "less than 10" in s:
        return "lt10"
    return "open"


# ---------------------------------------------------------------------------
# Structural and stylistic features
# ---------------------------------------------------------------------------

def punctuation_features(text: str) -> Dict[str, Any]:
    """Counts and ratios of typographic features that often differ across models."""
    if not text:
        return {
            "em_dash_count": 0, "en_dash_count": 0, "hyphen_count": 0,
            "ellipsis_count": 0, "semicolon_count": 0, "colon_count": 0,
            "comma_count": 0, "exclaim_count": 0, "question_count": 0,
            "parenthetical_count": 0,
            "smart_quote_double_count": 0, "straight_quote_double_count": 0,
            "smart_quote_single_count": 0, "straight_quote_single_count": 0,
            "smart_quote_share": 0.0,
        }

    em = text.count("\u2014")
    en = text.count("\u2013")
    # Hyphens between word chars only, to exclude em-dash-as-double-hyphen.
    hyphen = len(re.findall(r"(?<=\w)-(?=\w)", text))
    ellipsis = text.count("\u2026") + len(re.findall(r"\.\.\.+", text))
    semicolon = text.count(";")
    colon = text.count(":")
    comma = text.count(",")
    exclaim = text.count("!")
    question = text.count("?")
    paren = len(re.findall(r"\([^)]*\)", text))

    sd = text.count("\u201c") + text.count("\u201d")
    pd = text.count('"')
    ss = text.count("\u2018") + text.count("\u2019")
    ps = text.count("'")
    quote_total = sd + pd + ss + ps
    smart_share = (sd + ss) / quote_total if quote_total else 0.0

    return {
        "em_dash_count": em,
        "en_dash_count": en,
        "hyphen_count": hyphen,
        "ellipsis_count": ellipsis,
        "semicolon_count": semicolon,
        "colon_count": colon,
        "comma_count": comma,
        "exclaim_count": exclaim,
        "question_count": question,
        "parenthetical_count": paren,
        "smart_quote_double_count": sd,
        "straight_quote_double_count": pd,
        "smart_quote_single_count": ss,
        "straight_quote_single_count": ps,
        "smart_quote_share": round(smart_share, 4),
    }


def sentence_rhythm(sentences: Sequence[str]) -> Dict[str, Any]:
    """Sentence-length distribution features."""
    lengths = [len(tokenize(s)) for s in sentences if tokenize(s)]
    if not lengths:
        return {
            "sentence_count_alt": 0,
            "sent_len_mean": 0.0, "sent_len_median": 0.0, "sent_len_max": 0,
            "sent_len_std": 0.0,
            "very_short_sentence_share": 0.0,
            "very_long_sentence_share": 0.0,
            "first_sentence_len": 0, "last_sentence_len": 0,
            "closer_is_longest": False,
            "closer_is_shortest": False,
        }

    n = len(lengths)
    very_short = sum(1 for x in lengths if x < 5)
    very_long = sum(1 for x in lengths if x > 25)
    return {
        "sentence_count_alt": n,
        "sent_len_mean": round(mean(lengths), 4),
        "sent_len_median": round(median(lengths), 4),
        "sent_len_max": max(lengths),
        "sent_len_std": round(stdev(lengths), 4) if n >= 2 else 0.0,
        "very_short_sentence_share": round(very_short / n, 4),
        "very_long_sentence_share": round(very_long / n, 4),
        "first_sentence_len": lengths[0],
        "last_sentence_len": lengths[-1],
        "closer_is_longest": lengths[-1] == max(lengths) and n >= 2,
        "closer_is_shortest": lengths[-1] == min(lengths) and n >= 2,
    }


def paragraph_features(text: str) -> Dict[str, Any]:
    paras = paragraph_blocks(text)
    lines = nonempty_lines(text)
    return {
        "paragraph_count": len(paras),
        "is_single_block": len(paras) == 1,
        "line_count_nonempty_alt": len(lines),
        "blank_line_separated": "\n\n" in text,
    }


def title_or_preamble_flag(text: str) -> Dict[str, Any]:
    """Detect title lines, 'Title:' headers, or polite preambles before the work."""
    lines = nonempty_lines(text)
    if not lines:
        return {
            "has_title_line": False,
            "has_meta_preamble": False,
            "preamble_text": "",
        }
    first = lines[0].strip()
    text_lower = text.lower().lstrip()

    # Title heuristic: short first line (<=10 words), no terminal punctuation,
    # and either followed by a blank line or written in title case.
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
    preamble_text = first if (has_title_line or has_preamble) else ""

    return {
        "has_title_line": has_title_line,
        "has_meta_preamble": has_preamble,
        "preamble_text": preamble_text[:120],
    }


def repetition_features(sentences: Sequence[str], lines: Sequence[str]) -> Dict[str, Any]:
    """Anaphora at sentence and line level, plus repeated bigrams."""
    def _initial_word(seg: str) -> str:
        toks = tokenize(seg)
        return toks[0] if toks else ""

    sent_initials = [_initial_word(s) for s in sentences if _initial_word(s)]
    line_initials = [_initial_word(ln) for ln in lines if _initial_word(ln)]

    sent_initial_counter = Counter(sent_initials)
    line_initial_counter = Counter(line_initials)

    # Top repeated initial across sentences (any word, not just from list).
    if sent_initial_counter:
        top_word, top_n = sent_initial_counter.most_common(1)[0]
    else:
        top_word, top_n = "", 0
    if line_initial_counter:
        line_top_word, line_top_n = line_initial_counter.most_common(1)[0]
    else:
        line_top_word, line_top_n = "", 0

    # Anaphora score: max repetitions of any candidate-list initial across sentences.
    anaphora_max = 0
    anaphora_word = ""
    for w in ANAPHORA_CANDIDATES:
        c = sent_initial_counter.get(w, 0)
        if c > anaphora_max:
            anaphora_max = c
            anaphora_word = w

    # Repeated bigrams in body text.
    all_tokens = []
    for s in sentences:
        all_tokens.extend(tokenize(s))
    bigrams = [
        (all_tokens[i], all_tokens[i + 1])
        for i in range(len(all_tokens) - 1)
    ]
    bigram_counter = Counter(bigrams)
    repeated_bigrams = sum(1 for _, c in bigram_counter.items() if c >= 2)

    return {
        "sentence_initial_top_word": top_word,
        "sentence_initial_top_count": top_n,
        "line_initial_top_word": line_top_word,
        "line_initial_top_count": line_top_n,
        "anaphora_max_repeats": anaphora_max,
        "anaphora_word": anaphora_word,
        "repeated_bigram_types": repeated_bigrams,
    }


def hedge_and_intensifier_counts(tokens: Sequence[str], text_lower: str) -> Dict[str, Any]:
    def _count(items: Iterable[str]) -> int:
        c = Counter(tokens)
        total = 0
        for item in items:
            if " " in item:
                total += text_lower.count(item)
            else:
                total += c.get(item, 0)
        return total

    return {
        "hedge_count": _count(HEDGES),
        "intensifier_count": _count(INTENSIFIERS),
        "ending_pivot_present": any(
            f" {p} " in text_lower or text_lower.startswith(f"{p} ")
            for p in ENDING_PIVOTS
        ),
    }


def closing_features(sentences: Sequence[str]) -> Dict[str, Any]:
    """Properties of the final sentence."""
    if not sentences:
        return {
            "closer_starts_with_pivot": False,
            "closer_ends_with_ellipsis": False,
            "closer_ends_with_question": False,
            "closer_ends_with_exclaim": False,
        }
    last = sentences[-1].strip()
    last_lower = last.lower()
    starts_pivot = any(
        last_lower.startswith(p + " ") or last_lower.startswith(p + ",")
        for p in ENDING_PIVOTS
    )
    return {
        "closer_starts_with_pivot": starts_pivot,
        "closer_ends_with_ellipsis": last.endswith("\u2026") or last.endswith("..."),
        "closer_ends_with_question": last.endswith("?"),
        "closer_ends_with_exclaim": last.endswith("!"),
    }


# ---------------------------------------------------------------------------
# Coding
# ---------------------------------------------------------------------------

def code_record(record: Dict[str, Any], blind_label: str) -> Dict[str, Any]:
    response = clean_text(record.get("response"))
    text_lower = response.lower()
    tokens = tokenize(response)
    sentences = _split_sentences(response)
    lines = nonempty_lines(response)

    prompt_id = str(record.get("prompt_id", ""))
    prompt_text = str(record.get("prompt_text", ""))
    prompt_category = infer_prompt_category(prompt_id, prompt_text)
    length_condition = infer_length_condition(prompt_id, prompt_text)

    output_tokens = record.get("output_tokens")
    try:
        output_tokens_i = int(output_tokens) if output_tokens is not None else None
    except (TypeError, ValueError):
        output_tokens_i = None

    # Compliance using the alt sentence splitter.
    sent_count_alt = len(sentences)
    if length_condition == "lt5":
        compliance_alt = "yes" if sent_count_alt < 5 else "no"
    elif length_condition == "lt10":
        compliance_alt = "yes" if sent_count_alt < 10 else "no"
    else:
        compliance_alt = "not_applicable"

    row: Dict[str, Any] = {
        "output_id": stable_output_id(record),
        "blind_model": blind_label,
        "provider_hidden": "hidden",
        "model_hidden": "hidden",
        "prompt_id": prompt_id,
        "prompt_category": prompt_category,
        "length_condition": length_condition,
        "iteration": record.get("iteration"),
        "timestamp": record.get("timestamp"),
        "is_success": bool(record.get("error") is None and response),
        "is_empty_response": not bool(response),
        "is_truncated_400ish": bool(output_tokens_i is not None and output_tokens_i >= 400),
        "char_count": len(response),
        "word_count": len(tokens),
        "constraint_compliant_alt": compliance_alt,
        "response": response,
    }

    row.update(punctuation_features(response))
    row.update(sentence_rhythm(sentences))
    row.update(paragraph_features(response))
    row.update(title_or_preamble_flag(response))
    row.update(repetition_features(sentences, lines))
    row.update(hedge_and_intensifier_counts(tokens, text_lower))
    row.update(closing_features(sentences))

    return row


# ---------------------------------------------------------------------------
# Dataset I/O
# ---------------------------------------------------------------------------

def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON on line {line_no}: {e}") from e
    return records


def freeze_first_successes(
    records: Sequence[Dict[str, Any]], n_per_cell: int
) -> List[Dict[str, Any]]:
    """First n successful records per (model, prompt_id), ordered by timestamp.

    Mirrors the prereg's frozen-dataset rule and matches semantic_heuristics.py
    so the two coders operate on the same rows.
    """
    successes = [
        r for r in records
        if r.get("error") is None and clean_text(r.get("response"))
    ]
    successes.sort(key=lambda r: str(r.get("timestamp", "")))
    buckets: Dict[Tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)
    for r in successes:
        key = (str(r.get("model", "")), str(r.get("prompt_id", "")))
        if len(buckets[key]) < n_per_cell:
            buckets[key].append(r)
    frozen: List[Dict[str, Any]] = []
    for key in sorted(buckets):
        frozen.extend(buckets[key])
    frozen.sort(
        key=lambda r: (
            str(r.get("model", "")),
            str(r.get("prompt_id", "")),
            str(r.get("timestamp", "")),
        )
    )
    return frozen


def write_csv(path: Path, rows: Sequence[Dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    priority = [
        "output_id", "blind_model", "prompt_id", "prompt_category",
        "length_condition", "iteration", "timestamp",
        "is_success", "is_empty_response", "is_truncated_400ish",
        "char_count", "word_count",
        "sentence_count_alt", "constraint_compliant_alt",
        "sent_len_mean", "sent_len_median", "sent_len_std", "sent_len_max",
        "first_sentence_len", "last_sentence_len",
        "closer_is_longest", "closer_is_shortest",
        "very_short_sentence_share", "very_long_sentence_share",
        "paragraph_count", "is_single_block", "line_count_nonempty_alt",
        "has_title_line", "has_meta_preamble", "preamble_text",
        "em_dash_count", "ellipsis_count", "semicolon_count", "colon_count",
        "smart_quote_share",
        "anaphora_max_repeats", "anaphora_word",
        "sentence_initial_top_word", "sentence_initial_top_count",
        "line_initial_top_word", "line_initial_top_count",
        "repeated_bigram_types",
        "hedge_count", "intensifier_count",
        "closer_starts_with_pivot", "closer_ends_with_ellipsis",
        "closer_ends_with_question", "closer_ends_with_exclaim",
        "ending_pivot_present",
        "response",
    ]
    all_fields = set().union(*(r.keys() for r in rows))
    fields = [f for f in priority if f in all_fields] + sorted(all_fields - set(priority))
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


# ---------------------------------------------------------------------------
# Group summaries
# ---------------------------------------------------------------------------

NUMERIC_SUMMARY_FIELDS = (
    "word_count", "sentence_count_alt", "sent_len_mean", "sent_len_median",
    "sent_len_std", "sent_len_max",
    "first_sentence_len", "last_sentence_len",
    "very_short_sentence_share", "very_long_sentence_share",
    "paragraph_count", "line_count_nonempty_alt",
    "em_dash_count", "ellipsis_count", "semicolon_count", "colon_count",
    "smart_quote_share",
    "anaphora_max_repeats", "repeated_bigram_types",
    "hedge_count", "intensifier_count",
)

CATEGORICAL_SUMMARY_FIELDS = (
    "constraint_compliant_alt", "has_title_line", "has_meta_preamble",
    "is_single_block", "closer_is_longest", "closer_is_shortest",
    "closer_starts_with_pivot", "closer_ends_with_ellipsis",
    "closer_ends_with_question", "closer_ends_with_exclaim",
    "ending_pivot_present", "is_truncated_400ish",
    "sentence_initial_top_word", "anaphora_word",
)


def summarize_group(
    rows: Sequence[Dict[str, Any]], group_fields: Sequence[str]
) -> List[Dict[str, Any]]:
    groups: Dict[Tuple[str, ...], List[Dict[str, Any]]] = defaultdict(list)
    for r in rows:
        key = tuple(str(r.get(f, "")) for f in group_fields)
        groups[key].append(r)

    out_rows: List[Dict[str, Any]] = []
    for key, group in sorted(groups.items()):
        out: Dict[str, Any] = dict(zip(group_fields, key))
        out["n"] = len(group)

        for field in NUMERIC_SUMMARY_FIELDS:
            vals = []
            for r in group:
                v = r.get(field)
                if v in (None, ""):
                    continue
                try:
                    vals.append(float(v))
                except (TypeError, ValueError):
                    pass
            if vals:
                out[f"{field}_mean"] = round(mean(vals), 4)
                out[f"{field}_median"] = round(median(vals), 4)

        for field in CATEGORICAL_SUMMARY_FIELDS:
            c = Counter(str(r.get(field, "")) for r in group)
            if c:
                top, top_n = c.most_common(1)[0]
                out[f"{field}_top"] = top
                out[f"{field}_top_share"] = round(top_n / len(group), 4)

        out_rows.append(out)
    return out_rows


# ---------------------------------------------------------------------------
# Cross-coder join with semantic_heuristics output
# ---------------------------------------------------------------------------

def cross_coder_join(
    structural_rows: Sequence[Dict[str, Any]],
    semantic_csv: Path,
) -> List[Dict[str, Any]]:
    """Join on output_id and flag where the two coders disagree on basic counts.

    output_id is a hash of (provider, model, prompt_id, iteration, timestamp),
    so it joins exactly across coders even though the blind labels differ.
    """
    semantic_rows: Dict[str, Dict[str, Any]] = {}
    with semantic_csv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            semantic_rows[row["output_id"]] = row

    joined: List[Dict[str, Any]] = []
    for s in structural_rows:
        sem = semantic_rows.get(s["output_id"])
        if not sem:
            continue

        def _to_int(x: Any) -> Optional[int]:
            try:
                return int(float(x))
            except (TypeError, ValueError):
                return None

        sem_word_count = _to_int(sem.get("word_count"))
        struct_word_count = _to_int(s.get("word_count"))
        sem_sent_count = _to_int(sem.get("sentence_count_heuristic"))
        struct_sent_count = _to_int(s.get("sentence_count_alt"))

        word_disagreement = (
            sem_word_count is not None
            and struct_word_count is not None
            and sem_word_count != struct_word_count
        )
        sent_disagreement = (
            sem_sent_count is not None
            and struct_sent_count is not None
            and sem_sent_count != struct_sent_count
        )

        sem_compliance = sem.get("constraint_compliant_heuristic", "")
        struct_compliance = s.get("constraint_compliant_alt", "")
        compliance_disagreement = (
            sem_compliance not in ("", "not_applicable")
            and struct_compliance not in ("", "not_applicable")
            and sem_compliance != struct_compliance
        )

        joined.append({
            "output_id": s["output_id"],
            "blind_model_structural": s["blind_model"],
            "blind_model_semantic": sem.get("blind_model", ""),
            "prompt_id": s["prompt_id"],
            "prompt_category": s["prompt_category"],
            "length_condition": s["length_condition"],
            "word_count_structural": struct_word_count,
            "word_count_semantic": sem_word_count,
            "word_count_disagree": word_disagreement,
            "sentence_count_structural": struct_sent_count,
            "sentence_count_semantic": sem_sent_count,
            "sentence_count_disagree": sent_disagreement,
            "compliance_structural": struct_compliance,
            "compliance_semantic": sem_compliance,
            "compliance_disagree": compliance_disagreement,
        })
    return joined


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Blind structural/stylistic heuristic coder for results.jsonl"
    )
    p.add_argument("jsonl", type=Path, help="Path to results.jsonl")
    p.add_argument("--outdir", type=Path, default=Path("analysis_structural"))
    p.add_argument(
        "--seed", type=int, default=20260507,
        help="Seed for blind model labels. Independent of semantic coder's seed.",
    )
    p.add_argument(
        "--n-per-cell", type=int, default=10,
        help="First successful records per (model, prompt_id). Set 0 for all.",
    )
    p.add_argument(
        "--no-freeze", action="store_true",
        help="Code all successful records instead of first n per cell.",
    )
    p.add_argument(
        "--semantic-csv", type=Path, default=None,
        help="Optional path to coded_outputs.csv from semantic_heuristics.py "
             "for cross-coder join and disagreement flagging.",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)

    records = read_jsonl(args.jsonl)
    success_records = [
        r for r in records
        if r.get("error") is None and clean_text(r.get("response"))
    ]
    model_names = sorted({str(r.get("model", "")) for r in success_records})
    blind_map = build_blind_map(model_names, args.seed)

    if args.no_freeze:
        analysis_records = success_records
    else:
        analysis_records = freeze_first_successes(records, n_per_cell=args.n_per_cell)

    coded_rows = [
        code_record(r, blind_map[str(r.get("model", ""))])
        for r in analysis_records
    ]

    write_csv(args.outdir / "coded_outputs.csv", coded_rows)
    write_csv(
        args.outdir / "summary_by_blind_model.csv",
        summarize_group(coded_rows, ["blind_model"]),
    )
    write_csv(
        args.outdir / "summary_by_blind_model_prompt.csv",
        summarize_group(
            coded_rows,
            ["blind_model", "prompt_category", "length_condition"],
        ),
    )

    if args.semantic_csv:
        joined = cross_coder_join(coded_rows, args.semantic_csv)
        write_csv(args.outdir / "cross_coder_join.csv", joined)
        n_disagree_word = sum(1 for j in joined if j["word_count_disagree"])
        n_disagree_sent = sum(1 for j in joined if j["sentence_count_disagree"])
        n_disagree_comp = sum(1 for j in joined if j["compliance_disagree"])
    else:
        joined = []
        n_disagree_word = n_disagree_sent = n_disagree_comp = -1

    private_map = {
        "seed": args.seed,
        "warning": "PRIVATE: reveals blind model labels. Do not inspect "
                   "before any blind qualitative coding is complete.",
        "blind_map_model_to_label": blind_map,
        "blind_map_label_to_model": {v: k for k, v in blind_map.items()},
    }
    with (args.outdir / "blind_model_map_PRIVATE.json").open(
        "w", encoding="utf-8"
    ) as f:
        json.dump(private_map, f, indent=2, ensure_ascii=False)

    manifest = {
        "input_jsonl": str(args.jsonl),
        "outdir": str(args.outdir),
        "seed": args.seed,
        "records_in_jsonl": len(records),
        "successful_records_in_jsonl": len(success_records),
        "records_coded": len(coded_rows),
        "models_detected": len(model_names),
        "freeze_first_successes_per_cell": None if args.no_freeze else args.n_per_cell,
        "semantic_csv_joined": str(args.semantic_csv) if args.semantic_csv else None,
        "cross_coder_disagreements": {
            "word_count": n_disagree_word,
            "sentence_count": n_disagree_sent,
            "compliance": n_disagree_comp,
        },
        "author_disclosure": (
            "This script was authored by claude-opus-4-7, which is one of the "
            "subjects of the experiment. Structural features were chosen partly "
            "because they are less vulnerable to author bias than semantic "
            "content features, but they are not bias-free. Read findings "
            "accordingly, especially any finding involving Claude models."
        ),
        "notes": [
            "Heuristic labels are provisional weak signals.",
            "Model names are hidden in coded_outputs.csv and summaries.",
            "Do not inspect blind_model_map_PRIVATE.json until any blind "
            "qualitative coding is complete.",
            "This coder uses an independent blind map from "
            "semantic_heuristics.py; output_id (a hash of "
            "provider/model/prompt_id/iteration/timestamp) is the join key "
            "across coders.",
        ],
    }
    with (args.outdir / "manifest.json").open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
