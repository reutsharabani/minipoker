import tkinter as tk
import queue
import threading
import logging

from minipoker.logic import poker as ppoker, players

FORMAT = '%(name)s - %(message)s'
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
LOGGER = logging.getLogger("poker-gui")

event_queue = queue.Queue()
gui_to_logic_queue = queue.Queue()


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


ENABLE = 'active'
DISABLE = 'disabled'


class CallButton(tk.Button):
    def __init__(self, master):
        super(CallButton, self).__init__(master, text="call NA")
        self.action = players.Call

    def disable(self):
        self['state'] = DISABLE

    def enable(self):
        self['state'] = ENABLE

    def refresh(self, player, _round):
        if not player or not _round or not self.action.is_valid(player, _round):
            self.disable()
        else:
            self['text'] = 'Call %d' % _round.pot.amount_to_call(player)
            self['command'] = lambda: player.queue.put(self.action(player, _round))
            self.enable()


class CheckButton(tk.Button):
    def __init__(self, master):
        super(CheckButton, self).__init__(master, text="check NA")
        self.action = players.Check

    def disable(self):
        self['state'] = DISABLE

    def enable(self):
        self['state'] = ENABLE

    def refresh(self, player, _round):
        if not player or not _round or not self.action.is_valid(player, _round):
            self.disable()
        else:
            self['text'] = 'Check'
            self['command'] = lambda: player.queue.put(self.action(player, _round))
            self.enable()


class BetButton(tk.OptionMenu):
    def __init__(self, master):
        self.bet_var = tk.StringVar(master)
        self.bet_var.set("Bet NA")
        super(BetButton, self).__init__(master, self.bet_var, "Bet NA")
        self.action = players.Bet

    def disable(self):
        self['state'] = DISABLE

    def enable(self):
        self['state'] = ENABLE

    def refresh(self, player, _round):
        self['menu'].delete(0, tk.END)
        if not player or not _round or not self.action.is_valid(player, _round):
            self.disable()
        else:
            self.bet_var.set("Bet ...")
            minimum, maximum = _round.pot.minimum_to_bet(player), player.money
            step = max((maximum - minimum) // 10, 1)
            LOGGER.info("minimum: %d, maximum: %d, step: %d" % (minimum, maximum, step))

            def bet(_amount):
                return lambda: player.queue.put(players.Bet(player, _round, _amount))

            # add 10 betting options
            for amount in range(minimum, maximum, step):
                self['menu'].add_command(label="Bet %d" % amount,
                                         command=bet(amount))
            # add all-in option
            self['menu'].add_command(label="All In! (%d)" % maximum, command=bet(maximum))
            self.enable()


class FoldButton(tk.Button):
    def __init__(self, master):
        super(FoldButton, self).__init__(master, text="fold NA")
        self.action = players.Fold

    def disable(self):
        self['state'] = DISABLE

    def enable(self):
        self['state'] = ENABLE

    def refresh(self, player, _round):
        if not player or not _round or not self.action.is_valid(player, _round):
            self.disable()
        else:
            self['text'] = 'Fold'
            self['command'] = lambda: player.queue.put(self.action(player, _round))
            self.enable()


class GUIPlayer(tk.Frame):
    def __init__(self, master, player, moves):
        super(GUIPlayer, self).__init__(master)
        player.player_frame = self
        self.player = player
        self.moves = moves
        self.master = master
        self.row = player.id + 1
        self.name_label = tk.Label(master, text=player.name)
        self.cash_label = tk.Label(master, text=player.money)
        self.name_label.grid(row=self.row, column=0)
        self.cash_label.grid(row=self.row, column=1)

        self.pocket1 = tk.Label(master, text='na')
        self.pocket2 = tk.Label(master, text='na')
        self.pocket1.grid(row=self.row, column=2)
        self.pocket2.grid(row=self.row, column=3)

        self.pot = tk.Label(master, text='na')
        self.pot.grid(row=self.row, column=4)

        self.move_buttons = {
            "check": CheckButton(master),
            "bet": BetButton(master),
            "fold": FoldButton(master),
            "call": CallButton(master),
        }
        # place action buttons
        for offset, move in enumerate(self.move_buttons.values()):
            move.grid(row=self.row, column=5 + offset)
        self.refresh(None)

    def refresh(self, _round):
        if self.player.pocket:
            self.pocket1['text'] = self.player.pocket[0]
            self.pocket1['fg'] = self.player.pocket[0].color()
            self.pocket2['text'] = self.player.pocket[1]
            self.pocket2['fg'] = self.player.pocket[1].color()
        for move_button in self.move_buttons.values():
            move_button.refresh(self.player, _round)
        if _round:
            self.pot['text'] = _round.pot.player_bet(self.player)
            self.cash_label['text'] = "%d" % self.player.money

    def disable(self):
        for move_button in self.move_buttons.values():
            move_button['state'] = DISABLE


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

        # refresh gui
        event_queue.put((MESSAGES.REFRESH, _round,))

        # get move
        return self.queue.get()

    def get_amount(self, _min, _max):
        self.queue.get()

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

        for offset, title in enumerate("Player,Money,Card 1,Card2,Invested".split(",")):
            tk.Label(self.frame, text=title).grid(row=0, column=offset)

        self.player_frames = {}
        for player in self.game_logic.players:
            player_frame = GUIPlayer(self.frame, player, [])
            player_frame.grid(row=player.id + 1)
            self.player_frames[player] = player_frame

        tk.Label(self.frame, text="Community Cards:").grid(row=len(self.game_logic.players) + 1)

        self.community_cards = [tk.Label(self.frame, text='') for _ in range(5)]
        for offset, community_card in enumerate(self.community_cards):
            community_card.grid(row=len(self.game_logic.players) + 2, column=offset)

        # start game only after gui initialized
        self.game_thread = threading.Thread(target=self.game_logic.play)
        self.game_thread.start()
        self.frame.after(10, func=self.process_event_queue)
        self.frame.pack()

    @staticmethod
    def get_amount(_min, _max):
        print("get amount %d - %d" % (_min, _max))

    def process_event_queue(self):
        # this is needed to let UI thread update widgets
        # (tkinter does not support multi threading)
        try:
            # LOGGER.debug("processing events") # too much output
            message = event_queue.get(block=False)
            if message[0] == MESSAGES.REFRESH:
                _round = message[1]
                for player_frame in self.player_frames.values():
                    player = player_frame.player
                    if _round:
                        LOGGER.debug("Populating: %s" % player.name)
                        player_frame.refresh(_round)
                    if player is not _round.betting_player:
                        player_frame.disable()
                    LOGGER.debug("refreshing community cards %s" % str(_round.community_cards))
                    for label, card in zip(self.community_cards, _round.community_cards + [''] * 5):
                        label['text'] = card
                        if card:
                            LOGGER.debug("setting color to: %s" % card.color())
                            label['fg'] = card.color()
            self.frame.pack()
        except queue.Empty:
            pass
        self.frame.after(10, func=self.process_event_queue)


def main():
    root = tk.Tk()
    Menu(root)
    root.mainloop()
