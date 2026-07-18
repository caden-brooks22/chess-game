#ifndef SEARCH_H
#define SEARCH_H

#include <cstdint>

typedef int32_t (*EvaluatePositionFn)(const char* fen, bool side_to_move, unsigned int time_limit_ms);

const char* alpha_beta_search(
	const char* fen,
	bool side_to_move,
	unsigned int time_limit_ms,
	EvaluatePositionFn evaluate_position_fn
);


#endif // SEARCH_H