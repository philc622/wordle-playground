import argparse
import json
import random
from collections import Counter
from typing import List, Set

def scoreGuess(guess: str, solution: str) -> str:
    """
    Computes a 5-character score string comparing a guess to the solution using Wordle-like rules.
    """
    if len(guess) != 5 or len(solution) != 5:
        raise ValueError("Both guess and solution must be of length 5.")

    if not guess.isalpha() or not solution.isalpha():
        raise ValueError("Both guess and solution must contain only alphabetic characters.")

    guess = guess.upper()
    solution = solution.upper()

    score = ['0'] * 5
    solution_freq = Counter(solution)

    # Pass 1: Greens
    for i in range(5):
        if guess[i] == solution[i]:
            score[i] = '2'
            solution_freq[guess[i]] -= 1

    # Pass 2: Yellows
    for i in range(5):
        if score[i] != '2':
            ch = guess[i]
            if solution_freq.get(ch, 0) > 0:
                score[i] = '1'
                solution_freq[ch] -= 1

    return "".join(score)

def filterCandidates(guess: str, score: str, candidates: List[str]) -> List[str]:
    """
    Filters a list of candidate words based on a guess and its corresponding score.
    """
    if len(guess) != 5 or len(score) != 5:
        raise ValueError("Guess and score must both be of length 5.")
    if not guess.isalpha():
        raise ValueError("Guess must contain only alphabetic characters.")
    if not all(c in '012' for c in score):
        raise ValueError("Score must only contain characters '0', '1', or '2'.")

    guess = guess.upper()

    # 1. Build positional constraints and letter statistics
    must_be = [None] * 5
    forbid_at_pos: List[Set[str]] = [set() for _ in range(5)]

    greens = Counter()
    yellows = Counter()
    grays = Counter()

    for i, (gch, s) in enumerate(zip(guess, score)):
        if s == '2':
            must_be[i] = gch
            greens[gch] += 1
        elif s == '1':
            forbid_at_pos[i].add(gch)
            yellows[gch] += 1
        elif s == '0':
            forbid_at_pos[i].add(gch)
            grays[gch] += 1

    min_count = Counter()
    max_count = {}

    all_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for letter in all_letters:
        min_count[letter] = greens[letter] + yellows[letter]
        if grays[letter] > 0:
            max_count[letter] = min_count[letter]
        else:
            max_count[letter] = 5 # No upper bound from this clue

    # 2. Filter candidates
    result = []
    for candidate in candidates:
        # Assuming candidates are already valid 5-letter words
        # if len(candidate) != 5 or not candidate.isalpha():
        #     continue

        w = candidate.upper()

        ok = True

        # Greens check
        for i in range(5):
            if must_be[i] is not None and w[i] != must_be[i]:
                ok = False
                break
        if not ok:
            continue

        # Positional exclusions (covers both '0' and '1')
        for i in range(5):
            if w[i] in forbid_at_pos[i]:
                ok = False
                break
        if not ok:
            continue

        # Letter count bounds
        w_counts = Counter(w)
        for letter in all_letters:
            count = w_counts[letter]
            if not (min_count[letter] <= count <= max_count[letter]):
                ok = False
                break

        if ok:
            result.append(candidate)

    return result


def main():
    """
    Main program loop for the Wordle solver.
    """
    parser = argparse.ArgumentParser(description="A simple Wordle solver.")
    parser.add_argument("solution", type=str, help="The 5-letter solution word.")
    args = parser.parse_args()

    solution = args.solution.upper()
    if len(solution) != 5 or not solution.isalpha():
        raise ValueError("Solution must be a 5-letter alphabetic word.")

    try:
        with open("wordle/wordle-list.txt", "r") as f:
            word_list = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading or parsing wordle-list.txt: {e}")
        return

    candidates = word_list
    used_guesses = set()
    guess_count = 0

    print(f"Trying to guess the word: {solution}")
    print(f"Starting with {len(candidates)} possible words.")

    while True:
        if not candidates:
            print("No more candidate words left. Something went wrong.")
            break

        available_candidates = [c for c in candidates if c not in used_guesses]
        if not available_candidates:
            print("Ran out of unique words to guess from the candidate list. Something is wrong.")
            break

        guess = random.choice(available_candidates)
        used_guesses.add(guess)
        guess_count += 1

        score = scoreGuess(guess, solution)

        print(f"Guess {guess_count}: {guess} -> Score: {score}")

        if score == "22222":
            print(f"Successfully guessed the word '{guess}' in {guess_count} tries!")
            break

        candidates = filterCandidates(guess, score, candidates)
        print(f"  {len(candidates)} candidates remaining.")


if __name__ == "__main__":
    main()
