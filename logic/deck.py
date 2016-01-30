from random import shuffle

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

        self.cards = [Card(value, suit) for value in range(1, 14) for suit in SUITS]
        # don't forget to shuffle
        self.shuffle()

    def shuffle(self):
        shuffle(self.cards)

    def draw(self, number=1):
        drawn, self.cards = self.cards.pop(0), self.cards[number:]
        return drawn

