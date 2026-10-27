"""The title screen loops the crackle under the clips and the holds between them; a press stops it, and it
starts again when the game comes back to the title."""
import pygame

from audio import PygameAudio
from config import PRIZES, VISUAL
from conftest import press_space, screen, wait
from states.winner import RESET_DELAY

CRACKLE = VISUAL.IDLE_SOUND_FILE


def test_title_loops_the_crackle(make_game, audio):
    game = make_game()
    game.step()
    assert screen(game) == "Title"
    assert audio.looping == CRACKLE


def test_crackle_keeps_going_through_the_holds_and_the_clips(make_game, clock, audio):
    game = make_game(idle_video_files=VISUAL.IDLE_VIDEO_FILES[:1])
    game.step()
    wait(game, clock, game.idle_video.duration + VISUAL.IDLE_VIDEO_HOLD_BEFORE)   # one whole loop, and into the next hold
    assert audio.looping == CRACKLE
    assert audio.loops_started == 1


def test_press_stops_the_crackle(make_game, audio):
    game = make_game()
    game.step()
    press_space(game)
    assert screen(game) == "CandyPicker"
    assert audio.looping is None


def test_crackle_starts_again_back_at_the_title(make_game, clock, audio):
    game = make_game()
    game.step()
    press_space(game)
    press_space(game)
    assert screen(game) == "Winner"
    assert audio.looping is None

    wait(game, clock, RESET_DELAY + 0.1)

    assert screen(game) == "Title"
    assert audio.looping == CRACKLE


def test_no_crackle_file_leaves_the_title_silent(make_game, audio):
    game = make_game(idle_sound_file=None)
    game.step()
    assert screen(game) == "Title"
    assert audio.looping is None


def test_a_crackle_that_will_not_load_leaves_the_title_silent(clock, hardware):
    import game as game_module
    g = game_module.Game(hardware=hardware, clock=clock, audio=PygameAudio(), fullscreen=False,
                         idle_video_files=None, idle_sound_file="sounds/no-such-file.mp3")
    g.step()
    assert screen(g) == "Title"
    assert g.idle_sound is None
    pygame.quit()


def real_sounds():
    """The real mixer, with the crackle and a prize sound loaded."""
    pygame.init()
    audio = PygameAudio()
    crackle = audio.load(CRACKLE, VISUAL.IDLE_SOUND_VOLUME)
    prize_sound = audio.load(PRIZES.PRIZE_CATEGORIES["mini"]["sound_file"], 0.5)
    return audio, crackle, prize_sound


def test_other_sounds_play_over_the_crackle_without_stopping_it():
    audio, crackle, prize_sound = real_sounds()
    audio.loop(crackle)
    audio.play(prize_sound)
    assert crackle.get_num_channels() == 1
    assert prize_sound.get_num_channels() == 1
    pygame.quit()


def test_starting_the_crackle_cuts_off_no_sound_already_playing():
    """A prize sound can still be playing when the title comes back; it never sits on the crackle's channel."""
    audio, crackle, prize_sound = real_sounds()
    audio.play(prize_sound)
    audio.loop(crackle)
    assert prize_sound.get_num_channels() == 1
    assert crackle.get_num_channels() == 1
    pygame.quit()
