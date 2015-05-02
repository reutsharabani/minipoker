__author__ = 'reut'

from itertools import combinations
import os
import logging
from logic.poker.hands import Hand

LOGGER = logging.getLogger('poker')
LEVEL = logging.DEBUG
stream_handler = logging.StreamHandler()
LOGGER.setLevel(LEVEL)
LOGGER.addHandler(stream_handler)


class Action(object):

    def __init__(self, player, round_):
        self.player = player
        self.round = round_

    @staticmethod
    def is_valid(player, round_):
        raise NotImplementedError("Can not validate abstract Action")

    def apply(self):
        raise NotImplementedError("Can not apply abstract Action")


class AmountableAction(Action):

    def __init__(self, player, round_, amount):
        super(AmountableAction, self).__init__(player, round_)
        self.amount = amount

    @staticmethod
    def is_valid(player, round_):
        raise NotImplementedError("Can not validate abstract Action")

    def apply(self):
        raise NotImplementedError("Can not apply abstract Action")


class Fold(Action):

    @staticmethod
    def is_valid(player, round_):
        return not player.folded

    def apply(self):
        self.round.folded_players.append(self.player)


class Check(Action):

    @staticmethod
    def is_valid(player, round_):
        pot = round_.pot
        return pot.player_bet(player) == pot.current_bet

    def apply(self):
        self.player.checked = True


class Call(Action):

    def __init__(self, player, round_):
        super(Call, self).__init__(player, round_)

    @staticmethod
    def is_valid(player, round_):
        return player.money >= round_.pot.amount_to_call(player) > 0

    def apply(self):
        self.player.money -= self.round.pot.amount_to_call(self.player)


class Bet(AmountableAction):

    def __init__(self, player, round_, amount):
        bet_min, bet_max = round_.pot.minimum_to_bet(player), player.money
        if bet_max < amount < bet_min:
            raise NotEnoughMoneyException("%s can't bet %d - bet has to be between %d to %d!" % (
                player.name, amount, bet_min, bet_max
            ))
        super(Bet, self).__init__(player, round_, amount)

    @staticmethod
    def is_valid(player, round_):
        return player.money >= round_.pot.minimum_to_bet(player) > 0

    def apply(self):
        self.player.money -= self.round.pot.amount_to_call(self.player)


class NotEnoughMoneyException(Exception):
    pass


class BasePlayer(object):

    def __init__(self, name, starting_money):
        self.name = name
        self.pocket = None
        self.money = starting_money
        self.first_bet = False
        self.checked = False

    def set_pocket(self, card1, card2):
        self.pocket = [card1, card2]

    def bet(self, amount):
        if amount > self.money:
            raise NotEnoughMoneyException(
                "Player " + self.name + " does not have enough money (" + self.money + "/" + amount + ")"
            )
        self.money -= amount

    def force_bet(self, amount):
        """
        Force a bet from the player, even if the amount exceeds the player's funds
        :param amount: the amount to force on the player
        :return:
                amount of money actually taken
        """
        LOGGER.info("Forcing %s to bet %d" % (self.name, amount))
        amount = min(amount, self.money)
        self.bet(amount)
        return amount

    def interact(self, round_):
        raise NotImplementedError("Interact is not implemented on the Player's base class")

    def is_folded(self, round_):
        return round_.is_folded(self)

    def is_betting(self, round_):
        return len(round_.active_players) > 1 and (self.first_bet or (not self.is_folded(round_) and self.money > 0))

    def possible_hands(self, community_cards):
        return [Hand.get_hand(cards) for cards in combinations(community_cards + self.pocket, r=5)]

    def best_hand(self, community_cards):
        # TODO: add aces multiple value (1, 14)
        # print("Community Cards: %s" % community_cards)
        # print("Pocket cards: %s" % self.pocket)
        # print("possible hands:\n%s" % '\n'.join(map(str, self.possible_hands(community_cards))))
        best_hand = max(self.possible_hands(community_cards))
        return best_hand

    def available_actions(self, round_):
        return list(filter(lambda x: x.is_valid(self, round_), [Check, Call, Bet, Fold]))

    def choose_action_message(self, round_):
        return os.linesep.join([
            "%s, please choose an action:" % self.name
        ] + ['. '.join(
            [str(index), action_name.__name__]
        ) for index, action_name in enumerate(self.available_actions(round_))])


class HumanPlayer(BasePlayer):

    def interact(self, round_):
        self.first_bet = False

        action = None
        while action is None:
            try:
                available_actions = self.available_actions(round_)
                action = available_actions[int(input(self.choose_action_message(round_)))]

                while isinstance(action, AmountableAction):
                    # choose action amount (example: bet, 50)
                    while 0 > amount > self.money:
                        amount = int(input("How much?"))
                    return action(self, round_, amount)
                return action(self, round_)
            except ValueError:
                pass
            except IndexError:
                pass