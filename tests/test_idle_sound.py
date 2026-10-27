"""The title screen loops the crackle under the curtains and the show, and plays the soundtrack with each show;
a press stops both, and the crackle starts again when the game comes back to the title."""
import pygame

from audio import LOOP_CHANNEL, SHOW_CHANNEL, PygameAudio
from config import PRIZES, VISUAL
from conftest import press_space, screen, wait
from states.winner import RESET_DELAY

CRACKLE = VISUAL.IDLE_SOUND_FILE
SOUNDTRACK = VISUAL.IDLE_SHOW_SOUND_FILE
CHEAP = (VISUAL.IDLE_CURTAIN_FILE, VISUAL.IDLE_CURTAIN_FILE)   # the curtain clip stands in for the show: quicker to decode
SMALL = 0.001


def test_title_loops_the_crackle(make_game, audio):
    game = make_game()
    game.step()
    assert screen(game) == "Title"
    assert audio.looping == CRACKLE


def test_crackle_keeps_going_through_the_curtains_and_the_show(make_game, clock, audio):
    game = make_game(idle_video_files=CHEAP)
    game.step()
    wait(game, clock, game.idle_video.duration + VISUAL.IDLE_WAIT_SECONDS + SMALL)   # one whole loop, and into the next show
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


def test_soundtrack_starts_on_the_shows_first_frame(make_game, clock, audio):
    game = make_game(idle_video_files=CHEAP)
    game.step()
    wait(game, clock, VISUAL.IDLE_WAIT_SECONDS - SMALL)
    assert audio.shows_started == 0

    wait(game, clock, 2 * SMALL)
    assert audio.show == SOUNDTRACK
    assert audio.shows_started == 1
    assert audio.looping == CRACKLE
    assert audio.loops_started == 1   # the crackle was not restarted


def test_soundtrack_plays_once_per_show(make_game, clock, audio):
    game = make_game(idle_video_files=CHEAP)
    game.step()
    wait(game, clock, VISUAL.IDLE_WAIT_SECONDS + SMALL)
    for _ in range(5):
        wait(game, clock, game.idle_video.show.duration / 10)   # frames during the first show
    assert audio.shows_started == 1

    wait(game, clock, game.idle_video.duration)   # into the second show
    assert audio.shows_started == 2


def test_press_during_the_show_stops_the_soundtrack_and_the_crackle(make_game, clock, audio):
    game = make_game(idle_video_files=CHEAP)
    game.step()
    wait(game, clock, VISUAL.IDLE_WAIT_SECONDS + SMALL)
    assert audio.show == SOUNDTRACK

    press_space(game)
    assert screen(game) == "CandyPicker"
    assert audio.show is None
    assert audio.looping is None


def test_soundtrack_starts_again_with_the_first_show_back_at_the_title(make_game, clock, audio):
    game = make_game(idle_video_files=CHEAP)
    game.step()
    wait(game, clock, VISUAL.IDLE_WAIT_SECONDS + SMALL)
    press_space(game)
    press_space(game)
    wait(game, clock, RESET_DELAY + SMALL)
    assert screen(game) == "Title"
    assert audio.shows_started == 1

    wait(game, clock, VISUAL.IDLE_WAIT_SECONDS + SMALL)
    assert audio.shows_started == 2
    assert audio.show == SOUNDTRACK


def test_no_soundtrack_file_leaves_the_show_silent(make_game, clock, audio):
    game = make_game(idle_video_files=CHEAP, show_sound_file=None)
    game.step()
    wait(game, clock, VISUAL.IDLE_WAIT_SECONDS + SMALL)
    assert audio.shows_started == 0
    assert audio.looping == CRACKLE


def test_without_the_video_no_soundtrack_plays(make_game, clock, audio):
    game = make_game()   # still background: there is no show to play it with
    game.step()
    wait(game, clock, VISUAL.IDLE_WAIT_SECONDS + 1)
    assert audio.shows_started == 0


def test_a_soundtrack_that_will_not_load_leaves_the_show_silent(clock, hardware):
    import game as game_module
    g = game_module.Game(hardware=hardware, clock=clock, audio=PygameAudio(), fullscreen=False,
                         idle_video_files=None, show_sound_file="sounds/no-such-file.wav")
    g.step()
    assert screen(g) == "Title"
    assert g.show_sound is None
    pygame.quit()


def real_sounds():
    """The real mixer, with the crackle, the soundtrack and a prize sound loaded."""
    pygame.init()
    audio = PygameAudio()
    crackle = audio.load(CRACKLE, VISUAL.IDLE_SOUND_VOLUME)
    soundtrack = audio.load(SOUNDTRACK, VISUAL.IDLE_SHOW_SOUND_VOLUME)
    prize_sound = audio.load(PRIZES.PRIZE_CATEGORIES["mini"]["sound_file"], 0.5)
    return audio, crackle, soundtrack, prize_sound


def test_other_sounds_play_over_the_crackle_without_stopping_it():
    audio, crackle, soundtrack, prize_sound = real_sounds()
    audio.loop(crackle)
    audio.play(prize_sound)
    assert crackle.get_num_channels() == 1
    assert prize_sound.get_num_channels() == 1
    pygame.quit()


def test_starting_the_crackle_cuts_off_no_sound_already_playing():
    """A prize sound can still be playing when the title comes back; it never sits on the crackle's channel."""
    audio, crackle, soundtrack, prize_sound = real_sounds()
    audio.play(prize_sound)
    audio.loop(crackle)
    assert prize_sound.get_num_channels() == 1
    assert crackle.get_num_channels() == 1
    pygame.quit()


def test_crackle_soundtrack_and_prize_sound_play_together_on_their_own_channels():
    audio, crackle, soundtrack, prize_sound = real_sounds()
    audio.loop(crackle)
    audio.play_show(soundtrack)
    audio.play(prize_sound)
    assert pygame.mixer.Channel(LOOP_CHANNEL).get_sound() == crackle
    assert pygame.mixer.Channel(SHOW_CHANNEL).get_sound() == soundtrack
    assert prize_sound.get_num_channels() == 1
    pygame.quit()


def test_stopping_the_soundtrack_leaves_the_crackle_playing():
    audio, crackle, soundtrack, prize_sound = real_sounds()
    audio.loop(crackle)
    audio.play_show(soundtrack)
    audio.stop_show()
    assert soundtrack.get_num_channels() == 0
    assert crackle.get_num_channels() == 1
    pygame.quit()
