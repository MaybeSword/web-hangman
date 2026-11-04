# Web Hangman

A browser Hangman game. Live at https://hangman-n5f4.onrender.com. The Flask server runs all the game logic. The browser
client (HTML/CSS/JavaScript) talks to it only through a small JSON REST API.
The client does not get the hidden word until the game is over.

- `game.py`: game engine (`HangmanGame`) and word lists (`WordManager`). It does not use Flask.
- `server.py`: Flask app and REST API. It also serves the page at `/`.
- `static/`: browser client (`index.html`, `style.css`, `app.js`).
- `words/`: `easy.txt`, `medium.txt` and `hard.txt`, one word per line.
- `tests/`: unit tests, API tests and an end-to-end HTTP test.
- `SPECIFICATION.md`: the original specification. `TODO.md`: the phased plan with reduced scope.

## Install

Requires Python 3.10+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run locally

```bash
python server.py
```

Open http://127.0.0.1:5000. Debug mode stays off unless you set `FLASK_DEBUG=1`.
To use a different port, set `PORT`, for example `PORT=8000 python server.py`.

## Run the tests

```bash
python -m unittest discover -s tests -t . -v
```

## API

All bodies are JSON. Errors return `{"error": "..."}`.

| Method | Path | Success | Errors |
|---|---|---|---|
| POST | `/api/games` | 201 | 400 bad difficulty or malformed body |
| GET | `/api/games/{game_id}` | 200 | 404 unknown game |
| POST | `/api/games/{game_id}/guess` | 200 | 400 invalid letter or body, 404 unknown game, 409 duplicate guess or game already over |

### Create a game

```bash
curl -s -X POST http://127.0.0.1:5000/api/games \
  -H 'Content-Type: application/json' -d '{"difficulty":"medium"}'
```

```json
{"game_id":"Xk3vR9aQb1E","pattern":"_ _ _ _ _ _","guessed_letters":[],
 "incorrect_letters":[],"remaining_guesses":6,"status":"playing","difficulty":"medium"}
```

`difficulty` can be `easy`, `medium` or `hard`. If you leave it out, the server uses `medium`.

### Guess a letter

```bash
curl -s -X POST http://127.0.0.1:5000/api/games/Xk3vR9aQb1E/guess \
  -H 'Content-Type: application/json' -d '{"letter":"e"}'
```

```json
{"game_id":"Xk3vR9aQb1E","pattern":"_ _ _ _ e _","guessed_letters":["e"],
 "incorrect_letters":[],"remaining_guesses":6,"status":"playing","difficulty":"medium"}
```

When the game ends, `status` becomes `won` or `lost`, and the response includes `"word"`.

### Get current state

```bash
curl -s http://127.0.0.1:5000/api/games/Xk3vR9aQb1E
```

This returns the same shape as a guess response.

## Deploy to Render

1. Push this repo to GitHub.
2. In Render, create a **Web Service** from the repo, or use **Blueprint**, which reads `render.yaml`.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn --bind 0.0.0.0:$PORT --workers 1 server:app`
5. Open the `.onrender.com` URL and play a game to check that it works.

In production, gunicorn imports `server:app` directly. The `app.run(...)` block never runs, so debug mode is always off.

## Known limitations

- Games are stored in memory. They are lost when the server restarts, and Render's free tier sleeps when idle.
- Use one gunicorn worker only. Each worker has its own memory, so with more than one worker, a guess can reach a worker that doesn't know the game and get a 404.
- Finished games are never cleaned up, so memory use grows slowly over time.
- There are no accounts, leaderboard, evaluation mode, bots or terminal client. These are out of scope (see `TODO.md`).
