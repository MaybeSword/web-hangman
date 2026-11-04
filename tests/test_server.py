import random
import threading
import unittest
import json
import urllib.request

from werkzeug.serving import make_server

from game import WordManager
from server import create_app


class FixedWords(WordManager):
    def __init__(self, word):
        super().__init__(rng=random.Random(0))
        self.word = word

    def random_word(self, difficulty):
        super().random_word(difficulty)  # still validates difficulty
        return self.word


def client(word="apple"):
    return create_app(FixedWords(word)).test_client()


class ApiTests(unittest.TestCase):
    def new_game(self, c, **body):
        r = c.post("/api/games", json=body or {"difficulty": "easy"})
        self.assertEqual(r.status_code, 201)
        return r.get_json()

    def test_create_game(self):
        data = self.new_game(client())
        self.assertEqual(data["pattern"], "_ _ _ _ _")
        self.assertEqual(data["remaining_guesses"], 6)
        self.assertEqual(data["status"], "playing")
        self.assertIn("game_id", data)
        self.assertNotIn("word", data)

    def test_create_default_and_empty_body(self):
        r = client().post("/api/games")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.get_json()["difficulty"], "medium")

    def test_invalid_difficulty(self):
        r = client().post("/api/games", json={"difficulty": "extreme"})
        self.assertEqual(r.status_code, 400)
        self.assertIn("error", r.get_json())

    def test_malformed_create_body(self):
        r = client().post("/api/games", data="{oops", content_type="application/json")
        self.assertEqual(r.status_code, 400)

    def test_get_state_and_unknown_id(self):
        c = client()
        gid = self.new_game(c)["game_id"]
        self.assertEqual(c.get(f"/api/games/{gid}").status_code, 200)
        self.assertEqual(c.get("/api/games/nope").status_code, 404)
        self.assertEqual(c.post("/api/games/nope/guess", json={"letter": "a"}).status_code, 404)

    def test_guess_correct_and_incorrect(self):
        c = client()
        gid = self.new_game(c)["game_id"]
        d = c.post(f"/api/games/{gid}/guess", json={"letter": "p"}).get_json()
        self.assertEqual(d["pattern"], "_ p p _ _")
        d = c.post(f"/api/games/{gid}/guess", json={"letter": "z"}).get_json()
        self.assertEqual(d["incorrect_letters"], ["z"])
        self.assertEqual(d["remaining_guesses"], 5)

    def test_bad_guesses(self):
        c = client()
        gid = self.new_game(c)["game_id"]
        url = f"/api/games/{gid}/guess"
        self.assertEqual(c.post(url, json={"letter": "ab"}).status_code, 400)
        self.assertEqual(c.post(url, json={"letter": 5}).status_code, 400)
        self.assertEqual(c.post(url, json={}).status_code, 400)
        self.assertEqual(c.post(url, data="x", content_type="text/plain").status_code, 400)
        c.post(url, json={"letter": "a"})
        r = c.post(url, json={"letter": "A"})
        self.assertEqual(r.status_code, 409)

    def test_win_reveals_word(self):
        c = client("cat")
        gid = self.new_game(c)["game_id"]
        for ch in "ca":
            d = c.post(f"/api/games/{gid}/guess", json={"letter": ch}).get_json()
            self.assertNotIn("word", d)
        d = c.post(f"/api/games/{gid}/guess", json={"letter": "t"}).get_json()
        self.assertEqual(d["status"], "won")
        self.assertEqual(d["word"], "cat")
        r = c.post(f"/api/games/{gid}/guess", json={"letter": "z"})
        self.assertEqual(r.status_code, 409)

    def test_loss_and_no_leak_while_playing(self):
        c = client("cat")
        gid = self.new_game(c)["game_id"]
        for ch in "bdefg":
            d = c.post(f"/api/games/{gid}/guess", json={"letter": ch}).get_json()
            self.assertNotIn("word", d)
            self.assertNotIn("cat", json.dumps(c.get(f"/api/games/{gid}").get_json()))
        d = c.post(f"/api/games/{gid}/guess", json={"letter": "h"}).get_json()
        self.assertEqual(d["status"], "lost")
        self.assertEqual(d["word"], "cat")

    def test_index_served(self):
        r = client().get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"Hangman", r.data)


class EndToEndTest(unittest.TestCase):
    """Play a full game over real HTTP against a running server."""

    def test_full_game_over_http(self):
        server = make_server("127.0.0.1", 0, create_app(FixedWords("dog")))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{server.server_port}"

        def post(path, body):
            req = urllib.request.Request(base + path, data=json.dumps(body).encode(),
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req) as r:
                return json.loads(r.read())

        try:
            gid = post("/api/games", {"difficulty": "hard"})["game_id"]
            for ch in "dog":
                state = post(f"/api/games/{gid}/guess", {"letter": ch})
            self.assertEqual(state["status"], "won")
            self.assertEqual(state["word"], "dog")
        finally:
            server.shutdown()


if __name__ == "__main__":
    unittest.main()
