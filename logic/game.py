__author__ = 'reut'

from random import choice, shuffle
from itertools import combinations


class Pot(object):
    pass

SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]


class Card(object):
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit

    def __gt__(self, other):
        if not isinstance(other, Card):
            return False
        return self.value > other.value

    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self.value == other.value and self.suit == other.suit

    def __repr__(self):
        return str(self.value) + self.suit[0]





class Deck(object):

    def __init__(self):

        self.cards = [Card(value, suit) for value in range(13) for suit in SUITS]
        # don't forget to shuffle
        self.shuffle()

    def shuffle(self):
        shuffle(self.cards)

    def draw(self, number=1):
        drawn, self.cards = self.cards.pop(0), self.cards[number:]
        return drawn


class Poker(object):

    def __init__(self, players):
        self.finished_players = []
        self.players = players
        self.active_players = [players]
        self.button_player = choice(self.players)
        self.small_blind = 1
        self.betting_player = None
        self.pot = Pot()
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

        # set all players to active for this round
        self.active_players = self.players[:]

        print("Dealing cards")
        for player in self.active_players:
            player.set_pocket(self.deck.draw(), self.deck.draw())

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


class NotEnoughMoneyException(Exception):
    pass


class Player(object):

    def __init__(self, name, starting_money):
        self.name = name
        self.pocket = None
        self.money = starting_money

    def set_pocket(self, card1, card2):
        self.pocket = [card1, card2]

    def bet(self, amount):
        if amount > self.money:
            raise NotEnoughMoneyException("Player " + self.name + " does not have enough money (" + self.money + "/" + amount + ")")
        self.money -= amount

    def force_bet(self, amount):
        """
        Force a bet from the player, even if the amount exceeds the player's funds
        :param amount: the amount to force on the player
        :return:
                amount of money actually taken
        """
        amount = min(amount, self.money)
        self.bet(amount)
        return amount

    def interact(self, game):
        return "blah"

    def is_betting(self, game):
        return choice([False] * 10 + [True])

    def get_best_hand(self, community_cards):
        # TODO: add aces multiple value (1, 14)
        print("Community Cards: %s" % community_cards)
        print("Pocket cards: %s" % self.pocket)
        best_hand = max(combinations(community_cards + self.pocket, r=5))
        print("Best hand for player %s: %s" % (self.name, best_hand))
        print("Community cards %s:" % community_cards)
        print("Pocket cards %s:" % self.pocket)
        return best_hand

import unittest


class TestPokerGame(unittest.TestCase):

    def setUp(self):
        self.game = Poker([Player("Player" + str(i), 100) for i in range(3)])

    def test_test(self):
        print("Community cards: " + ','.join(self.game.community_cards))

    def test_active_players_simple(self):
        self.game.play()
        assert self.game.active_players == self.game.players