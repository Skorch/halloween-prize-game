"""The light strip behind the screen: each screen shows its scene from LIGHTS in config.py, the spin thumps on every
beep and brightens in the countdown, and no scene goes past the brightness cap."""
import pygame
import pytest

from config import LIGHTS, PRIZES, VISUAL
from conftest import OUT, press_space, screen, wait
from fakes import ScriptedPicks
from lights import EFFECTS, Lights, strip_bytes, SPI_ONE, SPI_ZERO
from states.candy_picker import STEP_RATE_CURVE

DARK = (0, 0, 0)
BRIGHTEST = round(255 * LIGHTS.MAX_BRIGHTNESS)


def spin_to_last_card(game, clock):
    for interval in STEP_RATE_CURVE:
        wait(game, clock, interval + 0.001)


def levels(lights, seconds, step=1 / 240):
    """The brightest channel of the first LED, sampled every `step` seconds from 0 for `seconds`."""
    return [max(lights.colours(i * step)[0]) for i in range(round(seconds / step))]


def thumps(samples):
    """How many times the samples jump past half their peak, a start above it counting as one."""
    half = max(samples) / 2
    return sum(1 for before, after in zip([0] + samples, samples) if before <= half < after)


def test_title_shows_the_title_scene(make_game, clock, hardware):
    game = make_game()
    game.step()
    wait(game, clock, 0.5)

    assert game.lights.scene_name == LIGHTS.TITLE
    assert hardware.strip[-1] != [DARK] * LIGHTS.NUM_LEDS
    assert len(hardware.strip[-1]) == LIGHTS.NUM_LEDS
    assert hardware.strip[-1] != hardware.strip[-2]          # it moves


def fire_levels(seconds):
    """The title scene's first LED, frame by frame at 30 frames a second."""
    lights = Lights()
    lights.show(LIGHTS.TITLE, 0.0)
    return [max(lights.colours(i / 30)[0]) for i in range(round(seconds * 30))]


def test_the_fire_drops_nearly_dark_between_flares():
    samples = fire_levels(8)

    assert min(samples) < 0.15 * max(samples)


def test_the_fire_flickers():
    """Its brightness turns from rising to falling, or back, at least 6 times a second."""
    samples = fire_levels(8)
    turns = sum(1 for a, b, c in zip(samples, samples[1:], samples[2:]) if (b - a) * (c - b) < 0)

    assert turns / 8 >= 6


def test_the_strip_gets_one_frame_per_game_frame(make_game, hardware):
    game = make_game()
    for _ in range(5):
        game.step()

    assert len(hardware.strip) == 5


def test_slow_cards_show_the_spin_scene_and_quick_ones_the_fast_scene(make_game, clock):
    game = make_game()
    game.step()
    press_space(game)

    assert screen(game) == "CandyPicker"
    assert STEP_RATE_CURVE[0] >= LIGHTS.SPIN_FAST_SECONDS
    assert game.lights.scene_name == LIGHTS.SPIN
    spin_to_last_card(game, clock)
    assert STEP_RATE_CURVE[-1] < LIGHTS.SPIN_FAST_SECONDS
    assert game.lights.scene_name == LIGHTS.SPIN_FAST


def test_the_strip_is_brightest_on_each_beep(make_game, clock, audio, hardware):
    """Each beep starts a thump on its own frame: no frame of that card is brighter."""
    game = make_game()
    game.step()
    press_space(game)
    cards = []                                   # each card's strip levels, from the frame its beep played
    beeps = 0
    for _ in range(round((VISUAL.TIMER_START_SECONDS - VISUAL.TIMER_SHOW_AT_SECONDS) * 30) - 1):
        if audio.played.count(PRIZES.BEEP_SOUND_FILE) > beeps:
            beeps = audio.played.count(PRIZES.BEEP_SOUND_FILE)
            cards.append([])
        cards[-1].append(max(hardware.strip[-1][0]))
        wait(game, clock, 1 / 30)

    slow_cards = sum(1 for seconds in STEP_RATE_CURVE if seconds >= LIGHTS.SPIN_FAST_SECONDS)
    assert len(cards) > slow_cards + 1          # quick cards were reached too
    for card in cards[:-1]:                      # the last card is cut short by the end of the loop
        assert card[0] == max(card)
        assert card[0] > card[-1]


def test_a_slow_card_thumps_twice_and_a_quick_one_flashes_once():
    slow, quick = Lights(), Lights()
    slow.beat(LIGHTS.SPIN, 0.0, STEP_RATE_CURVE[0])
    quick.beat(LIGHTS.SPIN_FAST, 0.0, STEP_RATE_CURVE[-1])

    assert thumps(levels(slow, STEP_RATE_CURVE[0])) == 2
    assert thumps(levels(quick, STEP_RATE_CURVE[-1])) == 1


def test_the_glow_brightens_as_the_countdown_runs_down(make_game, clock):
    game = make_game()
    game.step()
    press_space(game)
    hidden_for = VISUAL.TIMER_START_SECONDS - VISUAL.TIMER_SHOW_AT_SECONDS

    wait(game, clock, hidden_for - 0.1)
    assert game.lights.boost == 0
    wait(game, clock, VISUAL.TIMER_SHOW_AT_SECONDS / 2 + 0.1)
    assert game.lights.boost == pytest.approx(0.5)
    wait(game, clock, VISUAL.TIMER_SHOW_AT_SECONDS / 2 - 0.1)
    assert game.lights.boost > 0.9


@pytest.mark.parametrize("prize_type", sorted(LIGHTS.WINNER))
def test_each_prize_lights_its_own_scene(make_game, clock, prize_type):
    game = make_game(rng=ScriptedPicks(["mini"] * 5 + [prize_type] + ["mini"] * 20))
    game.step()
    press_space(game)
    for interval in STEP_RATE_CURVE[:5]:
        wait(game, clock, interval + 0.001)

    press_space(game)

    assert game.state_stack[-1].prize["type"] == prize_type
    assert game.lights.scene_name == LIGHTS.WINNER[prize_type]


def test_back_at_the_title_the_title_scene_shows_again(make_game):
    game = make_game()
    game.step()
    press_space(game)
    press_space(game)
    press_space(game)

    assert screen(game) == "Title"
    assert game.lights.scene_name == LIGHTS.TITLE


def test_the_strip_goes_dark_when_the_game_quits(make_game, hardware):
    game = make_game()
    game.step()

    game.quit_game()

    assert hardware.strip[-1] == [DARK] * LIGHTS.NUM_LEDS


def test_boost_lifts_the_scene_to_the_cap():
    plain, boosted = Lights(), Lights()
    plain.show(LIGHTS.SPIN, 0.0)
    boosted.show(LIGHTS.SPIN, 0.0)
    boosted.boost = 1

    assert max(levels(plain, 2)) < max(levels(boosted, 2)) <= BRIGHTEST


@pytest.mark.parametrize("name", sorted(LIGHTS.SCENES))
def test_no_scene_goes_past_the_cap(name):
    lights = Lights()
    lights.show(name, 0.0)
    lights.boost = 1

    for step in range(300):                                  # 10 s
        for colour in lights.colours(step / 30):
            assert all(0 <= c <= BRIGHTEST for c in colour)
            assert all(isinstance(c, int) for c in colour)


@pytest.mark.parametrize("effect", sorted(EFFECTS))
def test_each_effect_gives_one_colour_per_led(effect):
    colours = EFFECTS[effect](1.3, LIGHTS.NUM_LEDS, [(255, 0, 0), (0, 0, 255)])

    assert len(colours) == LIGHTS.NUM_LEDS


def data(sent):
    """One LED's 24 SPI bytes (8 for each bit), with the line held low before and after them."""
    start = next(i for i, b in enumerate(sent) if b)
    assert set(sent[:start]) == {0}
    assert set(sent[start + 24:]) == {0}
    return sent[start:start + 24]


def test_strip_bytes_send_green_then_red_then_blue():
    sent = data(strip_bytes([(255, 0, 0)]))

    assert sent[0:8] == bytes([SPI_ZERO] * 8)     # green: 0
    assert sent[8:16] == bytes([SPI_ONE] * 8)     # red: 255
    assert sent[16:24] == bytes([SPI_ZERO] * 8)   # blue: 0


def test_strip_bytes_send_the_highest_bit_first():
    sent = data(strip_bytes([(0, 0b10000001, 0)]))

    assert sent[0:8] == bytes([SPI_ONE] + [SPI_ZERO] * 6 + [SPI_ONE])


def test_outputs_show_in_the_mat_on_the_mac(make_game, clock):
    game = make_game(show_outputs=True)
    game.step()
    wait(game, clock, 0.5)
    shown = pygame.display.get_surface()

    for centre in game.output_dot_centres(shown.get_size())[:LIGHTS.NUM_LEDS]:
        assert shown.get_at(centre)[:3] != DARK
    OUT.mkdir(exist_ok=True)
    pygame.image.save(shown, str(OUT / "outputs-in-the-mat.png"))   # for a person to look at


def test_outputs_stay_hidden_without_show_outputs(make_game, clock):
    game = make_game()
    game.step()
    wait(game, clock, 0.5)
    shown = pygame.display.get_surface()

    for centre in game.output_dot_centres(shown.get_size()):
        assert shown.get_at(centre)[:3] == DARK
