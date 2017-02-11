from minipoker.logic.deck import Deck, Card, Suits
import itertools
from minipoker.logic.hands import Hand
import random

import logging

LOGGER = logging.getLogger("ai-utils")
LOGGER.setLevel(logging.WARN)


def generate_possible_hands(pocket, community_cards):
    return [Hand.get_hand(_cards) for _cards in itertools.combinations(community_cards + pocket, r=5)]


def naive_rank(pocket, community_cards, sampling_factor=1.0):
    pocket = [Card(v, s) for v, s in pocket]
    community_cards = [Card(v, s) for v, s in community_cards]
    unopened_slots = min(3, 7 - len(pocket) - len(community_cards))
    deck = Deck()
    deck.removeall(pocket + community_cards)
    count = 0
    _rank = 0
    for possibility in itertools.combinations(deck.cards, r=unopened_slots):
        # randomly sample less the more possible hands there are
        if len(community_cards) not in (0, 3) or random.random() < sampling_factor:
            _rank += max(generate_possible_hands(pocket, community_cards + list(possibility))).rank
            count += 1
    LOGGER.debug("Evaluated %d hands" % count)

    return _rank / count


if "__main__" == __name__:
    test_cards = (
        [Card(14, Suits.HEARTS), Card(13, Suits.SPADES)],
        [Card(12, Suits.SPADES), Card(13, Suits.SPADES)],
        [Card(2, Suits.HEARTS), Card(2, Suits.SPADES)],
    )
    for cards in test_cards:
        for comm in [[], [Card(13, Suits.HEARTS)],
                     [Card(10, Suits.SPADES), Card(11, Suits.SPADES), Card(14, Suits.SPADES)]]:
            print("Naive rank %s with %s: %f" % (str(cards), comm, naive_rank(cards, comm)))
