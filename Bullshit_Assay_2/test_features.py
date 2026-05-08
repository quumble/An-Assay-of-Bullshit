"""
Tests for analysis.features.

These exercise structural and rule-based features that don't require
spaCy or the Brysbaert lexicon to work. POS, concreteness, and rhyme
features are tested in light fashion since they depend on external
resources.

Run with: python -m unittest analysis.tests.test_features
or via:   python run_analysis.py test
"""

import unittest
from analysis.features import (
    detect_preamble, structural_features, person_features, parse_length_cap,
    compliance, split_lines, split_stanzas,
)
from analysis.tests.fixtures import ALL_FIXTURES


class TestStructural(unittest.TestCase):
    def test_simple_4_line_poem(self):
        body = "Line one.\nLine two.\nLine three.\nLine four."
        feats = structural_features(body)
        self.assertEqual(feats["line_count"], 4)
        self.assertEqual(feats["stanza_count"], 1)
        self.assertEqual(feats["total_words"], 8)

    def test_two_stanzas(self):
        body = "First stanza line.\nAnother line.\n\nSecond stanza here.\nFinal line."
        feats = structural_features(body)
        self.assertEqual(feats["line_count"], 4)
        self.assertEqual(feats["stanza_count"], 2)

    def test_empty(self):
        feats = structural_features("")
        self.assertEqual(feats["line_count"], 0)
        self.assertEqual(feats["stanza_count"], 0)
        self.assertEqual(feats["total_words"], 0)

    def test_single_line(self):
        feats = structural_features("Just one line of poetry.")
        self.assertEqual(feats["line_count"], 1)
        self.assertEqual(feats["stanza_count"], 1)
        self.assertEqual(feats["total_words"], 5)

    def test_words_per_line_consistency(self):
        body = "One two three.\nFour five six."
        feats = structural_features(body)
        self.assertEqual(feats["line_count"], 2)
        self.assertEqual(feats["words_per_line_mean"], 3.0)
        self.assertEqual(feats["words_per_line_sd"], 0.0)


class TestPerson(unittest.TestCase):
    def test_first_singular(self):
        body = "I walk alone tonight.\nMy shadow follows me.\nMine is the silence."
        feats = person_features(body)
        self.assertEqual(feats["person"], "1st_singular")

    def test_first_plural(self):
        body = "We gather in the dark.\nOur voices rise as one.\nWe are not afraid."
        feats = person_features(body)
        self.assertEqual(feats["person"], "1st_plural")

    def test_second(self):
        body = "You walk through the door.\nYour hands tremble.\nYour gaze finds mine."
        # "mine" is 1st singular, so 2nd: 3, 1s: 1 → 2nd wins (3/4 = 0.75 > 0.5)
        feats = person_features(body)
        self.assertEqual(feats["person"], "2nd")

    def test_third(self):
        body = "He walked alone.\nShe followed him.\nThey met at dawn."
        feats = person_features(body)
        self.assertEqual(feats["person"], "3rd")

    def test_impersonal(self):
        body = "The wind blows hard.\nLeaves fall.\nNight comes."
        feats = person_features(body)
        self.assertEqual(feats["person"], "impersonal")

    def test_mixed_at_50_50(self):
        # 2 1st singular, 2 third — exactly 50%, should be mixed
        body = "I see her face.\nMy hand finds his."
        feats = person_features(body)
        # 1s: i, my = 2; 3rd: her, his = 2; total=4; max/total = 0.5 ≤ 0.5 → mixed
        self.assertEqual(feats["person"], "mixed")

    def test_pronoun_followed_by_punctuation(self):
        # "I." should still count as 1st singular pronoun
        body = "I.\nMe.\nMyself."
        feats = person_features(body)
        self.assertEqual(feats["person"], "1st_singular")
        self.assertEqual(feats["pronoun_count_1s"], 3)


class TestPreambleDetection(unittest.TestCase):
    """These tests do invoke spaCy lazily; if spaCy is unavailable, skip."""

    @classmethod
    def setUpClass(cls):
        try:
            from analysis.features import get_nlp
            get_nlp()
        except SystemExit:
            raise unittest.SkipTest("spaCy not available")

    def test_no_preamble_when_no_blank_line(self):
        body = "A short poem.\nWith no preamble."
        preamble, body_out = detect_preamble(body)
        self.assertIsNone(preamble)
        self.assertEqual(body_out, body)

    def test_with_simple_preamble(self):
        text = "Sure, here you go:\n\nThe sky is blue,\nThe field is green."
        preamble, body_out = detect_preamble(text)
        self.assertIsNotNone(preamble)
        self.assertIn("Sure", preamble)
        self.assertIn("sky", body_out)
        self.assertNotIn("Sure", body_out)


class TestCompliance(unittest.TestCase):
    def test_parse_cap(self):
        self.assertEqual(parse_length_cap("poem_write_5"), 5)
        self.assertEqual(parse_length_cap("poem_compose_10"), 10)
        self.assertEqual(parse_length_cap("poem_gimme_20"), 20)
        self.assertIsNone(parse_length_cap("poem_open"))

    def test_compliant(self):
        self.assertTrue(compliance(4, 5))
        self.assertFalse(compliance(5, 5))
        self.assertFalse(compliance(6, 5))

    def test_compliance_no_cap(self):
        self.assertIsNone(compliance(10, None))


class TestSplitting(unittest.TestCase):
    def test_split_lines_drops_blanks(self):
        self.assertEqual(split_lines("a\n\nb\n  \nc"), ["a", "b", "c"])

    def test_split_stanzas(self):
        text = "a\nb\n\nc\nd\n\n\ne"
        stanzas = split_stanzas(text)
        self.assertEqual(len(stanzas), 3)
        self.assertEqual(stanzas[0], ["a", "b"])
        self.assertEqual(stanzas[1], ["c", "d"])
        self.assertEqual(stanzas[2], ["e"])


class TestFixtures(unittest.TestCase):
    """Run all fixtures and check expected values where they don't depend on spaCy."""

    def test_all_fixtures_structural(self):
        for fix in ALL_FIXTURES:
            with self.subTest(name=fix["name"]):
                # For fixtures with known preamble, we'd need spaCy. Skip those.
                response = fix["response"]
                expected = fix["expected"]
                # Non-preamble fixtures: structural runs on full response
                # Preamble fixtures: structural will count preamble lines too
                # We use the structural counts as reported in expected
                if "line_count" in expected and not expected.get("has_preamble", False):
                    feats = structural_features(response)
                    self.assertEqual(
                        feats["line_count"], expected["line_count"],
                        f"line_count mismatch in {fix['name']}",
                    )
                    if "stanza_count" in expected:
                        self.assertEqual(
                            feats["stanza_count"], expected["stanza_count"],
                            f"stanza_count mismatch in {fix['name']}",
                        )

    def test_all_fixtures_person(self):
        for fix in ALL_FIXTURES:
            with self.subTest(name=fix["name"]):
                if "person" not in fix["expected"]:
                    continue
                # For preamble fixtures, run on the full response — preamble
                # text is conversational and shouldn't affect person heavily
                # for these fixtures, but to be safe we strip preamble manually
                # for such fixtures. Easier: only test person on no-preamble fixtures.
                if fix["expected"].get("has_preamble"):
                    continue
                feats = person_features(fix["response"])
                self.assertEqual(
                    feats["person"], fix["expected"]["person"],
                    f"person mismatch in {fix['name']}: got {feats['person']}",
                )


if __name__ == "__main__":
    unittest.main()
