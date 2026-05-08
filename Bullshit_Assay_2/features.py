"""
Per-poem feature extraction.

Every decision in this module is locked in `coding_heuristic.md`.
Any change here must be recorded in `deviations.md` with a date and a reason.

This module is deterministic and pure: given a poem string, it returns a dict
of features. No statistics, no aggregation, no model identity awareness.

External resources (auto-downloaded with cache on first use):
- spaCy `en_core_web_trf` model
- Brysbaert et al. 2014 concreteness norms (40k words)
- CMU pronouncing dict (via `pronouncing` package)
"""

from __future__ import annotations

import csv
import io
import os
import re
import sys
import urllib.request
import zipfile
from dataclasses import dataclass, asdict, field
from functools import lru_cache
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Constants — locked, do not change without a deviations.md entry
# ---------------------------------------------------------------------------

PRONOUNS_1S = {"i", "me", "my", "mine", "myself"}
PRONOUNS_1P = {"we", "us", "our", "ours", "ourselves"}
PRONOUNS_2 = {"you", "your", "yours", "yourself", "yourselves"}
PRONOUNS_3 = {
    "he", "she", "it", "they", "him", "her", "them",
    "his", "hers", "its", "their", "theirs",
    "himself", "herself", "itself", "themselves",
}

ALL_PRONOUNS = PRONOUNS_1S | PRONOUNS_1P | PRONOUNS_2 | PRONOUNS_3

CONCRETENESS_COVERAGE_FLAG_THRESHOLD = 0.30

# Brysbaert et al. 2014 supplementary materials.
# Source: https://link.springer.com/article/10.3758/s13428-013-0403-5
# The supplement is hosted as a zip containing an Excel file. We cache a
# CSV-converted version locally; first run downloads and converts it.
BRYSBAERT_URL = (
    "https://static-content.springer.com/esm/"
    "art%3A10.3758%2Fs13428-013-0403-5/MediaObjects/"
    "13428_2013_403_MOESM1_ESM.xlsx"
)
DATA_CACHE_DIR = Path.home() / ".cache" / "bullshit_assay_2"
BRYSBAERT_CACHE_PATH = DATA_CACHE_DIR / "brysbaert_concreteness.csv"

SPACY_MODEL = "en_core_web_trf"


# ---------------------------------------------------------------------------
# Lazy-loaded resources
# ---------------------------------------------------------------------------

_NLP = None
_BRYSBAERT: Optional[dict[str, float]] = None
_PRONOUNCING = None


def _ensure_cache_dir() -> None:
    DATA_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_nlp():
    """Load spaCy model, downloading if not present."""
    global _NLP
    if _NLP is not None:
        return _NLP
    try:
        import spacy
    except ImportError:
        sys.exit("spacy not installed. Run: pip install spacy")
    try:
        _NLP = spacy.load(SPACY_MODEL)
    except OSError:
        print(f"Downloading spaCy model {SPACY_MODEL}...", file=sys.stderr)
        from spacy.cli import download as spacy_download
        spacy_download(SPACY_MODEL)
        _NLP = spacy.load(SPACY_MODEL)
    return _NLP


def get_brysbaert() -> dict[str, float]:
    """Load Brysbaert concreteness norms, downloading + caching if not present."""
    global _BRYSBAERT
    if _BRYSBAERT is not None:
        return _BRYSBAERT
    _ensure_cache_dir()
    if not BRYSBAERT_CACHE_PATH.exists():
        _download_brysbaert()
    norms: dict[str, float] = {}
    with BRYSBAERT_CACHE_PATH.open("r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # header
        for row in reader:
            if len(row) < 2:
                continue
            word, rating = row[0], row[1]
            try:
                norms[word.strip().lower()] = float(rating)
            except ValueError:
                continue
    _BRYSBAERT = norms
    return _BRYSBAERT


def _download_brysbaert() -> None:
    """Fetch the Brysbaert supplementary xlsx and convert to CSV cache."""
    print(f"Downloading Brysbaert concreteness norms to {BRYSBAERT_CACHE_PATH}...",
          file=sys.stderr)
    try:
        import openpyxl
    except ImportError:
        sys.exit(
            "openpyxl required to read Brysbaert norms. Run: pip install openpyxl\n"
            "Or place a CSV at " + str(BRYSBAERT_CACHE_PATH) +
            " with header 'Word,Conc.M' and lowercase word lookups."
        )
    tmp_xlsx = BRYSBAERT_CACHE_PATH.with_suffix(".xlsx")
    urllib.request.urlretrieve(BRYSBAERT_URL, tmp_xlsx)
    wb = openpyxl.load_workbook(tmp_xlsx, read_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    # Find Word and Conc.M columns
    header = [str(c) if c is not None else "" for c in rows[0]]
    try:
        word_col = header.index("Word")
    except ValueError:
        word_col = 0
    try:
        conc_col = header.index("Conc.M")
    except ValueError:
        # The supplement uses "Conc.M" but be lenient
        conc_col = next(
            (i for i, h in enumerate(header) if "conc" in h.lower() and "m" in h.lower()),
            2,
        )
    with BRYSBAERT_CACHE_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Word", "Conc.M"])
        for row in rows[1:]:
            if not row or row[word_col] is None:
                continue
            writer.writerow([row[word_col], row[conc_col]])
    tmp_xlsx.unlink(missing_ok=True)


def get_pronouncing():
    """Lazy import of pronouncing library."""
    global _PRONOUNCING
    if _PRONOUNCING is not None:
        return _PRONOUNCING
    try:
        import pronouncing
    except ImportError:
        sys.exit("pronouncing not installed. Run: pip install pronouncing")
    _PRONOUNCING = pronouncing
    return _PRONOUNCING


# ---------------------------------------------------------------------------
# Preamble detection
# ---------------------------------------------------------------------------

def detect_preamble(response: str) -> tuple[Optional[str], str]:
    """
    Return (preamble, poem_body).

    Decision rule (locked in coding_heuristic.md):
    A poem has a preamble if the response contains at least one
    blank-line-separated block before any line that contains a verb,
    noun, or adjective per the spaCy tagger. The preamble is everything
    up to and including the first blank line. If no blank line separates
    the preamble from the poem, the response has no preamble (the whole
    thing is the poem).
    """
    if not response or not response.strip():
        return None, ""

    # Split on blank lines
    blocks = re.split(r"\n\s*\n", response, maxsplit=1)
    if len(blocks) < 2:
        return None, response

    first_block, rest = blocks
    # Check whether first block contains any noun/verb/adj per spaCy
    nlp = get_nlp()
    doc = nlp(first_block)
    has_content_word = any(t.pos_ in {"NOUN", "PROPN", "VERB", "AUX", "ADJ"} for t in doc)
    # If the first block is all conversational ("Sure!", "Here you go:") it
    # will typically still have a verb. The discriminating signal is whether
    # the *rest* exists at all and whether the first block reads like prose
    # framing. The locked rule above is permissive: if we got here via a
    # blank-line split, treat the first block as preamble unless it's already
    # poem-shaped.
    # Heuristic for "poem-shaped first block": multiple lines with line breaks.
    first_block_lines = [l for l in first_block.split("\n") if l.strip()]
    if len(first_block_lines) > 2 and has_content_word:
        # First block is itself multi-line and substantive — probably the poem
        return None, response
    return first_block.strip(), rest.lstrip("\n")


# ---------------------------------------------------------------------------
# Tokenization helpers
# ---------------------------------------------------------------------------

def split_lines(poem_body: str) -> list[str]:
    """Return non-empty lines, preserving order."""
    return [line for line in poem_body.split("\n") if line.strip()]


def split_stanzas(poem_body: str) -> list[list[str]]:
    """Split into stanzas (blocks separated by ≥1 blank line)."""
    raw_blocks = re.split(r"\n\s*\n", poem_body)
    stanzas = []
    for block in raw_blocks:
        lines = [l for l in block.split("\n") if l.strip()]
        if lines:
            stanzas.append(lines)
    return stanzas


WORD_RE = re.compile(r"\S+")


def words_in_line(line: str) -> list[str]:
    """Whitespace tokenization."""
    return WORD_RE.findall(line)


def strip_trailing_punct(word: str) -> str:
    return word.rstrip(".,;:!?\"')]}—–-")


def strip_all_punct_for_pronoun_match(word: str) -> str:
    """Strip leading and trailing punctuation for pronoun matching."""
    return word.strip(".,;:!?\"'()[]{}—–-").lower()


# ---------------------------------------------------------------------------
# Structural features
# ---------------------------------------------------------------------------

def structural_features(poem_body: str) -> dict:
    lines = split_lines(poem_body)
    stanzas = split_stanzas(poem_body)
    line_word_counts = [len(words_in_line(l)) for l in lines]
    all_words = [w for l in lines for w in words_in_line(l)]

    line_count = len(lines)
    stanza_count = len(stanzas)
    total_words = len(all_words)

    if line_word_counts:
        words_per_line_mean = sum(line_word_counts) / len(line_word_counts)
        if len(line_word_counts) > 1:
            mean = words_per_line_mean
            words_per_line_sd = (
                sum((c - mean) ** 2 for c in line_word_counts) / (len(line_word_counts) - 1)
            ) ** 0.5
        else:
            words_per_line_sd = 0.0
    else:
        words_per_line_mean = 0.0
        words_per_line_sd = 0.0

    if all_words:
        mean_word_length = sum(len(w) for w in all_words) / len(all_words)
    else:
        mean_word_length = 0.0

    return {
        "line_count": line_count,
        "stanza_count": stanza_count,
        "words_per_line_mean": words_per_line_mean,
        "words_per_line_sd": words_per_line_sd,
        "total_words": total_words,
        "mean_word_length": mean_word_length,
    }


# ---------------------------------------------------------------------------
# Compliance
# ---------------------------------------------------------------------------

def parse_length_cap(prompt_id: str) -> Optional[int]:
    """Extract N from prompt_id like 'poem_write_10' → 10."""
    match = re.search(r"_(\d+)$", prompt_id)
    return int(match.group(1)) if match else None


def compliance(line_count: int, length_cap: Optional[int]) -> Optional[bool]:
    if length_cap is None:
        return None
    return line_count < length_cap


# ---------------------------------------------------------------------------
# POS features
# ---------------------------------------------------------------------------

# spaCy tags considered "content tokens" for ratio denominators.
# Excludes punctuation (PUNCT), whitespace (SPACE), and symbols (SYM).
NON_CONTENT_POS = {"PUNCT", "SPACE", "SYM"}


def pos_features(poem_body: str) -> dict:
    nlp = get_nlp()
    doc = nlp(poem_body)
    content_tokens = [t for t in doc if t.pos_ not in NON_CONTENT_POS]
    if not content_tokens:
        return {
            "noun_ratio": 0.0,
            "verb_ratio": 0.0,
            "adj_ratio": 0.0,
            "adv_ratio": 0.0,
            "pronoun_ratio": 0.0,
            "content_token_count": 0,
        }
    n = len(content_tokens)
    counts = {"NOUN": 0, "PROPN": 0, "VERB": 0, "AUX": 0, "ADJ": 0, "ADV": 0, "PRON": 0}
    for t in content_tokens:
        if t.pos_ in counts:
            counts[t.pos_] += 1
    return {
        "noun_ratio": (counts["NOUN"] + counts["PROPN"]) / n,
        "verb_ratio": (counts["VERB"] + counts["AUX"]) / n,
        "adj_ratio": counts["ADJ"] / n,
        "adv_ratio": counts["ADV"] / n,
        "pronoun_ratio": counts["PRON"] / n,
        "content_token_count": n,
    }


# ---------------------------------------------------------------------------
# Person / voice
# ---------------------------------------------------------------------------

def person_features(poem_body: str) -> dict:
    counts = {"1s": 0, "1p": 0, "2": 0, "3": 0}
    for line in split_lines(poem_body):
        for raw_word in words_in_line(line):
            w = strip_all_punct_for_pronoun_match(raw_word)
            if w in PRONOUNS_1S:
                counts["1s"] += 1
            elif w in PRONOUNS_1P:
                counts["1p"] += 1
            elif w in PRONOUNS_2:
                counts["2"] += 1
            elif w in PRONOUNS_3:
                counts["3"] += 1

    total = sum(counts.values())
    if total == 0:
        person = "impersonal"
    else:
        # Locked precedence: 1s > 1p > 2 > 3 for tie-breaks
        precedence = ["1s", "1p", "2", "3"]
        max_count = max(counts.values())
        # Top categories in precedence order
        top = [k for k in precedence if counts[k] == max_count]
        winner = top[0]
        # Locked rule: mixed if largest category has ≤ 50% of total
        if max_count / total <= 0.5:
            person = "mixed"
        else:
            person = {
                "1s": "1st_singular",
                "1p": "1st_plural",
                "2": "2nd",
                "3": "3rd",
            }[winner]

    return {
        "person": person,
        "pronoun_count_1s": counts["1s"],
        "pronoun_count_1p": counts["1p"],
        "pronoun_count_2": counts["2"],
        "pronoun_count_3": counts["3"],
    }


# ---------------------------------------------------------------------------
# Concreteness
# ---------------------------------------------------------------------------

def concreteness_features(poem_body: str) -> dict:
    """
    Mean Brysbaert concreteness across content words present in the lexicon.

    Locked decisions:
    - Exact match, lowercased, no lemmatization.
    - Words not in lexicon are excluded from the mean (not zeroed, not missing).
    - Coverage = fraction of content words that hit the lexicon.
    - Coverage < 0.30 sets concreteness_low_coverage_flag = True.
    """
    norms = get_brysbaert()
    nlp = get_nlp()
    doc = nlp(poem_body)
    content_tokens = [t for t in doc if t.pos_ not in NON_CONTENT_POS]
    if not content_tokens:
        return {
            "concreteness_mean": None,
            "concreteness_coverage": 0.0,
            "concreteness_low_coverage_flag": True,
            "concreteness_words_matched": 0,
            "concreteness_words_total": 0,
        }
    matched_ratings = []
    for t in content_tokens:
        word = t.text.lower()
        if word in norms:
            matched_ratings.append(norms[word])
    coverage = len(matched_ratings) / len(content_tokens)
    mean = sum(matched_ratings) / len(matched_ratings) if matched_ratings else None
    return {
        "concreteness_mean": mean,
        "concreteness_coverage": coverage,
        "concreteness_low_coverage_flag": coverage < CONCRETENESS_COVERAGE_FLAG_THRESHOLD,
        "concreteness_words_matched": len(matched_ratings),
        "concreteness_words_total": len(content_tokens),
    }


# ---------------------------------------------------------------------------
# Rhyme
# ---------------------------------------------------------------------------

def line_terminal_rhyme_part(line: str) -> Optional[str]:
    """
    Return CMU rhyming-part for the last word of the line, or None if the
    word isn't in CMU dict. Locked rule: no guessing.
    """
    pronouncing = get_pronouncing()
    words = words_in_line(line)
    if not words:
        return None
    last = strip_trailing_punct(words[-1]).lower()
    last = re.sub(r"[^a-z'-]", "", last)
    if not last:
        return None
    phones = pronouncing.phones_for_word(last)
    if not phones:
        return None
    return pronouncing.rhyming_part(phones[0])


def rhyme_features(poem_body: str) -> dict:
    lines = split_lines(poem_body)
    if not lines:
        return {
            "rhyme_participation_rate": 0.0,
            "rhyme_scheme": "",
            "rhyme_scheme_known_only": "",
            "rhyme_lines_unknown": 0,
            "rhyme_lines_total": 0,
        }

    # Per-line rhyming parts
    parts: list[Optional[str]] = [line_terminal_rhyme_part(l) for l in lines]

    # Build scheme labels
    label_for_part: dict[str, str] = {}
    next_label_idx = 0
    scheme_chars: list[str] = []
    known_chars: list[str] = []
    for part in parts:
        if part is None:
            scheme_chars.append("?")
        else:
            if part not in label_for_part:
                label_for_part[part] = chr(ord("A") + next_label_idx) if next_label_idx < 26 else f"[{next_label_idx}]"
                next_label_idx += 1
            scheme_chars.append(label_for_part[part])

    # known_only scheme: re-letter using only the known-part lines
    known_label_for_part: dict[str, str] = {}
    next_known_idx = 0
    for part in parts:
        if part is None:
            continue
        if part not in known_label_for_part:
            known_label_for_part[part] = chr(ord("A") + next_known_idx) if next_known_idx < 26 else f"[{next_known_idx}]"
            next_known_idx += 1
        known_chars.append(known_label_for_part[part])

    # Participation rate: fraction of lines whose terminal rhyming-part appears in another line
    part_counts: dict[str, int] = {}
    for p in parts:
        if p is not None:
            part_counts[p] = part_counts.get(p, 0) + 1
    participating = 0
    countable = 0
    for p in parts:
        if p is None:
            continue
        countable += 1
        if part_counts[p] >= 2:
            participating += 1
    participation_rate = (participating / countable) if countable > 0 else 0.0

    return {
        "rhyme_participation_rate": participation_rate,
        "rhyme_scheme": "".join(scheme_chars),
        "rhyme_scheme_known_only": "".join(known_chars),
        "rhyme_lines_unknown": sum(1 for p in parts if p is None),
        "rhyme_lines_total": len(parts),
    }


# ---------------------------------------------------------------------------
# Top-level entry
# ---------------------------------------------------------------------------

@dataclass
class PoemFeatures:
    run_id: str
    model: str
    prompt_id: str
    iteration: int
    has_preamble: bool
    preamble_text: Optional[str]
    poem_body: str
    length_cap: Optional[int]
    compliant: Optional[bool]
    structural: dict = field(default_factory=dict)
    pos: dict = field(default_factory=dict)
    person: dict = field(default_factory=dict)
    concreteness: dict = field(default_factory=dict)
    rhyme: dict = field(default_factory=dict)


def extract_features(record: dict) -> PoemFeatures:
    """
    Extract all per-poem features from a single results.jsonl record.
    """
    response = record.get("response") or ""
    preamble, body = detect_preamble(response)
    structural = structural_features(body)
    cap = parse_length_cap(record["prompt_id"])
    compl = compliance(structural["line_count"], cap)
    return PoemFeatures(
        run_id=record["run_id"],
        model=record["model"],
        prompt_id=record["prompt_id"],
        iteration=record["iteration"],
        has_preamble=preamble is not None,
        preamble_text=preamble,
        poem_body=body,
        length_cap=cap,
        compliant=compl,
        structural=structural,
        pos=pos_features(body),
        person=person_features(body),
        concreteness=concreteness_features(body),
        rhyme=rhyme_features(body),
    )


def features_to_flat_dict(pf: PoemFeatures) -> dict:
    """Flatten to a single-level dict for CSV/dataframe consumption."""
    out = {
        "run_id": pf.run_id,
        "model": pf.model,
        "prompt_id": pf.prompt_id,
        "iteration": pf.iteration,
        "length_cap": pf.length_cap,
        "compliant": pf.compliant,
        "has_preamble": pf.has_preamble,
        "poem_body": pf.poem_body,
        "preamble_text": pf.preamble_text,
    }
    for prefix, group in [
        ("", pf.structural),
        ("pos_", pf.pos),
        ("", pf.person),
        ("", pf.concreteness),
        ("", pf.rhyme),
    ]:
        for k, v in group.items():
            out[prefix + k] = v
    return out
