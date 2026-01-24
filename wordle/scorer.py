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


class WordleGame:
    def __init__(self, solution: str, word_list: List[str]):
        if len(solution) != 5 or not solution.isalpha():
            raise ValueError("Solution must be a 5-letter alphabetic word.")
        self.solution = solution.upper()
        self.candidates = word_list
        self.used_guesses = set()
        self.guess_count = 0
        self.solved = False

    def suggest_guess(self) -> str:
        available_candidates = [c for c in self.candidates if c not in self.used_guesses]
        if not available_candidates:
            raise ValueError("No more candidate words to suggest.")
        return random.choice(available_candidates)

    def guess_and_update(self, guess: str):
        self.used_guesses.add(guess)
        score = scoreGuess(guess, self.solution)
        if score == "22222":
            self.solved = True
        self.candidates = filterCandidates(guess, score, self.candidates)
        return score

    def play_game(self):
        print(f"Trying to guess the word: {self.solution}")
        print(f"Starting with {len(self.candidates)} possible words.")

        while not self.solved:
            if not self.candidates:
                print("No more candidate words left. Something went wrong.")
                break

            try:
                guess = self.suggest_guess()
            except ValueError as e:
                print(e)
                break

            self.guess_count += 1
            score = self.guess_and_update(guess)
            print(f"Guess {self.guess_count}: {guess} -> Score: {score}")

            if self.solved:
                print(f"Successfully guessed the word '{guess}' in {self.guess_count} tries!")
                break

            print(f"  {len(self.candidates)} candidates remaining.")


class QuordleGame:
    def __init__(self, solutions: List[str], word_list: List[str]):
        self.games = [WordleGame(s, word_list.copy()) for s in solutions]
        self.guess_count = 0
        self.used_guesses = set()

    def suggest_guess(self) -> str:
        # For simplicity, we'll just use the suggestion from the first unsolved game.
        # A more advanced solver might try to find a word that is optimal for all games.
        for game in self.games:
            if not game.solved:
                available_candidates = [c for c in game.candidates if c not in self.used_guesses]
                if not available_candidates:
                    continue
                return random.choice(available_candidates)
        raise ValueError("No more candidate words to suggest across all games.")

    def play_game(self):
        print("--- Welcome to Quordle Solver ---")
        for i, game in enumerate(self.games):
            print(f"Game {i+1} Solution: {game.solution}")
        print("---------------------------------")

        while not all(g.solved for g in self.games):
            self.guess_count += 1

            try:
                guess = self.suggest_guess()
                self.used_guesses.add(guess)
            except ValueError as e:
                print(e)
                break

            print(f"Guess {self.guess_count}: {guess}")

            scores = []
            for i, game in enumerate(self.games):
                if not game.solved:
                    score = game.guess_and_update(guess)
                    scores.append(f"Game {i+1}: {score}")
                    if game.solved:
                        print(f"  Game {i+1} solved! Word: {game.solution}")
                else:
                    scores.append(f"Game {i+1}: SOLVED")

            print("  Scores: " + ", ".join(scores))

            if self.guess_count >= 9:
                print("\nQuordle failed to solve within 9 guesses.")
                break

        if all(g.solved for g in self.games):
            print(f"\nSuccessfully solved Quordle in {self.guess_count} guesses!")


def main():
    parser = argparse.ArgumentParser(description="A Wordle and Quordle solver.")
    # Wordle arguments
    parser.add_argument("--solution", type=str, help="The 5-letter solution word for Wordle.")
    # Quordle arguments
    parser.add_argument("--s1", type=str, help="Solution for the first Quordle game.")
    parser.add_argument("--s2", type=str, help="Solution for the second Quordle game.")
    parser.add_argument("--s3", type=str, help="Solution for the third Quordle game.")
    parser.add_argument("--s4", type=str, help="Solution for the fourth Quordle game.")

    args = parser.parse_args()

    try:
        with open("wordle/wordle-list.txt", "r") as f:
            word_list = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading or parsing wordle-list.txt: {e}")
        return

    if args.s1 and args.s2 and args.s3 and args.s4:
        # Run Quordle
        solutions = [args.s1, args.s2, args.s3, args.s4]
        game = QuordleGame(solutions, word_list)
        game.play_game()
    elif args.solution:
        # Run Wordle
        game = WordleGame(solution=args.solution, word_list=word_list)
        game.play_game()
    else:
        print("Please provide a solution for Wordle (--solution) or four solutions for Quordle (--s1, --s2, --s3, --s4).")


if __name__ == "__main__":
    main()
