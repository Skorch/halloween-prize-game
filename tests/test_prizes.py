"""Prize picks: the odds follow the stock, and no big prize comes before the minimum spins."""
import random
from collections import Counter

from config import PRIZES
from fakes import FakeAudio
from prizes import Prizes


def test_no_big_prize_before_the_minimum_spins():
    prizes = Prizes(FakeAudio(), random.Random(3))

    early = [prizes.pick(tick, "")["type"]
             for tick in range(1, PRIZES.MIN_SPINS_FOR_BIG_PRIZE)
             for _ in range(500)]
    from_minimum = [prizes.pick(PRIZES.MIN_SPINS_FOR_BIG_PRIZE, "")["type"] for _ in range(500)]

    assert "big_prize" not in early
    assert "big_prize" in from_minimum


def test_odds_follow_stock():
    prizes = Prizes(FakeAudio(), random.Random(7))
    picks = 20000

    counts = Counter(prizes.pick(PRIZES.MIN_SPINS_FOR_BIG_PRIZE, "")["type"] for _ in range(picks))

    total_stock = sum(prizes.inventory.values())
    for prize_type, stock in prizes.inventory.items():
        assert abs(counts[prize_type] / picks - stock / total_stock) < 0.02, (prize_type, counts)


def test_a_prize_never_shows_the_same_card_twice_in_a_row():
    prizes = Prizes(FakeAudio(), random.Random(5))
    previous = ""

    for tick in range(1, 300):
        card = prizes.pick(tick, previous)["filename"]
        assert card != previous
        previous = card
