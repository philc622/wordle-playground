# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Run all tests:**
```bash
python -m pytest wordle/ -v
```

**Run a single test file:**
```bash
python -m pytest wordle/test_scorer.py -v
python -m pytest wordle/test_evaluator.py -v
```

**Run the Wordle solver (single game):**
```bash
python wordle/scorer.py --solution CRANE
```

**Run the Quordle solver (4 simultaneous games):**
```bash
python wordle/scorer.py --s1 BRICK --s2 FIGHT --s3 MOUND --s4 WRONG
```

**Evaluate starting word strategies:**
```bash
python wordle/evaluator.py --num-runs 100 --words CRANE STALE
```

## Architecture

The project implements a Wordle solver in two forms: a Python CLI/library and a JavaScript web version. Both share the same core algorithm.

### Core Algorithm (Python: `wordle/scorer.py`)

Two foundational pure functions power everything:

- **`scoreGuess(guess, solution) -> str`** — Returns a 5-char string of `"0"` (gray), `"1"` (yellow), `"2"` (green). Uses a two-pass algorithm to correctly handle duplicate letters.
- **`filterCandidates(guess, score, candidates) -> List[str]`** — Filters the word list given a guess and its score, enforcing positional constraints and letter count rules.

These are composed into game classes:
- **`WordleGame`** — Single game state: tracks candidates, guesses, and solution. `suggest_guess()` picks randomly from remaining candidates.
- **`QuordleGame`** — Wraps 4 `WordleGame` instances; chooses guesses that advance multiple games simultaneously. Limit is 9 guesses.

### Strategy Evaluator (`wordle/evaluator.py`)

Runs many simulated games and reports average guess counts. Used to compare starting word effectiveness. Supports a forced first guess via `--words`.

### Web Solver (`docs/`)

A JavaScript port of the same algorithm (`docs/solver.js`) with a minimal HTML/CSS UI. Fetches `wordle-list.json` at runtime. Deployed via GitHub Pages from the `docs/` directory.

### Word List

`wordle/wordle-list.txt` — 2,311 valid 5-letter words in JSON array format. The Python code normalizes to uppercase; the JavaScript version works with lowercase. The `docs/wordle-list.json` is the same data served for the web solver.

### Key Design Notes

- The solver uses **random candidate selection**, not an optimized strategy (e.g., minimax). This means results vary between runs.
- No external dependencies — pure Python stdlib and vanilla JavaScript.
- Tests use mocking for randomness to ensure determinism.
