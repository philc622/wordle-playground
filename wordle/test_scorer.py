import pytest
from scorer import scoreGuess, filterCandidates, main
from unittest.mock import patch, mock_open
import io
import sys
import json

# The test vectors are taken directly from the technical specification.
# Note: There is a discrepancy in the spec for the "RAISE" vs "ARISE" case.
# The spec's example asserts "11212", but its own described algorithm correctly
# yields "11222" because 'S' at index 3 is a green match. This test suite
# validates against the algorithm's correct output.
@pytest.mark.parametrize("guess, solution, expected_score", [
    # Basic correctness
    ("APPLE", "APPLE", "22222"),
    # Validated, precise set from spec
    ("CIGAR", "REACT", "10011"),
    ("SLATE", "STALE", "21212"),
    ("RAISE", "ARISE", "11222"), # Corrected based on algorithm
    # Duplicate in guess; single in solution
    ("BANAL", "CANOE", "02200"),
    # Duplicate in solution; single in guess
    # Note: The spec and a code review suggested "02122", but the algorithm
    # correctly produces "02222" as T is a green match at index 2.
    ("MOTOR", "ROTOR", "02222"),
    # Duplicates on both sides
    ("ALLEY", "BELLE", "01210"), # Corrected based on algorithm
    # All wrong letters
    ("PUFFS", "CRANE", "00000"),
    # All correct, different case
    ("apple", "APPLE", "22222"),
    # Classic Wordle example (duplicates careful)
    ("ARRAY", "CIGAR", "01020"),
    # Another duplicate-handling check
    ("SHEET", "STEEL", "20221"),
])
def test_score_guess_vectors(guess, solution, expected_score):
    assert scoreGuess(guess, solution) == expected_score

def test_invalid_length_guess():
    with pytest.raises(ValueError, match="Both guess and solution must be of length 5."):
        scoreGuess("FOUR", "APPLE")

def test_invalid_length_solution():
    with pytest.raises(ValueError, match="Both guess and solution must be of length 5."):
        scoreGuess("APPLE", "FOUR")

def test_non_alphabetic_guess():
    with pytest.raises(ValueError, match="Both guess and solution must contain only alphabetic characters."):
        scoreGuess("APPL3", "APPLE")

def test_non_alphabetic_solution():
    with pytest.raises(ValueError, match="Both guess and solution must contain only alphabetic characters."):
        scoreGuess("APPLE", "APPL3")

# Tests for filterCandidates
# Note: Several test cases from the specification had incorrect expected outputs.
# The expected values below have been corrected to align with the specified algorithm.
@pytest.mark.parametrize("guess, score, candidates, expected", [
    # Worked Example
    ("STARE", "20011", ["GREAT","SCREW","ALIGN","GIVEN","SUPER","SAVER"], ["SCREW", "SUPER"]),
    # A) Simple mix of green/yellow/gray
    ("PLANT", "21000", ["PLAZA","PEARL","PLAIN","PLATE","ALLOT"], []),
    # B) Duplicates in guess; exact count clamp via gray
    ("BALMY", "01020", ["DRAMA","SCRAM","PARAM","MAMMA","MADAM"], ["DRAMA"]),
    # C) Duplicates with mixed 2/0/1 for the same letter (exact count = 2)
    ("MUMMY", "20010", ["MAMMA","MOMMY","MADAM","MIMIC","SMELT"], ["MADAM"]),
    # D) Classic “over‑guess” limiting counts
    ("PRESS", "10020", ["SPARE","PRESS","DRESS","PRESSY","PRESSS"], []),
    # E) Both sides duplicates; single‑letter exact count via 0 + 2
    ("ARRAY", "01020", ["CIGAR","SOLAR","GUARD","RADAR","AVAST","SUGAR"], ["CIGAR","SOLAR","SUGAR"]),
    # F) All grays (quick elimination)
    ("TOUGH", "00000", ["THORN","COUGH","PATIO","MINUS","BODED"], []),
])
def test_filter_candidates_vectors(guess, score, candidates, expected):
    # Sort the lists to ensure comparison is order-independent
    assert sorted(filterCandidates(guess, score, candidates)) == sorted(expected)

def test_filter_invalid_guess_length():
    with pytest.raises(ValueError, match="Guess and score must both be of length 5."):
        filterCandidates("FOUR", "20011", ["GREAT"])

def test_filter_invalid_score_length():
    with pytest.raises(ValueError, match="Guess and score must both be of length 5."):
        filterCandidates("STARE", "2001", ["GREAT"])

def test_filter_invalid_score_char():
    with pytest.raises(ValueError, match="Score must only contain characters '0', '1', or '2'."):
        filterCandidates("STARE", "2001X", ["GREAT"])

def test_filter_non_alphabetic_guess():
    with pytest.raises(ValueError, match="Guess must contain only alphabetic characters."):
        filterCandidates("STA-E", "20011", ["GREAT"])

@patch('argparse.ArgumentParser.parse_args')
@patch('scorer.random.choice')
@patch('builtins.open', new_callable=mock_open, read_data=json.dumps(["crane", "plane", "apple"]))
def test_main_loop_success(mock_file, mock_random_choice, mock_parse_args):
    # Arrange
    # Mock command line arguments
    mock_parse_args.return_value.solution = "apple"

    # Mock the sequence of random choices to ensure a deterministic test
    mock_random_choice.side_effect = ["crane", "plane", "apple"]

    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    # Act
    main()

    # Restore stdout
    sys.stdout = old_stdout

    # Assert
    output = captured_output.getvalue()
    assert "Trying to guess the word: APPLE" in output
    assert "Guess 1: crane -> Score: 00102" in output
    assert "Guess 2: plane -> Score: 11102" in output
    assert "Guess 3: apple -> Score: 22222" in output
    assert "Successfully guessed the word 'apple' in 3 tries!" in output
