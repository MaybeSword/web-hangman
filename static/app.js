// Browser client: talks to the server only through fetch(). It never knows the
// hidden word; the server sends `word` only after the game has ended.
(function () {
  "use strict";

  const $ = (id) => document.getElementById(id);
  const parts = document.querySelectorAll("#gallows .part");
  const MAX_WRONG = parts.length; // 6
  let gameId = null;
  let state = null;
  let busy = false;

  // Build the A–Z on-screen keyboard.
  const keyboard = $("keyboard");
  for (const ch of "abcdefghijklmnopqrstuvwxyz") {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = ch;
    b.dataset.letter = ch;
    b.addEventListener("click", () => guess(ch));
    keyboard.appendChild(b);
  }

  async function api(path, body) {
    const res = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || `Server error (${res.status})`);
    return data;
  }

  async function newGame() {
    setMessage("Starting…");
    try {
      const data = await api("/api/games", { difficulty: $("difficulty").value });
      gameId = data.game_id;
      render(data);
    } catch (err) {
      setMessage(err.message, "error");
    }
  }

  async function guess(letter) {
    if (!gameId || busy || !state || state.status !== "playing") return;
    if (state.guessed_letters.includes(letter)) return;
    busy = true;
    try {
      const data = await api(`/api/games/${encodeURIComponent(gameId)}/guess`, { letter });
      render(data);
    } catch (err) {
      setMessage(err.message, "error");
    } finally {
      busy = false;
    }
  }

  function render(data) {
    state = data;
    $("pattern").textContent = data.pattern;
    $("remaining").textContent = data.remaining_guesses;
    $("guessed").textContent = data.guessed_letters.join(" ").toUpperCase() || "–";
    $("incorrect").textContent = data.incorrect_letters.join(" ").toUpperCase() || "–";

    const wrong = MAX_WRONG - data.remaining_guesses;
    parts.forEach((p, i) => p.classList.toggle("shown", i < wrong));

    const over = data.status !== "playing";
    for (const b of keyboard.children) {
      const l = b.dataset.letter;
      const guessed = data.guessed_letters.includes(l);
      b.disabled = guessed || over;
      b.classList.toggle("hit", guessed && !data.incorrect_letters.includes(l));
      b.classList.toggle("miss", data.incorrect_letters.includes(l));
    }

    if (data.status === "won") setMessage(`You won! The word was “${data.word}”.`, "won");
    else if (data.status === "lost") setMessage(`You lost. The word was “${data.word}”.`, "lost");
    else setMessage("");
  }

  function setMessage(text, kind) {
    const m = $("message");
    m.textContent = text;
    m.className = "message" + (kind ? " " + kind : "");
  }

  $("new-game").addEventListener("click", newGame);
  document.addEventListener("keydown", (e) => {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    if (e.target.tagName === "SELECT") return;
    const k = e.key.toLowerCase();
    if (k.length === 1 && k >= "a" && k <= "z") guess(k);
  });

  newGame();
})();
