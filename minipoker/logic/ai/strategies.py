import logging
import random
from minipoker.logic.ai import utils
import multiprocessing

pool = multiprocessing.Pool(max(multiprocessing.cpu_count() // 2, 1))

LOGGER = logging.getLogger("ai-strategies")


class CFRDistribution:
    # need things like "call small raise" ...
    def __init__(self, call, fold, bet, check):
        from minipoker.logic.players import Call, Fold, Bet, Check  # can be moved to enum here
        self.call = int(call * 100)
        self.fold = int(fold * 100)
        self.bet = int(bet * 100)
        self.check = int(check * 100)
        self.distributions = {
            self.call: Call,
            self.fold: Fold,
            self.bet: Bet,
            self.check: Check
        }

    def decision(self):
        s = random.randint(1, sum((self.call, self.fold, self.bet, self.check,)))
        print(self.distributions)
        for (weight, value) in self.distributions.items():
            s -= weight
            if s <= 0:
                return value
        raise Exception("Error while fetching decision")


class PokerStrategy:
    def __init__(self, call_bias, fold_bias, bet_bias, check_bias):
        self.call_bias = call_bias
        self.fold_bias = fold_bias
        self.bet_bias = bet_bias
        self.check_bias = check_bias

    def rank(self, _game):
        raise Exception("not implemented")


def make_args_from_cards(cards):
    return tuple((c.value, c.suit) for c in cards)


class SimpleSaneStrategy(PokerStrategy):
    def rank(self, _game):
        _round = _game.current_round
        # ranks are 0 - 8 in naive rank
        v = utils.naive_rank(make_args_from_cards(_round.betting_player.pocket),
                                                     make_args_from_cards(_round.community_cards))
        if _round.community_cards:
            # if community cards exist - remove their detached value from hand value
            community_v =utils.naive_rank(make_args_from_cards(_round.community_cards), tuple())
            v = v - community_v
        else:
            print("no community cards, fetching hand value")
        print("v: %f" % v)

        if v < 0.7:
            dist = CFRDistribution(0.05, 0.7, 0.05, 0.2)
        elif v < 1:
            dist = CFRDistribution(0.3, 0.2, 0.1, 0.4)
        elif v < 1.3:
            dist = CFRDistribution(0.35, 0.1, 0.2, 0.35)
        elif v < 1.6:
            dist = CFRDistribution(0.35, 0.1, 0.25, 0.4)
        else:
            dist = CFRDistribution(0.45, 0.05, 0.3, 0.1)
        print("ai player dist: %s" % dist)
        return dist.decision()

# def randomize_sample(community_count):
#     _deck = deck.Deck()
#     pocket = _deck.draw(2)
#     community = _deck.draw(community_count)
#     result = utils.naive_rank(pocket, community)
#     print("pocket: %s, community: %s, result: %f" % (pocket, community, result))
#     return result
#
#
# if "__main__" == __name__:
#     print(utils.naive_rank([(2, deck.Suits.SPADES), (7, deck.Suits.CLUBS)], []))
