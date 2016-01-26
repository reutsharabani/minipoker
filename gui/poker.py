from logic.poker.players import Action
import tkinter as tk
from logic.poker import poker as ppoker, players
import queue
import threading

import logging

LOGGER = logging.getLogger("poker-gui")
sh = logging.StreamHandler()
LEVEL = logging.DEBUG
sh.setLevel(LEVEL)
LOGGER.setLevel(LEVEL)
LOGGER.addHandler(sh)


class MESSAGES:
    REFRESH = "refresh"


class Menu(tk.Frame):
    def __init__(self, master):
        super(Menu, self).__init__(master, height=500, width=200)
        self.master = master
        players_selection_var = tk.IntVar(self)
        players_selection_var.set(2)
        players_menu = tk.OptionMenu(self, players_selection_var, 2, 3, 4, 5, 6, 7, 8)
        player_count_label = tk.Label(self)
        player_count_label['text'] = 'number of players'
        player_count_label.grid(row=0, column=0)
        players_menu.grid(row=0, column=1)

        cash_selection_var = tk.IntVar(self)
        cash_selection_var.set(100)
        cash_menu = tk.OptionMenu(self, cash_selection_var, 100, 500, 1000)
        starting_cash_label = tk.Label(self)
        starting_cash_label['text'] = 'starting cash'
        starting_cash_label.grid(row=1, column=0)
        cash_menu.grid(row=1, column=1)

        start_button = tk.Button(self,
                                 text='Start!',
                                 command=lambda: self.make_game(master, players_selection_var.get(),
                                                                cash_selection_var.get()))
        start_button.grid(row=3, column=0)

        self.pack()

    def make_game(self, master, player_count, cash):
        for widget in self.grid_slaves():
            widget.grid_forget()
        _players = [GUIHumanPlayer("Player %d" % i, cash, master) for i in range(player_count)]
        return Game(self, ppoker.Poker(_players))


class ValidMove(tk.Frame):
    # filler and parent to actual moves
    def __init__(self, master, player):
        super(ValidMove, self).__init__(master)
        self.player = player
        self.widget = tk.Label(self, text="NA")

    def set_label(self, text):
        self.widget['text'] = text


class GUIPlayer(tk.Frame):
    def __init__(self, master, player, moves):
        super(GUIPlayer, self).__init__(master)
        player.player_frame = self
        self.player = player
        self.moves = moves
        self.master = master
        self.name_label = tk.Label(master, text=player.name)
        self.cash_label = tk.Label(master, text=player.money)
        self.name_label.grid(row=player.id, column=0)
        self.cash_label.grid(row=player.id, column=1)

        self.move_frames = {x.__class__: ValidMove(master, self.player) for x in
                            Action.ALL_ACTIONS_F()}
        for offset, move in enumerate(self.move_frames.values()):
            move.grid(row=player.id, column=2 + offset)

    def refresh_moves(self, moves):
        LOGGER.debug("%s has %d moves", self.player.name, len(self.moves))
        for move in moves:
            move_frame = self.move_frames[move.__class__]
            move_frame.set_label("test")


class GUIHumanPlayer(players.BasePlayer):
    def __init__(self, name, money, gui_game):
        super(GUIHumanPlayer, self).__init__(name, money)
        self.gui_game = gui_game
        LOGGER.debug("%s interacting" % self.name)
        self.queue = queue.Queue()
        self.player_frame = None
        self.gui = None

    def interact(self, _round):
        LOGGER.debug("refreshing gui")
        self.gui.queue_refresh(_round)
        return self.queue.get()

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


class Game(object):
    def __init__(self, frame, logic):

        self.frame = frame

        self.game_logic = logic

        for player in self.game_logic.players:
            player.gui = self

        self.event_queue = queue.Queue()

        self.player_frames = []
        for player in self.game_logic.players:
            player_frame = GUIPlayer(self.frame, player, [])
            player_frame.grid(row=player.id)
            self.player_frames.append(player_frame)

        # start game only after gui initialized
        self.game_thread = threading.Thread(target=self.game_logic.play)
        self.game_thread.start()
        self.frame.after(10, func=self.process_event_queue)
        self.frame.pack()

    @staticmethod
    def get_amount(_min, _max):
        print("get amount %d - %d" % (_min, _max))

    def queue_refresh(self, _round):
        self.event_queue.put((MESSAGES.REFRESH, _round,))

    def process_event_queue(self):
        try:
            # LOGGER.debug("processing events") # too much output
            message = self.event_queue.get(block=False)
            if message[0] == MESSAGES.REFRESH:
                _round = message[1]
                for player_frame in self.player_frames:
                    player = player_frame.player
                    player_frame.moves = []
                    if len(player_frame.moves) > 0:
                        LOGGER.debug("Clearing: %s" % player.name)
                        player_frame.moves = []
                        player_frame.refresh_moves()
                    if _round and player is _round.betting_player:
                        LOGGER.debug("Populating: %s" % player.name)
                        moves = player.available_actions(_round)
                        LOGGER.debug("Adding %d moves to player: %s", len(moves), player.name)
                        player_frame.refresh_moves(moves)
            self.frame.pack()
        except queue.Empty:
            pass
        self.frame.after(10, func=self.process_event_queue)


root = tk.Tk()
menu = Menu(root)
root.mainloop()
