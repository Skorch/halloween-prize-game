"""The title screen holds, plays the idle clips in order, holds, and loops; it shows the still background
when no clip loads. Most tests load only the first clips: each takes a moment to decode."""
import pygame

from config import VISUAL
from conftest import press_space, screen, wait
from states.winner import RESET_DELAY

SMALL = 0.001
FIRST_TWO = VISUAL.IDLE_VIDEO_FILES[:2]


def showing(game, frame):
    """True when the canvas holds exactly this frame."""
    return pygame.image.tobytes(game.game_canvas, "RGB") == pygame.image.tobytes(frame, "RGB")


def test_title_holds_the_first_frame_then_plays_the_clips_in_order(make_game, clock, snap):
    game = make_game(idle_video_files=FIRST_TWO)
    first, second = game.idle_video.clips
    game.step()
    snap(game, "start")
    assert showing(game, first.frames[0])

    wait(game, clock, VISUAL.IDLE_VIDEO_HOLD_BEFORE - SMALL)
    assert showing(game, first.frames[0])

    wait(game, clock, 10 / first.fps + 2 * SMALL)
    assert showing(game, first.frames[10])

    wait(game, clock, first.duration - 10 / first.fps)
    snap(game, "second-clip")
    assert showing(game, second.frames[0])


def test_after_the_last_clip_it_holds_the_last_frame_then_starts_over(make_game, clock):
    game = make_game(idle_video_files=FIRST_TWO)
    video = game.idle_video
    first, last = video.clips
    game.step()

    wait(game, clock, VISUAL.IDLE_VIDEO_HOLD_BEFORE + first.duration + last.duration + SMALL)
    assert showing(game, last.frames[-1])

    wait(game, clock, VISUAL.IDLE_VIDEO_HOLD_AFTER - 2 * SMALL)
    assert showing(game, last.frames[-1])

    wait(game, clock, 2 * SMALL + VISUAL.IDLE_VIDEO_HOLD_BEFORE + 10 / first.fps)   # a whole loop later
    assert showing(game, first.frames[10])


def test_back_at_the_title_the_clips_start_over_without_loading_again(make_game, clock):
    game = make_game(idle_video_files=FIRST_TWO[:1])
    video = game.idle_video
    game.step()
    wait(game, clock, VISUAL.IDLE_VIDEO_HOLD_BEFORE + 1)
    press_space(game)
    press_space(game)
    assert screen(game) == "Winner"

    wait(game, clock, RESET_DELAY + SMALL)
    assert screen(game) == "Title"
    wait(game, clock, VISUAL.IDLE_VIDEO_HOLD_BEFORE + 10 / video.clips[0].fps + SMALL)

    assert game.idle_video is video
    assert showing(game, video.clips[0].frames[10])


def test_a_clip_that_will_not_load_is_skipped(make_game):
    game = make_game(idle_video_files=["assets/idle/missing.mp4", FIRST_TWO[0]])

    assert len(game.idle_video.clips) == 1


def test_when_no_clip_loads_the_title_shows_the_still_background(make_game, snap):
    game = make_game(idle_video_files=["assets/idle/missing.mp4"])
    game.step()
    snap(game, "title")

    assert game.idle_video is None
    assert screen(game) == "Title"
    assert not showing(game, pygame.Surface(game.GAME_DIMENSIONS))   # something was drawn
