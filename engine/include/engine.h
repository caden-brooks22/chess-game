#ifndef ENGINE_H
#define ENGINE_H

#define INFINIT_TIME_LIMIT    0

#ifdef __cplusplus
extern "C" {
#endif

__declspec(dllexport) const char* find_best_move(const char* input, bool side_to_move, unsigned int time_limit_ms);

#ifdef __cplusplus
}
#endif

#endif // ENGINE_H
