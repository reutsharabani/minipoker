__author__ = 'reut'

from itertools import combinations
import os
import logging

LOGGER = logging.getLogger('poker')
LEVEL = logging.DEBUG
stream_handler = logging.StreamHandler()
LOGGER.setLevel(LEVEL)
LOGGER.addHandler(stream_handler)


class Action(object):

    def __init__(self, player, game):
        self.player = player
        self.game = game

    @staticmethod
    def is_valid(player, game):
        raise NotImplementedError("Can not validate abstract Action")

    def apply(self):
        raise NotImplementedError("Can not apply abstract Action")


class AmountableAction(Action):

    def __init__(self, player, game, amount):
        super(AmountableAction, self).__init__(player, game)
        self.amount = amount

    @staticmethod
    def is_valid(player, game):
        raise NotImplementedError("Can not validate abstract Action")

    def apply(self):
        raise NotImplementedError("Can not apply abstract Action")


class Fold(Action):

    @staticmethod
    def is_valid(player, game):
        return not player.folded

    def apply(self):
        self.player.folded = True


class Check(Action):

    @staticmethod
    def is_valid(player, game):
        pot = game.pot
        return pot.player_bet(player) == pot.current_bet

    def apply(self):
        self.player.checked = True


class Call(Action):

    def __init__(self, player, game):
        super(Call, self).__init__(player, game)

    @staticmethod
    def is_valid(player, game):
        return player.money >= game.pot.amount_to_call(player) > 0

    def apply(self):
        self.player.money -= self.game.pot.amount_to_call(self.player)


class Bet(AmountableAction):

    def __init__(self, player, game, amount):
        bet_min, bet_max = game.pot.minimum_to_bet(player), player.money
        if bet_max < amount < bet_min:
            raise NotEnoughMoneyException("%s can't bet %d - bet has to be between %d to %d!" % (
                player.name, amount, bet_min, bet_max
            ))
        super(Bet, self).__init__(player, game, amount)

    @staticmethod
    def is_valid(player, game):
        return player.money >= game.pot.minimum_to_bet(player) > 0

    def apply(self):
        self.player.money -= self.game.pot.amount_to_call(self.player)


class NotEnoughMoneyException(Exception):
    pass


class BasePlayer(object):

    def __init__(self, name, starting_money):
        self.name = name
        self.pocket = None
        self.money = starting_money
        self.folded = False
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

    def interact(self, game):
        raise NotImplementedError("Interact is not implemented on the Player's base class")

    def is_betting(self, game):
        return len(game.active_players) > 1 and (self.first_bet or (not self.folded and self.money > 0))

    def get_best_hand(self, community_cards):
        # TODO: add aces multiple value (1, 14)
        print("Community Cards: %s" % community_cards)
        print("Pocket cards: %s" % self.pocket)
        best_hand = max(combinations(community_cards + self.pocket, r=5))
        print("Best hand for player %s: %s" % (self.name, best_hand))
        print("Community cards %s:" % community_cards)
        print("Pocket cards %s:" % self.pocket)
        return best_hand

    def available_actions(self, game):
        return filter(lambda x: x.is_valid(self, game), [Check, Call, Bet, Fold])

    def choose_action_message(self, game):
        return os.linesep.join([
            "%s, please choose an action:" % self.name
        ] + ['. '.join(
            [str(index), action_name.__name__]
        ) for index, action_name in enumerate(self.available_actions(game))])


class HumanPlayer(BasePlayer):

    def interact(self, game):
        self.first_bet = False

        action = None
        while action is None:
            try:
                action = self.available_actions(game)[int(input(self.choose_action_message(game)))]
            except ValueError:
                pass