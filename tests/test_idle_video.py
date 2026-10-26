"""The title screen loops the idle video, and shows the still background when the video cannot load."""
import pygame

from config import VISUAL
from conftest import press_space, screen, wait
from states.winner import RESET_DELAY

SMALL = 0.001


def showing(game, frame):
    """True when the canvas holds exactly this frame."""
    return pygame.image.tobytes(game.game_canvas, "RGB") == pygame.image.tobytes(frame, "RGB")


def test_title_plays_the_video(make_game, clock, snap):
    game = make_game(idle_video_file=VISUAL.IDLE_VIDEO_FILE)
    video = game.idle_video
    game.step()
    snap(game, "start")

    assert showing(game, video.frames[0])

    wait(game, clock, 10 / video.fps + SMALL)
    assert showing(game, video.frames[10])

    wait(game, clock, len(video.frames) / 2 / video.fps)
    snap(game, "middle")
    assert not showing(game, video.frames[0])


def test_video_holds_its_last_frame_for_the_loop_delay_then_plays_again(make_game, clock):
    game = make_game(idle_video_file=VISUAL.IDLE_VIDEO_FILE)
    video = game.idle_video
    game.step()

    wait(game, clock, video.duration + SMALL)
    assert showing(game, video.frames[-1])

    wait(game, clock, VISUAL.IDLE_VIDEO_LOOP_DELAY - 2 * SMALL)
    assert showing(game, video.frames[-1])

    wait(game, clock, 2 * SMALL)
    assert showing(game, video.frames[0])

    wait(game, clock, video.duration + VISUAL.IDLE_VIDEO_LOOP_DELAY)   # and again, a whole loop later
    assert showing(game, video.frames[0])


def test_back_at_the_title_the_video_starts_over_without_loading_again(make_game, clock):
    game = make_game(idle_video_file=VISUAL.IDLE_VIDEO_FILE)
    video = game.idle_video
    game.step()
    wait(game, clock, 1)
    press_space(game)
    press_space(game)
    assert screen(game) == "Winner"

    wait(game, clock, RESET_DELAY + SMALL)
    assert screen(game) == "Title"
    game.step()

    assert game.idle_video is video
    assert showing(game, video.frames[0])


def test_a_video_that_will_not_load_shows_the_still_background(make_game, snap):
    game = make_game(idle_video_file="assets/backgrounds/missing.mp4")
    game.step()
    snap(game, "title")

    assert game.idle_video is None
    assert screen(game) == "Title"
    assert not showing(game, pygame.Surface(game.GAME_DIMENSIONS))   # something was drawn
