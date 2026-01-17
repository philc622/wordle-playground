import pytest
from scorer import scoreGuess

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
    ("MOTOR", "ROTOR", "02222"), # Corrected based on algorithm
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
