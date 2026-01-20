function scoreGuess(guess, solution) {
    if (guess.length !== 5 || solution.length !== 5) {
        throw new Error("Both guess and solution must be of length 5.");
    }

    if (!/^[a-zA-Z]+$/.test(guess) || !/^[a-zA-Z]+$/.test(solution)) {
        throw new Error("Both guess and solution must contain only alphabetic characters.");
    }

    guess = guess.toUpperCase();
    solution = solution.toUpperCase();

    const score = Array(5).fill('0');
    const solutionFreq = {};

    for (const char of solution) {
        solutionFreq[char] = (solutionFreq[char] || 0) + 1;
    }

    // Pass 1: Greens
    for (let i = 0; i < 5; i++) {
        if (guess[i] === solution[i]) {
            score[i] = '2';
            solutionFreq[guess[i]] -= 1;
        }
    }

    // Pass 2: Yellows
    for (let i = 0; i < 5; i++) {
        if (score[i] !== '2') {
            const char = guess[i];
            if (solutionFreq[char] > 0) {
                score[i] = '1';
                solutionFreq[char] -= 1;
            }
        }
    }

    return score.join("");
}

function filterCandidates(guess, score, candidates) {
    if (guess.length !== 5 || score.length !== 5) {
        throw new Error("Guess and score must both be of length 5.");
    }
    if (!/^[a-zA-Z]+$/.test(guess)) {
        throw new Error("Guess must contain only alphabetic characters.");
    }
    if (!/^[012]+$/.test(score)) {
        throw new Error("Score must only contain characters '0', '1', or '2'.");
    }

    guess = guess.toUpperCase();

    const mustBe = Array(5).fill(null);
    const forbidAtPos = Array.from({ length: 5 }, () => new Set());
    const greens = {};
    const yellows = {};
    const grays = {};

    for (let i = 0; i < 5; i++) {
        const gch = guess[i];
        const s = score[i];
        if (s === '2') {
            mustBe[i] = gch;
            greens[gch] = (greens[gch] || 0) + 1;
        } else if (s === '1') {
            forbidAtPos[i].add(gch);
            yellows[gch] = (yellows[gch] || 0) + 1;
        } else if (s === '0') {
            grays[gch] = (grays[gch] || 0) + 1;
        }
    }

    const minCount = {};
    const maxCount = {};
    const allLetters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";

    for (const letter of allLetters) {
        minCount[letter] = (greens[letter] || 0) + (yellows[letter] || 0);
        if (grays[letter] > 0) {
            maxCount[letter] = minCount[letter];
        } else {
            maxCount[letter] = 5;
        }
    }

    return candidates.filter(candidate => {
        const w = candidate.toUpperCase();

        for (let i = 0; i < 5; i++) {
            if (mustBe[i] !== null && w[i] !== mustBe[i]) {
                return false;
            }
        }

        for (let i = 0; i < 5; i++) {
            if (forbidAtPos[i].has(w[i])) {
                return false;
            }
        }

        const wCounts = {};
        for (const char of w) {
            wCounts[char] = (wCounts[char] || 0) + 1;
        }

        for (const letter of allLetters) {
            const count = wCounts[letter] || 0;
            if (!(count >= minCount[letter] && count <= maxCount[letter])) {
                return false;
            }
        }

        return true;
    });
}

async function getWordList() {
    try {
        const response = await fetch('wordle-list.txt');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const text = await response.text();
        return JSON.parse(text);
    } catch (e) {
        console.error("Error fetching or parsing word list:", e);
        return [];
    }
}

async function solve() {
    const solutionInput = document.getElementById('solution');
    const resultsDiv = document.getElementById('results');
    const solution = solutionInput.value.toUpperCase();

    if (solution.length !== 5 || !/^[a-zA-Z]+$/.test(solution)) {
        resultsDiv.innerHTML = "Solution must be a 5-letter alphabetic word.";
        return;
    }

    resultsDiv.innerHTML = `Trying to guess the word: ${solution}<br>`;

    const wordList = await getWordList();
    if (wordList.length === 0) {
        resultsDiv.innerHTML += "Could not load word list.";
        return;
    }

    let candidates = [...wordList];
    const usedGuesses = new Set();
    let guessCount = 0;

    resultsDiv.innerHTML += `Starting with ${candidates.length} possible words.<br>`;

    while (true) {
        if (candidates.length === 0) {
            resultsDiv.innerHTML += "No more candidate words left. Something went wrong.<br>";
            break;
        }

        const availableCandidates = candidates.filter(c => !usedGuesses.has(c));
        if (availableCandidates.length === 0) {
            resultsDiv.innerHTML += "Ran out of unique words to guess from the candidate list.<br>";
            break;
        }

        const guess = availableCandidates[Math.floor(Math.random() * availableCandidates.length)];
        usedGuesses.add(guess);
        guessCount++;

        const score = scoreGuess(guess, solution);

        resultsDiv.innerHTML += `Guess ${guessCount}: ${guess} -> Score: ${score}<br>`;

        if (score === "22222") {
            resultsDiv.innerHTML += `Successfully guessed the word '${guess}' in ${guessCount} tries!<br>`;
            break;
        }

        candidates = filterCandidates(guess, score, candidates);
        resultsDiv.innerHTML += `  ${candidates.length} candidates remaining.<br>`;
    }
}

document.getElementById('solve').addEventListener('click', solve);
