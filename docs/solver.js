document.addEventListener('DOMContentLoaded', () => {
    const solveButton = document.getElementById('solve-button');
    const solutionInput = document.getElementById('solution');
    const resultsDiv = document.getElementById('results');
    let wordList = [];

    // Fetch the word list
    fetch('wordle-list.json')
        .then(response => response.json())
        .then(data => {
            wordList = data;
        })
        .catch(error => {
            console.error('Error loading word list:', error);
            resultsDiv.innerHTML = '<p>Error loading word list. Please check the console.</p>';
        });

    solveButton.addEventListener('click', () => {
        const solution = solutionInput.value.trim().toUpperCase();
        if (solution.length !== 5 || !/^[A-Z]+$/.test(solution)) {
            resultsDiv.innerHTML = '<p>Please enter a valid 5-letter solution.</p>';
            return;
        }
        if (!wordList.includes(solution.toLowerCase())) {
            resultsDiv.innerHTML = `<p>The word "${solution}" is not in our word list.</p>`;
            return;
        }
        solve(solution);
    });

    function scoreGuess(guess, solution) {
        const score = new Array(5).fill('0');
        const solutionFreq = {};

        for (const char of solution) {
            solutionFreq[char] = (solutionFreq[char] || 0) + 1;
        }

        // Pass 1: Greens
        for (let i = 0; i < 5; i++) {
            if (guess[i] === solution[i]) {
                score[i] = '2';
                solutionFreq[guess[i]]--;
            }
        }

        // Pass 2: Yellows
        for (let i = 0; i < 5; i++) {
            if (score[i] !== '2') {
                const char = guess[i];
                if (solutionFreq[char] > 0) {
                    score[i] = '1';
                    solutionFreq[char]--;
                }
            }
        }
        return score.join('');
    }

    function filterCandidates(guess, score, candidates) {
        const mustBe = new Array(5).fill(null);
        const forbidAtPos = Array.from({ length: 5 }, () => new Set());
        const greens = {};
        const yellows = {};
        const grays = {};
        const minCount = {};
        const maxCount = {};

        for (let i = 0; i < 5; i++) {
            const gch = guess[i];
            const s = score[i];
            if (s === '2') {
                mustBe[i] = gch;
                greens[gch] = (greens[gch] || 0) + 1;
            } else if (s === '1') {
                forbidAtPos[i].add(gch);
                yellows[gch] = (yellows[gch] || 0) + 1;
            } else { // s === '0'
                // No positional constraint for grays, but will be used for max_count
                grays[gch] = (grays[gch] || 0) + 1;
            }
        }

        const allLetters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        for (const letter of allLetters) {
            minCount[letter] = (greens[letter] || 0) + (yellows[letter] || 0);
            if (grays[letter] > 0 && (greens[letter] > 0 || yellows[letter] > 0)) {
                maxCount[letter] = minCount[letter];
            } else if (grays[letter] > 0) {
                 maxCount[letter] = (greens[letter] || 0);
            }
            else {
                maxCount[letter] = 5; // No upper bound
            }
        }

        return candidates.filter(candidate => {
            const w = candidate.toUpperCase();

            // Greens check
            for (let i = 0; i < 5; i++) {
                if (mustBe[i] && w[i] !== mustBe[i]) {
                    return false;
                }
            }

            // Yellows positional check
             for (let i = 0; i < 5; i++) {
                if (forbidAtPos[i].has(w[i])) {
                     return false;
                }
            }


            // Letter count bounds
            const wCounts = {};
            for (const char of w) {
                wCounts[char] = (wCounts[char] || 0) + 1;
            }

            for (const letter of allLetters) {
                const count = wCounts[letter] || 0;
                if (count < minCount[letter] || count > maxCount[letter]) {
                    return false;
                }
            }

            return true;
        });
    }

    function solve(solution) {
        let candidates = [...wordList];
        let solved = false;
        let guessCount = 0;
        const usedGuesses = new Set();
        resultsDiv.innerHTML = ''; // Clear previous results

        const guessHistory = [];

        while (!solved && guessCount < 10) { // Safety break
            if (candidates.length === 0) {
                resultsDiv.innerHTML += `<p>No more candidate words left. Something went wrong.</p>`;
                break;
            }

            let availableCandidates = candidates.filter(c => !usedGuesses.has(c));
            if (availableCandidates.length === 0) {
                 resultsDiv.innerHTML += `<p>Ran out of unique words to guess.</p>`;
                 break;
            }
            // A good starting word, or a random one if it's not available
            let guess = (guessCount == 0 && availableCandidates.includes("crane")) ? "crane" : availableCandidates[Math.floor(Math.random() * availableCandidates.length)];
            usedGuesses.add(guess);
            guessCount++;

            const score = scoreGuess(guess.toUpperCase(), solution);
            const remainingCandidates = filterCandidates(guess.toUpperCase(), score, candidates);

            const resultEntry = document.createElement('div');
            resultEntry.classList.add('result-step');
            resultEntry.innerHTML = `
                <p><strong>Guess ${guessCount}:</strong> ${guess.toUpperCase()}</p>
                <p><strong>Score:</strong> ${score}</p>
                <p><strong>Candidates remaining:</strong> ${remainingCandidates.length}</p>
            `;
            resultsDiv.appendChild(resultEntry);


            if (score === "22222") {
                solved = true;
                const successMsg = document.createElement('p');
                successMsg.className = 'success';
                successMsg.textContent = `Successfully guessed the word '${guess.toUpperCase()}' in ${guessCount} tries!`;
                resultsDiv.appendChild(successMsg);
                break;
            }

            candidates = remainingCandidates;
        }

         if (!solved) {
            const errorMsg = document.createElement('p');
            errorMsg.className = 'error';
            errorMsg.textContent = 'Failed to solve the puzzle.';
            resultsDiv.appendChild(errorMsg);
        }
    }
});
