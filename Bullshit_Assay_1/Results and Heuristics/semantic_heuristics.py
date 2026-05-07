#!/usr/bin/env python3
"""
semantic_heuristics.py

Blind, provisional heuristic coder for the model-comparison JSONL.

Design goals:
- Work directly on results.jsonl from run_experiment.py.
- Avoid model-name leakage during qualitative review.
- Use deterministic, inspectable lexical heuristics rather than model-assisted coding.
- Produce row-level codes plus grouped summaries.
- Be useful before any human has read the outputs.

Example:
    python semantic_heuristics.py results.jsonl --outdir analysis_semantic --seed 20260507

Outputs:
    analysis_semantic/coded_outputs.csv
    analysis_semantic/summary_by_blind_model.csv
    analysis_semantic/summary_by_blind_model_prompt.csv
    analysis_semantic/blind_review_sample.csv
    analysis_semantic/blind_model_map_PRIVATE.json

Important:
    The blind model map is intentionally written as PRIVATE. Do not open it until after
    qualitative coding is complete.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import random
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# Lexicons
# Keep these deliberately simple and transparent. They are weak signals, not truth.
# ---------------------------------------------------------------------------

SETTING_LEXICONS: Dict[str, set[str]] = {
    "natural": {
        "forest", "woods", "tree", "trees", "leaf", "leaves", "river", "stream",
        "brook", "mountain", "valley", "hill", "meadow", "field", "garden",
        "flower", "flowers", "grass", "moss", "stone", "stones", "rain", "snow",
        "wind", "sun", "moon", "stars", "sky", "cloud", "clouds", "bird",
        "birds", "wolf", "fox", "deer", "bear", "rabbit", "owl", "ocean", "sea",
        "shore", "beach", "lake", "pond", "island", "desert", "dawn", "dusk",
        "night", "spring", "summer", "autumn", "fall", "winter", "season", "seasons",
    },
    "domestic": {
        "house", "home", "kitchen", "bedroom", "attic", "porch", "window", "door",
        "hearth", "fireplace", "table", "chair", "room", "rooms", "cottage", "blanket",
        "shelf", "cup", "tea", "lamp", "stairs", "floor", "wall", "walls", "roof",
    },
    "urban": {
        "city", "street", "streets", "alley", "subway", "train", "station", "apartment",
        "building", "buildings", "neon", "traffic", "taxi", "bus", "sidewalk", "market",
        "shop", "cafe", "office", "elevator", "rooftop", "skyscraper", "bridge",
    },
    "futuristic": {
        "robot", "robots", "android", "ai", "algorithm", "machine", "machines", "spaceship",
        "starship", "rocket", "colony", "colonies", "mars", "satellite", "orbit",
        "hologram", "holographic", "laser", "quantum", "cyber", "neural", "drone",
        "drones", "synthetic", "terraform", "galaxy", "interstellar", "spacecraft",
    },
    "fantastical": {
        "dragon", "dragons", "wizard", "witch", "spell", "spells", "magic", "magical",
        "kingdom", "castle", "fairy", "fae", "elf", "elves", "dwarf", "dwarves",
        "orc", "goblin", "phoenix", "unicorn", "griffin", "mermaid", "curse", "enchanted",
        "sorcerer", "sorceress", "prophecy", "portal", "realm", "myth", "mythic",
    },
    "historical": {
        "king", "queen", "prince", "princess", "emperor", "empire", "knight", "sword",
        "village", "villagers", "harbor", "ship", "sail", "sails", "carriage", "lantern",
        "candle", "monastery", "abbey", "cathedral", "war", "soldier", "soldiers",
        "ancient", "old", "century", "centuries", "medieval",
    },
    "cosmic": {
        "star", "stars", "moon", "planet", "planets", "galaxy", "galaxies", "cosmos",
        "universe", "void", "orbit", "comet", "nebula", "asteroid", "meteor", "sun",
        "solar", "lunar", "celestial", "constellation", "constellations",
    },
}

MOOD_LEXICONS: Dict[str, set[str]] = {
    "wistful": {
        "memory", "memories", "remember", "remembered", "forgotten", "once", "longing",
        "yearning", "faded", "fading", "echo", "echoes", "old", "return", "returned",
        "dusk", "twilight", "soft", "quiet", "gentle", "almost", "still", "again",
    },
    "melancholic": {
        "sad", "sorrow", "sorrowful", "grief", "lonely", "alone", "loss", "lost",
        "mourning", "tears", "wept", "weeping", "ache", "aching", "empty", "silence",
        "silent", "shadow", "shadows", "dark", "darkness", "hollow", "broken",
    },
    "romantic": {
        "love", "loved", "lover", "beloved", "kiss", "kissed", "heart", "hearts",
        "romance", "romantic", "desire", "darling", "tender", "embrace", "embraced",
        "hand", "hands", "together", "wedding", "bride", "groom",
    },
    "playful": {
        "laugh", "laughed", "laughing", "giggle", "giggled", "silly", "mischief",
        "mischievous", "trick", "tricks", "joke", "joked", "funny", "whimsy", "whimsical",
        "bounce", "bounced", "dance", "danced", "delight", "delighted",
    },
    "eerie": {
        "eerie", "strange", "haunted", "ghost", "ghosts", "whisper", "whispers",
        "whispered", "crept", "creeping", "shadow", "shadows", "mist", "fog", "chill",
        "chilled", "horror", "monster", "monsters", "unseen", "midnight", "grave",
    },
    "adventurous": {
        "journey", "quest", "adventure", "adventurer", "explore", "explored", "discover",
        "discovered", "map", "treasure", "sail", "sailed", "climb", "climbed", "escape",
        "escaped", "chase", "chased", "hunt", "hunted", "brave", "danger", "dangerous",
    },
    "serene": {
        "peace", "peaceful", "calm", "stillness", "still", "gentle", "quiet", "soft",
        "tranquil", "serene", "hush", "hushed", "rest", "rested", "slow", "slowly",
        "warm", "glow", "glowing", "light", "golden",
    },
    "dark": {
        "blood", "death", "dead", "die", "died", "kill", "killed", "knife", "grave",
        "graveyard", "curse", "cursed", "rot", "rotting", "bone", "bones", "terror",
        "scream", "screamed", "nightmare", "cruel", "violence", "violent",
    },
    "inspirational": {
        "hope", "hoped", "dream", "dreams", "dreamed", "courage", "brave", "rise",
        "rose", "shine", "shone", "bright", "brighter", "believe", "believed", "possible",
        "promise", "tomorrow", "heal", "healed", "new", "beginning", "began",
    },
}

PLOT_LEXICONS: Dict[str, set[str]] = {
    "discovery": {
        "found", "discover", "discovered", "uncovered", "revealed", "realized", "learned",
        "noticed", "saw", "opened", "secret", "hidden", "map", "door", "message",
    },
    "transformation": {
        "became", "become", "changed", "change", "transformed", "grew", "turned",
        "shifted", "learned", "healed", "new", "different", "finally", "no longer",
    },
    "loss": {
        "lost", "gone", "left", "vanished", "died", "death", "forgotten", "missing",
        "empty", "goodbye", "last", "never", "alone", "grief",
    },
    "reunion": {
        "returned", "return", "reunited", "again", "found each other", "came back", "home",
        "embraced", "together", "waited", "recognized",
    },
    "escape": {
        "escape", "escaped", "ran", "fled", "flight", "free", "freedom", "break", "broke",
        "door", "gate", "prison", "trap", "trapped", "chase", "chased",
    },
    "creation": {
        "made", "created", "built", "wrote", "painted", "sang", "invented", "crafted",
        "grew", "planted", "baked", "carved", "composed", "designed",
    },
    "survival": {
        "survive", "survived", "survival", "hunger", "hungry", "storm", "cold", "danger",
        "wounded", "fight", "fought", "safe", "shelter", "saved", "rescue", "rescued",
    },
    "observation": {
        "watched", "looked", "listened", "sat", "stood", "noticed", "wondered", "waited",
        "saw", "heard", "felt", "thought", "remembered",
    },
}

IMAGERY_LEXICONS: Dict[str, set[str]] = {
    "nature": SETTING_LEXICONS["natural"],
    "light_dark": {
        "light", "dark", "darkness", "shadow", "shadows", "glow", "glowed", "glowing",
        "bright", "dim", "dawn", "dusk", "twilight", "night", "sun", "moon", "lamp",
        "lantern", "fire", "flame", "spark", "stars",
    },
    "seasons_time": {
        "spring", "summer", "autumn", "fall", "winter", "season", "seasons", "time",
        "hour", "hours", "year", "years", "century", "centuries", "morning", "evening",
        "dawn", "dusk", "midnight", "yesterday", "tomorrow", "forever",
    },
    "ocean_water": {
        "ocean", "sea", "river", "stream", "brook", "lake", "pond", "rain", "wave",
        "waves", "tide", "tides", "shore", "beach", "harbor", "water", "waters",
    },
    "stars_space": SETTING_LEXICONS["cosmic"] | SETTING_LEXICONS["futuristic"],
    "machines": {
        "machine", "machines", "robot", "robots", "engine", "engines", "gear", "gears",
        "clock", "clocks", "circuit", "circuits", "wire", "wires", "screen", "screens",
        "algorithm", "hologram", "drone", "drones", "synthetic",
    },
    "body": {
        "hand", "hands", "heart", "hearts", "eyes", "eye", "mouth", "voice", "skin",
        "bone", "bones", "blood", "breath", "arms", "face", "hair", "feet", "finger",
        "fingers", "chest", "shoulder", "shoulders",
    },
    "memory": {
        "memory", "memories", "remember", "remembered", "forgot", "forgotten", "past",
        "once", "old", "childhood", "echo", "echoes", "photograph", "letter", "letters",
    },
}

CLICHE_PHRASES: Tuple[str, ...] = (
    "once upon a time",
    "little did",
    "from that day on",
    "and they lived",
    "in a world where",
    "as the sun set",
    "at the end of the day",
    "never looked back",
    "deep in the forest",
    "in the heart of",
    "a small village",
    "the old man",
    "the old woman",
    "for the first time",
)

REFUSAL_PATTERNS: Tuple[str, ...] = (
    "i'm sorry",
    "i am sorry",
    "i can't assist",
    "i cannot assist",
    "i can't help",
    "i cannot help",
    "as an ai",
    "i'm unable",
    "i am unable",
)

COMMON_ANIMALS: set[str] = {
    "cat", "dog", "bird", "wolf", "fox", "bear", "rabbit", "deer", "owl", "mouse",
    "rat", "lion", "tiger", "elephant", "giraffe", "zebra", "monkey", "ape", "gorilla",
    "whale", "dolphin", "shark", "fish", "octopus", "squid", "seal", "penguin", "otter",
    "horse", "cow", "pig", "sheep", "goat", "chicken", "duck", "goose", "swan", "eagle",
    "hawk", "falcon", "crow", "raven", "sparrow", "butterfly", "bee", "ant", "spider",
    "snake", "lizard", "frog", "toad", "turtle", "tortoise", "dragonfly", "moth",
    "lynx", "panther", "leopard", "cheetah", "rhino", "rhinoceros", "hippo", "hippopotamus",
    "kangaroo", "koala", "panda", "sloth", "badger", "weasel", "ferret", "hedgehog",
}

HYBRID_MARKERS: Tuple[str, ...] = (
    "-", "wing", "horn", "fire", "moon", "star", "shadow", "crystal", "cloud",
    "feather", "scale", "silver", "golden", "glass", "mist", "storm",
)


# ---------------------------------------------------------------------------
# Basic text processing
# ---------------------------------------------------------------------------

WORD_RE = re.compile(r"\b[a-zA-Z][a-zA-Z'’-]*\b")
SENTENCE_END_RE = re.compile(r"[.!?]+(?:[\"'”’)]*)\s+")


def clean_text(text: Optional[str]) -> str:
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text.strip()


def tokenize(text: str) -> List[str]:
    return [m.group(0).lower().replace("’", "'") for m in WORD_RE.finditer(text)]


def sentence_count(text: str) -> int:
    """Very simple sentence estimate. Good enough for provisional blind coding."""
    text = clean_text(text)
    if not text:
        return 0
    # Split on punctuation followed by whitespace. Add 1 if terminal punctuation exists.
    parts = re.split(r"(?<=[.!?])\s+", text)
    parts = [p.strip() for p in parts if p.strip()]
    return len(parts)


def nonempty_lines(text: str) -> List[str]:
    return [ln.strip() for ln in clean_text(text).split("\n") if ln.strip()]


def stanza_count(text: str) -> int:
    text = clean_text(text)
    if not text:
        return 0
    stanzas = [s for s in re.split(r"\n\s*\n+", text) if s.strip()]
    return len(stanzas)


def first_word_bigram(tokens: Sequence[str]) -> Tuple[str, str]:
    first = tokens[0] if tokens else ""
    bigram = " ".join(tokens[:2]) if len(tokens) >= 2 else ""
    return first, bigram


def type_token_ratio(tokens: Sequence[str]) -> float:
    if not tokens:
        return math.nan
    return len(set(tokens)) / len(tokens)


# ---------------------------------------------------------------------------
# Prompt and blind-model handling
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
    if "lt5" in s or "fewer than 5" in s or "less than 5" in s or "<5" in s:
        return "lt5"
    if "lt10" in s or "fewer than 10" in s or "less than 10" in s or "<10" in s:
        return "lt10"
    return "open"


def build_blind_map(models: Sequence[str], seed: int) -> Dict[str, str]:
    shuffled = list(sorted(set(models)))
    rng = random.Random(seed)
    rng.shuffle(shuffled)
    labels = [f"Model {chr(ord('A') + i)}" for i in range(len(shuffled))]
    return {model: label for model, label in zip(shuffled, labels)}


def stable_output_id(record: Dict[str, Any]) -> str:
    raw = "|".join(
        str(record.get(k, ""))
        for k in ["provider", "model", "prompt_id", "iteration", "timestamp"]
    )
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]


# ---------------------------------------------------------------------------
# Heuristic coders
# ---------------------------------------------------------------------------


def count_lexicon(tokens: Sequence[str], lexicon: Iterable[str]) -> int:
    token_counts = Counter(tokens)
    count = 0
    for term in lexicon:
        if " " in term:
            # Phrase handled elsewhere.
            continue
        count += token_counts[term]
    return count


def phrase_count(text_lower: str, phrases: Iterable[str]) -> int:
    return sum(text_lower.count(p.lower()) for p in phrases)


def score_categories(tokens: Sequence[str], text_lower: str, lexicons: Dict[str, set[str]]) -> Dict[str, int]:
    scores: Dict[str, int] = {}
    for label, lexicon in lexicons.items():
        unigram_terms = {x for x in lexicon if " " not in x}
        phrase_terms = {x for x in lexicon if " " in x}
        scores[label] = count_lexicon(tokens, unigram_terms) + phrase_count(text_lower, phrase_terms)
    return scores


def top_labels(scores: Dict[str, int], min_score: int = 1, max_labels: int = 3) -> List[str]:
    items = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
    return [k for k, v in items if v >= min_score][:max_labels]


def dominant_label(scores: Dict[str, int], min_score: int = 1) -> str:
    labels = top_labels(scores, min_score=min_score, max_labels=1)
    return labels[0] if labels else "none_detected"


def pronoun_counts(tokens: Sequence[str]) -> Dict[str, int]:
    first = {"i", "me", "my", "mine", "we", "us", "our", "ours"}
    second = {"you", "your", "yours", "yourself", "yourselves"}
    third = {
        "he", "him", "his", "she", "her", "hers", "they", "them", "their", "theirs",
        "it", "its", "himself", "herself", "themselves",
    }
    return {
        "first_person_pronouns": count_lexicon(tokens, first),
        "second_person_pronouns": count_lexicon(tokens, second),
        "third_person_pronouns": count_lexicon(tokens, third),
    }


def infer_person(tokens: Sequence[str]) -> str:
    counts = pronoun_counts(tokens)
    f = counts["first_person_pronouns"]
    s = counts["second_person_pronouns"]
    t = counts["third_person_pronouns"]
    total = f + s + t
    if total == 0:
        return "none_detected"
    max_val = max(f, s, t)
    winners = []
    if f == max_val and f > 0:
        winners.append("first")
    if s == max_val and s > 0:
        winners.append("second")
    if t == max_val and t > 0:
        winners.append("third")
    if len(winners) > 1:
        return "mixed"
    # Require a little separation to avoid overclassifying a stray pronoun.
    if max_val < 2 and total > 1:
        return "mixed"
    return winners[0]


def tense_scores(tokens: Sequence[str]) -> Dict[str, int]:
    past_aux = {
        "was", "were", "had", "did", "went", "came", "saw", "found", "made", "said",
        "knew", "thought", "felt", "became", "took", "gave", "left", "returned", "remembered",
    }
    present_aux = {
        "is", "are", "am", "do", "does", "has", "have", "go", "goes", "come", "comes",
        "see", "sees", "find", "finds", "make", "makes", "say", "says", "know", "knows",
        "feel", "feels", "think", "thinks",
    }
    future_aux = {"will", "shall", "would", "could", "might"}

    past_suffix = sum(1 for w in tokens if len(w) > 4 and w.endswith("ed"))
    present_suffix = sum(1 for w in tokens if len(w) > 4 and w.endswith("s"))
    going_to = 0
    for i in range(len(tokens) - 1):
        if tokens[i] == "going" and tokens[i + 1] == "to":
            going_to += 1

    return {
        "past_tense_score": count_lexicon(tokens, past_aux) + past_suffix,
        "present_tense_score": count_lexicon(tokens, present_aux) + present_suffix,
        "future_tense_score": count_lexicon(tokens, future_aux) + going_to,
    }


def infer_tense(tokens: Sequence[str]) -> str:
    scores = tense_scores(tokens)
    past = scores["past_tense_score"]
    pres = scores["present_tense_score"]
    fut = scores["future_tense_score"]
    if max(past, pres, fut) == 0:
        return "none_detected"
    ordered = sorted([("past", past), ("present", pres), ("future", fut)], key=lambda kv: -kv[1])
    if ordered[0][1] == ordered[1][1]:
        return "mixed"
    # If top two are close, call mixed.
    if ordered[1][1] > 0 and ordered[0][1] / ordered[1][1] < 1.5:
        return "mixed"
    return ordered[0][0]


def detect_poetic_mode(text: str, tokens: Sequence[str], prompt_category: str) -> str:
    lines = nonempty_lines(text)
    if prompt_category != "poem" and len(lines) < 3:
        return "not_poem_like"

    if len(lines) >= 3:
        last_words = []
        for ln in lines:
            ws = tokenize(ln)
            if ws:
                last_words.append(ws[-1])
        # crude rhyme: repeated final 2-3 letters across line endings
        endings = [w[-3:] if len(w) >= 3 else w for w in last_words]
        repeated_endings = sum(v for v in Counter(endings).values() if v >= 2)
        avg_line_len = mean([len(tokenize(ln)) for ln in lines]) if lines else 0
        if repeated_endings >= max(2, len(lines) // 3):
            return "rhyme_heavy"
        if avg_line_len <= 7:
            return "lyric_or_imagistic"
        return "free_verse_or_narrative"

    return "prose_like"


def ending_valence(tokens: Sequence[str], text_lower: str) -> str:
    # Heuristic based on final third of text.
    if not tokens:
        return "none_detected"
    final_tokens = tokens[max(0, int(len(tokens) * 0.67)):]
    final_text = " ".join(final_tokens)

    positive = {
        "happy", "happily", "joy", "joyful", "smile", "smiled", "laugh", "laughed",
        "hope", "hopeful", "home", "together", "peace", "safe", "saved", "warm", "light",
        "new", "beginning", "love", "free", "freedom",
    }
    negative = {
        "sad", "sorrow", "lost", "alone", "empty", "dark", "darkness", "died", "dead",
        "death", "tears", "wept", "gone", "never", "silence", "broken", "cold",
    }
    unresolved = {"perhaps", "maybe", "still", "waiting", "waited", "wondered", "unknown", "mystery"}
    twist_markers = {"but", "however", "instead", "suddenly", "then", "only", "realized"}

    pos = count_lexicon(final_tokens, positive)
    neg = count_lexicon(final_tokens, negative)
    unres = count_lexicon(final_tokens, unresolved)
    twist = count_lexicon(final_tokens, twist_markers)

    if twist >= 2 or "but" in final_tokens[-15:]:
        return "twist_or_turn"
    if unres >= 2:
        return "unresolved"
    if pos > neg:
        return "positive"
    if neg > pos:
        return "negative"
    if pos > 0 and neg > 0:
        return "bittersweet"
    return "neutral_or_unclear"


def detect_animal_entities(text: str, tokens: Sequence[str]) -> Dict[str, Any]:
    text_lower = text.lower()
    animals = sorted({w for w in tokens if w in COMMON_ANIMALS})

    # Capitalized noun-ish phrases. Crude but useful for invented names.
    cap_phrases = re.findall(r"\b(?:[A-Z][a-z]+(?:[- ][A-Z]?[a-z]+){0,3})\b", text)
    cap_phrases = [p.strip() for p in cap_phrases if p.strip()]
    # Remove sentence-initial common words that are likely not names.
    stop_caps = {
        "The", "A", "An", "In", "On", "At", "When", "While", "Before", "After", "Every",
        "Once", "One", "By", "For", "And", "But", "So", "Then", "There", "This", "That",
    }
    cap_phrases = [p for p in cap_phrases if p.split()[0] not in stop_caps]

    hybrids = []
    invented = []
    for phrase in cap_phrases:
        pl = phrase.lower()
        if any(marker in pl for marker in HYBRID_MARKERS) and not any(a in pl.split() for a in COMMON_ANIMALS):
            hybrids.append(phrase)
        elif not any(a in pl.split() for a in COMMON_ANIMALS):
            invented.append(phrase)

    # Lowercase hyphen compounds like fire-lynx, cloud-otter, etc.
    hyphen_compounds = re.findall(r"\b[a-z]+-[a-z]+\b", text_lower)
    for comp in hyphen_compounds:
        if any(a in comp for a in COMMON_ANIMALS) or any(m in comp for m in HYBRID_MARKERS):
            hybrids.append(comp)

    return {
        "real_animals_detected": ";".join(animals),
        "real_animal_count": len(animals),
        "invented_entity_candidates": ";".join(sorted(set(invented))),
        "invented_entity_candidate_count": len(set(invented)),
        "hybrid_entity_candidates": ";".join(sorted(set(hybrids))),
        "hybrid_entity_candidate_count": len(set(hybrids)),
    }


def formulaicness_score(text_lower: str, tokens: Sequence[str]) -> int:
    score = phrase_count(text_lower, CLICHE_PHRASES)
    # Add a small penalty for very common story scaffolding words.
    scaffolding = {"suddenly", "finally", "little", "old", "small", "village", "forest", "realized"}
    score += count_lexicon(tokens, scaffolding)
    return score


def refusal_flag(text_lower: str) -> bool:
    return any(p in text_lower for p in REFUSAL_PATTERNS)


def code_record(record: Dict[str, Any], blind_model: str) -> Dict[str, Any]:
    response = clean_text(record.get("response"))
    text_lower = response.lower()
    tokens = tokenize(response)
    prompt_id = str(record.get("prompt_id", ""))
    prompt_text = str(record.get("prompt_text", ""))
    prompt_category = infer_prompt_category(prompt_id, prompt_text)
    length_condition = infer_length_condition(prompt_id, prompt_text)
    first, bigram = first_word_bigram(tokens)

    setting_scores = score_categories(tokens, text_lower, SETTING_LEXICONS)
    mood_scores = score_categories(tokens, text_lower, MOOD_LEXICONS)
    plot_scores = score_categories(tokens, text_lower, PLOT_LEXICONS)
    imagery_scores = score_categories(tokens, text_lower, IMAGERY_LEXICONS)
    p_counts = pronoun_counts(tokens)
    t_scores = tense_scores(tokens)
    animal_info = detect_animal_entities(response, tokens) if prompt_category == "animal" else {
        "real_animals_detected": "",
        "real_animal_count": 0,
        "invented_entity_candidates": "",
        "invented_entity_candidate_count": 0,
        "hybrid_entity_candidates": "",
        "hybrid_entity_candidate_count": 0,
    }

    sent_count = sentence_count(response)
    line_count = len(nonempty_lines(response))
    word_count = len(tokens)
    output_tokens = record.get("output_tokens")
    try:
        output_tokens_i = int(output_tokens) if output_tokens is not None else None
    except Exception:
        output_tokens_i = None

    compliance = "not_applicable"
    if length_condition == "lt5":
        compliance = "yes" if sent_count < 5 else "no"
    elif length_condition == "lt10":
        compliance = "yes" if sent_count < 10 else "no"

    row: Dict[str, Any] = {
        "output_id": stable_output_id(record),
        "blind_model": blind_model,
        "provider_hidden": "hidden",
        "model_hidden": "hidden",
        "prompt_id": prompt_id,
        "prompt_category": prompt_category,
        "length_condition": length_condition,
        "iteration": record.get("iteration"),
        "timestamp": record.get("timestamp"),
        "error": record.get("error"),
        "is_success": bool(record.get("error") is None and response),
        "is_refusal_like": refusal_flag(text_lower),
        "is_truncated_400ish": bool(output_tokens_i is not None and output_tokens_i >= 400),
        "char_count": len(response),
        "word_count": word_count,
        "sentence_count_heuristic": sent_count,
        "line_count_nonempty": line_count,
        "stanza_count_heuristic": stanza_count(response),
        "type_token_ratio": round(type_token_ratio(tokens), 4) if tokens else "",
        "first_word": first,
        "first_bigram": bigram,
        "constraint_compliant_heuristic": compliance,
        "person_heuristic": infer_person(tokens),
        "tense_heuristic": infer_tense(tokens),
        "poetic_mode_heuristic": detect_poetic_mode(response, tokens, prompt_category),
        "ending_valence_heuristic": ending_valence(tokens, text_lower),
        "dominant_setting_heuristic": dominant_label(setting_scores),
        "setting_labels_heuristic": ";".join(top_labels(setting_scores)),
        "dominant_mood_heuristic": dominant_label(mood_scores),
        "mood_labels_heuristic": ";".join(top_labels(mood_scores)),
        "dominant_plot_arc_heuristic": dominant_label(plot_scores),
        "plot_arc_labels_heuristic": ";".join(top_labels(plot_scores)),
        "dominant_imagery_heuristic": dominant_label(imagery_scores),
        "imagery_labels_heuristic": ";".join(top_labels(imagery_scores)),
        "formulaicness_score_heuristic": formulaicness_score(text_lower, tokens),
        "response": response,
    }

    row.update(p_counts)
    row.update(t_scores)
    row.update({f"setting_score_{k}": v for k, v in setting_scores.items()})
    row.update({f"mood_score_{k}": v for k, v in mood_scores.items()})
    row.update({f"plot_score_{k}": v for k, v in plot_scores.items()})
    row.update({f"imagery_score_{k}": v for k, v in imagery_scores.items()})
    row.update(animal_info)
    return row


# ---------------------------------------------------------------------------
# Dataset loading, freezing, and writing
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


def freeze_first_successes(records: Sequence[Dict[str, Any]], n_per_cell: int = 10) -> List[Dict[str, Any]]:
    """Keep first n successful records per (model, prompt_id), ordered by timestamp.

    This mirrors the preregistration logic. It ignores smoke-test detection because that
    depends on how files are stored; if smoke-test and full-run records are mixed, pass
    a clean main-run JSONL or filter externally.
    """
    successes = [r for r in records if r.get("error") is None and clean_text(r.get("response"))]
    successes.sort(key=lambda r: str(r.get("timestamp", "")))
    buckets: Dict[Tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)
    for r in successes:
        key = (str(r.get("model", "")), str(r.get("prompt_id", "")))
        if len(buckets[key]) < n_per_cell:
            buckets[key].append(r)
    frozen: List[Dict[str, Any]] = []
    for key in sorted(buckets):
        frozen.extend(buckets[key])
    frozen.sort(key=lambda r: (str(r.get("model", "")), str(r.get("prompt_id", "")), str(r.get("timestamp", ""))))
    return frozen


def write_csv(path: Path, rows: Sequence[Dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    # Stable field order: common fields first, then the rest alphabetically.
    priority = [
        "output_id", "blind_model", "prompt_id", "prompt_category", "length_condition",
        "iteration", "timestamp", "is_success", "is_refusal_like", "is_truncated_400ish",
        "word_count", "sentence_count_heuristic", "line_count_nonempty", "stanza_count_heuristic",
        "constraint_compliant_heuristic", "first_word", "first_bigram", "person_heuristic",
        "tense_heuristic", "dominant_setting_heuristic", "setting_labels_heuristic",
        "dominant_mood_heuristic", "mood_labels_heuristic", "dominant_plot_arc_heuristic",
        "plot_arc_labels_heuristic", "dominant_imagery_heuristic", "imagery_labels_heuristic",
        "poetic_mode_heuristic", "ending_valence_heuristic", "formulaicness_score_heuristic",
        "response",
    ]
    all_fields = set().union(*(r.keys() for r in rows))
    fields = [f for f in priority if f in all_fields] + sorted(all_fields - set(priority))
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def count_values(rows: Sequence[Dict[str, Any]], field: str) -> Counter:
    return Counter(str(r.get(field, "")) for r in rows)


def summarize_group(rows: Sequence[Dict[str, Any]], group_fields: Sequence[str]) -> List[Dict[str, Any]]:
    groups: Dict[Tuple[str, ...], List[Dict[str, Any]]] = defaultdict(list)
    for r in rows:
        key = tuple(str(r.get(f, "")) for f in group_fields)
        groups[key].append(r)

    summary_rows: List[Dict[str, Any]] = []
    categorical_fields = [
        "person_heuristic", "tense_heuristic", "dominant_setting_heuristic",
        "dominant_mood_heuristic", "dominant_plot_arc_heuristic", "dominant_imagery_heuristic",
        "poetic_mode_heuristic", "ending_valence_heuristic", "constraint_compliant_heuristic",
        "first_word", "first_bigram",
    ]
    numeric_fields = [
        "word_count", "sentence_count_heuristic", "line_count_nonempty", "stanza_count_heuristic",
        "type_token_ratio", "formulaicness_score_heuristic", "first_person_pronouns",
        "second_person_pronouns", "third_person_pronouns", "real_animal_count",
        "invented_entity_candidate_count", "hybrid_entity_candidate_count",
    ]

    for key, group in sorted(groups.items()):
        out: Dict[str, Any] = {field: value for field, value in zip(group_fields, key)}
        out["n"] = len(group)
        out["refusal_like_rate"] = round(mean([bool(r.get("is_refusal_like")) for r in group]), 4)
        out["truncated_400ish_rate"] = round(mean([bool(r.get("is_truncated_400ish")) for r in group]), 4)

        for field in numeric_fields:
            vals = []
            for r in group:
                v = r.get(field)
                if v in (None, ""):
                    continue
                try:
                    vals.append(float(v))
                except Exception:
                    pass
            if vals:
                out[f"{field}_mean"] = round(mean(vals), 4)
                out[f"{field}_median"] = round(median(vals), 4)

        for field in categorical_fields:
            c = count_values(group, field)
            if c:
                top, top_n = c.most_common(1)[0]
                out[f"{field}_top"] = top
                out[f"{field}_top_share"] = round(top_n / len(group), 4)
                out[f"{field}_counts"] = json.dumps(dict(c.most_common()), ensure_ascii=False)

        summary_rows.append(out)
    return summary_rows


def make_blind_review_sample(
    rows: Sequence[Dict[str, Any]],
    per_model_category: int,
    seed: int,
) -> List[Dict[str, Any]]:
    """Mechanically sampled blind review file.

    Includes raw response but not heuristic labels, so a human or Claude can code it cold.
    Stratified by blind_model × prompt_category.
    """
    rng = random.Random(seed)
    buckets: Dict[Tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)
    for r in rows:
        buckets[(str(r.get("blind_model")), str(r.get("prompt_category")))].append(r)

    sample: List[Dict[str, Any]] = []
    for key, group in sorted(buckets.items()):
        group_copy = list(group)
        rng.shuffle(group_copy)
        for r in group_copy[:per_model_category]:
            sample.append({
                "output_id": r["output_id"],
                "blind_model": r["blind_model"],
                "prompt_id": r["prompt_id"],
                "prompt_category": r["prompt_category"],
                "length_condition": r["length_condition"],
                "response": r["response"],
                # Empty columns for manual coding.
                "human_mood": "",
                "human_setting": "",
                "human_tense": "",
                "human_person": "",
                "human_plot_arc_or_poetic_mode": "",
                "human_imagery": "",
                "human_formulaicness_notes": "",
                "human_originality_notes": "",
            })
    rng.shuffle(sample)
    return sample


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Blind semantic heuristic coder for results.jsonl")
    p.add_argument("jsonl", type=Path, help="Path to results.jsonl")
    p.add_argument("--outdir", type=Path, default=Path("analysis_semantic"))
    p.add_argument("--seed", type=int, default=20260507, help="Seed for blind model labels and sampling")
    p.add_argument("--n-per-cell", type=int, default=10, help="First successful records per model × prompt_id")
    p.add_argument("--no-freeze", action="store_true", help="Code all successful records instead of first n per cell")
    p.add_argument("--blind-sample-per-model-category", type=int, default=3)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)

    records = read_jsonl(args.jsonl)
    success_records = [r for r in records if r.get("error") is None and clean_text(r.get("response"))]
    model_names = sorted({str(r.get("model", "")) for r in success_records})
    blind_map = build_blind_map(model_names, args.seed)

    if args.no_freeze:
        analysis_records = success_records
    else:
        analysis_records = freeze_first_successes(records, n_per_cell=args.n_per_cell)

    coded_rows = [code_record(r, blind_map[str(r.get("model", ""))]) for r in analysis_records]

    write_csv(args.outdir / "coded_outputs.csv", coded_rows)
    write_csv(args.outdir / "summary_by_blind_model.csv", summarize_group(coded_rows, ["blind_model"]))
    write_csv(
        args.outdir / "summary_by_blind_model_prompt.csv",
        summarize_group(coded_rows, ["blind_model", "prompt_category", "length_condition"]),
    )
    write_csv(
        args.outdir / "blind_review_sample.csv",
        make_blind_review_sample(
            coded_rows,
            per_model_category=args.blind_sample_per_model_category,
            seed=args.seed + 1,
        ),
    )

    # Private file. Do not open until after blind qualitative coding.
    private_map = {
        "seed": args.seed,
        "warning": "PRIVATE: reveals blind model labels. Do not inspect before blind coding is complete.",
        "blind_map_model_to_label": blind_map,
        "blind_map_label_to_model": {v: k for k, v in blind_map.items()},
    }
    with (args.outdir / "blind_model_map_PRIVATE.json").open("w", encoding="utf-8") as f:
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
        "notes": [
            "Heuristic labels are provisional weak signals.",
            "Model names are hidden in coded_outputs.csv and summaries.",
            "Do not inspect blind_model_map_PRIVATE.json until after blind coding.",
        ],
    }
    with (args.outdir / "manifest.json").open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
