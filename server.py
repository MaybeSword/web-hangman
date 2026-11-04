"""Flask REST server for Hangman. All game logic lives in game.py."""

import os
import secrets
import threading

from flask import Flask, jsonify, request, send_from_directory

from game import (DIFFICULTIES, DuplicateGuess, GameOver, HangmanGame,
                  InvalidGuess, WordManager)


def create_app(word_manager=None):
    app = Flask(__name__, static_folder="static", static_url_path="/static")
    app.json.sort_keys = False
    words = word_manager or WordManager()
    games = {}
    lock = threading.Lock()

    def error(message, status):
        return jsonify({"error": message}), status

    def get_json_body():
        data = request.get_json(silent=True)
        return data if isinstance(data, dict) else None

    @app.get("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    @app.post("/api/games")
    def create_game():
        data = get_json_body()
        if data is None:
            if request.get_data(as_text=True).strip():
                return error("request body must be a JSON object", 400)
            data = {}
        difficulty = data.get("difficulty", "medium")
        if difficulty not in DIFFICULTIES:
            return error(f"difficulty must be one of: {', '.join(DIFFICULTIES)}", 400)
        game = HangmanGame(words.random_word(difficulty), difficulty=difficulty)
        game_id = secrets.token_urlsafe(8)
        with lock:
            games[game_id] = game
        return jsonify({"game_id": game_id, **game.to_dict()}), 201

    @app.get("/api/games/<game_id>")
    def get_game(game_id):
        game = games.get(game_id)
        if game is None:
            return error("game not found", 404)
        return jsonify({"game_id": game_id, **game.to_dict()})

    @app.post("/api/games/<game_id>/guess")
    def guess(game_id):
        game = games.get(game_id)
        if game is None:
            return error("game not found", 404)
        data = get_json_body()
        if data is None or "letter" not in data:
            return error('request body must be JSON like {"letter": "e"}', 400)
        with lock:
            try:
                game.guess(data["letter"])
            except InvalidGuess as e:
                return error(str(e), 400)
            except (DuplicateGuess, GameOver) as e:
                return error(str(e), 409)
            state = game.to_dict()
        return jsonify({"game_id": game_id, **state})

    @app.errorhandler(404)
    def not_found(_):
        return error("not found", 404)

    @app.errorhandler(405)
    def method_not_allowed(_):
        return error("method not allowed", 405)

    return app


app = create_app()

if __name__ == "__main__":
    # Local development only. Production uses gunicorn (see README).
    debug = os.environ.get("FLASK_DEBUG") == "1"
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), debug=debug)
