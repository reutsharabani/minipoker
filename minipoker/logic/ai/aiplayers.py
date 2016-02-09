from minipoker.logic.players import BasePlayer
from minipoker.logic.ai import strategies
import random


class SimpleAIPlayer(BasePlayer):

    NAME = "Simple AI"

    def __init__(self, name, starting_money):
        super(SimpleAIPlayer, self).__init__(name, starting_money)
        self.strat = strategies.SimpleSaneStrategy(1, 1, 1, 1)

    def interact(self, _game):
        round_ = _game.current_round
        action = self.strat.rank(_game)
        while action not in self.available_actions(round_):
            action = self.strat.rank(_game)
        return action(self, round_)

    def get_amount(self, _min, _max):
        return random.randint(_min, _max)
