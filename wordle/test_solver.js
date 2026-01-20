// A simple assertion function for our tests
function assertEqual(actual, expected, testName) {
    const actualStr = JSON.stringify(actual);
    const expectedStr = JSON.stringify(expected);
    if (actualStr !== expectedStr) {
        console.error(`❌ FAILED: ${testName}`);
        console.error(`   Expected: ${expectedStr}`);
        console.error(`   Got: ${actualStr}`);
        throw new Error(`Assertion failed for ${testName}`);
    }
    console.log(`✅ PASSED: ${testName}`);
}

// --- Test Suite for scoreGuess ---
function testScoreGuess() {
    console.log("\n--- Running scoreGuess Tests ---");
    // All correct
    assertEqual(scoreGuess("crane", "crane"), "22222", "All letters correct and in position");
    // All present but in wrong positions
    assertEqual(scoreGuess("enarc", "crane"), "11111", "All letters present, wrong positions");
    // Some correct, some present, some absent
    assertEqual(scoreGuess("croup", "crane"), "21000", "Mixed correct, present, absent");
    // No letters in common
    assertEqual(scoreGuess("flits", "crane"), "00000", "No letters in common");
    // Duplicate letters in guess, single in solution
    assertEqual(scoreGuess("sassy", "crane"), "02000", "Duplicate in guess, single in solution");
    // Single letter in guess, duplicate in solution
    assertEqual(scoreGuess("robot", "abbot"), "01222", "Single in guess, duplicate in solution");
    // Duplicate letters in both guess and solution
    assertEqual(scoreGuess("apple", "paper"), "12100", "Duplicates in both guess and solution");
    assertEqual(scoreGuess("abbot", "robot"), "01022", "Another duplicate case");
    console.log("--- scoreGuess Tests Complete ---");
}

// --- Test Suite for filterCandidates ---
function testFilterCandidates() {
    console.log("\n--- Running filterCandidates Tests ---");
    const wordList = ["aback", "abase", "abate", "abbey", "abbot", "abhor", "abide", "crane", "sassy", "paper", "robot"];

    // Guess: "aback", Score: "22000" (vs solution "abbot")
    // Meaning: 'a' is at index 0, 'b' is at index 1. 'a', 'c', 'k' are not in the word otherwise.
    let guess1 = "aback";
    let score1 = "22000";
    let expected1 = ["abbey", "abbot"];
    assertEqual(filterCandidates(guess1, score1, wordList), expected1, "Green letters and exact count");

    // Guess: "robot", Score: "01222" (vs solution "abbot")
    // Meaning: 'o' is not at index 1, but is in the word. 'b' is at index 2. 'o' is at index 3. 't' is at index 4.
    // 'r' is not in the word.
    // 'b' is present (yellow from guess[1], green from guess[2]). 'o' is present. 't' is present.
    let guess2 = "robot";
    let score2 = "01222";
    let expected2 = ["abbot"];
    assertEqual(filterCandidates(guess2, score2, wordList), expected2, "Yellow and green letters");

    // Guess: "sassy", Solution: "abase" -> score: "11000"
    // Constraints: one 'a' is yellow, one 's' is yellow, the other 's' is gray, 'y' is gray.
    // This means there is exactly one 's' in the solution.
    let guess3 = "sassy";
    let score3 = "11000";
    let expected3 = ["abase"];
    assertEqual(filterCandidates(guess3, score3, wordList), expected3, "Complex gray/yellow with duplicates");

    console.log("--- filterCandidates Tests Complete ---");
}


// --- Run all tests ---
try {
    // In a browser, you would need to load solver.js first.
    // This script is intended for manual review or execution in an environment where the functions are available.
    // Assuming scoreGuess and filterCandidates from solver.js are loaded.
    testScoreGuess();
    testFilterCandidates();
    console.log("\n🎉 All tests passed successfully!");
} catch (e) {
    console.error("\n🔥 One or more tests failed.");
}
