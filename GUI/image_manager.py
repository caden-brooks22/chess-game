from pathlib import Path

from PIL import Image, ImageTk, ImageDraw

IMG_DIR = Path(__file__).resolve().parent / "img"

class Piece():
    Pieces = {"P" : ("pawn", "white"),
             "N" : ("knight", "white"),
             "B" : ("bishop", "white"),
             "R" : ("rook", "white"),
             "Q" : ("queen", "white"),
             "K" : ("king", "white"),
             "p" : ("pawn", "black"),
             "n" : ("knight", "black"),
             "b" : ("bishop", "black"),
             "r" : ("rook", "black"),
             "q" : ("queen", "black"),
             "k" : ("king", "black"),
             "." : ("square", "empty")}
    
    def __init__(self, letter):
        self.color = Piece.Pieces[letter][1]
        self.name = f"{self.color}-{Piece.Pieces[letter][0]}"
        self.letter = letter
        
        self.open_image = Image.open(IMG_DIR / f"{self.name}.png")
        try:
            self.image= ImageTk.PhotoImage(self.open_image)
        except:
            print("ERROR: could not create ImageTK.PhotoImage (probably because no default tk window found)")

    def rescale_img(self, size):
        self.scaled_image = self.open_image.resize((size, size), Image.LANCZOS)
        self.image = ImageTk.PhotoImage(self.scaled_image)

        # # Create a new image with a transparent background
        # width, height = self.scaled_image.size  # Adjust as needed
        # self.image_overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        # # Create a drawing object
        # draw = ImageDraw.Draw(self.image_overlay)

        # # Define circle parameters
        # circle_center = (width // 2, height // 2)
        # circle_radius = self.scaled_image.size[0] // 5

        # # Draw a circle with X % transparency
        # if self.color == 'black':
        #     circle_color = (255, 255, 255, int(255 * 0.2))  # RGBA format (red, green, blue, alpha)
        # else:
        #     circle_color = (0, 0, 0, int(255 * 0.2))  # RGBA format (red, green, blue, alpha)
        # draw.ellipse(
        #     [
        #         circle_center[0] - circle_radius,
        #         circle_center[1] - circle_radius,
        #         circle_center[0] + circle_radius,
        #         circle_center[1] + circle_radius,
        #     ],
        #     fill=circle_color,
        # )

        # # Apply the mask       
        # self.legal_move_image = Image.new("RGBA", self.scaled_image.size)
        # self.legal_move_image = Image.alpha_composite(self.legal_move_image, self.scaled_image)
        # self.legal_move_image = Image.alpha_composite(self.legal_move_image, self.image_overlay)
        # self.show_legal_move_img = ImageTk.PhotoImage(self.legal_move_image)

        return self.image
    
    def __str__(self):
        return self.letter


class DisplayBoard():   
    def __init__(self, string_board):
        DisplayBoard.board = [[None,None,None,None,None,None,None,None],
                              [None,None,None,None,None,None,None,None],
                              [None,None,None,None,None,None,None,None],
                              [None,None,None,None,None,None,None,None],
                              [None,None,None,None,None,None,None,None],
                              [None,None,None,None,None,None,None,None],
                              [None,None,None,None,None,None,None,None],
                              [None,None,None,None,None,None,None,None]]

        self.update_board(string_board)

    def update_board(self, string_board):
        for x in range(8):
            for y in range(8):
                DisplayBoard.board[x][y] = (Piece(string_board[x*8+y]))

    def __str__(self):
        ret_str = ""
        for row in DisplayBoard.board:
            for piece in row:
                ret_str += (piece.letter)
            ret_str += "\n"
        return ret_str
            

    



        