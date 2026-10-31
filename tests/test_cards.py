"""A prize card fills the whole canvas on the spin and winner screens, as the title video does, so render() stretches
it back to its own shape on the 4:3 display. The 2026 cards are 4:3; kept at their shape on the square canvas, they
stopped short of its bottom quarter."""

from config import PRIZES
from conftest import press_space, screen, wait
from fakes import ScriptedPicks
from states.candy_picker import STEP_RATE_CURVE

SMALL = 0.001
BLACK = (0, 0, 0)


def near_the_bottom(game):
    """The canvas pixel a tenth of the way up from the bottom, in the middle: on a card's name plaque."""
    width, height = game.GAME_DIMENSIONS
    return tuple(game.game_canvas.get_at((width // 2, int(height * 0.9))))[:3]


def test_the_spinning_card_reaches_the_bottom_of_the_canvas(make_game):
    game = make_game()
    game.step()

    press_space(game)

    assert screen(game) == "CandyPicker"
    assert near_the_bottom(game) != BLACK


def test_the_won_card_reaches_the_bottom_of_the_canvas(make_game, clock):
    game = make_game(rng=ScriptedPicks(["mini"] * 5 + ["big_prize"] + ["mini"] * 20))
    game.step()
    press_space(game)
    for interval in STEP_RATE_CURVE[:5]:
        wait(game, clock, interval + SMALL)

    press_space(game)
    wait(game, clock, PRIZES.WIN_SOUND_DELAY + SMALL)

    assert screen(game) == "Winner"
    assert near_the_bottom(game) != BLACK
