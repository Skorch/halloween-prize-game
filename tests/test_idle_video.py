"""The title screen repeats the curtain clip for the wait, plays the show once, and starts over; it shows the
still background when the video does not load. The IdleVideo tests use small made-up clips, and only one test
decodes the real show, which takes a few seconds."""
import pygame
import pytest

from config import VISUAL
from conftest import press_space, screen, wait
from states.winner import RESET_DELAY
from video import Clip, IdleVideo

SMALL = 0.001
REAL = (VISUAL.IDLE_CURTAIN_FILE, VISUAL.IDLE_SHOW_FILE)
CHEAP = (VISUAL.IDLE_CURTAIN_FILE, VISUAL.IDLE_CURTAIN_FILE)   # the curtain clip stands in for the show: quicker to decode


def showing(game, frame):
    """True when the canvas holds exactly this frame."""
    return pygame.image.tobytes(game.game_canvas, "RGB") == pygame.image.tobytes(frame, "RGB")


def made_up_clip(frame_count, fps=10):
    return Clip([pygame.Surface((1, 1)) for _ in range(frame_count)], fps)


def test_curtains_repeat_for_the_wait_then_the_show_plays_then_it_starts_over():
    curtain, show = made_up_clip(20), made_up_clip(30)   # 2 s and 3 s
    video = IdleVideo(curtain, show, wait=5)

    assert video.frame_at(0) is curtain.frames[0]
    assert video.frame_at(1.05) is curtain.frames[10]
    assert video.frame_at(2.05) is curtain.frames[0]     # the curtain clip starts again
    assert video.frame_at(4.95) is curtain.frames[9]     # the wait can end part way through the clip
    assert video.frame_at(5) is show.frames[0]
    assert video.frame_at(7.95) is show.frames[29]
    assert video.frame_at(8) is curtain.frames[0]        # 5 s wait + 3 s show, then it starts over


def test_shows_started_counts_each_show_from_its_first_frame():
    video = IdleVideo(made_up_clip(20), made_up_clip(30), wait=5)

    times = [0, 4.99, 5, 7.99, 8, 12.99, 13]
    assert [video.shows_started(t) for t in times] == [0, 0, 1, 1, 1, 1, 2]


def test_title_shows_the_curtains_then_the_show_then_the_curtains(make_game, clock, snap):
    game = make_game(idle_video_files=REAL)
    curtain, show = game.idle_video.curtain, game.idle_video.show
    game.step()
    snap(game, "curtains")
    assert showing(game, curtain.frames[0])

    wait(game, clock, VISUAL.IDLE_WAIT_SECONDS + SMALL)
    snap(game, "show-start")
    assert showing(game, show.frames[0])

    wait(game, clock, show.duration / 2)
    snap(game, "show-middle")
    assert showing(game, show.frames[len(show.frames) // 2])

    wait(game, clock, show.duration / 2)
    snap(game, "curtains-again")
    assert showing(game, curtain.frames[0])


def test_back_at_the_title_the_video_starts_over_without_loading_again(make_game, clock):
    game = make_game(idle_video_files=CHEAP)
    video = game.idle_video
    game.step()
    wait(game, clock, VISUAL.IDLE_WAIT_SECONDS + 1)
    press_space(game)
    press_space(game)
    assert screen(game) == "Winner"

    wait(game, clock, RESET_DELAY + SMALL)
    assert screen(game) == "Title"
    wait(game, clock, 10 / video.curtain.fps + SMALL)

    assert game.idle_video is video
    assert showing(game, video.curtain.frames[10])


@pytest.mark.parametrize("files", [("assets/idle/missing.mp4", VISUAL.IDLE_CURTAIN_FILE),
                                   (VISUAL.IDLE_CURTAIN_FILE, "assets/idle/missing.mp4")],
                         ids=["curtain-missing", "show-missing"])
def test_when_either_clip_will_not_load_the_title_shows_the_still_background(make_game, snap, files):
    game = make_game(idle_video_files=files)
    game.step()
    snap(game, "title")

    assert game.idle_video is None
    assert screen(game) == "Title"
    assert not showing(game, pygame.Surface(game.GAME_DIMENSIONS))   # something was drawn
