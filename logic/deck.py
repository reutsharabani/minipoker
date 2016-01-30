from random import shuffle

SUITS = ("Hearts", "Diamonds", "Clubs", "Spades")
symbols = {"Spades": u'♠', "Hearts": u'♥', "Diamonds": u'♦', "Clubs": u'♣'}


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

    def __str__(self):
        return str(self.value) + symbols[self.suit]

    def color(self):
        return "red" if self.suit in ("Hearts", "Diamonds") else "black"


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
