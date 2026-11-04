# TODO — Web Hangman (Reduced Scope)

Implementation roadmap for a web-based Hangman game: a Flask backend plus an
HTML/CSS/JavaScript browser client, deployed to the cloud.

The authoritative requirements are in `SPECIFICATION.md`. This plan covers only
the parts of that specification that are in scope (see "Out of Scope" below).

> Note: the previous TODO had every phase checked off, but that code is not in
> this project folder. Every in-scope task starts unchecked here and is checked
> only after it is implemented **and verified** in this folder.

## Implementation Rules

- Implement one phase at a time; complete and test it before starting the next.
- Keep the game engine independent of Flask and the browser UI.
- The server is authoritative; the client holds no game logic beyond display.
- Never expose the hidden word while `status` is `playing`.
- Do not change the REST API in `SPECIFICATION.md` unless necessary; document
  any deviation in the README.
- Add tests with each phase. Check a task off only after it is verified.

---

## Phase 1 — Game Engine and Word Management

### Tasks

- [x] Create project structure (`game.py`, `words/`, `tests/`).
- [x] Add `words/easy.txt`, `words/medium.txt`, `words/hard.txt`.
- [x] Implement `HangmanGame` class (no Flask/UI imports).
- [x] Store hidden word internally; track guessed and incorrect letters.
- [x] Allow six incorrect guesses (configurable maximum).
- [x] Validate single alphabetic letter guesses (case-insensitive).
- [x] Reject duplicate guesses without changing state.
- [x] Produce the masked pattern (`"_ e _ _ e"` format).
- [x] Detect win and loss; status values `playing`, `won`, `lost`.
- [x] Reject guesses after the game has ended.
- [x] Return a client-safe state dictionary; include `word` only when finished.
- [x] Implement `WordManager`: load lists, keep alphabetic words only, lowercase,
      de-duplicate.
- [x] Random word selection by difficulty; injectable RNG for tests.
- [x] Reject invalid difficulty cleanly.
- [x] Unit tests for engine and word manager (no server required).

### Completion Criteria

A full game can be played and tested without a web server. All core rules and
word-loading behavior are covered by unit tests.

---

## Phase 2 — Flask Server and REST API

### Tasks

- [x] Create `server.py` with a Flask app factory.
- [x] In-memory storage for active games with unique, unguessable IDs.
- [x] `POST /api/games` (body `{"difficulty": ...}`, default `medium`).
- [x] `GET /api/games/{game_id}`.
- [x] `POST /api/games/{game_id}/guess` (body `{"letter": ...}`).
- [x] Validate difficulty and guess input; handle malformed JSON.
- [x] Consistent JSON responses and error bodies.
- [x] Appropriate status codes (201, 200, 400, 404, 409).
- [x] 404 for unknown game IDs.
- [x] Never leak the hidden word during an active game.
- [x] Serve `static/index.html` at `/`.
- [x] Add `requirements.txt`.
- [x] API tests using the Flask test client.

### Completion Criteria

A complete game can be played with `curl` alone.

---

## Phase 3 — Browser Client

### Tasks

- [x] `static/index.html`, `static/style.css`, `static/app.js`.
- [x] Difficulty selector and New Game button.
- [x] Display masked word, guessed letters, incorrect letters, remaining guesses.
- [x] On-screen alphabet keyboard; disable already-guessed letters.
- [x] Physical keyboard input.
- [x] Graphical Hangman drawing that updates after incorrect guesses.
- [x] Win/loss messages; reveal word only from the server's final response.
- [x] Communicate only via `fetch()` to the REST API.
- [x] Show server/network errors to the user.
- [x] Responsive layout for desktop and mobile widths.

### Completion Criteria

A player can play a full game in a browser. No hidden word exists in browser
JavaScript before the game ends.

---

## Phase 4 — Testing and Debugging

### Tasks

- [x] Engine and word-manager tests complete.
- [x] API tests: duplicate, invalid letter, invalid difficulty, unknown ID,
      malformed body, guess after game over.
- [x] Win and loss paths through the API.
- [x] Answer-disclosure tests (no `word` while `playing`).
- [x] End-to-end test: create game and play to completion over HTTP.
- [x] Browser client manual/automated check (load page, play a game, no console
      errors, mobile width).
- [x] Fix any bugs found; record notable fixes.

### Completion Criteria

Major user flows and failure cases are covered by automated tests, and the
browser client has been exercised against a running server.

---

## Phase 5 — Cloud Deployment

### Tasks

- [x] Add a production WSGI server (`gunicorn`) to `requirements.txt`.
- [x] Add deployment config (e.g. `Procfile` / `render.yaml`) and Python version.
- [x] Read port/host from environment; disable debug in production.
- [x] Note: in-memory games are per process — run a single worker (or document
      the limitation).
- [ ] Deploy to a cloud host (e.g. Render free tier).
- [ ] Smoke-test the deployed URL (page loads, game playable).
- [x] `README.md`: install, run locally, test, API summary, deploy steps.

### Completion Criteria

The game is reachable at a public URL and playable end to end.

---

## Out of Scope

These items from the original TODO / specification are **out of scope** and
will not be implemented:

- ~~Human terminal client (`terminal_client.py`)~~ — out of scope
- ~~Reference automated clients (`random_bot.py`, `frequency_bot.py`)~~ — out of scope
- ~~Dictionary-based bot (`dictionary_bot.py`)~~ — out of scope
- ~~Student bot documentation~~ — out of scope
- ~~Evaluation mode (`/api/evaluation/*`)~~ — out of scope
- ~~Scoring system~~ — out of scope
- ~~Leaderboard (`/api/leaderboard`, browser leaderboard view)~~ — out of scope
- ~~Evaluation integrity / anti-cheating safeguards~~ — out of scope
- ~~Logging and replay (`/log`, `/replay`, `replay.py`)~~ — out of scope
- ~~Optional future phases: persistent storage, accounts, tournaments,
  advanced bot analysis, multiplayer~~ — out of scope
