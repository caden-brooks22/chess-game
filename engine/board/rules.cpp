#include "rules.h"

#include <cctype>
#include <sstream>

namespace cchess {

static bool is_digit(char ch) {
	return ch >= '0' && ch <= '9';
}

char piece_to_fen(Piece piece) {
	switch (piece.type) {
		case PieceType::Pawn: return piece.color == Color::White ? 'P' : 'p';
		case PieceType::Knight: return piece.color == Color::White ? 'N' : 'n';
		case PieceType::Bishop: return piece.color == Color::White ? 'B' : 'b';
		case PieceType::Rook: return piece.color == Color::White ? 'R' : 'r';
		case PieceType::Queen: return piece.color == Color::White ? 'Q' : 'q';
		case PieceType::King: return piece.color == Color::White ? 'K' : 'k';
		case PieceType::None:
		default:
			return '.';
	}
}

Piece piece_from_fen(char fen_piece) {
	Piece piece{};
	piece.color = std::isupper(static_cast<unsigned char>(fen_piece)) ? Color::White : Color::Black;

	switch (std::tolower(static_cast<unsigned char>(fen_piece))) {
		case 'p': piece.type = PieceType::Pawn; break;
		case 'n': piece.type = PieceType::Knight; break;
		case 'b': piece.type = PieceType::Bishop; break;
		case 'r': piece.type = PieceType::Rook; break;
		case 'q': piece.type = PieceType::Queen; break;
		case 'k': piece.type = PieceType::King; break;
		default: piece.type = PieceType::None; break;
	}

	return piece;
}

const char* square_to_string(int square, char buffer[3]) {
	buffer[0] = static_cast<char>('a' + square_file(square));
	buffer[1] = static_cast<char>('1' + square_rank(square));
	buffer[2] = '\0';
	return buffer;
}

bool parse_uci_move(std::string_view text, Move& move) {
	if (text.size() != 4 && text.size() != 5) {
		return false;
	}

	const char from_file = text[0];
	const char from_rank = text[1];
	const char to_file = text[2];
	const char to_rank = text[3];

	if (from_file < 'a' || from_file > 'h' || to_file < 'a' || to_file > 'h') {
		return false;
	}
	if (from_rank < '1' || from_rank > '8' || to_rank < '1' || to_rank > '8') {
		return false;
	}

	move.from = static_cast<uint8_t>(make_square(from_file - 'a', from_rank - '1'));
	move.to = static_cast<uint8_t>(make_square(to_file - 'a', to_rank - '1'));
	move.promotion = 0;
	move.flags = MoveFlagNone;

	if (text.size() == 5) {
		switch (text[4]) {
			case 'q': case 'Q': move.promotion = static_cast<uint8_t>(PieceType::Queen); break;
			case 'r': case 'R': move.promotion = static_cast<uint8_t>(PieceType::Rook); break;
			case 'b': case 'B': move.promotion = static_cast<uint8_t>(PieceType::Bishop); break;
			case 'n': case 'N': move.promotion = static_cast<uint8_t>(PieceType::Knight); break;
			default: return false;
		}
		move.flags |= MoveFlagPromotion;
	}

	return true;
}

bool parse_fen(std::string_view fen,
			   std::array<Piece, 64>& squares,
			   Color& side_to_move,
			   uint8_t& castling_rights,
			   int8_t& en_passant_square,
			   uint16_t& halfmove_clock,
			   uint16_t& fullmove_number) {
	squares.fill(Piece{});
	side_to_move = Color::White;
	castling_rights = 0;
	en_passant_square = -1;
	halfmove_clock = 0;
	fullmove_number = 1;

	size_t index = 0;
	int rank = 7;
	int file = 0;

	while (index < fen.size() && fen[index] != ' ') {
		const char ch = fen[index++];
		if (ch == '/') {
			if (file != 8 || rank == 0) {
				return false;
			}
			--rank;
			file = 0;
			continue;
		}

		if (is_digit(ch)) {
			file += ch - '0';
			if (file > 8) {
				return false;
			}
			continue;
		}

		if (file >= 8 || rank < 0) {
			return false;
		}

		const Piece piece = piece_from_fen(ch);
		if (piece.type == PieceType::None) {
			return false;
		}

		squares[make_square(file, rank)] = piece;
		++file;
	}

	if (rank != 0 || file != 8) {
		return false;
	}

	if (index >= fen.size() || fen[index] != ' ') {
		return false;
	}
	++index;

	if (index >= fen.size()) {
		return false;
	}
	if (fen[index] == 'w') {
		side_to_move = Color::White;
	} else if (fen[index] == 'b') {
		side_to_move = Color::Black;
	} else {
		return false;
	}

	while (index < fen.size() && fen[index] != ' ') {
		++index;
	}
	if (index >= fen.size()) {
		return false;
	}
	++index;

	if (index >= fen.size()) {
		return false;
	}

	if (fen[index] == '-') {
		++index;
	} else {
		while (index < fen.size() && fen[index] != ' ') {
			switch (fen[index]) {
				case 'K': castling_rights |= 1 << 0; break;
				case 'Q': castling_rights |= 1 << 1; break;
				case 'k': castling_rights |= 1 << 2; break;
				case 'q': castling_rights |= 1 << 3; break;
				default: return false;
			}
			++index;
		}
	}

	if (index >= fen.size() || fen[index] != ' ') {
		return false;
	}
	++index;

	if (index >= fen.size()) {
		return false;
	}

	if (fen[index] == '-') {
		en_passant_square = -1;
		++index;
	} else {
		if (index + 1 >= fen.size()) {
			return false;
		}
		const char file_char = fen[index];
		const char rank_char = fen[index + 1];
		if (file_char < 'a' || file_char > 'h' || rank_char < '1' || rank_char > '8') {
			return false;
		}
		en_passant_square = static_cast<int8_t>(make_square(file_char - 'a', rank_char - '1'));
		index += 2;
	}

	if (index >= fen.size() || fen[index] != ' ') {
		return false;
	}
	++index;

	uint16_t value = 0;
	bool has_value = false;
	while (index < fen.size() && fen[index] != ' ') {
		if (!is_digit(fen[index])) {
			return false;
		}
		has_value = true;
		value = static_cast<uint16_t>(value * 10 + (fen[index] - '0'));
		++index;
	}
	if (!has_value) {
		return false;
	}
	halfmove_clock = value;

	if (index >= fen.size() || fen[index] != ' ') {
		return false;
	}
	++index;

	value = 0;
	has_value = false;
	while (index < fen.size() && fen[index] != ' ') {
		if (!is_digit(fen[index])) {
			return false;
		}
		has_value = true;
		value = static_cast<uint16_t>(value * 10 + (fen[index] - '0'));
		++index;
	}
	if (!has_value || value == 0) {
		return false;
	}
	fullmove_number = value;

	return true;
}

std::string format_board(const std::array<Piece, 64>& squares,
						 Color side_to_move,
						 uint8_t castling_rights,
						 int8_t en_passant_square,
						 uint16_t halfmove_clock,
						 uint16_t fullmove_number) {
	std::string out;
	out.reserve(256);

	for (int rank = 7; rank >= 0; --rank) {
		out.push_back(static_cast<char>('1' + rank));
		out.push_back(' ');
		for (int file = 0; file < 8; ++file) {
			const Piece piece = squares[make_square(file, rank)];
			out.push_back(piece.is_empty() ? '.' : piece_to_fen(piece));
			out.push_back(' ');
		}
		out.push_back('\n');
	}

	out.append("  a b c d e f g h\n");
	out.append("Side: ");
	out.push_back(side_to_move == Color::White ? 'w' : 'b');
	out.push_back('\n');
	out.append("Castling: ");
	if (castling_rights == 0) {
		out.push_back('-');
	} else {
		if (castling_rights & (1 << 0)) out.push_back('K');
		if (castling_rights & (1 << 1)) out.push_back('Q');
		if (castling_rights & (1 << 2)) out.push_back('k');
		if (castling_rights & (1 << 3)) out.push_back('q');
	}
	out.push_back('\n');
	out.append("En passant: ");
	if (en_passant_square >= 0) {
		char buffer[3];
		out.append(square_to_string(en_passant_square, buffer));
	} else {
		out.push_back('-');
	}
	out.push_back('\n');
	out.append("Halfmove: ");
	out.append(std::to_string(halfmove_clock));
	out.push_back('\n');
	out.append("Fullmove: ");
	out.append(std::to_string(fullmove_number));
	out.push_back('\n');

	return out;
}

} // namespace cchess
