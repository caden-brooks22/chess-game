#include "engine.h"

#include <cstdio>
#include <cstring>
#include <string>

#include "search/search.h"
#include "evaluate/evaluate.h"


/* 
 * This function finds the best move for a given:
 *  - chess position represented in FEN format, 
 *  - the amount of time in ms allowed
 *  - TODO: CPU multi cores acceleration or GPU acceleration
 * 
 * Input - FEN string, side_to_move, and time limit in milliseconds
 * Output - Best move in UCI format (e.g., "e2e4")
 */
__declspec(dllexport)
const char* find_best_move(const char* input, bool side_to_move, unsigned int time_limit_ms) {
    static char buffer[256]; // Static buffer to hold the processed output

    printf("Received input: %s\n", input); // Debug print to verify input
    printf("Time limit: %u ms\n", time_limit_ms); // Debug print to verify time limit
    printf("Side to move: %s\n", side_to_move ? "true" : "false"); // Debug print to verify side to move

    // consider time allowed
    // call the searching algorithm. Use basic alpha-beta pruning or minimax for now.
    // the searching algorithm will call a evaluation function
    // the searching algorithm will optionally use hardware acceleration (GPU or multi-core CPU) to search in parallel
    const char* best_move;
    try {
        best_move = alpha_beta_search(input, side_to_move, time_limit_ms, evaluate_position);
    } catch (const std::exception& e) {
        printf("Engine exception: %s\n", e.what());
        return nullptr; // Return null on error
    }
    
    std::memcpy(buffer, best_move, std::strlen(best_move) + 1); // Copy the best move to the buffer
    return buffer; // Return the best move as a C-style string 
}





