__author__ = 'reut'

import tkinter as tk
from logic.poker import poker as ppoker, players as pplayers, players
import random
import queue
import threading

import logging

LOGGER = logging.getLogger("poker-gui")
sh = logging.StreamHandler()
LEVEL = logging.DEBUG
sh.setLevel(LEVEL)
LOGGER.setLevel(LEVEL)
LOGGER.addHandler(sh)


class Menu(tk.Frame):
    def __init__(self, master):
        super(Menu, self).__init__(master, height=500, width=200)

        player_count_frame = tk.Frame(self)
        players_selection_var = tk.IntVar(self)
        players_selection_var.set(2)
        players_menu = tk.OptionMenu(player_count_frame, players_selection_var, 2, 3, 4, 5, 6, 7, 8)
        players_menu.pack(side=tk.RIGHT)
        player_count_label = tk.Label(player_count_frame)
        player_count_label['text'] = 'number of players'
        player_count_label.pack(side=tk.LEFT)

        starting_cash_frame = tk.Frame(self)
        cash_selection_var = tk.IntVar(self)
        cash_selection_var.set(100)
        cash_menu = tk.OptionMenu(starting_cash_frame, cash_selection_var, 100, 500, 1000)
        cash_menu.pack(side=tk.RIGHT)
        starting_cash_label = tk.Label(starting_cash_frame)
        starting_cash_label['text'] = 'starting cash'
        starting_cash_label.pack(side=tk.LEFT)

        start_button = tk.Button(self,
                                 text='Start!',
                                 command=lambda: self.make_game(master, players_selection_var.get(),
                                                                cash_selection_var.get()))

        # players_menu.pack()
        # cash_menu.pack()
        player_count_frame.pack()
        starting_cash_frame.pack()
        start_button.pack()

    def make_game(self, master, player_count, cash):
        self.pack_forget()
        _players = [GUIHumanPlayer("Player %d" % i, cash, master) for i in range(player_count)]
        return Game(master, ppoker.Poker(_players))


class ValidMove(tk.Button):
    def __init__(self, master, player, move):
        super(ValidMove, self).__init__(master, text=move.name)
        self.player = player
        self.move = move


class GUIPlayer(tk.Frame):
    def __init__(self, master, player, game_logic):
        super(GUIPlayer, self).__init__(master)
        self.game_logic = game_logic
        player.player_frame = self
        self.player = player
        self.name_label = tk.Label(self, text=player.name)
        self.cash_label = tk.Label(self, text=player.money)
        self.valid_moves = [ValidMove(self, self.player, move) for move in
                            self.player.available_actions(self.game_logic.current_round)]
        self.actions_frame = tk.Frame(self)
        self.refresh()

    def refresh(self):
        self.pack_forget()
        self.name_label.pack(side=tk.LEFT)
        self.cash_label.pack(side=tk.RIGHT)
        self.actions_frame.pack(side=tk.RIGHT)
        self.valid_moves = [ValidMove(self, self.player, move) for move in
                            self.player.available_actions(self.game_logic.current_round)]
        LOGGER.debug("%s has %d moves", self.player.name, len(self.valid_moves))
        for move in self.valid_moves:
            LOGGER.debug("valid move: %s", move.name)
            move.pack(side=tk.RIGHT)


class GUIHumanPlayer(players.BasePlayer):
    def __init__(self, name, money, gui_game):
        super(GUIHumanPlayer, self).__init__(name, money)
        self.gui_game = gui_game
        LOGGER.debug("%s interacting" % self.name)
        self.queue = queue.Queue()
        self.player_frame = None

    def interact(self, round_):
        self.gui_game.pack_forget()
        self.player_frame.refresh()
        self.gui_game.pack()
        return self.queue.get()
        # self.gui_game.update_gui(round_)
        # self.gui_game.logic_to_gui_queue.put(('interact', (self, self.available_actions(round_))))
        # return self.gui_game.gui_to_logic_queue.get()

    def get_amount(self, _min, _max):
        self.gui_game.update_gui(self)
        self.gui_game.logic_to_gui_queue.put(('get amount', (_min, _max)))
        return self.gui_game.gui_to_logic_queue.get()

    @staticmethod
    def gui_get_amount(_min, _max):
        while True:
            amount_selected_event = threading.Event()
            popup = tk.Toplevel()
            title = tk.Label(popup, text="How much [%d - %d]?" % (_min, _max), height=0, width=100)
            title.pack()

            amount_var = tk.StringVar()
            amount_var.set("%d" % _min)
            entry = tk.Entry(popup, textvariable=amount_var)
            entry.pack()

            confirm_amount = tk.Button(popup, text="ok", command=lambda: amount_selected_event.set())
            confirm_amount.pack()

            amount_selected_event.wait()
            if not amount_var.get().isdigit():
                print("amount not a number")
                continue
            amount = int(amount_var.get())
            if not _min <= amount <= _max:
                print("amount not in range")
                continue
            return amount


class Game(tk.Frame):
    def __init__(self, master, logic):
        super(Game, self).__init__(master, height=500, width=200)

        self.game_to_gui_messages_dict = {
            'interact': self.interact,
            'get amount': self.get_amount
        }
        self.gui_to_logic_queue = queue.Queue()
        self.logic_to_gui_queue = queue.Queue()

        self.game_logic = logic
        threading.Thread(target=self.game_logic.play)

        self.players_list = tk.Listbox(self)
        self.players_to_frames = {}
        for player in self.game_logic.players:
            player_frame = GUIPlayer(self.players_list, player, self.game_logic)
            self.players_list.insert(tk.END, player_frame)
            player_frame.pack()
            self.players_to_frames[player] = player_frame

        separator_label = tk.Label(self.players_list, text='options:')

        self.players_list.insert(tk.END, separator_label)

        self.players_list.pack()
        self.pack()

    def interact(self, player_button, available_actions):
        print("interact with %s (actions: %s)" % (player_button.name, str(available_actions)))
        action_buttons = [tk.Button(self.players_list, text=type(action).name) for action in available_actions]
        for action_button in action_buttons:
            self.players_list.insert(action_button)
            action_button.pack()
        self.players_list.pack()

    @staticmethod
    def get_amount(_min, _max):
        print("get amount %d - %d" % (_min, _max))

    def check_queue(self):
        print("checking queue")
        if self.should_update:
            self.update_gui(self.game_logic.current_round)
            self.should_update = False

        try:
            item, args = self.logic_to_gui_queue.get(timeout=1)
            # react to game message
            self.game_to_gui_messages_dict[item](*args)
            self.should_update = True
            print("got %s" % item)
        except Exception as e:
            print("no item in queue %s" % str(e))
        self.after(50, self.check_queue)

    def update_gui(self, _round):
        print("player %s" % str(_round.betting_player))
        self.players_to_frames[_round.betting_player].configure(bg="#999")
        self.pack()


root = tk.Tk()
menu = Menu(root)
menu.pack()
root.mainloop()
