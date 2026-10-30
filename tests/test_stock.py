"""The prizes left live in a YAML file: the game reads it before every spin and takes one off each win, a number set
in it by hand counts from the next spin with no restart, and with nothing left the title says so."""
import random

import yaml

from config import PRIZES
from conftest import press_space, screen, wait
from fakes import FakeAudio, ScriptedPicks
from prizes import Prizes
from states.candy_picker import STEP_RATE_CURVE

STARTING = {"mini": PRIZES.MINI_CANDY_INVENTORY, "playdough": PRIZES.PLAYDOUGH_INVENTORY,
            "big_prize": PRIZES.BIG_PRIZE_INVENTORY}


def read(path):
    return yaml.safe_load(path.read_text())


def write(path, stock):
    path.write_text(yaml.safe_dump(stock))


def win(game, clock, cards=6):
    """Press, let `cards` cards show, press again: the winner screen."""
    press_space(game)
    for interval in STEP_RATE_CURVE[:cards - 1]:
        wait(game, clock, interval + 0.001)
    press_space(game)
    assert screen(game) == "Winner"
    return game.state_stack[-1].prize["type"]


def test_a_missing_file_is_written_from_the_starting_stock(make_game, tmp_path):
    stock_file = tmp_path / "stock.yaml"

    make_game(stock_file=str(stock_file))

    assert read(stock_file) == STARTING


def test_a_win_takes_one_off_the_file(make_game, clock, tmp_path):
    stock_file = tmp_path / "stock.yaml"
    write(stock_file, {"mini": 10, "playdough": 10, "big_prize": 10})
    game = make_game(rng=ScriptedPicks(["mini"] * 5 + ["big_prize"] + ["mini"] * 20), stock_file=str(stock_file))
    game.step()

    assert win(game, clock) == "big_prize"

    assert read(stock_file) == {"mini": 10, "playdough": 10, "big_prize": 9}
    assert game.prizes.probability["big_prize"] == 9 / 29


def test_a_number_set_by_hand_counts_from_the_next_spin(make_game, clock, tmp_path):
    stock_file = tmp_path / "stock.yaml"
    game = make_game(stock_file=str(stock_file))
    game.step()

    write(stock_file, {"mini": 0, "playdough": 5, "big_prize": 0})   # set while the game runs
    press_space(game)
    picker = game.state_stack[-1]
    seen = set()
    for interval in STEP_RATE_CURVE[:10]:
        seen.add(picker.current_prize["type"])
        wait(game, clock, interval + 0.001)

    assert seen == {"playdough"}


def test_a_number_set_by_hand_during_a_spin_is_kept(make_game, clock, tmp_path):
    stock_file = tmp_path / "stock.yaml"
    game = make_game(rng=ScriptedPicks(["mini"] * 30), stock_file=str(stock_file))
    game.step()
    press_space(game)

    write(stock_file, {"mini": 30, "playdough": 0, "big_prize": 0})  # more supplies arrive mid-spin
    press_space(game)

    assert screen(game) == "Winner"
    assert read(stock_file)["mini"] == 29


def test_with_nothing_left_the_title_says_out_of_candy_and_ignores_the_button(make_game, tmp_path, snap):
    stock_file = tmp_path / "stock.yaml"
    write(stock_file, {"mini": 0, "playdough": 0, "big_prize": 0})
    game = make_game(stock_file=str(stock_file))
    game.step()

    press_space(game)

    assert screen(game) == "Title"
    assert game.state_stack[-1].out_of_stock
    snap(game, "out-of-candy")


def test_restocking_brings_the_button_back(make_game, tmp_path):
    stock_file = tmp_path / "stock.yaml"
    write(stock_file, {"mini": 0, "playdough": 0, "big_prize": 0})
    game = make_game(stock_file=str(stock_file))
    game.step()
    press_space(game)
    assert screen(game) == "Title"

    write(stock_file, {"mini": 5, "playdough": 0, "big_prize": 0})
    press_space(game)

    assert screen(game) == "CandyPicker"


def test_the_last_prize_won_brings_out_of_candy(make_game, clock, tmp_path):
    stock_file = tmp_path / "stock.yaml"
    write(stock_file, {"mini": 1, "playdough": 0, "big_prize": 0})
    game = make_game(stock_file=str(stock_file))
    game.step()
    win(game, clock)

    press_space(game)                                    # leaves the winner screen

    assert screen(game) == "Title"
    assert game.state_stack[-1].out_of_stock


def test_a_file_that_will_not_read_keeps_the_last_stock(make_game, tmp_path):
    stock_file = tmp_path / "stock.yaml"
    write(stock_file, {"mini": 7, "playdough": 3, "big_prize": 2})
    game = make_game(stock_file=str(stock_file))
    game.step()

    stock_file.write_text("mini: lots\n")               # a typo
    press_space(game)

    assert screen(game) == "CandyPicker"
    assert game.prizes.inventory == {"mini": 7, "playdough": 3, "big_prize": 2}


def test_a_prize_at_zero_is_never_picked(tmp_path):
    stock_file = tmp_path / "stock.yaml"
    write(stock_file, {"mini": 5, "playdough": 0, "big_prize": 5})
    prizes = Prizes(FakeAudio(), random.Random(2), str(stock_file))

    picks = {prizes.pick(PRIZES.MIN_SPINS_FOR_BIG_PRIZE, "")["type"] for _ in range(500)}

    assert picks == {"mini", "big_prize"}


def test_when_only_big_prizes_are_left_one_can_be_won_before_the_minimum_spins(tmp_path):
    stock_file = tmp_path / "stock.yaml"
    write(stock_file, {"mini": 0, "playdough": 0, "big_prize": 3})
    prizes = Prizes(FakeAudio(), random.Random(2), str(stock_file))

    assert prizes.pick(1, "")["type"] == "big_prize"
