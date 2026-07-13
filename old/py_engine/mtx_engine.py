### Matrix Engine ###
#
# Python chess engine that using matrix based (bit board) calculations to speed up the engine
# rather then a using exsesive conditional branching. This matrix based approuch
# should also make the transition for a GPU based engine easier.

import chess
import old.py_engine.chess_openings as chess_openings
import random
import time

depth = 6          # default depth = 6
stop_event = None  # Event to stop the bot if needed
best_move = None

def reset_mtx_engine():
    global depth, stop_event, best_move
    depth = 6
    stop_event = None
    best_move = None

def find_best_move(game_state, depth=depth, stop_event=None):
    # Check if the current position is in the opening book
    fen = game_state.board.fen()
    opening_move = game_state.in_opening_table(fen)
    if opening_move:
        return opening_move

    # If not in the opening book, use the bot to find the best move
    for move in game_state.board.legal_moves:
        if stop_event:
            break
        game_state.board.push(move)
        score = -game_state.bot.search(game_state.board, depth - 1, -float('inf'), float('inf'))
        game_state.board.pop()
        if best_move is None or score > best_move[1]:
            best_move = (move.uci(), score)
        

def in_opening_table(fen):
    """Returns a move from the opening book if available."""
    if fen in chess_openings.openings:
        opening_moves = chess_openings.openings[fen]

        moves = [move[1] for move in opening_moves]  # Get the UCI moves
        probabilities = [move[0] for move in opening_moves]  # Get the probabilities

        # Use random.choices to select a move based on probabilities
        return random.choices(moves, probabilities)[0]

def evaluate_position(game_state):
    # Placeholder for position evaluation logic
    return 0