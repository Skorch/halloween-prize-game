"""The beep has a channel of its own, so each card's beep cuts off the one before and none is dropped; the winner
screen stops it, leaves a gap of PRIZES.WIN_SOUND_DELAY, and then plays the prize sound."""
import pygame

from audio import BEEP_CHANNEL, PygameAudio
from config import PRIZES
from conftest import press_space, screen, wait
from fakes import ScriptedPicks
from states.candy_picker import STEP_RATE_CURVE

BEEP = PRIZES.BEEP_SOUND_FILE
MINI_SOUND = PRIZES.PRIZE_CATEGORIES["mini"]["sound_file"]
STOP_SOUND = "sounds/beep.wav"       # any sound in the repo stands in for a stop sound
SMALL = 0.001


def to_winner(game, clock):
    game.step()
    press_space(game)
    for interval in STEP_RATE_CURVE[:3]:
        wait(game, clock, interval + SMALL)
    press_space(game)
    assert screen(game) == "Winner"


def test_every_card_beeps_on_the_beeps_own_channel(make_game, clock, audio):
    game = make_game()
    game.step()
    press_space(game)
    for interval in STEP_RATE_CURVE[:5]:
        assert audio.beep == BEEP
        wait(game, clock, interval + SMALL)

    assert audio.played.count(BEEP) == 6


def test_the_winner_screen_stops_the_beep(make_game, clock, audio):
    game = make_game(rng=ScriptedPicks(["mini"] * 30))

    to_winner(game, clock)

    assert audio.beep is None


def test_the_prize_sound_waits_for_the_gap(make_game, clock, audio):
    game = make_game(rng=ScriptedPicks(["mini"] * 30))
    to_winner(game, clock)

    wait(game, clock, PRIZES.WIN_SOUND_DELAY - 0.05)
    assert MINI_SOUND not in audio.played
    wait(game, clock, 0.05 + SMALL)
    assert audio.played[-1] == MINI_SOUND
    for _ in range(10):
        wait(game, clock, 0.1)
    assert audio.played.count(MINI_SOUND) == 1


def test_a_stop_sound_plays_as_the_winner_screen_opens(make_game, clock, audio):
    game = make_game(rng=ScriptedPicks(["mini"] * 30), stop_sound_file=STOP_SOUND)

    to_winner(game, clock)

    assert audio.played[-1] == STOP_SOUND


def test_without_a_stop_sound_the_gap_is_silent(make_game, clock, audio):
    game = make_game(rng=ScriptedPicks(["mini"] * 30))
    to_winner(game, clock)
    before = len(audio.played)

    wait(game, clock, PRIZES.WIN_SOUND_DELAY / 2)

    assert len(audio.played) == before


def real_sounds():
    pygame.mixer.quit()
    audio = PygameAudio()
    beep = audio.load(BEEP, PRIZES.BEEP_SOUND_VOLUME)
    prize_sound = audio.load(MINI_SOUND, PRIZES.PRIZE_SOUND_VOLUME)
    return audio, beep, prize_sound


def test_a_new_beep_cuts_off_the_one_before():
    audio, beep, prize_sound = real_sounds()
    audio.play_beep(beep)
    audio.play_beep(beep)

    assert pygame.mixer.Channel(BEEP_CHANNEL).get_sound() == beep
    assert beep.get_num_channels() == 1
    pygame.quit()


def test_a_prize_sound_never_takes_the_beeps_channel():
    audio, beep, prize_sound = real_sounds()
    audio.play_beep(beep)
    audio.play(prize_sound)

    assert pygame.mixer.Channel(BEEP_CHANNEL).get_sound() == beep
    assert prize_sound.get_num_channels() == 1
    pygame.quit()
