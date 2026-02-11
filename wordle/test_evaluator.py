import pytest
from unittest.mock import patch
from wordle.evaluator import simulate_game, evaluate_strategy

def test_simulate_game_first_guess_correct():
    """Test that if the first guess is correct, it returns 1."""
    word_list = ["APPLE", "BANAL", "CRANE"]
    solution = "APPLE"
    guesses = simulate_game(solution, word_list, first_guess="APPLE")
    assert guesses == 1

def test_simulate_game_multiple_guesses():
    """Test that multiple guesses are counted correctly."""
    word_list = ["APPLE", "BANAL", "CRANE"]
    solution = "CRANE"

    # We'll mock WordleGame.suggest_guess to control the flow
    # Note: simulate_game creates a new WordleGame instance
    with patch('wordle.evaluator.WordleGame.suggest_guess') as mock_suggest:
        mock_suggest.side_effect = ["APPLE", "BANAL", "CRANE"]

        guesses = simulate_game(solution, word_list)

        # Should be 3: APPLE (1), BANAL (2), CRANE (3)
        assert guesses == 3
        assert mock_suggest.call_count == 3

def test_evaluate_strategy_averaging():
    """Test that evaluate_strategy correctly averages the results."""
    word_list = ["APPLE", "BANAL", "CRANE"]
    num_runs = 3

    with patch('wordle.evaluator.simulate_game') as mock_simulate:
        mock_simulate.side_effect = [2, 4, 6]
        with patch('wordle.evaluator.random.choice') as mock_choice:
            mock_choice.return_value = "APPLE"

            avg = evaluate_strategy(word_list, num_runs)

            assert avg == 4.0
            assert mock_simulate.call_count == 3

def test_simulate_game_with_provided_first_guess():
    """Test simulate_game with a forced first guess."""
    word_list = ["APPLE", "BANAL", "CRANE"]
    solution = "CRANE"

    with patch('wordle.evaluator.WordleGame.suggest_guess') as mock_suggest:
        mock_suggest.side_effect = ["APPLE", "CRANE"]

        # First guess is BANAL
        # Then APPLE
        # Then CRANE
        guesses = simulate_game(solution, word_list, first_guess="BANAL")

        assert guesses == 3
        # suggest_guess should have been called twice (for APPLE and CRANE)
        assert mock_suggest.call_count == 2
