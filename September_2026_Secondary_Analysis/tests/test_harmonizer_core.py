import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve()
SCRIPTS = HERE.parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from harmonizer_core import (
    basic_body_features,
    looks_like_preamble,
    opening_features,
    parse_surface,
    pronoun_features,
)


class TestSurfaceParser(unittest.TestCase):
    def test_preamble_not_title(self):
        text = "Here is a short poem:\n\nThe sun dips low,\nThe stars appear."
        p = parse_surface(text)
        self.assertTrue(p.preamble_present)
        self.assertFalse(p.title_present)
        self.assertEqual(p.creative_body, "The sun dips low,\nThe stars appear.")

    def test_preamble_then_markdown_title(self):
        text = "Here's a poem:\n\n**The Quiet Hour**\n\nThe sun slips low.\nStars appear."
        p = parse_surface(text)
        self.assertTrue(p.preamble_present)
        self.assertTrue(p.title_present)
        self.assertEqual(p.title_text, "**The Quiet Hour**")
        self.assertEqual(p.creative_body, "The sun slips low.\nStars appear.")

    def test_markdown_heading_title_without_blank(self):
        text = "# The Lighthouse Keeper\nFor forty years, Marcus tended the light."
        p = parse_surface(text)
        self.assertFalse(p.preamble_present)
        self.assertTrue(p.title_present)
        self.assertEqual(p.creative_body, "For forty years, Marcus tended the light.")

    def test_plain_title(self):
        text = "The Quiet Hour\n\nThe sun slips low.\nThe stars appear."
        p = parse_surface(text)
        self.assertTrue(p.title_present)
        self.assertEqual(p.creative_body, "The sun slips low.\nThe stars appear.")

    def test_poem_line_not_false_title_without_blank(self):
        text = "The sun slips low,\nThe stars appear,\nNight gathers."
        p = parse_surface(text)
        self.assertFalse(p.title_present)
        self.assertEqual(p.creative_body, text)

    def test_emphasized_poem_line_not_title_without_blank(self):
        text = "*The sun slips low,*\n*The stars appear.*"
        p = parse_surface(text)
        self.assertFalse(p.title_present)

    def test_empty_fallback_heading_only(self):
        text = "# A Title Only"
        p = parse_surface(text)
        self.assertFalse(p.title_present)
        self.assertEqual(p.creative_body, text)

    def test_framing_detection_with_markdown(self):
        self.assertTrue(looks_like_preamble("**Here is a poem:**"))

    def test_basic_features(self):
        f = basic_body_features("One two three.\nFour five.")
        self.assertEqual(f["body_word_count"], 5)
        self.assertEqual(f["body_line_count_nonempty"], 2)

    def test_pronouns(self):
        f = pronoun_features("I see you and they see me.")
        self.assertEqual(f["pronoun_1s_count"], 2)
        self.assertEqual(f["pronoun_2_count"], 1)
        self.assertEqual(f["pronoun_3_count"], 1)

    def test_opening_markdown_punctuation(self):
        f = opening_features("**Moonlight** falls softly.")
        self.assertEqual(f["first_lexical_token"], "moonlight")
        self.assertEqual(f["opening_bigram"], "moonlight falls")


if __name__ == "__main__":
    unittest.main()
