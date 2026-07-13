#ifndef CCHESS_BOARD_H
#define CCHESS_BOARD_H

#include <array>
#include <cstdint>
#include <string>
#include <string_view>
#include <vector>

namespace cchess {

enum class Color : uint8_t {
	White = 0,
	Black = 1,
};

constexpr Color opposite(Color color) {
	return color == Color::White ? Color::Black : Color::White;
}

enum class PieceType : uint8_t {
	None = 0,
	Pawn = 1,
	Knight = 2,
	Bishop = 3,
	Rook = 4,
	Queen = 5,
	King = 6,
};

struct Piece {
	PieceType type{PieceType::None};
	Color color{Color::White};

	constexpr bool is_empty() const {
		return type == PieceType::None;
	}
};

struct Move {
	uint8_t from{0};
	uint8_t to{0};
	uint8_t promotion{0};
	uint8_t flags{0};
};

enum MoveFlags : uint8_t {
	MoveFlagNone = 0,
	MoveFlagCapture = 1 << 0,
	MoveFlagDoublePawnPush = 1 << 1,
	MoveFlagKingCastle = 1 << 2,
	MoveFlagQueenCastle = 1 << 3,
	MoveFlagEnPassant = 1 << 4,
	MoveFlagPromotion = 1 << 5,
};

constexpr bool is_valid_square(int square) {
	return square >= 0 && square < 64;
}

constexpr int square_file(int square) {
	return square & 7;
}

constexpr int square_rank(int square) {
	return square >> 3;
}

constexpr int make_square(int file, int rank) {
	return (rank << 3) | file;
}

bool parse_uci_move(std::string_view text, Move& move);
bool parse_fen(std::string_view fen,
			   std::array<Piece, 64>& squares,
			   Color& side_to_move,
			   uint8_t& castling_rights,
			   int8_t& en_passant_square,
			   uint16_t& halfmove_clock,
			   uint16_t& fullmove_number);

char piece_to_fen(Piece piece);
Piece piece_from_fen(char fen_piece);
const char* square_to_string(int square, char buffer[3]);
std::string format_board(const std::array<Piece, 64>& squares,
						 Color side_to_move,
						 uint8_t castling_rights,
						 int8_t en_passant_square,
						 uint16_t halfmove_clock,
						 uint16_t fullmove_number);

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

#endif // CCHESS_BOARD_H