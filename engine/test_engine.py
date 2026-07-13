from engine.engine_interface import engine
import chess

def main():
    time_ms = 19000  # 19 seconds
    board = chess.Board()

    #make some moves to test the engine
    moves = ["e4", "e5", "Nf3", "Nc6", "Bb5", "a6"]
    for move in moves:
        board.push_san(move)
    print(board)

    result = engine.find_best_move(str(board.fen()).encode('utf-8'), board.turn == chess.WHITE, time_ms)
    result = result.decode('utf-8')     # decode bytes to string
    print(f"\nBest move: {result}")

    try:
        board.push_uci(result)
        print(board)
    except Exception as e:
        print(f"Invalid move: {result}. Error: {e}")


if __name__ == "__main__":
    main()