#include <cstdio>
#include <iostream>
#include <string>
#include "engine.h"
#include "c_chess/chess.h"
#include "c_chess/rules.h"

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

    // consider time allowed here, implement later
    

    // call the searching algorithm here. Use basic alpha-beta pruning or minimax for now.
    // the searching algorithm will call a evaluation function
    // the searching algorithm will optionally use hardware acceleration (GPU or multi-core CPU) to search in parallel

    

    std::string example_move = "d2d4"; // Placeholder for the best move logic
    memcpy(buffer, example_move.c_str(), example_move.size() + 1); // Copy the best move to the buffer
    return buffer; // Return the best move as a C-style string 
}





