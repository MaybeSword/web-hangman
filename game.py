"""Hangman game engine and word management.

No Flask or UI imports: this module can be used and tested on its own.
"""

import random
from pathlib import Path

DIFFICULTIES = ("easy", "medium", "hard")
DEFAULT_MAX_INCORRECT = 6
WORDS_DIR = Path(__file__).parent / "words"


class GuessError(ValueError):
    """Raised for a guess that is rejected and does not change game state."""


class InvalidGuess(GuessError):
    pass


class DuplicateGuess(GuessError):
    pass


class GameOver(GuessError):
    pass


class InvalidDifficulty(ValueError):
    pass


class HangmanGame:
    def __init__(self, word, max_incorrect=DEFAULT_MAX_INCORRECT, difficulty=None):
        word = word.strip().lower()
        if not word.isalpha() or not word.isascii():
            raise ValueError("word must contain only letters a-z")
        self._word = word
        self.max_incorrect = max_incorrect
        self.difficulty = difficulty
        self.guessed_letters = []
        self.incorrect_letters = []

    @property
    def remaining_guesses(self):
        return self.max_incorrect - len(self.incorrect_letters)

    @property
    def status(self):
        if all(ch in self.guessed_letters for ch in self._word):
            return "won"
        if self.remaining_guesses <= 0:
            return "lost"
        return "playing"

    @property
    def is_over(self):
        return self.status != "playing"

    @property
    def pattern(self):
        return " ".join(ch if ch in self.guessed_letters else "_" for ch in self._word)

    def guess(self, letter):
        """Apply a guess. Returns True if correct. Raises GuessError if rejected."""
        if self.is_over:
            raise GameOver("game is already over")
        if not isinstance(letter, str):
            raise InvalidGuess("guess must be a single letter")
        letter = letter.strip().lower()
        if len(letter) != 1 or not ("a" <= letter <= "z"):
            raise InvalidGuess("guess must be a single letter a-z")
        if letter in self.guessed_letters:
            raise DuplicateGuess(f"letter '{letter}' was already guessed")
        self.guessed_letters.append(letter)
        correct = letter in self._word
        if not correct:
            self.incorrect_letters.append(letter)
        return correct

    def to_dict(self):
        """Client-safe state. The word is included only after the game ends."""
        state = {
            "pattern": self.pattern,
            "guessed_letters": list(self.guessed_letters),
            "incorrect_letters": list(self.incorrect_letters),
            "remaining_guesses": self.remaining_guesses,
            "status": self.status,
        }
        if self.difficulty:
            state["difficulty"] = self.difficulty
        if self.is_over:
            state["word"] = self._word
        return state


class WordManager:
    def __init__(self, words_dir=WORDS_DIR, rng=None):
        self.rng = rng or random.Random()
        self.words = {d: self._load(Path(words_dir) / f"{d}.txt") for d in DIFFICULTIES}
        for d, words in self.words.items():
            if not words:
                raise ValueError(f"word list for '{d}' is empty")

    @staticmethod
    def _load(path):
        seen, words = set(), []
        for line in path.read_text(encoding="utf-8").splitlines():
            w = line.strip().lower()
            if w and w.isascii() and w.isalpha() and w not in seen:
                seen.add(w)
                words.append(w)
        return words

    def random_word(self, difficulty):
        if difficulty not in self.words:
            raise InvalidDifficulty(
                f"difficulty must be one of: {', '.join(DIFFICULTIES)}"
            )
        return self.rng.choice(self.words[difficulty])
