__author__ = 'reut'

from collections import Counter


class Card(object):
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit

    def __hash__(self):
        return hash(self.value)

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


class InvalidHandException(Exception):
    pass


class Hand(object):

    def __init__(self, cards):
        if len(cards) != 5:
            raise InvalidHandException("Card count was not 5!")
        self.cards = sorted(cards)

    @staticmethod
    def get_hand(cards):

        classification_candidates = [
            StraightFlush,
            FourOfAKind,
            FullHouse,
            Flush,
            Straight,
            ThreeOfAKind,
            TwoPairs,
            Pair,
        ]
        for candidate in classification_candidates:
            if candidate.is_valid(cards):
                print("%s: %s" % (candidate.__name__, str(cards)))
                return candidate(cards)

        # nothing identified, play using highest cards
        return HighCard(cards)


    @staticmethod
    def is_valid(cards):
        raise NotImplemented("is_valid not implemented for abstract hand!")


class StraightFlush(Hand):

    def __init__(self, cards):
        super(StraightFlush, self).__init__(cards)

    @staticmethod
    def is_valid(cards):
        return Flush.is_valid(cards) and Straight.is_valid(cards)


class FourOfAKind(Hand):

    def __init__(self, cards):
        super(FourOfAKind, self).__init__(cards)

    @staticmethod
    def is_valid(cards):
        counter = Counter([card.value for card in cards])
        return max(counter.values()) == 4


class FullHouse(Hand):

    def __init__(self, cards):
        super(FullHouse, self).__init__(cards)

    @staticmethod
    def is_valid(cards):
        counter = Counter([card.value for card in cards])
        return 2 in counter.values() and 3 in counter.values()


class Flush(Hand):

    def __init__(self, cards):
        super(Flush, self).__init__(cards)

    @staticmethod
    def is_valid(cards):
        return all(card.suit == cards[0].suit for card in cards)


class Straight(Hand):

    def __init__(self, cards):
        super(Straight, self).__init__(cards)

    @staticmethod
    def is_valid(cards):
        return all(card.value == v for card, v in zip(cards, range(cards[0].value, cards[0].value + 5)))


class ThreeOfAKind(Hand):

    def __init__(self, cards):
        super(ThreeOfAKind, self).__init__(cards)

    @staticmethod
    def is_valid(cards):
        counter = Counter([card.value for card in cards])
        return max(counter.values()) == 3


class TwoPairs(Hand):

    def __init__(self, cards):
        super(TwoPairs, self).__init__(cards)

    @staticmethod
    def is_valid(cards):
        counter = Counter([card.value for card in cards])
        return sorted(counter.values())[-2:] == [2, 2]


class Pair(Hand):

    def __init__(self, cards):
        super(Pair, self).__init__(cards)

    @staticmethod
    def is_valid(cards):
        counter = Counter([card.value for card in cards])
        return max(counter.values()) == 2


class HighCard(Hand):
    def __init__(self, cards):
        super(HighCard, self).__init__(cards)

    @staticmethod
    def is_valid(cards):
        return

import unittest


class TestHands(unittest.TestCase):

    def test_straight_flush(self):
        assert type(Hand.get_hand([Card(v, 'SUIT') for v in [1, 2, 3, 4, 5]])) is StraightFlush
        assert type(Hand.get_hand([Card(v, 'SUIT') for v in [1, 2, 3, 5, 6]])) is not StraightFlush

    def test_four_of_a_kind(self):
        assert type(Hand.get_hand([Card(v, s) for v, s in [(1, 'h'), (1, 'd'), (1, 'c'), (1, 's'), (5, 'c')]])) is FourOfAKind
        assert type(Hand.get_hand([Card(v, s) for v, s in [(1, 'h'), (1, 'd'), (1, 'c'), (2, 's'), (5, 'c')]])) is not FourOfAKind

    def test_full_house(self):
        assert type(Hand.get_hand([Card(v, s) for v, s in [(1, 'h'), (1, 'd'), (1, 'c'), (5, 's'), (5, 'c')]])) is FullHouse
        assert type(Hand.get_hand([Card(v, s) for v, s in [(1, 'h'), (1, 'd'), (1, 'c'), (2, 's'), (5, 'c')]])) is not FullHouse

    def test_flush(self):
        assert type(Hand.get_hand([Card(v, s) for v, s in [(1, 'd'), (2, 'd'), (5, 'd'), (6, 'd'), (7, 'd')]])) is Flush
        assert type(Hand.get_hand([Card(v, s) for v, s in [(1, 'h'), (1, 'd'), (1, 'c'), (2, 's'), (5, 'c')]])) is not Flush

    def test_straight(self):
        assert type(Hand.get_hand([Card(v, s) for v, s in [(1, 'd'), (2, 'd'), (3, 'd'), (4, 'c'), (5, 'd')]])) is Straight
        assert type(Hand.get_hand([Card(v, s) for v, s in [(1, 'h'), (1, 'd'), (1, 'c'), (2, 's'), (5, 'c')]])) is not Straight

    def test_three_of_a_kind(self):
        assert type(Hand.get_hand([Card(v, s) for v, s in [(1, 'd'), (1, 'd'), (1, 'd'), (4, 'c'), (5, 'd')]])) is ThreeOfAKind
        assert type(Hand.get_hand([Card(v, s) for v, s in [(1, 'h'), (1, 'd'), (2, 'c'), (2, 's'), (5, 'c')]])) is not ThreeOfAKind

    def test_two_pairs(self):
        assert type(Hand.get_hand([Card(v, s) for v, s in [(1, 'h'), (1, 'd'), (2, 'c'), (2, 's'), (5, 'c')]])) is TwoPairs
        assert type(Hand.get_hand([Card(v, s) for v, s in [(1, 'd'), (1, 'd'), (1, 'd'), (4, 'c'), (5, 'd')]])) is not TwoPairs

    def test_one_pair(self):
        assert type(Hand.get_hand([Card(v, s) for v, s in [(1, 'h'), (10, 'd'), (2, 'c'), (2, 's'), (5, 'c')]])) is Pair
        assert type(Hand.get_hand([Card(v, s) for v, s in [(1, 'd'), (1, 'd'), (1, 'd'), (4, 'c'), (5, 'd')]])) is not Pair
