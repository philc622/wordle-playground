import argparse
import json
import random
import sys
import os

# Add the root directory to sys.path to allow absolute imports if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from wordle.scorer import WordleGame
except ImportError:
    # Fallback for running directly from the wordle directory
    from scorer import WordleGame

def simulate_game(solution, word_list, first_guess=None):
    """
    Simulates a single Wordle game for a given solution and word list.
    Optionally starts with a specific first guess.
    """
    game = WordleGame(solution, word_list.copy())

    if first_guess:
        game.guess_count += 1
        game.guess_and_update(first_guess)
        if game.solved:
            return game.guess_count

    while not game.solved:
        try:
            guess = game.suggest_guess()
        except ValueError:
            # Should not happen as long as the solution is in the word_list
            break
        game.guess_count += 1
        game.guess_and_update(guess)
        if game.guess_count > 100: # Safety break
            break
    return game.guess_count

def evaluate_strategy(word_list, num_runs, first_guess=None):
    """
    Runs num_runs simulations and returns the average number of guesses.
    If first_guess is None, the solver uses its default suggestion for each guess.
    """
    total_guesses = 0
    for _ in range(num_runs):
        solution = random.choice(word_list)
        total_guesses += simulate_game(solution, word_list, first_guess)
    return total_guesses / num_runs

def main():
    parser = argparse.ArgumentParser(description="Evaluate Wordle strategies.")
    parser.add_argument("--num-runs", type=int, default=100, help="Number of runs to average (default: 100)")
    parser.add_argument("--words", nargs="+", help="Specific first guesses to evaluate")
    args = parser.parse_args()

    # Determine the path to wordle-list.txt relative to this script
    word_list_path = os.path.join(os.path.dirname(__file__), "wordle-list.txt")
    try:
        with open(word_list_path, "r") as f:
            # Normalize all words to uppercase to ensure consistent behavior
            word_list = [w.upper() for w in json.load(f)]
    except Exception as e:
        print(f"Error loading word list from {word_list_path}: {e}")
        return

    word_set = set(word_list)

    if not args.words:
        # Strategy 1: Baseline with random first guess for each run
        avg = evaluate_strategy(word_list, args.num_runs)
        print(f"Average number of guesses (random first guess) over {args.num_runs} runs: {avg:.2f}")
    else:
        # Strategy 2: Evaluate each provided word as a first guess
        for word in args.words:
            word_upper = word.upper()
            # Basic validation: check if the word is in the list
            if word_upper not in word_set:
                print(f"Warning: '{word}' is not in the word list.")

            avg = evaluate_strategy(word_list, args.num_runs, first_guess=word_upper)
            print(f"Average number of guesses (starting with '{word_upper}') over {args.num_runs} runs: {avg:.2f}")

if __name__ == "__main__":
    main()
