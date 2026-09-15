#!/usr/bin/env python3
"""Core parsing and feature extraction for the September 2026 harmonized analysis.

This module intentionally contains no outcome analysis. It implements the locked
HARMONIZED_CODING_SPEC.md and is shared by the validation-packet builder and the
post-validation harmonizer.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, asdict
from typing import Any, Optional

FRAMING_MARKERS = (
    "here is",
    "here's",
    "here you go",
    "sure",
    "certainly",
    "of course",
    "absolutely",
    "below is",
    "a short poem",
    "a poem",
    "poem:",
    "story:",
)

TITLE_FUNCTION_WORDS = {"a", "an", "the", "of", "and", "or", "in", "on", "to", "for"}

LEXICAL_RE = re.compile(r"[A-Za-z]+(?:['’\-][A-Za-z]+)*")
BLANK_BOUNDARY_RE = re.compile(r"\n[ \t]*\n+")
ELLIPSIS_RE = re.compile(r"\.{3,}")

PRONOUNS_1S = {"i", "me", "my", "mine", "myself"}
PRONOUNS_1P = {"we", "us", "our", "ours", "ourselves"}
PRONOUNS_2 = {"you", "your", "yours", "yourself", "yourselves"}
PRONOUNS_3 = {
    "he", "she", "it", "they", "him", "her", "them",
    "his", "hers", "its", "their", "theirs",
    "himself", "herself", "itself", "themselves",
}

PUNCTUATION_CHARS = {
    "em_dash": "—",
    "semicolon": ";",
    "colon": ":",
    "comma": ",",
    "exclamation": "!",
    "question": "?",
}


def normalize_text(text: Optional[str]) -> str:
    if not text:
        return ""
    return text.replace("\r\n", "\n").replace("\r", "\n").strip()


def lexical_tokens(text: str) -> list[str]:
    return [m.group(0) for m in LEXICAL_RE.finditer(text)]


def _strip_detection_markup(text: str) -> str:
    s = text.lstrip()
    s = re.sub(r"^[>#*_\-`~\s]+", "", s)
    return s.strip()


def _token_count_ws(text: str) -> int:
    return len(text.split())


def looks_like_preamble(block: str) -> bool:
    if not block.strip() or _token_count_ws(block) > 30:
        return False
    candidate = _strip_detection_markup(block).lower()
    candidate = candidate.lstrip("\"'“‘([{")
    return any(candidate.startswith(marker) for marker in FRAMING_MARKERS)


def _split_first_blank_block(text: str) -> Optional[tuple[str, str]]:
    m = BLANK_BOUNDARY_RE.search(text)
    if not m:
        return None
    first = text[:m.start()].strip()
    rest = text[m.end():].lstrip("\n")
    if not first or not rest.strip():
        return None
    return first, rest


def _first_line_and_rest(text: str) -> tuple[str, str]:
    if "\n" not in text:
        return text.strip(), ""
    first, rest = text.split("\n", 1)
    return first.strip(), rest


def _has_blank_boundary_after_first_line(text: str) -> bool:
    return bool(re.match(r"^[^\n]+\n[ \t]*\n+", text))


def _strip_title_markup(line: str) -> str:
    s = line.strip()
    s = re.sub(r"^\s{0,3}#{1,6}\s+", "", s)
    pairs = (("**", "**"), ("__", "__"), ("*", "*"), ("_", "_"))
    for left, right in pairs:
        if s.startswith(left) and s.endswith(right) and len(s) > len(left) + len(right):
            s = s[len(left):-len(right)].strip()
            break
    return s


def _plain_title_case_rule(line: str) -> bool:
    candidate = _strip_title_markup(line)
    tokens = candidate.split()
    if not 1 <= len(tokens) <= 12:
        return False
    if candidate.endswith((".", "!", "?")):
        return False
    if looks_like_preamble(candidate):
        return False

    alpha_tokens = []
    uppercase_initial = 0
    for tok in tokens:
        cleaned = re.sub(r"^[^A-Za-z]+|[^A-Za-z]+$", "", tok)
        if not cleaned:
            continue
        if cleaned.lower() in TITLE_FUNCTION_WORDS:
            continue
        alpha_tokens.append(cleaned)
        if cleaned[0].isupper():
            uppercase_initial += 1

    if not alpha_tokens:
        return False
    return uppercase_initial / len(alpha_tokens) >= 0.5


def detect_title(text_after_preamble: str) -> tuple[bool, str, str]:
    text = text_after_preamble.strip()
    first, rest = _first_line_and_rest(text)
    if not first or not rest.strip():
        return False, "", text

    if re.match(r"^\s{0,3}#{1,6}\s+\S", first):
        body = rest.lstrip("\n")
        if body.strip():
            return True, first, body.strip()
        return False, "", text

    blank_after = _has_blank_boundary_after_first_line(text)

    emphasized = any(
        first.startswith(left) and first.endswith(right) and len(first) > len(left) + len(right)
        for left, right in (("**", "**"), ("__", "__"), ("*", "*"), ("_", "_"))
    )
    if emphasized and _token_count_ws(_strip_title_markup(first)) <= 12 and blank_after:
        body = re.sub(r"^[^\n]+\n[ \t]*\n+", "", text, count=1)
        if body.strip():
            return True, first, body.strip()
        return False, "", text

    if blank_after and _plain_title_case_rule(first):
        body = re.sub(r"^[^\n]+\n[ \t]*\n+", "", text, count=1)
        if body.strip():
            return True, first, body.strip()
        return False, "", text

    return False, "", text


@dataclass
class SurfaceParse:
    normalized_response: str
    preamble_present: bool
    preamble_text: str
    text_after_preamble: str
    title_present: bool
    title_text: str
    creative_body: str
    parse_empty_fallback: bool
    preamble_token_count: int
    title_token_count: int


def parse_surface(response: Optional[str]) -> SurfaceParse:
    full = normalize_text(response)
    if not full:
        return SurfaceParse(
            normalized_response="",
            preamble_present=False,
            preamble_text="",
            text_after_preamble="",
            title_present=False,
            title_text="",
            creative_body="",
            parse_empty_fallback=False,
            preamble_token_count=0,
            title_token_count=0,
        )

    preamble_present = False
    preamble_text = ""
    after_preamble = full

    split = _split_first_blank_block(full)
    if split is not None:
        first_block, rest = split
        if looks_like_preamble(first_block):
            preamble_present = True
            preamble_text = first_block
            after_preamble = rest.strip()

    title_present, title_text, body = detect_title(after_preamble)
    fallback = False

    if not body.strip():
        fallback = True
        if title_present:
            title_present = False
            title_text = ""
            body = after_preamble
        elif preamble_present:
            preamble_present = False
            preamble_text = ""
            after_preamble = full
            body = full
        else:
            body = full

    return SurfaceParse(
        normalized_response=full,
        preamble_present=preamble_present,
        preamble_text=preamble_text,
        text_after_preamble=after_preamble,
        title_present=title_present,
        title_text=title_text,
        creative_body=body.strip(),
        parse_empty_fallback=fallback,
        preamble_token_count=_token_count_ws(preamble_text) if preamble_present else 0,
        title_token_count=_token_count_ws(_strip_title_markup(title_text)) if title_present else 0,
    )


def _nonempty_lines(text: str) -> list[str]:
    return [line for line in text.split("\n") if line.strip()]


def _stanza_blocks(text: str) -> list[str]:
    return [b for b in re.split(r"\n[ \t]*\n+", text) if b.strip()]


def basic_body_features(body: str) -> dict[str, Any]:
    words = lexical_tokens(body)
    lines = _nonempty_lines(body)
    stanzas = _stanza_blocks(body)

    per_line = [len(lexical_tokens(line)) for line in lines]
    mean_wpl = sum(per_line) / len(per_line) if per_line else 0.0
    if len(per_line) >= 2:
        var = sum((x - mean_wpl) ** 2 for x in per_line) / (len(per_line) - 1)
        sd_wpl = math.sqrt(var)
    else:
        sd_wpl = 0.0

    mean_word_length = (
        sum(len(re.sub(r"[^A-Za-z]", "", w)) for w in words) / len(words)
        if words else 0.0
    )

    return {
        "body_word_count": len(words),
        "body_line_count_nonempty": len(lines),
        "body_stanza_count": len(stanzas),
        "words_per_line_mean": mean_wpl,
        "words_per_line_sd": sd_wpl,
        "mean_word_length": mean_word_length,
    }


def pronoun_features(body: str) -> dict[str, Any]:
    toks = [t.lower().replace("’", "'") for t in lexical_tokens(body)]
    c1s = sum(t in PRONOUNS_1S for t in toks)
    c1p = sum(t in PRONOUNS_1P for t in toks)
    c2 = sum(t in PRONOUNS_2 for t in toks)
    c3 = sum(t in PRONOUNS_3 for t in toks)
    total = c1s + c1p + c2 + c3
    denom = total if total else 1
    return {
        "pronoun_1s_count": c1s,
        "pronoun_1p_count": c1p,
        "pronoun_2_count": c2,
        "pronoun_3_count": c3,
        "pronoun_total_count": total,
        "pronoun_1s_share": c1s / denom if total else 0.0,
        "pronoun_1p_share": c1p / denom if total else 0.0,
        "pronoun_2_share": c2 / denom if total else 0.0,
        "pronoun_3_share": c3 / denom if total else 0.0,
    }


def punctuation_features(body: str, body_word_count: int) -> dict[str, Any]:
    denom = body_word_count if body_word_count else 1
    counts = {f"{name}_count": body.count(ch) for name, ch in PUNCTUATION_CHARS.items()}
    counts["ellipsis_count"] = body.count("…") + len(ELLIPSIS_RE.findall(body))
    rates = {
        key.replace("_count", "_per_100_words"): (value / denom * 100.0 if body_word_count else 0.0)
        for key, value in counts.items()
    }
    return {**counts, **rates}


def opening_features(body: str) -> dict[str, str]:
    toks = [t.lower() for t in lexical_tokens(body)]
    return {
        "first_lexical_token": toks[0] if toks else "",
        "opening_bigram": " ".join(toks[:2]) if len(toks) >= 2 else "",
    }


NON_CONTENT_POS = {"PUNCT", "SPACE", "SYM"}


def load_spacy_model(model_name: str = "en_core_web_trf"):
    try:
        import spacy
    except ImportError as exc:
        raise RuntimeError(
            "spaCy is not installed. Install the September requirements first."
        ) from exc
    try:
        return spacy.load(model_name)
    except OSError as exc:
        raise RuntimeError(
            f"spaCy model {model_name!r} is not installed. Run: "
            f"python -m spacy download {model_name}"
        ) from exc


def pos_features(body: str, nlp) -> dict[str, Any]:
    doc = nlp(body)
    toks = [t for t in doc if t.pos_ not in NON_CONTENT_POS]
    n = len(toks)
    if not n:
        return {
            "pos_noun_ratio": 0.0,
            "pos_verb_ratio": 0.0,
            "pos_adj_ratio": 0.0,
            "pos_adv_ratio": 0.0,
            "pos_pronoun_ratio": 0.0,
            "pos_content_token_count": 0,
        }

    counts = {"NOUN": 0, "PROPN": 0, "VERB": 0, "AUX": 0, "ADJ": 0, "ADV": 0, "PRON": 0}
    for t in toks:
        if t.pos_ in counts:
            counts[t.pos_] += 1

    return {
        "pos_noun_ratio": (counts["NOUN"] + counts["PROPN"]) / n,
        "pos_verb_ratio": (counts["VERB"] + counts["AUX"]) / n,
        "pos_adj_ratio": counts["ADJ"] / n,
        "pos_adv_ratio": counts["ADV"] / n,
        "pos_pronoun_ratio": counts["PRON"] / n,
        "pos_content_token_count": n,
    }


def infer_genre(prompt_id: str, prompt_text: str) -> str:
    s = f"{prompt_id} {prompt_text}".lower()
    if "poem" in s:
        return "poem"
    if "animal" in s:
        return "animal"
    if "story" in s:
        return "story"
    return "unknown"


def infer_length_cap(prompt_id: str, prompt_text: str) -> Optional[int]:
    s = f"{prompt_id} {prompt_text}".lower()
    m = re.search(r"(?:_|-)(5|10|20)$", prompt_id.lower())
    if m:
        return int(m.group(1))
    if "lt5" in s or "fewer than 5" in s or "fewer then 5" in s or "less than 5" in s:
        return 5
    if "lt10" in s or "fewer than 10" in s or "fewer then 10" in s or "less than 10" in s:
        return 10
    if "lt20" in s or "fewer than 20" in s or "fewer then 20" in s or "less than 20" in s:
        return 20
    return None


def infer_phrasing(prompt_id: str, prompt_text: str, study: str) -> str:
    if study == "BA2":
        s = f"{prompt_id} {prompt_text}".lower()
        for p in ("write", "compose", "gimme"):
            if p in s:
                return p
    first = prompt_text.strip().split(maxsplit=1)
    return first[0].lower().strip(".,:;!?") if first else ""


def harmonized_metadata(record: dict[str, Any], study: str) -> dict[str, Any]:
    prompt_id = str(record.get("prompt_id") or "")
    prompt_text = str(record.get("prompt_text") or "")
    cap = infer_length_cap(prompt_id, prompt_text)
    return {
        "study": study,
        "provider": record.get("provider"),
        "model": record.get("model"),
        "prompt_id": prompt_id,
        "prompt_text": prompt_text,
        "iteration": record.get("iteration"),
        "temperature": record.get("temperature"),
        "max_tokens": record.get("max_tokens") if record.get("max_tokens") is not None else record.get("max_output_tokens"),
        "timestamp": record.get("timestamp"),
        "source_run_id": record.get("run_id") or record.get("output_id") or record.get("id"),
        "genre": infer_genre(prompt_id, prompt_text),
        "length_cap": cap,
        "length_condition": str(cap) if cap is not None else "open",
        "phrasing": infer_phrasing(prompt_id, prompt_text, study),
    }


def surface_dict(parsed: SurfaceParse) -> dict[str, Any]:
    return asdict(parsed)
