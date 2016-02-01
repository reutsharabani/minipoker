from minipoker.logic.hands import *
from minipoker.logic.poker import *
from minipoker.logic.players import *
import unittest


class TestPokerGame(unittest.TestCase):
    def setUp(self):
        self.game = Poker([HumanPlayer("Player" + str(i), 100) for i in range(3)])

    def test_active_players_simple(self):
        self.game.play()
        assert self.game.current_round.active_players == self.game.players


class TestHands(unittest.TestCase):
    def test_straight_flush(self):
        assert type(Hand.get_hand([Card(v, 'SUIT') for v in [1, 2, 3, 4, 5]])) is StraightFlush
        assert type(Hand.get_hand([Card(v, 'SUIT') for v in [1, 2, 3, 5, 6]])) is not StraightFlush

    def test_four_of_a_kind(self):
        assert type(
            Hand.get_hand([Card(v, s) for v, s in [(1, 'h'), (1, 'd'), (1, 'c'), (1, 's'), (5, 'c')]])) is FourOfAKind
        assert type(Hand.get_hand(
            [Card(v, s) for v, s in [(1, 'h'), (1, 'd'), (1, 'c'), (2, 's'), (5, 'c')]])) is not FourOfAKind

    def test_full_house(self):
        assert type(
            Hand.get_hand([Card(v, s) for v, s in [(1, 'h'), (1, 'd'), (1, 'c'), (5, 's'), (5, 'c')]])) is FullHouse
        assert type(
            Hand.get_hand([Card(v, s) for v, s in [(1, 'h'), (1, 'd'), (1, 'c'), (2, 's'), (5, 'c')]])) is not FullHouse

    def test_flush(self):
        assert type(Hand.get_hand([Card(v, s) for v, s in [(1, 'd'), (2, 'd'), (5, 'd'), (6, 'd'), (7, 'd')]])) is Flush
        assert type(
            Hand.get_hand([Card(v, s) for v, s in [(1, 'h'), (1, 'd'), (1, 'c'), (2, 's'), (5, 'c')]])) is not Flush

    def test_straight(self):
        assert type(
            Hand.get_hand([Card(v, s) for v, s in [(1, 'd'), (2, 'd'), (3, 'd'), (4, 'c'), (5, 'd')]])) is Straight
        assert type(
            Hand.get_hand([Card(v, s) for v, s in [(1, 'h'), (1, 'd'), (1, 'c'), (2, 's'), (5, 'c')]])) is not Straight

    def test_three_of_a_kind(self):
        assert type(
            Hand.get_hand([Card(v, s) for v, s in [(1, 'd'), (1, 'd'), (1, 'd'), (4, 'c'), (5, 'd')]])) is ThreeOfAKind
        assert type(Hand.get_hand(
            [Card(v, s) for v, s in [(1, 'h'), (1, 'd'), (2, 'c'), (2, 's'), (5, 'c')]])) is not ThreeOfAKind

    def test_two_pairs(self):
        assert type(
            Hand.get_hand([Card(v, s) for v, s in [(1, 'h'), (1, 'd'), (2, 'c'), (2, 's'), (5, 'c')]])) is TwoPairs
        assert type(
            Hand.get_hand([Card(v, s) for v, s in [(1, 'd'), (1, 'd'), (1, 'd'), (4, 'c'), (5, 'd')]])) is not TwoPairs

    def test_one_pair(self):
        assert type(Hand.get_hand([Card(v, s) for v, s in [(1, 'h'), (10, 'd'), (2, 'c'), (2, 's'), (5, 'c')]])) is Pair
        assert type(
            Hand.get_hand([Card(v, s) for v, s in [(1, 'd'), (1, 'd'), (1, 'd'), (4, 'c'), (5, 'd')]])) is not Pair
