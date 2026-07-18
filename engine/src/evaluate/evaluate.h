#ifndef EVALUATE_H
#define EVALUATE_H

#include <cstdint>

int32_t evaluate_position(const char* fen, bool side_to_move, unsigned int time_limit_ms);

#endif // EVALUATE_H