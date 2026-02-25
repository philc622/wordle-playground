"""
Ranks every word in the Wordle list by its average usefulness as a guess.

"Usefulness" is defined as the total score a word achieves when guessed
against every other word in the list, where each position contributes:
  2 = green (correct letter, correct position)
  1 = yellow (correct letter, wrong position)
  0 = gray   (letter not present)

A higher total means the word reveals more information on average.
"""

import argparse
import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from wordle.scorer import scoreGuess
except ImportError:
    from scorer import scoreGuess


def score_word(word: str, word_list: list[str]) -> int:
    """Return the total score of guessing `word` against every word in the list."""
    total = 0
    for solution in word_list:
        if solution == word:
            continue
        for ch in scoreGuess(word, solution):
            total += int(ch)
    return total


def rank_words(word_list: list[str], verbose: bool = False) -> list[tuple[str, int]]:
    """
    Returns a list of (word, total_score) tuples sorted descending by score.
    """
    n = len(word_list)
    scores = []

    for i, word in enumerate(word_list):
        if verbose and i % 100 == 0:
            print(f"  Scoring word {i+1}/{n}...", end="\r", flush=True)
        total = score_word(word, word_list)
        scores.append((word, total))

    if verbose:
        print()  # newline after progress

    scores.sort(key=lambda x: x[1], reverse=True)
    return scores


def main():
    parser = argparse.ArgumentParser(
        description="Rank Wordle words by total score against the full word list."
    )
    parser.add_argument(
        "--top", type=int, default=None,
        help="Only show the top N words (default: show all)"
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Write ranked word list (one word per line) to this file"
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Show progress while scoring"
    )
    args = parser.parse_args()

    word_list_path = os.path.join(os.path.dirname(__file__), "wordle-list.txt")
    try:
        with open(word_list_path, "r") as f:
            word_list = [w.upper() for w in json.load(f)]
    except Exception as e:
        print(f"Error loading word list from {word_list_path}: {e}")
        return

    print(f"Scoring {len(word_list)} words against each other...")
    ranked = rank_words(word_list, verbose=args.verbose)

    display = ranked[:args.top] if args.top else ranked
    max_score = ranked[0][1] if ranked else 1

    print(f"\nRank  Word   Total Score")
    print(f"----  -----  -----------")
    for rank, (word, score) in enumerate(display, start=1):
        print(f"{rank:>4}  {word}  {score:>11}")

    if args.output:
        with open(args.output, "w") as f:
            for word, score in ranked:
                f.write(f"{word}\n")
        print(f"\nRanked word list written to: {args.output}")


if __name__ == "__main__":
    main()
