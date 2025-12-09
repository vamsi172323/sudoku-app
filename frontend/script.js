// script.js

// 🚨 CRITICAL: REPLACE THESE PLACEHOLDER VALUES 🚨
// 1. Your deployed Cloud Run service URL
const BACKEND_URL = "https://sudoku-backend-service-291632986324.europe-west1.run.app/"; 
// 2. The secure API_KEY you set as an environment variable in Cloud Run
const API_KEY = "API_KEY_FOR_SUDOKU_BACKEND"; 
// --------------------------------------------------------

const SUDOKU_BOARD = document.getElementById('sudoku-grid');
const NEW_GAME_BUTTON = document.getElementById('new-game-button');
const MESSAGE_DIV = document.getElementById('message');
const DIFFICULTY_SELECT = document.getElementById('difficulty');
const BOARD_SIZE = 9;

// Stores the full solution for the current puzzle
let SOLUTION_BOARD = [];

// --- API FETCH FUNCTION ---

async function fetchNewSudoku(difficulty) {
    MESSAGE_DIV.textContent = "Loading new puzzle...";
    
    // Construct the URL with the difficulty parameter
    const url = `${BACKEND_URL}/generate-sudoku?difficulty=${difficulty}`;

    try {
        const response = await fetch(url, {
            method: 'GET',
            // CRITICAL: Include the custom API Key header for Cloud Run validation
            headers: {
                'X-Api-Key': API_KEY,
                'Content-Type': 'application/json'
            }
        });

        // Check for HTTP errors (e.g., 401 Unauthorized from your API key check)
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: `HTTP Error: ${response.status} ${response.statusText}` }));
            throw new Error(`API Error: ${errorData.error || 'Server rejected the request.'}`);
        }

        const data = await response.json();
        return data;

    } catch (error) {
        console.error("Fetch error:", error);
        MESSAGE_DIV.textContent = `Error: ${error.message}. Check the API Key and Cloud Run URL.`;
        return null;
    }
}

// --- RENDERING & GAME LOGIC ---

function createEmptyGrid() {
    SUDOKU_BOARD.innerHTML = ''; // Clear existing grid
    for (let i = 0; i < BOARD_SIZE * BOARD_SIZE; i++) {
        const cell = document.createElement('div');
        cell.classList.add('cell');
        
        // Add classes for grid section borders
        const row = Math.floor(i / BOARD_SIZE);
        const col = i % BOARD_SIZE;

        if (row % 3 === 0 && row !== 0) cell.style.borderTopWidth = '3px';
        if (col % 3 === 0 && col !== 0) cell.style.borderLeftWidth = '3px';
        
        // Use input type number for mobile-friendly input, but style it as a div
        const input = document.createElement('input');
        input.setAttribute('type', 'number');
        input.setAttribute('maxlength', '1'); // Limit input to one digit
        input.addEventListener('input', validateInput);
        
        cell.appendChild(input);
        SUDOKU_BOARD.appendChild(cell);
    }
}

function renderPuzzle(puzzleArray, solutionArray) {
    const cells = SUDOKU_BOARD.querySelectorAll('.cell > input');
    SOLUTION_BOARD = solutionArray; // Store the solution

    cells.forEach((input, index) => {
        const value = puzzleArray[index];
        
        // Clear old classes/values
        input.value = '';
        input.classList.remove('given', 'incorrect');
        
        if (value !== 0) {
            // This is a given number from the API
            input.value = value;
            input.classList.add('given');
            input.disabled = true; // Prevent editing pre-filled cells
        } else {
            // This is an empty cell for the user
            input.disabled = false;
        }
    });
    MESSAGE_DIV.textContent = `New ${DIFFICULTY_SELECT.value} game loaded!`;
}

function validateInput(event) {
    let input = event.target;
    // Ensure only one digit (1-9) is entered
    input.value = input.value.replace(/[^1-9]/g, '').slice(0, 1);
    
    // Simple self-check: check if the entered number matches the solution
    const cellIndex = Array.from(SUDOKU_BOARD.querySelectorAll('.cell > input')).indexOf(input);
    const enteredValue = parseInt(input.value);
    
    if (enteredValue && enteredValue === SOLUTION_BOARD[cellIndex]) {
        input.classList.remove('incorrect');
    } else if (enteredValue) {
        // Simple visual feedback if a number is wrong
        input.classList.add('incorrect');
    } else {
        input.classList.remove('incorrect');
    }

    checkWinCondition();
}

function checkWinCondition() {
    const cells = SUDOKU_BOARD.querySelectorAll('.cell > input');
    let solved = true;
    
    cells.forEach((input, index) => {
        // If any cell is empty or its value doesn't match the solution
        if (input.value === '' || parseInt(input.value) !== SOLUTION_BOARD[index]) {
            solved = false;
        }
    });

    if (solved) {
        MESSAGE_DIV.textContent = "🥳 CONGRATULATIONS! You solved the puzzle!";
        // Disable all cells after solving
        cells.forEach(input => input.disabled = true);
    }
}

// --- INITIALIZATION ---

async function initializeGame() {
    createEmptyGrid(); // Draw the initial 9x9 board structure
    const difficulty = DIFFICULTY_SELECT.value;
    const data = await fetchNewSudoku(difficulty);
    
    if (data) {
        // The API returns 'puzzle' and 'solution' as flattened 81-element arrays
        renderPuzzle(data.puzzle, data.solution);
    }
}

NEW_GAME_BUTTON.addEventListener('click', initializeGame);

// Start the first game when the page loads
window.onload = initializeGame;
