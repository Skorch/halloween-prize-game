"""The light strip behind the screen: each screen shows its scene from LIGHTS in config.py, the spin's heartbeat
follows the cards and the countdown, and no scene goes past the brightness cap."""
import pygame
import pytest

from config import LIGHTS, VISUAL
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
    """The brightest channel of the first LED, sampled every `step` seconds for `seconds`."""
    samples = []
    now = 0.0
    lights.colours(now)
    for _ in range(round(seconds / step)):
        now += step
        samples.append(max(lights.colours(now)[0]))
    return samples


def rises(samples):
    """How many times the samples climb past half their peak: one for each thump of a heartbeat."""
    half = max(samples) / 2
    return sum(1 for before, after in zip(samples, samples[1:]) if before <= half < after)


def test_title_shows_the_title_scene(make_game, clock, hardware):
    game = make_game()
    game.step()
    wait(game, clock, 0.5)

    assert game.lights.scene_name == LIGHTS.TITLE
    assert hardware.strip[-1] != [DARK] * LIGHTS.NUM_LEDS
    assert len(hardware.strip[-1]) == LIGHTS.NUM_LEDS
    assert hardware.strip[-1] != hardware.strip[-2]          # it moves


def test_the_strip_gets_one_frame_per_game_frame(make_game, hardware):
    game = make_game()
    for _ in range(5):
        game.step()

    assert len(hardware.strip) == 5


def test_spin_shows_the_spin_scene_and_its_pace_follows_the_cards(make_game, clock):
    game = make_game()
    game.step()
    press_space(game)

    assert screen(game) == "CandyPicker"
    assert game.lights.scene_name == LIGHTS.SPIN
    assert game.lights.pace == 0
    spin_to_last_card(game, clock)
    assert game.lights.pace == 1


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


def test_pace_speeds_the_heartbeat_up():
    calm, racing = Lights(), Lights()
    calm.show(LIGHTS.SPIN, 0.0)
    racing.show(LIGHTS.SPIN, 0.0)
    racing.pace = 1

    assert rises(levels(racing, 6)) > rises(levels(calm, 6))


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
    lights.pace, lights.boost = 1, 1

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
