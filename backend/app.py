# app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import random
import copy

# --- 1. CONFIGURATION AND INITIALIZATION ---

app = Flask(__name__)

# Load secret key from Cloud Run environment variable.
# It's crucial to set the API_KEY env var during deployment!
EXPECTED_API_KEY = os.environ.get("API_KEY", "SET_YOUR_API_KEY_IN_ENV") 
API_KEY_HEADER = "X-Api-Key"

# Replace [YOUR_BUCKET_NAME] with your actual bucket name when you deploy
FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "https://storage.googleapis.com/sudoku-app-478802/")

# Configure CORS: ONLY allow requests from your specific Cloud Storage domain
# This handles the Access-Control-Allow-Origin header automatically.
CORS(app, resources={
    r"/*": {
        "origins": FRONTEND_ORIGIN,
        "methods": ["GET"],
        "allow_headers": [API_KEY_HEADER, "Content-Type"],
        # Max age tells the browser to cache the CORS check for 30 minutes (1800 seconds)
        "max_age": 1800 
    }
})

# --- 2. SECURITY CHECKS (Before the request is processed) ---

@app.before_request
def check_api_key():
    """Checks for the required API Key in the custom header."""
    # NOTE: This runs *after* the request is routed and the instance is started.
    # It provides protection against casual unauthorized use but consumes a cold start.
    
    # 1. CORS Pre-flight Check (OPTIONS requests)
    # Flask-CORS should handle the OPTIONS response, but we ensure it doesn't fail here.
    if request.method == 'OPTIONS':
        # Return 200 OK immediately for preflight requests. Flask-CORS handles the headers.
        return '', 200

    # 2. API Key Check
    incoming_key = request.headers.get(API_KEY_HEADER)
    
    if not incoming_key or incoming_key != EXPECTED_API_KEY:
        print(f"Unauthorized access attempt with key: {incoming_key}")
        # Return 401 and stop processing the request
        return jsonify({"error": "Unauthorized Access"}), 401


# --- 3. SUDOKU LOGIC FUNCTIONS (Simplified) ---

# Constants
BOARD_SIZE = 9
BOX_SIZE = 3

def solve_board(board):
    # (Simplified solver logic to generate a full board - keeps the file minimal)
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == 0:
                for num in random.sample(range(1, 10), 9):
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if solve_board(board):
                            return True
                        board[row][col] = 0
                return False
    return True

def is_valid(board, row, col, num):
    # (Standard Sudoku validation check)
    for i in range(BOARD_SIZE):
        if board[row][i] == num or board[i][col] == num:
            return False
    start_row, start_col = row - row % BOX_SIZE, col - col % BOX_SIZE
    for i in range(BOX_SIZE):
        for j in range(BOX_SIZE):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def generate_full_board():
    board = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
    solve_board(board)
    return board

def generate_puzzle(difficulty='medium'):
    full_board = generate_full_board()
    puzzle_board = copy.deepcopy(full_board)
    
    holes_map = {'easy': 35, 'medium': 45, 'hard': 55}
    num_holes = holes_map.get(difficulty.lower(), 45)
    
    cells_to_remove = random.sample(range(81), num_holes)
    
    for index in cells_to_remove:
        row, col = divmod(index, BOARD_SIZE)
        puzzle_board[row][col] = 0
        
    # Flatten the 9x9 list of lists into a single 81-element list
    puzzle_flat = [cell for row in puzzle_board for cell in row]
    solution_flat = [cell for row in full_board for cell in row]
        
    return puzzle_flat, solution_flat


# --- 4. FLASK ROUTES ---

@app.route('/generate-sudoku', methods=['GET'])
def get_sudoku():
    """API endpoint to generate a Sudoku puzzle."""
    
    difficulty = request.args.get('difficulty', 'medium')
    
    if difficulty.lower() not in ['easy', 'medium', 'hard']:
        return jsonify({"error": "Invalid difficulty. Choose 'easy', 'medium', or 'hard'."}), 400
    
    try:
        puzzle, solution = generate_puzzle(difficulty)
        
        return jsonify({
            "difficulty": difficulty,
            "puzzle": puzzle,
            "solution": solution
        })
    except Exception as e:
        print(f"Generation error: {e}")
        return jsonify({"error": "Failed to generate Sudoku puzzle."}), 500

@app.route('/', methods=['GET'])
def home():
    """Simple health check endpoint."""
    return "Sudoku Generator API is running and protected!"

if __name__ == '__main__':
    # Used for local development only
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
