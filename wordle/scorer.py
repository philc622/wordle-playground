from collections import Counter

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
