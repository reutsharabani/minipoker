__author__ = 'reut'

import tkinter as tk
from logic.poker import poker as ppoker, players as pplayers, players
import random
import queue
import threading


class Menu(tk.Frame):
    def __init__(self, master):
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
        self.gui_game.update_gui(round_)
        self.gui_game.logic_to_gui_queue.put(('interact', (self, self.available_actions(round_))))
        return self.gui_game.gui_to_logic_queue.get()

    def get_amount(self, _min, _max):
        self.gui_game.update_gui(self)
        self.gui_game.logic_to_gui_queue.put(('get amount', (_min, _max)))
        return self.gui_game.gui_to_logic_queue.get()

    def gui_get_amount(self, _min, _max):
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

    def __init__(self, master, _menu, player_count, cash):
        super(Game, self).__init__(master, height=500, width=200)

        self.game_to_gui_messages_dict = {
            'interact': self.interact,
            'get amount': self.get_amount
        }
        self.gui_to_logic_queue = queue.Queue()
        self.logic_to_gui_queue = queue.Queue()

        _menu.pack_forget()
        _players = [GUIHumanPlayer("Player %d" % i, cash, self) for i in range(player_count)]
        self.game_logic = ppoker.Poker(_players)

        self.menu = _menu

        self.players_list = tk.Listbox(self)
        self.players_to_buttons = {}
        for player in self.game_logic.players:
            player_button = GUIPlayer(self.players_list, player)
            self.players_list.insert(tk.END, player_button)
            player_button.pack()
            self.players_to_buttons[player] = player_button

        separator_label = tk.Label(self.players_list, text='options:')

        self.players_list.insert(tk.END, separator_label)

        self.players_list.pack()
        self.pack()

        self.game_thread = threading.Thread(target=self.game_logic.play)
        self.game_thread.start()

        self.should_update = True
        # start checking queue for game events
        self.after(50, self.check_queue)

    def interact(self, player_button, available_actions):
        print("interact with %s (actions: %s)" % (player_button.name, str(available_actions)))
        action_buttons = [tk.Button(self.players_list, text=type(action).name) for action in available_actions]
        for action_button in action_buttons:
            self.players_list.insert(action_button)
            action_button.pack()
        self.players_list.pack()

    def get_amount(self, _min, _max):
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
        self.players_to_buttons[_round.betting_player].configure(bg="#999")
        self.pack()




root = tk.Tk()
menu = Menu(root)
menu.pack()
root.mainloop()
