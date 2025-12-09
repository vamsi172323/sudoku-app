# app.py
from flask import Flask, jsonify, request
import random
import copy
from time import time
from flask_cors import CORS # Required for cross-origin requests from your Cloud Storage frontend

app = Flask(__name__)
# Enable CORS for all domains, necessary for a static frontend calling a Cloud Run API
CORS(app)

# Constants
BOARD_SIZE = 9
BOX_SIZE = 3

# --- Sudoku Generation Functions ---
# Note: A real-world generator is complex (ensuring unique solutions, etc.).
# This is a MINIMAL version using backtracking to generate a full board and then remove cells.

def solve_board(board):
    """Simple backtracking solver to find the next empty spot and fill it."""
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == 0:
                # Try numbers 1 to 9 in random order for variation
                for num in random.sample(range(1, 10), 9):
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if solve_board(board):
                            return True
                        board[row][col] = 0 # Backtrack
                return False
    return True # Board is full

def is_valid(board, row, col, num):
    """Check if 'num' is valid at board[row][col] according to Sudoku rules."""
    
    # Check row and column
    for i in range(BOARD_SIZE):
        if board[row][i] == num or board[i][col] == num:
            return False
            
    # Check 3x3 box
    start_row = row - row % BOX_SIZE
    start_col = col - col % BOX_SIZE
    for i in range(BOX_SIZE):
        for j in range(BOX_SIZE):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def generate_full_board():
    """Generates a complete, valid Sudoku board."""
    board = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
    # We use the solver to generate the full board
    solve_board(board)
    return board

def generate_puzzle(difficulty='medium'):
    """Generates the puzzle by removing cells from a solved board."""
    
    # Get a solved board
    full_board = generate_full_board()
    # Create a copy for the puzzle the user will solve
    puzzle_board = copy.deepcopy(full_board)
    
    # Define how many cells to remove based on difficulty
    # Adjust these numbers to fine-tune difficulty
    holes_map = {
        'easy': 35,
        'medium': 45,
        'hard': 55
    }
    num_holes = holes_map.get(difficulty.lower(), 45) # Default to medium
    
    cells_to_remove = random.sample(range(81), num_holes)
    
    for index in cells_to_remove:
        row, col = divmod(index, BOARD_SIZE)
        puzzle_board[row][col] = 0
        
    return puzzle_board, full_board # Puzzle for user, Solution for validation

# --- Flask Routes ---

@app.route('/generate-sudoku', methods=['GET'])
def get_sudoku():
    """API endpoint to generate a Sudoku puzzle."""
    difficulty = request.args.get('difficulty', 'medium')
    
    if difficulty.lower() not in ['easy', 'medium', 'hard']:
        return jsonify({"error": "Invalid difficulty. Choose 'easy', 'medium', or 'hard'."}), 400
    
    # Generate the boards
    puzzle, solution = generate_puzzle(difficulty)
    
    # Flatten the 9x9 list of lists into a single 81-element list for easier frontend handling
    puzzle_flat = [cell for row in puzzle for cell in row]
    solution_flat = [cell for row in solution for cell in row]
    
    # Return the data as JSON
    return jsonify({
        "difficulty": difficulty,
        "puzzle": puzzle_flat,
        "solution": solution_flat
    })

@app.route('/', methods=['GET'])
def home():
    """Simple health check endpoint."""
    return "Sudoku Generator API is running!"

if __name__ == '__main__':
    # Use 0.0.0.0 and the PORT environment variable for Cloud Run
    # Gunicorn (in Dockerfile) will manage this in production, but this is for local testing
    app.run(debug=True, host='0.0.0.0', port=8080)
