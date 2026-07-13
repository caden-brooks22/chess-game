#pragma once

#include <array>
#include <cstdint>
#include <string>
#include <string_view>

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

} // namespace cchess
