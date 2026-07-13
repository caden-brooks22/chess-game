import chess
import old.py_engine.py_engine as py_engine
from GUI.gui_settings import gameSettings
from GUI.image_manager import Piece, DisplayBoard

# TODO turn openings into a class with a funciton that takes the position as
#      a peramiter and deturmins if it's in libray of openings
openings = [
    "e2e4",
    "d2d4"
]

class GameState():
    bot = py_engine.Bot()
    def __init__(self):
        self.board = chess.Board()
        self.display_board = DisplayBoard(self.get_position())

        self.white_player = gameSettings.default_white_player
        self.black_player = gameSettings.default_black_player
        self.time_control = gameSettings.default_time_control

    def is_human_turn(self):
        return (self.board.turn and self.white_player == "human") or (not self.board.turn and self.black_player == "human")

    def move(self, move: str):
        """ Moves a piece on the board. Move should be in UCI format (e.g., 'e2e4'). """
        try:
            move = chess.Move.from_uci(move)
        except ValueError:
            return False
            # raise ValueError("Invalid move format. Use UCI format (e.g., 'e2e4').")
        self.board.push(move)
        self.display_board.update_board(self.get_position())

        if self.get_winner():
            print(self.get_winner())

        return True
        
    # def undo_move(self):
    #     self.board.pop()
       
    def reset_game(self):
        self.board.reset()
        self.display_board.update_board(self.get_position())

    def get_legal_moves(self):
        return self.board.legal_moves()
    
    def is_legal_move(self, move: str):
        try:
            move = chess.Move.from_uci(move)
        except:
            return False
        return move in self.board.legal_moves

    # def get_move_history(self):
    #     return self.board.move_stack

    def get_move_count(self):
        return self.board.fullmove_number

    def get_turn(self):
        return self.board.turn
    
    def get_winner(self):
        if self.board.is_checkmate():
            return "White" if GameState.get_turn() else "Black"
        if self.board.is_stalemate():
            return "Stalemate"
        if self.board.is_insufficient_material():
            return "Draw"
        if self.board.is_fivefold_repetition():
            return "Draw"
        return None

    def get_position(self):                                                        
        board_str = ""
        for rank in range(7, -1, -1):  # Iterate from rank 8 to rank 1
            for file in range(8):  # Iterate from file 'a' to 'h'
                square = chess.square(file, rank)  # Get the square index
                piece = self.board.piece_at(square)
                if piece:
                    board_str += piece.symbol()  # Add the piece symbol (e.g., 'p', 'P', 'r', etc.)
                else:
                    board_str += "."  # Add a special character for empty squares
            # board_str += "\n"  # Add a newline after each rank
        return board_str
    
    
# def main():
#     gameState = GameState()

# if __name__ == "__main__":
#     main()
