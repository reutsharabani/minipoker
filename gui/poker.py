__author__ = 'reut'

import tkinter as tk
from logic.poker import poker as ppoker, players as pplayers, players
import time
import random


class Menu(tk.Frame):
    def __init__(self, master, options_functions):
        super(Menu, self).__init__(master, height=500, width=200)
        players_selection_var = tk.IntVar(self)
        players_selection_var.set(2)
        players_menu = tk.OptionMenu(self, players_selection_var, 2, 3, 4, 5, 6, 7, 8)
        cash_selection_var = tk.IntVar(self)
        cash_selection_var.set(100)
        cash_menu = tk.OptionMenu(self, cash_selection_var, 100, 500, 1000)

        start_button = tk.Button(self, text='Start!',
                                 command=lambda: Game(master, self, players_selection_var.get(),
                                                            cash_selection_var.get()))

        players_menu.pack()
        cash_menu.pack()
        start_button.pack()


class GUIPlayer(tk.Button):

    def __init__(self, master, player):
        super(GUIPlayer, self).__init__(master, text=player.name, command=lambda: print(str(player)))


class GUIHumanPlayer(players.BasePlayer):

    def __init__(self, name, money, gui_game):
        super(GUIHumanPlayer, self).__init__(name, money)
        self.gui_game = gui_game

    def interact(self, round_):
        self.gui_game.update_gui(self)
        return random.choice(self.available_actions(round_))(self, round_)

    def get_amount(self, description):


class Game(tk.Frame):

    def __init__(self, master, _menu, player_count, cash):
        super(Game, self).__init__(master, height=500, width=200)

        _menu.pack_forget()
        _players = [GUIHumanPlayer("Player %d" % i, cash, self) for i in range(player_count)]
        self.game_logic = ppoker.Poker(_players)

        self.menu = _menu

        players_list = tk.Listbox(self)
        self.players_to_buttons = {}
        for player in self.game_logic.players:
            player_button = GUIPlayer(players_list, player)
            players_list.insert(tk.END, player_button)
            player_button.pack()
            self.players_to_buttons[player] = player_button

        players_list.pack()
        self.pack()

        self.game_logic.play()

    def update_gui(self, active_player):
        print("player %s" % str(active_player))
        self.players_to_buttons[active_player].configure(bg="#999")
        self.pack()




root = tk.Tk()
menu = Menu(root, [('text', lambda: 1)])
menu.pack()
root.mainloop()
