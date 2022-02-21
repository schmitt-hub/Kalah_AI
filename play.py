# Module concerned with building a GUI for playing against the AI or against another user

from tkinter import *
from math import ceil
import os
from utils import *
from mcts import *


class App:
    def __init__(self):
        super().__init__()
        self.initialize_startscreen_window({'houses': 6, 'seeds': 4,  'start player': 0, 'mode': True})

    # methods for the start screen
    def initialize_startscreen_window(self, game_settings):
        self.startscreen_window = Tk()
        self.startscreen_window.rowconfigure(list(range(5)), minsize=50)
        self.startscreen_window.columnconfigure(list(range(9)), minsize=50)
        self.startscreen_window.title("Set your preferences")

        self.min_nr_of_houses = 2
        self.max_nr_of_houses = 9
        self.min_nr_of_seeds = 2
        self.max_nr_of_seeds = 9

        self.start_player = game_settings['start player']
        self.nr_of_houses = game_settings['houses']
        self.nr_of_seeds = game_settings['seeds']
        self.is_single_player = game_settings['mode']
        self.game_settings = {'houses': self.nr_of_houses, 'seeds': self.nr_of_seeds, 'start player': self.start_player,
                              'mode': self.is_single_player}

        self.btns = {'houses': {}, 'seeds': {}, 'start player': {}, 'mode': {}}

        # create buttons for the user to select the number of houses
        for houses in range(self.min_nr_of_houses, self.max_nr_of_houses + 1):
            self.btns['houses'][houses] = Button(master=self.startscreen_window, text=str(houses) + ' houses',
                                                 bg='white',
                                                 command=lambda arg=('houses', houses): self.configure_game(arg))
            self.btns['houses'][houses].grid(row=0, column=houses-1, sticky="nsew")
        self.btns['houses'][self.nr_of_houses]['bg'] = 'green'

        # create buttons for the user to select the number of seeds
        for seeds in range(self.min_nr_of_seeds, self.max_nr_of_seeds + 1):
            self.btns['seeds'][seeds] = Button(master=self.startscreen_window, text=str(seeds) + ' seeds', bg='white',
                                               command=lambda arg=('seeds', seeds): self.configure_game(arg))
            self.btns['seeds'][seeds].grid(row=1, column=seeds-1, sticky="nsew")
        self.btns['seeds'][self.nr_of_seeds]['bg'] = 'green'

        # create buttons for the user to select if he wants to play against another user or against the AI
        single_player_dict = {1: 'Player vs AI', 0: 'Player vs player'}
        for mode in range(2):
            self.btns['mode'][mode] = Button(master=self.startscreen_window, text=single_player_dict[mode], bg='white',
                                             command=lambda arg=('mode', mode): self.configure_game(arg))
            self.btns['mode'][mode].grid(row=2, column=1 + 4 * (1-mode), sticky="nsew", columnspan=4)
        self.btns['mode'][self.is_single_player]['bg'] = 'green'

        # create buttons for the user to select who starts
        start_player_dict = {0: 'User starts', 1: 'AI starts'}
        for player in range(2):
            self.btns['start player'][player] = Button(master=self.startscreen_window, text=start_player_dict[player],
                                                       bg='white',
                                                       command=lambda arg=('start player', player):
                                                       self.configure_game(arg))
            self.btns['start player'][player].grid(row=3, column=1 + 4 * player, sticky="nsew", columnspan=4)
        self.btns['start player'][self.start_player]['bg'] = 'green'

        # create a button to switch to the game window
        self.btn_start = Button(master=self.startscreen_window, text='Start the game', bg='white',
                                command=lambda: self.enter_game())
        self.btn_start.grid(row=4, column=1, sticky="nsew", columnspan=4)

        # create a button to exit
        self.btn_exit = Button(master=self.startscreen_window, text='Exit', bg='white',
                               command=lambda: self.exit())
        self.btn_exit.grid(row=4, column=5, sticky="nsew", columnspan=4)

        # create a few labels
        self.lbl_houses = Label(master=self.startscreen_window, text='How many houses?', bg='grey', relief='groove')
        self.lbl_houses.grid(row=0, column=0, sticky="nsew")
        self.lbl_seeds = Label(master=self.startscreen_window, text='How many seeds?', bg='grey', relief='groove')
        self.lbl_seeds.grid(row=1, column=0, sticky="nsew")
        self.lbl_single_player = Label(master=self.startscreen_window, text='Play mode?', bg='grey', relief='groove')
        self.lbl_single_player.grid(row=2, column=0, sticky="nsew")
        self.lbl_start_player = Label(master=self.startscreen_window, text='Who starts?', bg='grey', relief='groove')
        self.lbl_start_player.grid(row=3, column=0, sticky="nsew")
        self.lbl_proceed = Label(master=self.startscreen_window, text='', bg='grey', relief='groove')
        self.lbl_proceed.grid(row=4, column=0, sticky="nsew")

    def configure_game(self, arg):
        """
        configure the game settings in accordance to the buttons pressed
        """
        (param_type, param_value) = arg
        self.game_settings[param_type] = param_value
        for i, button in self.btns[param_type].items():
            if not i == param_value:
                button['bg'] = 'white'
        self.btns[param_type][param_value]['bg'] = 'green'
        if param_type == 'mode':
            if param_value == 0:
                self.btns['start player'][0]['text'] = 'Player 1 starts'
                self.btns['start player'][1]['text'] = 'Player 2 starts'
            else:
                self.btns['start player'][0]['text'] = 'Player starts'
                self.btns['start player'][1]['text'] = 'AI starts'

    def exit(self):
        """
        exit the applicaiton
        """
        self.startscreen_window.destroy()

    def enter_game(self):
        """
        switch to the game window
        """
        self.startscreen_window.destroy()
        self.initialize_game_window(self.game_settings)


    def initialize_game_window(self, game_settings):
        """
        methods for the game window
        """
        self.start_player = game_settings['start player']
        self.nr_of_houses = game_settings['houses']
        self.nr_of_seeds = game_settings['seeds']
        self.is_single_player = game_settings['mode']
        self.player = self.start_player
        self.is_move_finished = False
        self.has_move_started = False
        self.active_seeds = 0
        self.game_over = False
        self.board = [[self.nr_of_seeds] * self.nr_of_houses + [0], [self.nr_of_seeds] * self.nr_of_houses + [0]]

        self.photos = {}
        self.colors = {0: "blue", 1: "red"}
        self.btns = {0: {}, 1: {}}
        self.lbls = {}

        self.game_window = Tk()
        self.game_window.rowconfigure(list(range(5)), minsize=50)
        self.game_window.columnconfigure(list(range(self.nr_of_houses + 2)), minsize=50)
        self.game_window.title("Kalah")

        # Create a PhotoImages object to use as images
        self.photos = {i: PhotoImage(file=os.getcwd()+"\\Kalah_upload\\images\\Seed" + str(i) + ".png") for i in range(31)}

        self.lbl_score = Label(master=self.game_window, text='', font=("Courier", 30))
        self.lbl_score.grid(row=2, column=1, columnspan=self.nr_of_houses, sticky="nsew")

        self.lbl_result = Label(master=self.game_window, text='', font=("Courier", 20))
        self.lbl_result.grid(row=0, column=1, columnspan=self.nr_of_houses, sticky="nsew")

        self.btn_start = Button(master=self.game_window, text='Start game', font=("Courier", 30),
                                command=self.start_game)
        self.btn_start.grid(row=4, column=1, columnspan=ceil(self.nr_of_houses/2), sticky="nsew")

        self.btn_quit = Button(master=self.game_window, text='Quit game', font=("Courier", 30), command=self.quit_game)
        self.btn_quit.grid(row=4, column=1+ceil(self.nr_of_houses/2), columnspan=self.nr_of_houses//2, sticky="nsew")

        text_location = {0: "bottom", 1: "top"}
        for player in range(2):
            for house in range(self.nr_of_houses):
                self.btns[player][house] = Button(master=self.game_window, text=self.nr_of_seeds, font=("Courier", 15),
                                                  image=self.photos[self.nr_of_seeds], compound=text_location[player],
                                                  command=lambda arg=(player, house, player, 0, 0): self.move(arg))
                self.btns[player][house].grid(row=1 + 2 * (1 - player),
                                              column=house + 1 + player * (self.nr_of_houses - 1 - 2 * house),
                                              sticky="nsew")
                self.btns[player][house]["activebackground"] = self.colors[player]
                self.btns[player][house]["background"] = "silver"
                self.btns[player][house]["state"] = "disabled"


            self.lbls[player] = Label(master=self.game_window, text=0, bg=self.colors[player],
                                      image=self.photos[0])
            self.lbls[player].grid(row=2, column=(self.nr_of_houses + 1) * (1 - player), sticky="nsew")

    def visualize_move(self):
        """
        visualize the move on the board
        """
        for p in range(2):
            for i in range(self.nr_of_houses):
                self.btns[p][i]["text"] = self.board[p][i]
                self.btns[p][i]["image"] = self.photos[min(30, self.board[p][i])]
                if not self.is_move_finished:
                    # disable the button by setting the command to zero but keep its appearance "active looking"
                    self.btns[p][i]["command"] = 0
                    self.btns[p][i]["state"] = "active"
                else:
                    # activate those buttons that are allowed to be pressed
                    # the other buttons take on a "disabled looking" appearance
                    self.btns[p][i]["command"] = lambda arg=(p, i, p, 0, 0): self.move(arg)
                    if self.player != p or self.board[p][i] == 0:
                        self.btns[p][i]["state"] = "disabled"
            self.lbls[p]["text"] = self.board[p][-1]
            self.lbls[p]["image"] = self.photos[min(30, self.board[p][-1])]
        self.lbl_score["text"] = str(self.lbls[1]["text"]) + " - " + str(self.lbls[0]["text"])
        # don't allow restarting/quitting in the middle of a move
        if not self.is_move_finished:
            self.btn_start["state"] = "disabled"
            self.btn_quit["state"] = "disabled"
        else:
            self.btn_start["state"] = "active"
            self.btn_quit["state"] = "active"

    def move(self, arg):
        """
        change the board seed by seed
        """
        (player, house, side, self.active_seeds, self.has_move_started) = arg
        self.board, side, house, self.player, self.active_seeds, self.has_move_started, self.is_move_finished = \
            compute_state_stepwise(player, self.board, side, house, self.active_seeds, self.has_move_started)
        self.game_over = is_game_over(self.board, self.is_move_finished)
        self.visualize_move()

        if is_game_over(self.board, self.is_move_finished):
            self.board = end_the_game(self.board)
            self.visualize_move()
            self.display_result()
        # continue displaying the move
        elif not self.is_move_finished:
            self.btns[0][0].after(300, self.move, (self.player, house, side, self.active_seeds, self.has_move_started))
        # ai's turn
        elif self.is_single_player and self.player == 1:
            self.is_move_finished = False
            house = get_ai_house(self.player, self.board, 2)
            self.btns[0][0].after(300, self.move, (self.player, house, self.player, self.active_seeds, 0))

    def display_result(self):
        """
        display the game result
        """
        if self.lbls[0]["text"] > self.lbls[1]["text"]:
            if self.is_single_player:
                self.lbl_result["text"] = "You won!"
            else:
                self.lbl_result["text"] = "Player 1 won!"
        elif self.lbls[0]["text"] < self.lbls[1]["text"]:
            if self.is_single_player:
                self.lbl_result["text"] = "The AI won!"
            else:
                self.lbl_result["text"] = "Player 2 won!"
        else:
            self.lbl_result["text"] = "It's a tie!"

    def reset_board(self):
        """
        reset the board to its initial settings
        """
        self.player = self.start_player
        self.is_move_finished = False
        self.has_move_started = False
        self.game_over = False
        self.active_seeds = 0
        self.board = [[self.nr_of_seeds] * self.nr_of_houses + [0], [self.nr_of_seeds] * self.nr_of_houses + [0]]
        self.lbl_score['text'] = ''
        self.lbl_result['text'] = ''
        for player in range(2):
            for house in range(self.nr_of_houses):
                self.btns[player][house]['text'] = self.nr_of_seeds
                self.btns[player][house]['image'] = self.photos[self.nr_of_seeds]
            self.lbls[player]['text'] = 0
            self.lbls[player]['image'] = self.photos[0]

    def start_game(self):
        """
        start the game
        """
        for house in range(self.nr_of_houses):
            self.btns[self.start_player][house]["state"] = "active"
        self.btn_start["text"] = "Restart game"
        self.reset_board()
        if self.start_player == 1:
            house = get_ai_house(self.player, self.board, 1)
            self.btns[0][0].after(300, self.move, (self.player, house, self.player, 0, 0))

    def quit_game(self):
        """
        switch to the startscreen window
        """
        self.game_window.destroy()
        self.initialize_startscreen_window(self.game_settings)


if __name__ == "__main__":
    app = App()
    app.startscreen_window.mainloop()
