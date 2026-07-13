#include "board/board.h"

#include <cctype>
#include <cmath>

namespace cchess {

namespace {

constexpr uint8_t CASTLE_WHITE_KING = 1 << 0;
constexpr uint8_t CASTLE_WHITE_QUEEN = 1 << 1;
constexpr uint8_t CASTLE_BLACK_KING = 1 << 2;
constexpr uint8_t CASTLE_BLACK_QUEEN = 1 << 3;

constexpr int WHITE_KING_START = make_square(4, 0);
constexpr int WHITE_ROOK_KINGSIDE = make_square(7, 0);
constexpr int WHITE_ROOK_QUEENSIDE = make_square(0, 0);
constexpr int BLACK_KING_START = make_square(4, 7);
constexpr int BLACK_ROOK_KINGSIDE = make_square(7, 7);
constexpr int BLACK_ROOK_QUEENSIDE = make_square(0, 7);

int file_of(int square) {
	return square_file(square);
}

int rank_of(int square) {
	return square_rank(square);
}

int square_step(int from, int to) {
	const int from_file = file_of(from);
	const int from_rank = rank_of(from);
	const int to_file = file_of(to);
	const int to_rank = rank_of(to);
	const int file_delta = (to_file > from_file) - (to_file < from_file);
	const int rank_delta = (to_rank > from_rank) - (to_rank < from_rank);
	if (file_delta == 0 && rank_delta == 0) {
		return 0;
	}
	if (file_delta == 0) {
		return rank_delta * 8;
	}
	if (rank_delta == 0) {
		return file_delta;
	}
	if (std::abs(to_file - from_file) == std::abs(to_rank - from_rank)) {
		return rank_delta * 8 + file_delta;
	}
	return 0;
}

bool is_on_board(int square) {
	return square >= 0 && square < 64;
}

bool is_digit(char ch) {
	return ch >= '0' && ch <= '9';
}

} // namespace

Board::Board() {
	set_fen("rn1qkbnr/ppp1pppp/8/3p4/1b1P4/2N2N2/PPP1PPPP/R1BQKB1R w KQkq - 0 1");
}

Board::Board(std::string_view fen) {
	set_fen(fen);
}

bool Board::set_fen(std::string_view fen) {
	history_.clear();
	return parse_fen(fen, squares_, side_to_move_, castling_rights_, en_passant_square_, halfmove_clock_, fullmove_number_);
}

std::string Board::fen() const {
	std::string out;
	out.reserve(128);

	for (int rank = 7; rank >= 0; --rank) {
		int empty_count = 0;
		for (int file = 0; file < 8; ++file) {
			const Piece piece = squares_[make_square(file, rank)];
			if (piece.is_empty()) {
				++empty_count;
				continue;
			}

			if (empty_count != 0) {
				out.push_back(static_cast<char>('0' + empty_count));
				empty_count = 0;
			}
			out.push_back(piece_to_fen(piece));
		}

		if (empty_count != 0) {
			out.push_back(static_cast<char>('0' + empty_count));
		}

		if (rank != 0) {
			out.push_back('/');
		}
	}

	out.push_back(' ');
	out.push_back(side_to_move_ == Color::White ? 'w' : 'b');
	out.push_back(' ');
	if (castling_rights_ == 0) {
		out.push_back('-');
	} else {
		if (castling_rights_ & CASTLE_WHITE_KING) out.push_back('K');
		if (castling_rights_ & CASTLE_WHITE_QUEEN) out.push_back('Q');
		if (castling_rights_ & CASTLE_BLACK_KING) out.push_back('k');
		if (castling_rights_ & CASTLE_BLACK_QUEEN) out.push_back('q');
	}
	out.push_back(' ');
	if (en_passant_square_ >= 0) {
		char buffer[3];
		out.append(square_to_string(en_passant_square_, buffer));
	} else {
		out.push_back('-');
	}
	out.push_back(' ');
	out.append(std::to_string(halfmove_clock_));
	out.push_back(' ');
	out.append(std::to_string(fullmove_number_));

	return out;
}

std::string Board::ascii() const {
	return format_board(squares_, side_to_move_, castling_rights_, en_passant_square_, halfmove_clock_, fullmove_number_);
}

const Piece& Board::piece_at(int square) const {
	static const Piece empty_piece{};
	if (!is_valid_square(square)) {
		return empty_piece;
	}
	return squares_[square];
}

Color Board::side_to_move() const {
	return side_to_move_;
}

uint8_t Board::castling_rights() const {
	return castling_rights_;
}

int Board::en_passant_square() const {
	return en_passant_square_;
}

uint16_t Board::halfmove_clock() const {
	return halfmove_clock_;
}

uint16_t Board::fullmove_number() const {
	return fullmove_number_;
}

int Board::king_square(Color color) const {
	for (int square = 0; square < 64; ++square) {
		const Piece piece = squares_[square];
		if (piece.type == PieceType::King && piece.color == color) {
			return square;
		}
	}
	return -1;
}

bool Board::is_path_clear(int from, int to) const {
	const int step = square_step(from, to);
	if (step == 0) {
		return false;
	}

	for (int square = from + step; square != to; square += step) {
		if (!is_on_board(square) || !squares_[square].is_empty()) {
			return false;
		}
	}

	return true;
}

bool Board::is_square_attacked(int square, Color by_color) const {
	const int target_file = file_of(square);
	const int target_rank = rank_of(square);

	for (int from = 0; from < 64; ++from) {
		const Piece piece = squares_[from];
		if (piece.is_empty() || piece.color != by_color) {
			continue;
		}

		const int from_file = file_of(from);
		const int from_rank = rank_of(from);
		const int file_delta = std::abs(target_file - from_file);
		const int rank_delta = std::abs(target_rank - from_rank);

		switch (piece.type) {
			case PieceType::Pawn:
				if (by_color == Color::White) {
					if (target_rank == from_rank + 1 && file_delta == 1) {
						return true;
					}
				} else {
					if (target_rank + 1 == from_rank && file_delta == 1) {
						return true;
					}
				}
				break;
			case PieceType::Knight:
				if ((file_delta == 1 && rank_delta == 2) || (file_delta == 2 && rank_delta == 1)) {
					return true;
				}
				break;
			case PieceType::Bishop:
				if (file_delta == rank_delta && is_path_clear(from, square)) {
					return true;
				}
				break;
			case PieceType::Rook:
				if ((file_delta == 0 || rank_delta == 0) && is_path_clear(from, square)) {
					return true;
				}
				break;
			case PieceType::Queen:
				if (((file_delta == rank_delta) || (file_delta == 0 || rank_delta == 0)) && is_path_clear(from, square)) {
					return true;
				}
				break;
			case PieceType::King:
				if (file_delta <= 1 && rank_delta <= 1) {
					return true;
				}
				break;
			case PieceType::None:
			default:
				break;
		}
	}

	return false;
}

bool Board::in_check(Color color) const {
	const int king = king_square(color);
	if (king < 0) {
		return false;
	}
	return is_square_attacked(king, opposite(color));
}

bool Board::is_pseudo_legal(const Move& move, const Piece& piece, Piece target_piece) const {
	if (piece.is_empty() || piece.color != side_to_move_) {
		return false;
	}

	if (!is_valid_square(move.from) || !is_valid_square(move.to) || move.from == move.to) {
		return false;
	}

	const int from_file = file_of(move.from);
	const int from_rank = rank_of(move.from);
	const int to_file = file_of(move.to);
	const int to_rank = rank_of(move.to);
	const int file_delta = to_file - from_file;
	const int rank_delta = to_rank - from_rank;
	const int abs_file_delta = std::abs(file_delta);
	const int abs_rank_delta = std::abs(rank_delta);

	if (!target_piece.is_empty() && target_piece.color == piece.color) {
		return false;
	}

	switch (piece.type) {
		case PieceType::Pawn: {
			const int direction = piece.color == Color::White ? 1 : -1;
			const int start_rank = piece.color == Color::White ? 1 : 6;
			const int promotion_rank = piece.color == Color::White ? 7 : 0;

			if (file_delta == 0 && target_piece.is_empty()) {
				if (rank_delta == direction) {
					if (to_rank == promotion_rank && move.promotion == 0) {
						return false;
					}
					return true;
				}

				if (from_rank == start_rank && rank_delta == 2 * direction) {
					const int intermediate = move.from + direction * 8;
					return squares_[intermediate].is_empty();
				}

				return false;
			}

			if (abs_file_delta == 1 && rank_delta == direction) {
				if (!target_piece.is_empty()) {
					return true;
				}
				return en_passant_square_ == static_cast<int8_t>(move.to);
			}

			return false;
		}
		case PieceType::Knight:
			return (abs_file_delta == 1 && abs_rank_delta == 2) || (abs_file_delta == 2 && abs_rank_delta == 1);
		case PieceType::Bishop:
			return abs_file_delta == abs_rank_delta && is_path_clear(move.from, move.to);
		case PieceType::Rook:
			return (file_delta == 0 || rank_delta == 0) && is_path_clear(move.from, move.to);
		case PieceType::Queen:
			return ((abs_file_delta == abs_rank_delta) || (file_delta == 0 || rank_delta == 0)) && is_path_clear(move.from, move.to);
		case PieceType::King: {
			if (abs_file_delta <= 1 && abs_rank_delta <= 1) {
				return true;
			}

			if (piece.color == Color::White && move.from == WHITE_KING_START && rank_delta == 0) {
				if (move.to == make_square(6, 0) && (castling_rights_ & CASTLE_WHITE_KING)) {
					return squares_[make_square(5, 0)].is_empty() && squares_[make_square(6, 0)].is_empty();
				}
				if (move.to == make_square(2, 0) && (castling_rights_ & CASTLE_WHITE_QUEEN)) {
					return squares_[make_square(1, 0)].is_empty() && squares_[make_square(2, 0)].is_empty() && squares_[make_square(3, 0)].is_empty();
				}
			}

			if (piece.color == Color::Black && move.from == BLACK_KING_START && rank_delta == 0) {
				if (move.to == make_square(6, 7) && (castling_rights_ & CASTLE_BLACK_KING)) {
					return squares_[make_square(5, 7)].is_empty() && squares_[make_square(6, 7)].is_empty();
				}
				if (move.to == make_square(2, 7) && (castling_rights_ & CASTLE_BLACK_QUEEN)) {
					return squares_[make_square(1, 7)].is_empty() && squares_[make_square(2, 7)].is_empty() && squares_[make_square(3, 7)].is_empty();
				}
			}

			return false;
		}
		case PieceType::None:
		default:
			return false;
	}
}

bool Board::make_move(const Move& move, bool validate_legality) {
	if (!is_valid_square(move.from) || !is_valid_square(move.to)) {
		return false;
	}

	const Piece moving_piece = squares_[move.from];
	const Piece target_piece = squares_[move.to];
	if (!is_pseudo_legal(move, moving_piece, target_piece)) {
		return false;
	}

	HistoryEntry history_entry{};
	history_entry.move = move;
	history_entry.moved_piece = moving_piece;
	history_entry.captured_piece = target_piece;
	history_entry.previous_castling = castling_rights_;
	history_entry.previous_en_passant = en_passant_square_;
	history_entry.previous_halfmove = halfmove_clock_;
	history_entry.previous_fullmove = fullmove_number_;
	history_entry.previous_side = side_to_move_;

	int captured_square = move.to;
	bool is_capture = !target_piece.is_empty();

	squares_[move.from] = Piece{};

	if (moving_piece.type == PieceType::Pawn && move.to == en_passant_square_ && target_piece.is_empty()) {
		captured_square = move.to + (moving_piece.color == Color::White ? -8 : 8);
		history_entry.captured_square = captured_square;
		history_entry.captured_piece = squares_[captured_square];
		squares_[captured_square] = Piece{};
		is_capture = true;
	} else {
		history_entry.captured_square = captured_square;
	}

	if (moving_piece.type == PieceType::King) {
		if (moving_piece.color == Color::White) {
			castling_rights_ &= ~(CASTLE_WHITE_KING | CASTLE_WHITE_QUEEN);
		} else {
			castling_rights_ &= ~(CASTLE_BLACK_KING | CASTLE_BLACK_QUEEN);
		}

		if (move.from == WHITE_KING_START && move.to == make_square(6, 0)) {
			squares_[make_square(5, 0)] = squares_[make_square(7, 0)];
			squares_[make_square(7, 0)] = Piece{};
		} else if (move.from == WHITE_KING_START && move.to == make_square(2, 0)) {
			squares_[make_square(3, 0)] = squares_[make_square(0, 0)];
			squares_[make_square(0, 0)] = Piece{};
		} else if (move.from == BLACK_KING_START && move.to == make_square(6, 7)) {
			squares_[make_square(5, 7)] = squares_[make_square(7, 7)];
			squares_[make_square(7, 7)] = Piece{};
		} else if (move.from == BLACK_KING_START && move.to == make_square(2, 7)) {
			squares_[make_square(3, 7)] = squares_[make_square(0, 7)];
			squares_[make_square(0, 7)] = Piece{};
		}
	}

	if (moving_piece.type == PieceType::Rook) {
		if (move.from == WHITE_ROOK_KINGSIDE) castling_rights_ &= ~CASTLE_WHITE_KING;
		if (move.from == WHITE_ROOK_QUEENSIDE) castling_rights_ &= ~CASTLE_WHITE_QUEEN;
		if (move.from == BLACK_ROOK_KINGSIDE) castling_rights_ &= ~CASTLE_BLACK_KING;
		if (move.from == BLACK_ROOK_QUEENSIDE) castling_rights_ &= ~CASTLE_BLACK_QUEEN;
	}

	if (!target_piece.is_empty() && target_piece.type == PieceType::Rook) {
		if (move.to == WHITE_ROOK_KINGSIDE) castling_rights_ &= ~CASTLE_WHITE_KING;
		if (move.to == WHITE_ROOK_QUEENSIDE) castling_rights_ &= ~CASTLE_WHITE_QUEEN;
		if (move.to == BLACK_ROOK_KINGSIDE) castling_rights_ &= ~CASTLE_BLACK_KING;
		if (move.to == BLACK_ROOK_QUEENSIDE) castling_rights_ &= ~CASTLE_BLACK_QUEEN;
	}

	Piece placed_piece = moving_piece;
	if (moving_piece.type == PieceType::Pawn) {
		halfmove_clock_ = 0;
		const int promotion_rank = moving_piece.color == Color::White ? 7 : 0;
		if (rank_of(move.to) == promotion_rank) {
			if (move.promotion == 0) {
				undo_last_move();
				return false;
			}

			placed_piece.type = static_cast<PieceType>(move.promotion);
			if (placed_piece.type != PieceType::Queen && placed_piece.type != PieceType::Rook &&
				placed_piece.type != PieceType::Bishop && placed_piece.type != PieceType::Knight) {
				undo_last_move();
				return false;
			}
		}
	} else if (is_capture) {
		halfmove_clock_ = 0;
	} else {
		++halfmove_clock_;
	}

	squares_[move.to] = placed_piece;

	en_passant_square_ = -1;
	if (moving_piece.type == PieceType::Pawn && std::abs(rank_of(move.to) - rank_of(move.from)) == 2) {
		en_passant_square_ = static_cast<int8_t>(move.from + (moving_piece.color == Color::White ? 8 : -8));
	}

	if (side_to_move_ == Color::Black) {
		++fullmove_number_;
	}
	side_to_move_ = opposite(side_to_move_);

	history_.push_back(history_entry);

	if (validate_legality && in_check(history_entry.previous_side)) {
		undo_last_move();
		return false;
	}

	return true;
}

void Board::undo_last_move() {
	if (history_.empty()) {
		return;
	}

	const HistoryEntry history_entry = history_.back();
	history_.pop_back();

	side_to_move_ = history_entry.previous_side;
	castling_rights_ = history_entry.previous_castling;
	en_passant_square_ = history_entry.previous_en_passant;
	halfmove_clock_ = history_entry.previous_halfmove;
	fullmove_number_ = history_entry.previous_fullmove;

	squares_[history_entry.move.from] = history_entry.moved_piece;
	squares_[history_entry.move.to] = Piece{};

	if (history_entry.moved_piece.type == PieceType::King) {
		if (history_entry.move.from == WHITE_KING_START && history_entry.move.to == make_square(6, 0)) {
			squares_[make_square(7, 0)] = squares_[make_square(5, 0)];
			squares_[make_square(5, 0)] = Piece{};
		} else if (history_entry.move.from == WHITE_KING_START && history_entry.move.to == make_square(2, 0)) {
			squares_[make_square(0, 0)] = squares_[make_square(3, 0)];
			squares_[make_square(3, 0)] = Piece{};
		} else if (history_entry.move.from == BLACK_KING_START && history_entry.move.to == make_square(6, 7)) {
			squares_[make_square(7, 7)] = squares_[make_square(5, 7)];
			squares_[make_square(5, 7)] = Piece{};
		} else if (history_entry.move.from == BLACK_KING_START && history_entry.move.to == make_square(2, 7)) {
			squares_[make_square(0, 7)] = squares_[make_square(3, 7)];
			squares_[make_square(3, 7)] = Piece{};
		}
	}

	if (!history_entry.captured_piece.is_empty()) {
		squares_[history_entry.captured_square] = history_entry.captured_piece;
	}
}

bool Board::push_uci(std::string_view uci) {
	Move move{};
	if (!parse_uci_move(uci, move)) {
		return false;
	}
	return make_move(move, true);
}

bool Board::pop() {
	if (history_.empty()) {
		return false;
	}
	undo_last_move();
	return true;
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