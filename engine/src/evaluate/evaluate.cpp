#include "evaluate.h"
#include <stdexcept>

int32_t evaluate_position(const char* fen, bool side_to_move, unsigned int time_limit_ms) {
    int32_t score = 0;
    // extract the piece counts from the FEN string
    while (*fen && *fen != '\0') {
        ++fen;
        switch (*fen) {
            case 'P':
                score += 1;
                break;
            case 'N':
                score += 3;
                break;
            case 'B':
                score += 3;
                break;
            case 'R':
                score += 5;
                break;
            case 'Q':
                score += 9;
                break;
            case 'K':
                score += 0; // King has no material value
                break;
            case 'p':
                score -= 1;
                break;
            case 'n':
                score -= 3;
                break;
            case 'b':
                score -= 3;
                break;
            case 'r':
                score -= 5;
                break;
            case 'q':
                score -= 9;
                break;
            case 'k':
                score -= 0; // King has no material value
                break;
            case '1': case '2': case '3': case '4': case '5': case '6': case '7': case '8':
                // Empty squares, do nothing
                break;
            case '/':
                // Separator between ranks, do nothing
                break;
            case ' ':
                // End of piece placement, do nothing
                return score; // Return the score when we reach the end of the piece placement
            default:
                throw std::invalid_argument("Invalid FEN string: unexpected character");
        }
    }
    return score;
}