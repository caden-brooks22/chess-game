#include "search.h"

#include <cstring>


// use minimax or alpha-beta pruning to search for the best move
const char* alpha_beta_search(
    const char* fen,
    bool side_to_move,
    unsigned int time_limit_ms,
    EvaluatePositionFn evaluate_position_fn
) {
    // Determine search depth based on time limit
    uint8_t depth;
    if      (time_limit_ms > 30000) depth = 3;
    else if (time_limit_ms > 10000) depth = 2;
    else                            depth = 1;

    // static char best_move[8] = "d2d4";

    if (evaluate_position_fn != nullptr) {
        evaluate_position_fn(fen, side_to_move, time_limit_ms);
    }

    return best_move;
}

