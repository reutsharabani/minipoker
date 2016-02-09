from random import shuffle


class Suits:
    HEARTS = "Hearts"
    DIAMONDS = "Diamonds"
    CLUBS = "Clubs"
    SPADES = "Spades"
    SUITS = (HEARTS, DIAMONDS, CLUBS, SPADES)

symbols = {Suits.SPADES: u'♠', Suits.HEARTS: u'♥', Suits.DIAMONDS: u'♦', Suits.CLUBS: u'♣'}


class Card(object):
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit

    def __gt__(self, other):
        if not isinstance(other, Card):
            return False
        return self.value > other.value

    def __eq__(self, other):
        return isinstance(other, Card) and self.value == other.value and self.suit == other.suit

    def __repr__(self):
        return str(self.value) + self.suit[0]

    def __str__(self):
        return str(self.value) + symbols[self.suit]

    def __hash__(self):
        return hash(self.value) ^ hash(self.suit)

    def color(self):
        return "red" if self.suit in (Suits.HEARTS, Suits.DIAMONDS) else "black"


class Deck(object):
    def __init__(self):
        self.cards = [Card(value, suit) for value in range(1, 14) for suit in Suits.SUITS]
        # don't forget to shuffle
        self.shuffle()

    def shuffle(self):
        shuffle(self.cards)

    def draw(self, number=1):
        drawn, self.cards = self.cards[:number], self.cards[number:]
        return drawn

    def draw_single(self):
        return self.cards.pop()

    def removeall(self, cards):
        '''
        remove a sequence of cards from the deck
        :param cards: cards to remove from the deck
        :return: sequence of remaining cards
        '''
        remaining = set(self.cards) - set(cards)
        self.cards = list(remaining)
        return remaining
