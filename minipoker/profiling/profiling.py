from minipoker.logic.ai.utils import naive_rank
from minipoker.logic.deck import Deck, Suits
import time

deck = Deck()

# empty
for sampling_factor in [0.01, 0.1, 0.25, 0.5, 0.9, 1.0]:
    print()
    print()
    print()
    print("SAMPLING FACTOR: %f" % sampling_factor)
    for opts in [[], [3, 4, 5], [3, 4, 5, 6], [3, 4, 5, 6, 7]]:
        start = time.time() * 1000
        rank = naive_rank([(1, Suits.SPADES), (2, Suits.SPADES)], [(v, Suits.SPADES) for v in opts],
                          sampling_factor=sampling_factor)
        print("rank: ", rank)
        print("time elapsed (millis) for %d cards (%s): %d" % (len(opts), str(opts), (time.time() * 1000 - start)))
