"""Whole rounds of the game on fake hardware and a fake clock: title, spin, winner, back to title."""

import pi_dev2
from config import HW, PRIZES, VISUAL
from conftest import press_space, screen, wait
from fakes import ScriptedPicks
from states.candy_picker import RGB_COLOR_SEQUENCE, STEP_RATE_CURVE
from states.winner import RESET_DELAY

BEEP = PRIZES.BEEP_SOUND_FILE
BIG_PRIZE_SOUND = PRIZES.PRIZE_CATEGORIES[PRIZES.BIG_PRIZE_TYPE]["sound_file"]
SMALL = 0.001


def spin_to_card(game, clock, card):
    """From the first card of a spin, wait out each interval until `card` (1 = the first) is showing."""
    for interval in STEP_RATE_CURVE[:card - 1]:
        wait(game, clock, interval + SMALL)


def test_title_screen_idles(make_game, clock, hardware, snap):
    game = make_game()
    game.step()
    snap(game, "title")

    for _ in range(3):
        wait(game, clock, 1 + SMALL)

    assert screen(game) == "Title"
    assert hardware.count("toggle_led") == 3


def test_press_starts_a_spin(make_game, hardware, audio, snap):
    game = make_game()
    game.step()

    press_space(game)

    assert screen(game) == "CandyPicker"
    assert game.state_stack[-1].current_prize is not None
    assert hardware.count("led_on") == 1
    assert audio.played == [BEEP]
    snap(game, "first-card")


def test_spin_speeds_up(make_game, clock, hardware, audio):
    game = make_game()
    game.step()
    press_space(game)
    picker = game.state_stack[-1]

    for card, interval in enumerate(STEP_RATE_CURVE[:10], start=2):
        wait(game, clock, interval - 2 * SMALL)
        assert picker.current_tick == card - 1, f"card {card} came early"
        wait(game, clock, 3 * SMALL)
        assert picker.current_tick == card, f"card {card} did not come after {interval}s"

    assert audio.played.count(BEEP) == 11          # the first card and the 10 after it
    patterns = hardware.rgb_patterns()
    assert len(patterns) >= 8
    for i, pattern in enumerate(patterns):
        assert pattern == RGB_COLOR_SEQUENCE[i % len(RGB_COLOR_SEQUENCE)]


def test_press_stops_on_a_prize(make_game, clock, hardware, audio, snap):
    picks = ["mini"] * 5 + ["big_prize"] + ["mini"] * 20
    game = make_game(rng=ScriptedPicks(picks))
    game.step()
    press_space(game)
    spin_to_card(game, clock, 6)
    snap(game, "spinning")

    press_space(game)

    assert screen(game) == "Winner"
    assert game.state_stack[-1].prize["type"] == "big_prize"
    assert audio.played[-1] == BIG_PRIZE_SOUND
    assert hardware.calls[-1] == ("clear_rgb_leds",)
    snap(game, "winner")


def test_timer_stops_the_spin(make_game, clock, snap):
    game = make_game()
    game.step()
    press_space(game)
    picker = game.state_stack[-1]
    hidden_for = VISUAL.TIMER_START_SECONDS - VISUAL.TIMER_SHOW_AT_SECONDS

    wait(game, clock, hidden_for - 0.1)
    assert picker.timer_remaining > VISUAL.TIMER_SHOW_AT_SECONDS
    wait(game, clock, 0.2)
    assert picker.timer_remaining <= VISUAL.TIMER_SHOW_AT_SECONDS
    snap(game, "timer-showing")

    wait(game, clock, VISUAL.TIMER_SHOW_AT_SECONDS)

    assert screen(game) == "Winner"
    assert game.state_stack[-1].prize is picker.current_prize


def test_winner_returns_to_title_after_the_delay(make_game, clock):
    game = make_game()
    game.step()
    press_space(game)
    press_space(game)
    assert screen(game) == "Winner"

    wait(game, clock, RESET_DELAY - 0.1)
    assert screen(game) == "Winner"
    wait(game, clock, 0.2)

    assert screen(game) == "Title"


def test_press_on_winner_returns_to_title(make_game):
    game = make_game()
    game.step()
    press_space(game)
    press_space(game)
    assert screen(game) == "Winner"

    press_space(game)

    assert screen(game) == "Title"


def test_a_full_round_with_the_keyboard_hardware(make_game, clock):
    """pi_dev2, the module a Mac runs with, in place of the fake."""
    game = make_game(hardware=pi_dev2)
    game.step()

    press_space(game)
    spin_to_card(game, clock, 4)
    press_space(game)
    assert screen(game) == "Winner"
    wait(game, clock, RESET_DELAY + SMALL)

    assert screen(game) == "Title"


def test_stock_goes_down_when_a_prize_is_won(make_game, clock):
    picks = ["mini"] * 5 + ["big_prize"] + ["mini"] * 20
    game = make_game(rng=ScriptedPicks(picks))
    game.step()
    press_space(game)
    spin_to_card(game, clock, 6)
    press_space(game)
    assert game.state_stack[-1].prize["type"] == "big_prize"

    assert game.prizes.inventory["big_prize"] == PRIZES.BIG_PRIZE_INVENTORY - 1
    total = sum(game.prizes.inventory.values())
    assert game.prizes.probability["big_prize"] == game.prizes.inventory["big_prize"] / total
