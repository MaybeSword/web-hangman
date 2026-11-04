import random
import tempfile
import unittest
from pathlib import Path

from game import (DuplicateGuess, GameOver, HangmanGame, InvalidDifficulty,
                  InvalidGuess, WordManager)


class HangmanGameTests(unittest.TestCase):
    def test_initial_state(self):
        g = HangmanGame("apple")
        s = g.to_dict()
        self.assertEqual(s["pattern"], "_ _ _ _ _")
        self.assertEqual(s["remaining_guesses"], 6)
        self.assertEqual(s["status"], "playing")
        self.assertNotIn("word", s)

    def test_correct_guess_reveals_all_positions(self):
        g = HangmanGame("apple")
        self.assertTrue(g.guess("P"))
        self.assertEqual(g.pattern, "_ p p _ _")
        self.assertEqual(g.remaining_guesses, 6)

    def test_incorrect_guess(self):
        g = HangmanGame("apple")
        self.assertFalse(g.guess("z"))
        self.assertEqual(g.incorrect_letters, ["z"])
        self.assertEqual(g.remaining_guesses, 5)

    def test_invalid_guesses(self):
        g = HangmanGame("apple")
        for bad in ["", "ab", "1", "!", " ", None, "é"]:
            with self.assertRaises(InvalidGuess):
                g.guess(bad)
        self.assertEqual(g.guessed_letters, [])

    def test_duplicate_guess_rejected_without_state_change(self):
        g = HangmanGame("apple")
        g.guess("z")
        with self.assertRaises(DuplicateGuess):
            g.guess("Z")
        self.assertEqual(g.remaining_guesses, 5)

    def test_win(self):
        g = HangmanGame("cat")
        for ch in "cat":
            g.guess(ch)
        s = g.to_dict()
        self.assertEqual(s["status"], "won")
        self.assertEqual(s["word"], "cat")

    def test_loss_after_six_incorrect(self):
        g = HangmanGame("cat")
        for ch in "bdefg":
            g.guess(ch)
        self.assertEqual(g.status, "playing")
        self.assertNotIn("word", g.to_dict())
        g.guess("h")
        s = g.to_dict()
        self.assertEqual(s["status"], "lost")
        self.assertEqual(s["remaining_guesses"], 0)
        self.assertEqual(s["word"], "cat")

    def test_no_guess_after_game_over(self):
        g = HangmanGame("a")
        g.guess("a")
        with self.assertRaises(GameOver):
            g.guess("b")

    def test_bad_word_rejected(self):
        with self.assertRaises(ValueError):
            HangmanGame("two words")


class WordManagerTests(unittest.TestCase):
    def test_loads_real_lists(self):
        wm = WordManager()
        for d in ("easy", "medium", "hard"):
            word = wm.random_word(d)
            self.assertIn(word, wm.words[d])
            self.assertTrue(word.isalpha())

    def test_filters_and_dedupes(self):
        with tempfile.TemporaryDirectory() as tmp:
            for d in ("easy", "medium", "hard"):
                Path(tmp, f"{d}.txt").write_text("Cat\ncat\n\nbad-word\nd0g\n  fish \n")
            wm = WordManager(tmp)
            self.assertEqual(wm.words["easy"], ["cat", "fish"])

    def test_invalid_difficulty(self):
        with self.assertRaises(InvalidDifficulty):
            WordManager().random_word("extreme")

    def test_seeded_rng_is_deterministic(self):
        a = WordManager(rng=random.Random(1)).random_word("hard")
        b = WordManager(rng=random.Random(1)).random_word("hard")
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
