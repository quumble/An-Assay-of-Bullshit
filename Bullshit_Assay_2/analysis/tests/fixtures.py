"""
Hand-crafted test fixtures with known expected feature values.

Each fixture is a small poem chosen to exercise a specific edge case
in the feature extraction pipeline. Expected values are computed by
hand, not by running the extractor (otherwise the test is circular).
"""

# Fixture 1: simple AABB rhyme, 1st person singular, 4 lines, 1 stanza.
SIMPLE_AABB = {
    "name": "simple_aabb",
    "response": (
        "I walked along the silver shore,\n"
        "And listened as the seagulls soar.\n"
        "The sand beneath my feet was warm,\n"
        "I weathered every coming storm."
    ),
    "expected": {
        "has_preamble": False,
        "line_count": 4,
        "stanza_count": 1,
        "person": "1st_singular",
        # AABB rhyme: shore/soar (probably), warm/storm
        # We expect at least 50% participation
        "rhyme_participation_min": 0.5,
    },
}

# Fixture 2: preamble + poem, properly separated by blank line
WITH_PREAMBLE = {
    "name": "with_preamble",
    "response": (
        "Sure! Here's a short poem for you:\n"
        "\n"
        "The sky is blue,\n"
        "The grass is green,\n"
        "The morning's new,\n"
        "The world is clean."
    ),
    "expected": {
        "has_preamble": True,
        "line_count": 4,
        "stanza_count": 1,
        "person": "impersonal",
    },
}

# Fixture 3: 2nd person, no rhyme (free verse)
SECOND_PERSON_FREE = {
    "name": "second_person_free",
    "response": (
        "You walk through the door.\n"
        "The light catches your hair.\n"
        "Your hands tremble briefly.\n"
        "Outside, the city continues."
    ),
    "expected": {
        "has_preamble": False,
        "line_count": 4,
        "stanza_count": 1,
        "person": "2nd",
    },
}

# Fixture 4: multi-stanza, 3rd person
MULTI_STANZA_3P = {
    "name": "multi_stanza_3p",
    "response": (
        "He waited at the station,\n"
        "Counting hours and trains.\n"
        "\n"
        "She arrived at last,\n"
        "Carrying nothing but rain."
    ),
    "expected": {
        "has_preamble": False,
        "line_count": 4,
        "stanza_count": 2,
        "person": "3rd",
    },
}

# Fixture 5: empty / whitespace
EMPTY = {
    "name": "empty",
    "response": "",
    "expected": {
        "has_preamble": False,
        "line_count": 0,
        "stanza_count": 0,
        "person": "impersonal",
    },
}

# Fixture 6: single-line aphorism
SINGLE_LINE = {
    "name": "single_line",
    "response": "The heart is a clenched, unopened fist.",
    "expected": {
        "has_preamble": False,
        "line_count": 1,
        "stanza_count": 1,
        "person": "impersonal",
    },
}

# Fixture 7: mixed person — equal counts of I and you
MIXED_PERSON = {
    "name": "mixed_person",
    "response": (
        "I see you. You see me.\n"
        "I know you. You know me.\n"
        "We end where we began."
    ),
    "expected": {
        "has_preamble": False,
        # Should classify as 1st_plural (we) since pronouns 1s=2, 1p=2, 2=4 ... actually 2nd dominates
        # i,me appear 2 each; you appears 4 times; we appears 2 times
        # 1s=4 (i + me), 1p=2 (we), 2nd=4 (you)
        # max is tied between 1s and 2nd at 4. Precedence breaks tie to 1s.
        # but 4/(4+2+4) = 0.4 ≤ 0.5 so 'mixed'.
        "person": "mixed",
    },
}

# Fixture 8: compliance — over the cap
OVER_CAP = {
    "name": "over_cap",
    "response": (
        "One.\nTwo.\nThree.\nFour.\nFive.\n"
        "Six.\nSeven.\nEight.\nNine.\nTen."
    ),
    "expected": {
        "has_preamble": False,
        "line_count": 10,
        "stanza_count": 1,
    },
}

# Fixture 9: long preamble multi-line block then poem
LONG_PREAMBLE = {
    "name": "long_preamble",
    "response": (
        "Of course! I'd be happy to write a poem for you.\n"
        "Here's something I came up with:\n"
        "\n"
        "Wind across the plain,\n"
        "carrying old names.\n"
        "Nothing answers back."
    ),
    "expected": {
        "has_preamble": True,
        "line_count": 3,
        "stanza_count": 1,
    },
}

ALL_FIXTURES = [
    SIMPLE_AABB,
    WITH_PREAMBLE,
    SECOND_PERSON_FREE,
    MULTI_STANZA_3P,
    EMPTY,
    SINGLE_LINE,
    MIXED_PERSON,
    OVER_CAP,
    LONG_PREAMBLE,
]
