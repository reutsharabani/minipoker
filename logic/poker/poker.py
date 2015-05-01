__author__ = 'reut'

from random import choice
from logic.deck import *
from collections import defaultdict
from logic.poker.players import *


class Pot(object):

    def __init__(self, small_blind):
        self.current_bet = small_blind * 2
        self.bets = defaultdict(int)
        self.last_raise = small_blind

    def player_bet(self, player):
        return self.bets[player]

    def amount_to_call(self, player):
        return self.current_bet - self.bets[player]

    def minimum_to_bet(self, player):
        return self.current_bet + self.last_raise - self.player_bet(player)


class Poker(object):

    def __init__(self, players):
        self.finished_players = []
        self.players = players
        self.active_players = [players]
        self.button_player = choice(self.players)
        self.small_blind = 1
        self.betting_player = None
        self.pot = None
        self.deck = Deck()
        self.community_cards = []

    def winner(self):
        return self.players[0] if len(self.players) == 1 else None

    def after_active_player(self, player, offset=1):
        return self.after(player, self.active_players, offset)

    @staticmethod
    def after(player, players, offset=1):
        wanted_player_index = (players.index(player) + offset) % len(players)
        return players[wanted_player_index]

    def small_blind_amount(self):
        return self.small_blind

    def small_blind_player(self):
        return self.after(self.button_player, self.active_players)

    def big_blind_player(self):
        return self.after(self.button_player, self.active_players, 2)

    def take_blinds(self):
        self.small_blind_player().force_bet(self.small_blind_amount())
        self.big_blind_player().force_bet(2 * self.small_blind_amount())

    def set_next_betting_player(self):
        starting_player = self.betting_player
        self.betting_player = self.after_active_player(self.betting_player)
        print("Starting player: " + self.betting_player.name)
        while starting_player != self.betting_player:
            if self.betting_player.is_betting(self):
                # print("Found betting player")
                break
            # print("Did not find betting player")
            self.betting_player = self.after_active_player(self.betting_player)

        if starting_player == self.betting_player:
            self.betting_player = None

        return self.betting_player

    def pre_flop_betting(self):
        self.betting_player = self.after(self.big_blind_player(), self.active_players)
        self.place_bets()

    def pre_turn_betting(self):
        self.betting_player = self.after(self.button_player, self.active_players)
        self.place_bets()

    def pre_river_betting(self):
        self.betting_player = self.after(self.button_player, self.active_players)
        self.place_bets()

    def place_bets(self):
        # when no betting players are left
        # self.betting_player will be set to None
        while self.betting_player is not None:
            print("Searching for next betting player (is it " + self.betting_player.name + ") ?")
            self.betting_player.interact(self)
            self.set_next_betting_player()

        print("Done betting for pre_flop_round")

    def start_round(self):

        self.pot = Pot(self.small_blind)

        # set all players to active for this round
        self.active_players = self.players[:]

        print("Dealing cards")
        for player in self.active_players:
            player.set_pocket(self.deck.draw(), self.deck.draw())
            player.first_bet = True
            player.folded = False

    def play(self):

        while self.winner() is None:

            self.start_round()

            print("Playing another round of poker")

            self.take_blinds()

            print("Playing first round (pre-flop)")
            self.pre_flop_betting()
            self.open_flop_cards()

            print("Playing first round (pre-turn)")
            self.pre_turn_betting()
            self.open_turn_cards()

            print("Playing first round (pre-river)")
            self.pre_river_betting()
            self.open_river_cards()

            self.finish_round()

    def open_card(self):
        self.community_cards.append(self.deck.draw())

    def open_flop_cards(self):
        self.open_card()
        self.open_card()
        self.open_card()

    def open_turn_cards(self):
        self.open_card()

    def open_river_cards(self):
        self.open_card()

    def finish_round(self):
        for winner in self.get_round_winners():
            print("Giving pot to player: " + winner.name)

    def get_round_winners(self):
        return sorted(self.active_players, key=lambda x: x.get_best_hand(self.community_cards))


if __name__ == "__main__":
    print("Starting a pvp poker game")
    game = Poker([HumanPlayer("Human %d" % i, 100) for i in range(5)])
    game.play()