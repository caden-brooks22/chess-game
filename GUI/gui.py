import tkinter as tk
from tkinter import ttk
from random import randint
from pathlib import Path
from GUI.gui_settings import *
from GUI.game import GameState, openings
from PIL import Image, ImageTk
import threading
from time import sleep
import back_end.data_base as data_base
# import json

GUI_DIR = Path(__file__).resolve().parent

# TODO fix resizing img bug when making the window full screen.
#      it's easier to notice the bug when laptop is unplugged

class GUI():
    """Main GUI class for the chess game"""
    
    def start(gs = None):   # main function for the GUI
        """Main function to initialize and run the Tkinter GUI"""
        GUI.root = tk.Tk() 
        GUI.root.title('Chess') 
        GUI.root.geometry('900x600-0+0')    # "-0+0" puts window in top right corner
        GUI.stop_event = threading.Event()  # Event to signal threads to stop

        # GUI's refrence to the current game
        # if game state needs changed then update the refrence and store the old game elsewhere                                                       
        GUI.gameState = gs if gs else GameState() # Initialize game state if none provided

        GUI.theme = DefaultTheme()
        GUI.fonts = defaultFonts()
        GUI.user = data_base.login("Guest", "")

        # MUST create the frames before creating the content
        GUI.create_frame_layout(GUI.root)
        GUI.create_login_page(GUI.root)

        GUI.create_setting_content(GUI.setting_frame)
        GUI.create_local_game_content(GUI.local_game_frame)
        GUI.create_profile_content(GUI.profile_frame)

        # game_content must be called before left_content and right_content
        GUI.create_game_content(GUI.game_frame)

        GUI.create_left_content(GUI.left_header)
        GUI.create_right_content(GUI.right_header)
        GUI.create_opponent_content(GUI.opp_header)
        GUI.create_player_content(GUI.player_header)

        # Defer the binding until the root and widgets are fully initialized
        GUI.root.after(0, lambda: GUI.root.bind("<Configure>", lambda event: UpdateBoard.resize_handler(event)))
        GUI.root.after(0, lambda: UpdateBoard.resize_handler(None))
        
        GUI.root.mainloop()

    def create_frame_layout(root):
        """Creates the main layout frames"""
        
        GUI.main_game_frame = tk.Frame(root)
        GUI.main_game_frame.place(relx=0, rely=0, relheight=1, relwidth=1)
        frame = GUI.main_game_frame
        
        GUI.setting_frame = tk.Frame(frame)
        GUI.setting_frame.place(relx=0,rely=0,relwidth=.3, relheight=1)

        GUI.local_game_frame = tk.Frame(frame, bg=GUI.theme.local_game_menu)
        GUI.local_game_frame.place(relx=.15,rely=0,relwidth=.85, relheight=1)

        GUI.left_header = tk.Frame(frame, bg=GUI.theme.left_header)
        GUI.left_header.place(relx=0,rely=0,relwidth=.15, relheight=1)

        GUI.right_header = tk.Frame(frame, bg=GUI.theme.right_header)
        GUI.right_header.place(relx=.85,rely=0,relwidth=.15, relheight=1)

        GUI.opp_header = tk.Frame(frame, bg=GUI.theme.opp_header)
        GUI.opp_header.place(relx=.15,rely=0,relwidth=.7, relheight=.1)

        GUI.game_frame = tk.Frame(frame, bg=GUI.theme.game_frame)
        GUI.game_frame.place(relx=.15,rely=.1,relwidth=.7, relheight=.8)

        GUI.player_header = tk.Frame(frame, bg=GUI.theme.player_header)
        GUI.player_header.place(relx=.15,rely=.9,relwidth=.7, relheight=.1)

        GUI.profile_frame = tk.Frame(frame, bg=GUI.theme.profile_bg_color)
        GUI.profile_frame.place(relx=.15,rely=0,relwidth=.85, relheight=1)

    def create_setting_content(content_frame):
        # Create a canvas
        my_canvas = tk.Canvas(content_frame)
        my_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        #Add a scrollbar to the canvas
        my_scrollbar = tk.Scrollbar(content_frame, orient=tk.VERTICAL, command=my_canvas.yview)
        my_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        #configure the canvas
        my_canvas.configure(yscrollcommand=my_scrollbar.set)
        my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))

        # create another frame inside the canvas
        frame = tk.Frame(my_canvas, bg=GUI.theme.left_header)
        frame.pack(side='top',fill=tk.BOTH, expand=1)

        exit_setting_btn = tk.Button(frame, text='Save Prefrences', font=GUI.fonts.big_font, command=GUIController.un_focus_settings, bg=GUI.theme.save_n_exit_color, bd=0)
        exit_setting_btn.pack(fill='both')
        exit_setting_btn.bind('<Enter>', lambda event, widget=exit_setting_btn, color=GUI.theme.save_n_exit_highlight_color: GUIController.on_hover(event, widget, color))
        exit_setting_btn.bind('<Leave>', lambda event, widget=exit_setting_btn, color=GUI.theme.save_n_exit_color: GUIController.on_leave(event, widget, color))

        #TTK Styles
        check_box_style_1 = ttk.Style()
        check_box_style_1.configure(
            "Setting1.TCheckbutton",
            background=GUI.theme.setting_bg_1,
            font=GUI.fonts.setting_font,
            foreground=DefaultTheme.text_color
        )

        check_box_style_2 = ttk.Style()
        check_box_style_2.configure(
            "Setting2.TCheckbutton",
            background=GUI.theme.setting_bg_2,
            font=GUI.fonts.setting_font,
            foreground=GUI.theme.text_color
        )

        GUI.aq_bool = tk.BooleanVar(value=GUI.user["settings"]["auto_queen"])  
        GUI.auto_queen_btn = ttk.Checkbutton(frame, variable=GUI.aq_bool, style="Setting1.TCheckbutton" ,text="Auto Queen", var=GUI.aq_bool, command=lambda state=GUI.aq_bool, setting="auto_queen":GUIController.toggle_setting(state, setting))
        GUI.auto_queen_btn.pack(side='top', fill='x')

        GUI.af_bool = tk.BooleanVar(value=GUI.user["settings"]["auto_flip"])  
        GUI.auto_flip_btn = ttk.Checkbutton(frame, variable=GUI.af_bool, style="Setting2.TCheckbutton", text="Auto Flip (local only)", var=GUI.af_bool, command=lambda state=GUI.af_bool, setting="auto_flip":GUIController.toggle_setting(state, setting))
        GUI.auto_flip_btn.pack(side='top', fill='x')

        GUI.slm_bool = tk.BooleanVar(value=GUI.user["settings"]["show_legal_moves"])  
        GUI.show_legal_moves_btn = ttk.Checkbutton(frame, variable=GUI.slm_bool, style="Setting1.TCheckbutton", text="Show Legal Moves", var=GUI.slm_bool, command=lambda state=GUI.slm_bool, setting="show_legal_moves":GUIController.toggle_setting(state, setting))
        GUI.show_legal_moves_btn.pack(side='top', fill='x')

    def create_profile_content(parent_frame):
        # Load the image
        bg_img = Image.open(GUI_DIR / "img" / "simple-pawn.png")
        bg_img = bg_img.resize((parent_frame.winfo_screenwidth(), parent_frame.winfo_screenheight()), Image.Resampling.LANCZOS)
        GUI.profile_bg_photo = ImageTk.PhotoImage(bg_img)

        # Create a label for the background image
        background_label = tk.Label(parent_frame, image=GUI.profile_bg_photo)
        background_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        GUI.profile_content_frame = tk.Frame(parent_frame, width=300, height=320)
        frame = GUI.profile_content_frame
        frame.place(relx=0.5, rely=0.5, anchor='center')
        frame.pack_propagate(False)

        # canvas = tk.Canvas(frame, width=400, height=400)
        # canvas.pack(fill='both', expand=True)

        # # Ensure geometry is updated
        # frame.update_idletasks()
        # width, height = frame.winfo_width(), frame.winfo_height()
        # alpha = int(255 * 0.75)  # 75% opaque (25% transparent)
        # GUI.trans_img = Image.new("RGBA", (width, height), (0, 0, 0, alpha))

        # # Load and display background image
        # # bg_img = Image.open("./img/simple-pawn.png")
        # # bg_photo = ImageTk.PhotoImage(bg_img)
        # canvas.create_image(0, 0, image=GUI.trans_img, anchor='nw')

        # # Load button image and highlighted version
        # btn_img = Image.open("./img/white-rook.png")
        # btn_photo = ImageTk.PhotoImage(btn_img)
        # # Create a darkend version by adjusting the alpha values 
        # btn_img_highlight = btn_img.point(lambda p: int(p * 0.7))
        # btn_photo_highlight = ImageTk.PhotoImage(btn_img_highlight)

        GUI.username_lbl = tk.Label(frame, text=GUI.user["username"])
        GUI.username_lbl.pack()

    def create_left_content(frame):
        left_widgets = []

        button_stop = tk.Button(frame, text='Exit', command= lambda: GUIController.destroy_root(GUI.root), border=0, font=GUI.fonts.default_font, bg = GUI.theme.button_color, fg=GUI.theme.text_color, pady=10) 
        left_widgets.append(button_stop)
        
        button_setting = tk.Button(frame, text='Settings', command= lambda: GUIController.focus_settings_menu(), border=0, font=GUI.fonts.default_font, bg=GUI.theme.button_color, fg=GUI.theme.text_color, pady=10) 
        left_widgets.append(button_setting)

        button_analysis = tk.Button(frame, text='Analysis', command= lambda: GUIController.focus_chess_board(), border=0, font=GUI.fonts.default_font, bg=GUI.theme.button_color, fg=GUI.theme.text_color, pady=10) 
        left_widgets.append(button_analysis)

        button_play_local = tk.Button(frame, text='Play Local', command= lambda: GUIController.focus_local_menu(), border=0, font=GUI.fonts.default_font, bg=GUI.theme.button_color, fg=GUI.theme.text_color, pady=10) 
        left_widgets.append(button_play_local)

        button_play_online = tk.Button(frame, text='Play Online', border=0, font=GUI.fonts.default_font, bg=GUI.theme.button_color, fg=GUI.theme.text_color, pady=10) 
        left_widgets.append(button_play_online)
        button_play_online.config(state='disabled')

        button_profile = tk.Button(frame, text='Profile', command=GUIController.focus_profile, border=0, font=GUI.fonts.default_font, bg = GUI.theme.button_color, fg=GUI.theme.text_color, pady=10) 
        left_widgets.append(button_profile)

        # Packing widgets to the left frame and binding hover events
        for widget in left_widgets:
            widget.pack(side='top', fill="x")
            widget.bind('<Enter>', lambda event, widget=widget, color=GUI.theme.button_highlight_color: GUIController.on_hover(event, widget, color))
            widget.bind('<Leave>', lambda event, widget=widget, color=GUI.theme.button_color: GUIController.on_leave(event, widget, color))
            
    def create_right_content(frame):
        right_widgets = []

        reset_button = tk.Button(frame, text='Reset', command=lambda : GUIController.reset_game(), border=0, font=GUI.fonts.default_font, bg=GUI.theme.button_color, fg=GUI.theme.text_color, pady=10)
        right_widgets.append(reset_button)

        flip_button = tk.Button(frame, text='Flip', command=lambda: GUIController.toggle_perspective(), border=0, font=GUI.fonts.default_font, bg=GUI.theme.button_color, fg=GUI.theme.text_color, pady=10)
        right_widgets.append(flip_button)

        # Packing widgets to the right frame and binding hover events
        for widget in right_widgets:
            widget.pack(side='top', fill="x")
            widget.bind('<Enter>', lambda event, widget=widget, color=GUI.theme.button_highlight_color: GUIController.on_hover(event, widget, color))
            widget.bind('<Leave>', lambda event, widget=widget, color=GUI.theme.button_color: GUIController.on_leave(event, widget, color))

        move_history_frame = tk.Frame(frame)
        move_history_frame.pack(pady=(10,0))

        move_history_text_frame = tk.Frame(move_history_frame)
        move_history_text_frame.grid(row=0, column=0, sticky="nsew")
        # Create a Text widget
        text_widget = tk.Text(move_history_text_frame,width=int(12), height=20, font=("Helvetica", 12), wrap="word", state=tk.DISABLED)
        text_widget.pack(side='left', fill="both", expand=True)

        # Create a Scrollbar widget and attach it to the Text widget
        scrollbar = ttk.Scrollbar(move_history_text_frame, command=text_widget.yview)
        scrollbar.pack(side="right", fill="y")
        text_widget.config(yscrollcommand=scrollbar.set)

        # create a forward and back button for move history
        move_history_button_frame = tk.Frame(move_history_frame)
        move_history_button_frame.grid(row=1, column=0, sticky="nsew")

        #used to make buttons with text resize according to pixels not text
        pixel = tk.PhotoImage(width=1, height=1)

        move_back_history = tk.Button(move_history_button_frame, text='Back', width=1, height=12, border=1, relief=tk.SOLID, font=('Helvatical bold', 10), fg='black', image=pixel, compound="c")#, command=lambda: game_state.show_previous_move())
        move_back_history.pack(side='left', padx=0, pady=0, fill="both", expand=True)

        move_forward_history = tk.Button(move_history_button_frame, text='Forward', width=1, height=12, border=1, relief=tk.SOLID, font=('Helvatical bold', 10), fg='black', image=pixel, compound="c")#, command=lambda: game_state.show_next_move())
        move_forward_history.pack(side='right', padx=0, pady=0, fill="both", expand=True)
 
        # Configure row and column weights to make both frames take equal space
        move_history_frame.grid_rowconfigure(0, weight=3)
        move_history_frame.grid_rowconfigure(1, weight=1)
        move_history_frame.grid_columnconfigure(0, weight=1)

    def create_opponent_content(frame):
        tk.Label(frame, text="Self Analysis", font=GUI.fonts.default_font, bg=GUI.theme.opp_header, fg=GUI.theme.text_color).pack(fill='both', expand=True)

    def create_local_game_content(frame):
        """Creates the content for the local game menu"""
        button_start_game = tk.Button(frame, text='Start Game', command=lambda: GUIController.start_game(), border=0, font=GUI.fonts.big_font, bg=GUI.theme.button_color, fg=GUI.theme.text_color, pady=10)
        button_start_game.place(relx=.55, rely=.8, relwidth=.3, relheight=.1)
        button_start_game.bind('<Enter>', lambda event, widget=button_start_game, color=GUI.theme.button_highlight_color: GUIController.on_hover(event, widget, color))
        button_start_game.bind('<Leave>', lambda event, widget=button_start_game, color=GUI.theme.button_color: GUIController.on_leave(event, widget, color))

        button_back = tk.Button(frame, text='Back', command=lambda: GUIController.focus_chess_board(), border=0, font=GUI.fonts.big_font, bg=GUI.theme.button_color, fg=GUI.theme.text_color, pady=10)
        button_back.place(relx=.15, rely=.8, relwidth=.3, relheight=.1)
        button_back.bind('<Enter>', lambda event, widget=button_back, color=GUI.theme.button_highlight_color: GUIController.on_hover(event, widget, color))
        button_back.bind('<Leave>', lambda event, widget=button_back, color=GUI.theme.button_color: GUIController.on_leave(event, widget, color))

        white_player = tk.Label(frame, text="White Player", font=GUI.fonts.big_font, bg=GUI.theme.local_game_menu, fg=GUI.theme.text_color)
        white_player.place(relx=.15, rely=.1, relwidth=.3, relheight=.1)
        
        white_human = tk.Button(frame, text="Human", font=GUI.fonts.default_font, bg=GUI.theme.button_color, fg=GUI.theme.text_color, border=0)
        white_human.place(relx=.50, rely=.1, relwidth=.2, relheight=.1)
        white_human.bind('<Enter>', lambda event, widget=white_human, color=GUI.theme.button_highlight_color: GUIController.on_hover(event, widget, color))
        white_human.bind('<Leave>', lambda event, widget=white_human, color=GUI.theme.button_color: GUIController.on_leave(event, widget, color))

        white_comp = tk.Button(frame, text="Computer", font=GUI.fonts.default_font, bg=GUI.theme.button_color, fg=GUI.theme.text_color, border=0)
        white_comp.place(relx=.75, rely=.1, relwidth=.2, relheight=.1)
        white_comp.bind('<Enter>', lambda event, widget=white_comp, color=GUI.theme.button_highlight_color: GUIController.on_hover(event, widget, color))
        white_comp.bind('<Leave>', lambda event, widget=white_comp, color=GUI.theme.button_color: GUIController.on_leave(event, widget, color))

        white_human.config(command=lambda w_human=white_human, w_comp=white_comp: GUIController.set_player(w_human, w_comp,"white","human"))
        white_comp.config(command=lambda w_human=white_human, w_comp=white_comp: GUIController.set_player(w_human, w_comp,"white","computer"))

        GUIController.set_player(white_human, white_comp,"white",GUI.gameState.white_player)
        

        BlackPlayer = tk.Label(frame, text="Black Player", font=GUI.fonts.big_font, bg=GUI.theme.local_game_menu, fg=GUI.theme.text_color)
        BlackPlayer.place(relx=.15, rely=.3, relwidth=.3, relheight=.1)
        
        black_human = tk.Button(frame, text="Human", font=GUI.fonts.default_font, bg=GUI.theme.button_color, fg=GUI.theme.text_color, border=0)
        black_human.place(relx=.50, rely=.3, relwidth=.2, relheight=.1)
        black_human.bind('<Enter>', lambda event, widget=black_human, color=GUI.theme.button_highlight_color: GUIController.on_hover(event, widget, color))
        black_human.bind('<Leave>', lambda event, widget=black_human, color=GUI.theme.button_color: GUIController.on_leave(event, widget, color))

        black_comp = tk.Button(frame, text="Computer", font=GUI.fonts.default_font, bg=GUI.theme.button_color, fg=GUI.theme.text_color, border=0)
        black_comp.place(relx=.75, rely=.3, relwidth=.2, relheight=.1)
        black_comp.bind('<Enter>', lambda event, widget=black_comp, color=GUI.theme.button_highlight_color: GUIController.on_hover(event, widget, color))
        black_comp.bind('<Leave>', lambda event, widget=black_comp, color=GUI.theme.button_color: GUIController.on_leave(event, widget, color))

        black_human.config(command=lambda b_human=black_human, b_comp=black_comp: GUIController.set_player(b_human, b_comp,"black","human"))
        black_comp.config(command=lambda b_human=black_human, b_comp=black_comp: GUIController.set_player(b_human, b_comp,"black","computer"))
        GUIController.set_player(black_human, black_comp,"black",GUI.gameState.black_player)

        time_control_label = tk.Label(frame, text="Time Controls", font=GUI.fonts.big_font, bg=GUI.theme.local_game_menu, fg=GUI.theme.text_color)
        time_control_label.place(relx=.15, rely=.5, relwidth=.7, relheight=.1)

    def create_game_content(frame):
        GUI.chess_buttons = []

        # Create the 8x8 chessboard buttons
        for x in range(8):
            row = []
            for y in range(8):
                button = tk.Button(frame, image=GUI.gameState.display_board.board[x][y].image, border=0, bg=GUI.theme.light_square if (x + y) % 2 == 0 else GUI.theme.dark_square)
                button.pos = f"{chr(97+x)}{8-y}"
                button.config(command=lambda pos=button.pos, y=y, x=x: GUIController.on_square_click(pos, y, x))
                row.append(button)
            GUI.chess_buttons.append(row)

        # Bind the resize event to dynamically adjust button sizes
        frame.bind("<Configure>", lambda event: UpdateBoard.resize_board(event, frame))

        # Trigger the initial resize to set up the buttons
        frame.update_idletasks()
        UpdateBoard.resize_board(None, frame)
            
    def create_player_content(frame):
        GUI.player_title = tk.Label(frame, text=GUI.user["username"], font=GUI.fonts.default_font, bg=GUI.theme.player_header, fg=GUI.theme.text_color)
        GUI.player_title.pack(fill='both', expand=True)

    def create_login_page(root):
        # Load the image
        bg_img = Image.open(GUI_DIR / "img" / "simple-pieces.png")
        bg_img = bg_img.resize((root.winfo_screenwidth(), root.winfo_screenheight()), Image.Resampling.LANCZOS)
        GUI.login_bg_photo = ImageTk.PhotoImage(bg_img)

        # Create a label for the background image
        background_label = tk.Label(root, image=GUI.login_bg_photo)
        background_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        GUI.login_content_frame = tk.Frame(root, width=300, height=320)
        frame = GUI.login_content_frame
        frame.place(relx=0.5, rely=0.5, anchor='center')
        frame.pack_propagate(False)

        username_var = tk.StringVar()
        password_var = tk.StringVar()

        ttk.Label(frame, text="Welcome to Chess!", font=GUI.fonts.big_font).pack(anchor='n', pady=10, padx=10)
        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=(0,10))
        
        ttk.Label(frame, text="Username:").pack(anchor='w', pady=(0,2), padx=10)
        username_entry = ttk.Entry(frame, textvariable=username_var)
        username_entry.pack(fill='x', pady=(0,10), padx=10)

        ttk.Label(frame, text="Password:").pack(anchor='w', pady=(0,2), padx=10)
        password_entry = ttk.Entry(frame, textvariable=password_var, show="*")
        password_entry.pack(fill='x', pady=(0,10), padx=10)

        wrong_password_frame = tk.Frame(frame)
        wrong_password_frame.pack(side='top', padx=10, fill='x')

        GUI.wrong_login_lbl = ttk.Label(wrong_password_frame, text="", foreground='red')
        GUI.wrong_login_lbl.pack(side='left', pady=(0,10))

        forgot_btn = ttk.Button(wrong_password_frame, text="Forgot Password?", command=GUIController.on_forgot)
        forgot_btn.pack(side='right', anchor='e', pady=(0,10))

        signup_btn = ttk.Button(frame, text="Sign Up", command= lambda user=username_var, passw=password_var :GUIController.on_signup(user, passw))
        signup_btn.pack(side='bottom', fill='x', pady=(0,10), padx=10)

        continue_guest_btn = ttk.Button(frame, text="Continue as Guest", command=GUIController.guest_login)
        continue_guest_btn.pack(side='bottom', fill='x', pady=(0,10), padx=10)

        login_btn = ttk.Button(frame, text="Login", command= lambda user=username_var, passw=password_var :GUIController.on_login(user, passw))
        login_btn.pack(side='bottom', fill='x', pady=10, padx=10)
    
class GUIController():
    pos_start = None
    pos_end = None

    def on_hover(event, button, color):
        button.config(bg=color)

    def on_leave(event, button, color):
        button.config(bg=color)

    def destroy_root(root):
        def shutdown():
            if not GUI.stop_event.is_set():
                GUI.stop_event.set()  # Signal threads to stop
                print("Stopping threads...")

                # Wait for all threads to finish
                for thread in threading.enumerate():
                    if not (thread == threading.main_thread() or thread.name == "DestroyThread"):
                        print(f"Waiting for thread: {thread.name}")
                        thread.join()
                        print(f"Thread {thread.name} has finished.")

                print("Exiting program...")
                root.quit()

        # Run shutdown logic in a separate thread
        threading.Thread(target=shutdown, name="DestroyThread").start()

    def reset_game():
        GUI.gameState.reset_game()
        UpdateBoard.update_board()

    def toggle_perspective():
        gameSettings.perspective = not gameSettings.perspective
        UpdateBoard.resize_board(None, GUI.game_frame)

    def toggle_setting(state, setting):
        if state.get():
            GUI.user["settings"][setting] = True
        else:
            GUI.user["settings"][setting] = False

    def set_player(human_btn, comp_btn, color, player_type):
        """Sets the player type for the game"""
        if color == "white":
            GUI.gameState.white_player = player_type
        else:
            GUI.gameState.black_player = player_type

        if player_type == "human":
            human_btn.config(font=GUI.fonts.default_bold)
            comp_btn.config(font=GUI.fonts.default_font)
        else:
            human_btn.config(font=GUI.fonts.default_font)
            comp_btn.config(font=GUI.fonts.default_bold)

    def check_promotion(move):
        """Checks if a move is a promotion and returns the promotion piece"""
        file = ord(move[0]) - ord('a')  # Convert 'a'-'h' to 0-7
        rank = int(move[1]) - 1
        square = rank * 8 + file
        piece = GUI.gameState.board.piece_at(square)

        if piece and piece.piece_type == 1: # 1 == pawn
            if (piece.color == True and move[3] == '8') or (piece.color == False and move[3] == '1'):
                # Promotion detected
                if gameSettings.auto_queen:
                    move += 'q'
                else:
                    # TODO open a thread to allow user promotion for non-auto queening
                    move += 'q'

        return move

    def on_square_click(pos, y, x):
        # print(pos)
        if not GUIController.pos_start:
            GUIController.pos_start = pos
            GUI.chess_buttons[x][y].config(bg=GUI.theme.button_highlight_color)
        else:
            GUIController.pos_end = pos
            move = GUIController.pos_start + GUIController.pos_end
            move = GUIController.check_promotion(move)

            if GUI.gameState.is_human_turn() and GUI.gameState.is_legal_move(move):
                GUI.chess_buttons[x][y].config(bg=GUI.theme.button_color)
                has_winner = GUI.gameState.move(move)  # Call the move function with the selected move
                UpdateBoard.update_board()

                #If the game is over
                if not has_winner:
                    if has_winner == "White":
                        print("White Wins")
                    elif has_winner == "Black":
                        print("Black")
                    elif has_winner == "Stalemate":
                        print("Stalemate")
                    elif has_winner == "Draw":
                        print("Draw")
                    

                if GUI.gameState.is_human_turn() == False: # if it's now the bot's turn
                    threading.Thread(target=GUIController.bot_move_handler, args=(GUI.gameState.board,)).start()
            else:
                UpdateBoard.update_board()
                GUIController.pos_start = pos
                GUI.chess_buttons[x][y].config(bg=GUI.theme.button_highlight_color)
            
    def focus_profile():
        GUI.main_game_frame.lift()
        GUI.profile_frame.lift()
        GUI.left_header.lift()

    def focus_local_menu():
        """Focuses on the local game menu"""
        GUI.local_game_frame.lift()

    def focus_chess_board():
        """Focuses on the chess board"""
        GUI.main_game_frame.lift()
        GUI.game_frame.lift()
        GUI.left_header.lift()
        GUI.right_header.lift()
        GUI.opp_header.lift()
        GUI.player_header.lift()

    def focus_settings_menu():
        """Focuses on the settings menu"""
        GUI.game_frame.place(relx=.3)
        GUI.opp_header.place(relx=.3)
        GUI.player_header.place(relx=.3)
        GUI.setting_frame.lift()
        GUI.opp_header.lift()
        GUI.player_header.lift()
        GUI.game_frame.lift()

    def un_focus_settings():
        # Save all The settings
        data_base.edit_settings(GUI.user["username"], GUI.user["settings"])

        # Focus the game window
        GUI.game_frame.place(relx=.15)
        GUI.opp_header.place(relx=.15)
        GUI.player_header.place(relx=.15)
        GUI.left_header.lift()
        GUI.right_header.lift()
        GUI.opp_header.lift()
        GUI.player_header.lift()
        GUI.game_frame.lift()

    def on_wrong_login():
        # frame = GUI.login_content_frame
        #TODO after implementing a database add protection against ddos attacks
        GUI.wrong_login_lbl.config(text="incorect username or password")
        
    def on_login(username_var, password_var):
        # print("Login clicked. Username:", username_var.get(), "Password:", password_var.get())
        if data_base.login(username_var.get(), password_var.get()):
            GUI.user = data_base.login(username_var.get(), password_var.get())
            UpdateBoard.on_login(GUI.user)
            GUIController.focus_profile()
        else:
            GUIController.on_wrong_login()

    def on_signup(username_var, password_var):
        if username_var.get == "" or password_var.get() == "":
            user = 0
        else:
            user = data_base.add_user(username_var.get(), password_var.get())
        
        match user:
            case 0:
                GUI.wrong_login_lbl.config(text="enter a username and password\nto sign up")
            case 1:
                GUI.wrong_login_lbl.config(text="username is already taken")
            case 2:
                GUI.wrong_login_lbl.config(text="username contains unallowed\ncharicter(s)")
            case 3:
                GUI.wrong_login_lbl.config(text="password must be at least\n8 charicter long")
            case 4:
                GUI.wrong_login_lbl.config(text="password contains unallowed\ncharicter(s)")
            case 5:
                GUI.wrong_login_lbl.config(text="username must be at lesat\n3 charicter long")
            case _:
                print("signed up!")
                print(user)
                GUI.user = user
                UpdateBoard.on_login(GUI.user)
                GUIController.focus_profile()

    def guest_login():
        if data_base.login("Guest", ""):
            GUI.user = data_base.login("Guest", "")
        GUIController.focus_profile()

    def on_forgot():
        print("Forgot Password clicked.")

    def bot_move_handler(board):
        """Handles the bot's move"""
        while not GUI.gameState.is_human_turn() and not GUI.stop_event.is_set():
            sleep(.1) # temporary solution to let the GUI update quickly, rather then slowly

            move = GUI.gameState.bot.bestMove(board, GUI.stop_event)
            
            # TODO: handle these errors to garentee that the game keeps running
            if not move:
                raise ValueError("bot had error in bot.best_move()")
            if not GUI.gameState.is_legal_move(move):
                raise ValueError(f"bot returned an ilegal move: {move}")
            
            GUI.gameState.move(move)
            GUI.root.after(0, lambda: UpdateBoard.update_board()) 

    def start_game():
        GUIController.focus_chess_board()
        if GUI.gameState.white_player == "computer" and GUI.gameState.get_turn():  # if bot makes first move
            # start the bot thread to calculate the first move
            threading.Thread(target=GUIController.bot_move_handler, args=(GUI.gameState.board,)).start()

class UpdateBoard():
    img_size = 61 # default size of the image based on the default window size
    resize_timer = None

    def update_board(): # updates everything
        UpdateBoard.rescale_img()
        UpdateBoard.square_color()
        # print(GUI.gameState.display_board)

    def square_color():
        for x, row in enumerate(GUI.chess_buttons):
            for y, square in enumerate(row):
                if x%2 == 0 and y%2 == 0 or x%2 != 0 and y%2 != 0:
                    square.config(bg=GUI.theme.light_square)
                else:
                    square.config(bg=GUI.theme.dark_square)

    def resize_board(event, frame):
            # Get the current width and height of the frame
            frame_width = frame.winfo_width()
            frame_height = frame.winfo_height()

            # Calculate the size of each square (button)
            square_size = min(frame_width, frame_height) // 8

            offset_x = (frame_width - square_size * 8) / 2
            offset_y = (frame_height - square_size * 8) / 2

            # Update the position and size of each button
            for x in range(8):
                for y in range(8):
                    button = GUI.chess_buttons[
                        x if gameSettings.perspective == 1 else 7 - x][
                        y if gameSettings.perspective == 1 else 7 - y]
                    button.place(
                        x=x * square_size + offset_x,
                        y=y * square_size + offset_y,
                        width=square_size,
                        height=square_size
                    )
    
    def on_login(user):
        """updates app based on user prefrences"""
        GUI.aq_bool.set(user["settings"]["auto_queen"])
        GUI.af_bool.set(user["settings"]["auto_flip"])
        GUI.slm_bool.set(user["settings"]["show_legal_moves"])

        GUI.player_title.config(text=GUI.user["username"])

        match user["settings"]["theme"]:
            case "default":
                GUI.theme = DefaultTheme
            case "dark":
                GUI.theme = DefaultTheme
            case "blue":
                GUI.theme = BluesTheme

    def resize_handler(event):
        if event == None or event.widget == GUI.root:
            # Cancel any previously scheduled resize handling
            if UpdateBoard.resize_timer is not None:
                GUI.root.after_cancel(UpdateBoard.resize_timer)

            # Schedule the resize handling to occur after 100ms
            UpdateBoard.resize_timer = GUI.root.after(20, lambda: UpdateBoard.rescale_img(event))

    def rescale_img(event=None):
        size = min(GUI.game_frame.winfo_width(), GUI.game_frame.winfo_height()) // 8
        if(size != UpdateBoard.img_size) or event == None:
            if size > 0:
                UpdateBoard.img_size = size
            for y in range(8):
                for x in range(8):
                    GUI.gameState.display_board.board[x][y].rescale_img(UpdateBoard.img_size)
                    GUI.chess_buttons[y][x].config(image=GUI.gameState.display_board.board[x][y].image)




def main():
    GUI.start()

if __name__ == "__main__":
    main()