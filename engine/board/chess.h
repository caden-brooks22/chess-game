#ifndef CCHESS_CHESS_H
#define CCHESS_CHESS_H

#include "rules.h"

#include <array>
#include <cstdint>
#include <string>
#include <string_view>
#include <vector>

namespace cchess {

class Board {
public:
	Board();
	explicit Board(std::string_view fen);

	bool set_fen(std::string_view fen);
	std::string fen() const;
	std::string ascii() const;

	bool push_uci(std::string_view uci);
	bool pop();

	const Piece& piece_at(int square) const;
	Color side_to_move() const;
	uint8_t castling_rights() const;
	int en_passant_square() const;
	uint16_t halfmove_clock() const;
	uint16_t fullmove_number() const;

	bool in_check(Color color) const;
	bool is_square_attacked(int square, Color by_color) const;

private:
	struct HistoryEntry {
		Move move{};
		Piece moved_piece{};
		Piece captured_piece{};
		int captured_square{-1};
		uint8_t previous_castling{0};
		int8_t previous_en_passant{-1};
		uint16_t previous_halfmove{0};
		uint16_t previous_fullmove{1};
		Color previous_side{Color::White};
	};

	bool make_move(const Move& move, bool validate_legality);
	void undo_last_move();
	int king_square(Color color) const;
	bool is_path_clear(int from, int to) const;
	bool is_pseudo_legal(const Move& move, const Piece& piece, Piece target_piece) const;

	std::array<Piece, 64> squares_{};
	std::vector<HistoryEntry> history_{};
	Color side_to_move_{Color::White};
	uint8_t castling_rights_{0};
	int8_t en_passant_square_{-1};
	uint16_t halfmove_clock_{0};
	uint16_t fullmove_number_{1};
};

} // namespace cchess

#endif // CCHESS_CHESS_H
