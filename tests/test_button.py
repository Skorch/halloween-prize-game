"""The real button's path: the GPIO callback (Game.button_press), driven by the fake pin.

FakeHardware.clean_press() makes one rising and one falling edge, a press with no bounce. How the real
button bounces is not yet measured; until it is, these tests record what the code does with clean edges.
"""
from config import HW
from conftest import screen


def test_first_clean_press_starts_a_round(make_game, clock, hardware):
    game = make_game()
    game.step()
    clock.advance(HW.BUTTON_DELAY + 0.1)

    hardware.clean_press()
    game.step()

    assert screen(game) == "CandyPicker"


def test_press_within_the_button_delay_is_ignored(make_game, clock, hardware):
    game = make_game()
    game.step()
    clock.advance(HW.BUTTON_DELAY - 0.1)

    hardware.clean_press()
    game.step()

    assert screen(game) == "Title"


def test_every_second_clean_press_is_read_as_a_release(make_game, clock, hardware):
    """With clean edges, the press after a press posts a release, so it does not stop the spin.

    Current behaviour, recorded, not endorsed: Game.button_press posts a release on the next edge that
    reads high. A bouncing button may use that release up within one press; measuring it decides.
    """
    game = make_game()
    game.step()
    clock.advance(HW.BUTTON_DELAY + 0.1)
    hardware.clean_press()
    game.step()
    assert screen(game) == "CandyPicker"

    clock.advance(HW.BUTTON_DELAY + 0.1)
    hardware.clean_press()
    game.step()
    assert screen(game) == "CandyPicker"

    clock.advance(HW.BUTTON_DELAY + 0.1)
    hardware.clean_press()
    game.step()
    assert screen(game) == "Winner"
