"""The real button's path: the GPIO callback (Game.button_press), driven by the fake pin.

FakeHardware.recorded_press() replays a press as the real button made it (fakes.RECORDED_PRESSES): it
flickers, and a flicker uses up the "release" the code posts after a press, so every real press counts.
FakeHardware.clean_press() makes one rising and one falling edge; the real button never does, but the clean
tests record what the code would do with a button that does not bounce.
"""
from config import HW
from conftest import screen
from fakes import RECORDED_PRESSES


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

    Game.button_press posts a release on the next edge that reads high. The real button's flicker uses that
    release up within the same press; a button that does not bounce would lose every second press.
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


def test_every_real_press_starts_or_stops_a_round(make_game, clock, hardware):
    """Presses replayed as the real button made them (RECORDED_PRESSES): each one counts."""
    first, second = RECORDED_PRESSES
    game = make_game()
    game.step()

    for press, expected in [(first, "CandyPicker"), (second, "Winner"), (first, "Title"), (second, "CandyPicker")]:
        clock.advance(HW.BUTTON_DELAY + 0.5)
        hardware.recorded_press(clock, press)
        game.step()
        assert screen(game) == expected
