import chess
import old.py_engine.chess_openings as chess_openings
import random
import time


"""
ADD BETTER OUTPUTS FOR DEBUGGING
 -format data for easy analysis as I tweak the engine
 -cool if it generated a graphical tree of the moves it looked at

+++++++++++++++++++++++++++++++++++++++++++++++++++++
        Using matplotlib for a more custom tree

        If you want something dynamic and interactive:

        import networkx as nx
        import matplotlib.pyplot as plt

        G = nx.DiGraph()

        def add_edges(G, node):
            for child in node.children:
                G.add_edge(node.move or "root", child.move)
                add_edges(G, child)

        add_edges(G, root)
        nx.draw(G, with_labels=True, node_size=2000, node_color="lightblue")
        plt.show()


        This gives you a quick, visual way to see the tree.
+++++++++++++++++++++++++++++++++++++++++++++++++++++
"""

"""
how do humans imminently decide what lines to calculate first?

checks, captures, then attacks
evaluate checks first, then captures, then attacks. 

=========================================

figure out how long, on average, python takes for an iterations and how long a basic operation takes
based on that, figure out how many iterations can be done in a given time frame

=========================================

using the ordering and allowed time, figure out how deep the bot can go in a given time frame.
if the bot runs out of time before it finishes searching the current depth, it should return the current best move
and hopfully the current best move is good based on the ordering.

note: ordering might become complex for best results
      for example, go one (maybe two) moves deep on a check or capture to see if it leads to a better position
      these moves should be prioritized over other moves, the ordering algorithm will turn into a mix of 
      depth and breadth first search for best results. this is because humans do not look at all possible moves.
      humans do an extreamly shallow search of most moves, then a deep search of the best moves.
      It's critical that the algorithm can quickly identify the best moves quickly.

      If the bot is running out of time, it should dynamically prune more aggressively.
"""

class Bot:
    """A chess bot that uses a minimax algorithm with alpha-beta pruning to find the best move."""
    MAX_CACHE_SIZE = 1_500_000

    def __init__(self, depth=6):
        self.depth = depth
        self.stop_event = None  # Event to stop the bot if needed
        self.best_move = None

        
        
        self.position_cache  = {}  # Stores the best score and depth for each position
        self.move_order_cache = {}
        self.move_order_tracker = {}

        self.old_fen = None  # Previous FEN for tracking changes
        self.score_tracker = {}  # Stores the scores of all moves for each position

        self.root_moves_completed = 0
        self.root_moves_total = 0  # Total root moves to be completed

    def check_root_condition(self, fen, move=None):
        if self.stop_event and self.stop_event.is_set():
            raise Exception("Bot stopped by user request.")
        
        self.root_moves_completed += 1
        elapsed_time = time.time() - self.start_time
        self.start_time = time.time()  # Reset start time for next move

        # if elapsed_time > 10:  # If the search takes too long, stop
        #     return "stop"
        if fen:
            for item in self.score_tracker[fen].items():
                    print(f"score tracker: {item}")

        print(f"({self.root_moves_completed}/{self.root_moves_total}) Current move: {move.uci()}. Best move: {self.best_move.uci() if self.best_move else 'None'}. time elapsed: {elapsed_time:.2f} seconds")

    def order_moves(self, board):
        """Orders the legal moves based on a cached order then default order."""
        fen = board.fen()
        legal_moves = list(board.legal_moves)

        if fen in self.move_order_cache: # sort by cached order if available
            # self.count3 += 1
            cached_order = self.move_order_cache[fen]
            return sorted(
                legal_moves,
                key=lambda m: cached_order.index(m) if m in cached_order else len(cached_order)
            )
        else: # sort by move value if not cached
            # self.count4 += 1
            def move_value(move):
                if board.is_capture(move):
                    captured_piece = board.piece_at(move.to_square)
                    return evaluation.piece_value[captured_piece.piece_type] if captured_piece else 0
                return 0
            return sorted(board.legal_moves, key=move_value, reverse=True)

    def should_add_to_position_cache (self, fen, best_weight, depth):
        """Determines if the current board state should be added to the transposition table."""
        # Only add if the position is not already in the table or if the depth is greater than the stored depth
        if fen not in self.position_cache  or self.position_cache [fen][1] < depth:
            return True
        return False
    
    def should_use_position_cache (self, fen, depth):
        """Checks if the transposition table should be used for the current board state."""
        # Use the transposition table if the position is already evaluated and the depth is sufficient
        return fen in self.position_cache and self.position_cache [fen][1] >= depth

    def trim_cache(self, cache):
        while len(cache) > Bot.MAX_CACHE_SIZE:
            cache.pop(next(iter(cache)))  # Remove oldest entry

    def in_opening_table(self, fen):
        """Returns a move from the opening book if available."""
        if fen in chess_openings.openings:
            opening_moves = chess_openings.openings[fen]

            moves = [move[1] for move in opening_moves]  # Get the UCI moves
            probabilities = [move[0] for move in opening_moves]  # Get the probabilities

            # Use random.choices to select a move based on probabilities
            return random.choices(moves, probabilities)[0]

    def bestMove(self, board, stop_event = None):
        """Finds the best move for the current board state using minimax with alpha-beta pruning."""
        self.best_move = None
        self.stop_event = stop_event
        
        self.count1 = 0
        self.count2 = 0
        self.count3 = 0
        self.count4 = 0
        self.Prune_count = 0

        if self.in_opening_table(self.strip_fen(board.fen())):
            return self.in_opening_table(self.strip_fen(board.fen()))
            
        
        else:

            # print(f"move order cache size: {len(self.move_order_cache)}")
            # print(f"move order tracker size: {len(self.move_order_tracker)}")

            self.root_moves_completed = 0
            self.root_moves_total = len(list(board.legal_moves))

            total_time = time.time()
            self.start_time = time.time()

            self.score_tracker = {}  # Reset score tracker for the new search

            self.calcBestMove(board, self.depth)

            # clean up caches
            self.move_order_cache = self.move_order_tracker
            self.move_order_tracker = {}
            self.trim_cache(self.position_cache) # clear old positions to save memory

            # print(f"pruning occurred {self.Prune_count} times.")
            # print(f"trasposition table used {self.count1} times.")
            # print(f"trasposition table not used {self.count2} times.")
            # print(f"move order cache used {self.count3} times.")
            # print(f"move order cache not used {self.count4} times.")

            
            print(f"total time taken: {time.time() - total_time:.2f} seconds")
            print()

            return self.best_move.uci() if self.best_move else None

    def calcBestMove(self, board, depth, alpha=float('-inf'), beta=float('inf')):
        """returns best score for the current board state NOT the best move"""
        fen = board.fen()
        all_moves = {}

        if self.should_use_position_cache (fen, depth):
            # self.count1 += 1
            return self.position_cache [fen][0]
        # else:
            # self.count2 += 1

        if depth == 0:
            score = evaluation.evaluation(board)
            return score

        if board.is_checkmate():
            return float('inf') if board.turn == chess.BLACK else float('-inf')
        
        if board.is_stalemate() or board.is_insufficient_material() or board.is_fivefold_repetition():
            return 0  # Draw


        best_weight = float('-inf') if board.turn == chess.WHITE else float('inf')

        is_maximizing = board.turn == chess.WHITE

        for move in self.order_moves(board):
            board.push(move)
            score = self.calcBestMove(board, depth - 1, alpha, beta)
            board.pop()

            all_moves[move] = score

            if is_maximizing:
                if score > best_weight:
                    best_weight = score
                    if depth == self.depth:
                        self.best_move = move
                alpha = max(alpha, best_weight)
            else:
                if score < best_weight:
                    best_weight = score
                    if depth == self.depth:
                        self.best_move = move
                beta = min(beta, best_weight)

            if depth == self.depth:
                self.check_root_condition(self.old_fen, move)
                print()

            if beta <= alpha:
                # self.Prune_count += 1
                break
        
        # Store the best score in the transposition table
        if self.should_add_to_position_cache(fen, best_weight, depth):
            self.position_cache[fen] = (best_weight, depth)
        
        self.move_order_tracker[fen] = sorted(all_moves.keys(), key=lambda x: all_moves[x], reverse=True)
        self.score_tracker[fen] = all_moves
        self.old_fen = fen

        return best_weight
    
    def strip_fen(self, fen):
        """Strips the FEN string to only include the board position and turn."""
        return ' '.join(fen.split(' ')[:4])
    
    def __str__(self):
        return f"Bot evaluating at depth {self.depth}"


class evaluation():
    # OPENING_MAT_COUNT = 78
    MID_GAME_MAT_COUNT = 50
    END_GAME_MAT_COUNT = 20

    piece_value = {
        chess.PAWN: 1000,
        chess.KNIGHT: 3000,
        chess.BISHOP: 3000,
        chess.ROOK: 5000,
        chess.QUEEN: 9000,
        chess.KING: 0  # King is invaluable
    }

    

    

    def find_piece_positions(board, piece):
        """Finds all positions of a given piece type on the board."""
        positions = {}
        for square in chess.SQUARES:
            piece_at_square = board.piece_at(square)
            if piece_at_square and piece_at_square.piece_type == piece:
                positions[square] = piece_at_square.color
        return positions
    
    
    """Evaluation class for the chess engine."""
    def evaluation(board):
        """Evaluates the board as a whole and returns a score."""
        return (evaluation.evaluate_pieces(board) + evaluation.evaluate_position(board))
    
    def evaluate_pieces(board):
        """Evaluates a score based on the pieces on the board."""
        score = 0
        for piece_type in evaluation.piece_value:
            score += len(board.pieces(piece_type, chess.WHITE)) * evaluation.piece_value[piece_type]
            score -= len(board.pieces(piece_type, chess.BLACK)) * evaluation.piece_value[piece_type]

        return score

    def evaluate_position(board):
        """Evaluates a score based on the position of pieces."""
        # TODO add depper analysis of what game phase the game is in

        material = evaluation.count_material(board)

        if material > evaluation.MID_GAME_MAT_COUNT:
            game_phase = "opening"
        elif material <= evaluation.END_GAME_MAT_COUNT:
            game_phase = "end_game"
        else:
            game_phase = "mid_game"

        positional_score = 0

        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is None:
                continue
            
            lookup_square = square
            if piece.color == chess.BLACK:
                lookup_square = chess.square_mirror(square)

            match piece.piece_type:
                case chess.PAWN:
                    if game_phase == "opening" or game_phase == "midgame" or game_phase == "end_game":
                        positional_score += Pawn.central_pawns(board, lookup_square)
                        # positional_score += Pawn.doubled_pawns(board, lookup_square, board.pieces(chess.PAWN, chess.WHITE))
                        # positional_score += Pawn.isolated_pawns(board, lookup_square, board.pieces(chess.PAWN, chess.WHITE))
                        # positional_score += Pawn.passed_pawns(board, lookup_square, board.pieces(chess.PAWN, chess.WHITE))
                        # positional_score += Pawn.backward_pawns(board, lookup_square)
                        # positional_score += Pawn.pawn_chains(board, lookup_square)
                    
                    else:
                        raise ValueError("Invalid game phase. Must be 'opening', 'mid_game', or 'end_game'.")
                    
                case chess.KNIGHT:
                    if game_phase == "opening" or game_phase == "midgame" or game_phase == "end_game":
                        positional_score += Knight.positions(lookup_square)
                    
                    else:
                        raise ValueError("Invalid game phase. Must be 'opening', 'mid_game', or 'end_game'.")
                                    
                case chess.BISHOP:
                    if game_phase == "opening" or game_phase == "midgame" or game_phase == "end_game":
                        positional_score += Bishop.positions(lookup_square)
                    
                    else:
                        raise ValueError("Invalid game phase. Must be 'opening', 'mid_game', or 'end_game'.")
                                    
                case chess.ROOK:
                    if game_phase == "opening" or game_phase == "midgame" or game_phase == "end_game":
                        positional_score += Rook.positions(lookup_square)
                    
                    else:
                        raise ValueError("Invalid game phase. Must be 'opening', 'mid_game', or 'end_game'.")
                                    
                case chess.QUEEN:
                    if game_phase == "opening" or game_phase == "midgame" or game_phase == "end_game":
                        positional_score += Queen.positions(lookup_square)
                    
                    else:
                        raise ValueError("Invalid game phase. Must be 'opening', 'mid_game', or 'end_game'.")
                                    
                case chess.KING:
                    if game_phase == "opening" or game_phase == "midgame" or game_phase == "end_game":
                        positional_score += King.positions(lookup_square)
                    
                    else:
                        raise ValueError("Invalid game phase. Must be 'opening', 'mid_game', or 'end_game'.")
                    
        return positional_score
                
        if board.turn == chess.BLACK:
            return -positional_score
        return positional_score
    
    def count_material(board):
        """Counts the material on the board. returns total material value."""
        material = 0
        for piece_type in chess.PIECE_TYPES:
            material += len(board.pieces(piece_type, chess.WHITE)) * evaluation.piece_value[piece_type]
            material += len(board.pieces(piece_type, chess.BLACK)) * evaluation.piece_value[piece_type]
        return material



class Pawn:
    
    pawn_positions = {
        chess.C3 : 50, chess.C4 : 25,
        chess.D3 : 200, chess.D4 : 350, chess.D5 : 100,
        chess.E3 : 200, chess.E4 : 350, chess.E5 : 100,
        chess.F3 : 50, chess.F4 : 25
    }
    
    # RULES
    """
            Central Pawns - Reward control of central files.

            Doubled Pawns - Penalize pawns stacked on the same file.

            Isolated Pawns - Penalize pawns with no friendly pawns on adjacent files.

            Passed Pawns - Reward pawns with a clear path to promotion.

            Backward Pawns - Penalize pawns that are behind their neighbors and cannot advance safely.

            Pawn Chains - Reward solid chains (e.g., d4-e5-f6).

            Pawn Majority on Flanks - Slight bonus if you can create a passed pawn on one wing.
        """

    def central_pawns(board, square):
        """Evaluates a pawn's position on the board."""
        
        if square in Pawn.pawn_positions:
            return Pawn.pawn_positions[square]
        return 0

    def doubled_pawns(board, square, pawns):
        # Check for doubled pawns
        file = chess.square_file(square)
        for other_square in pawns:
            if chess.square_file(other_square) == file and other_square != square:
                return 50
        return 0

    def isolated_pawns(board, square, pawns):
        # Check for isolated pawns
        file = chess.square_file(square)
        adjacent_files = [file - 1, file + 1]
        has_adjacent_pawn = any(
            chess.square_file(other_square) in adjacent_files for other_square in pawns if other_square != square
        )
        if not has_adjacent_pawn:
            return 50
        return 0

    def passed_pawns(board, square, pawns):
        # Check for passed pawns
        file = chess.square_file(square)
        if all(
            board.piece_at(chess.square(file, rank)) is None
            for rank in range(chess.square_rank(square) + 1, 8)
        ):
            return 100
        return 0

    def backward_pawns(board, square):
        # Check for backward pawns
        rank = chess.square_rank(square)
        if rank < 7:
            if not any(
                board.piece_at(chess.square(file, rank + 1)) is not None
                for file in [chess.square_file(square) - 1, chess.square_file(square), chess.square_file(square) + 1]
            ):
                return 50
            return 0
        
    def pawn_chains(board, square):
        # Check for pawn chains
        file = chess.square_file(square)
        rank = chess.square_rank(square)
        total = 0
        if board.piece_at(chess.square(file - 1, rank + 1)):
            total += 50
        if board.piece_at(chess.square(file + 1, rank + 1)):
            total += 50
        return total
    
    def flank_majority(board, square, pawns):
        # check for flank majority
        return 0

class Knight:
    knight_positions = {
        chess.C2 : 0,   chess.C3 : 200,
        chess.D2 : 100, chess.D3 : 50, chess.D5 : 50,
        chess.E2 : 100, chess.E3 : 50, chess.E5 : 50,
        chess.F2 : 0,   chess.F3 : 200,
    }

    def positions(square):
        if square in Knight.knight_positions:
            return Knight.knight_positions[square]
        return 0

    def check_outpost(board, square):
        """Checks if a knight can move to a square."""
        knight_moves = chess.knight_moves(square)
        for move in knight_moves:
            if board.is_legal(chess.Move(square, move)):
                return 200
        return 0

class Bishop:
    bishop_positions = {
        #dark squares
        chess.B2 : 200,
        chess.D2 : 50,
        chess.E3 : 75,
        chess.F4 : 200,
        chess.G5 : 150,
        #light squares
        chess.G2 : 200,
        chess.E2 : 50,
        chess.D3 : 75,
        chess.C4 : 200,
        chess.B5 : 150,
    }

    def positions(square):
        if square in Bishop.bishop_positions:
            return Bishop.bishop_positions[square]
        return 0

class Rook:
    rook_positions = {
        chess.D1 : 50,
        chess.E1 : 50,
    }

    def positions(square):
        if square in Rook.rook_positions:
            return Rook.rook_positions[square]
        return 0

class Queen:
    queen_positions = {
        # none: queens should be evaluated based on their mobility and control of the board
    }

    def positions(square):
        if square in Queen.queen_positions:
            return Queen.queen_positions[square]
        return 0

class King:
    king_positions = {
        chess.C1 : 500,
        chess.G1 : 500,
    }

    def positions(square):
        if square in King.king_positions:
            return King.king_positions[square]
        return 0
    
