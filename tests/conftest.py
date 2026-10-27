"""Shared setup for every test: no window, no sound, and the repo folder as the working folder.

The game loads images, fonts and sounds by paths relative to the repo folder, and SDL reads its
driver settings when pygame starts, so both are set here, before any test imports the game.
"""
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

os.environ["SDL_VIDEODRIVER"] = "dummy"   # draw in memory, no window
os.environ["SDL_AUDIODRIVER"] = "dummy"   # play sounds into nothing
os.chdir(REPO)
sys.path.insert(0, str(REPO))

import random

import pygame
import pytest

from config import VISUAL
from fakes import FakeAudio, FakeClock, FakeHardware

OUT = REPO / "tests" / "out"


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def hardware():
    return FakeHardware()


@pytest.fixture
def audio():
    return FakeAudio()


@pytest.fixture
def make_game(clock, hardware, audio):
    """Builds a Game on the fakes. rng defaults to a seeded random source, so every run picks the same.

    The title shows the still background unless a test passes idle_video_files: decoding the video takes
    seconds, which most tests do not need.
    """
    import game

    def make(rng=None, hardware=hardware, idle_video_files=None, idle_sound_file=VISUAL.IDLE_SOUND_FILE,
             show_sound_file=VISUAL.IDLE_SHOW_SOUND_FILE):
        return game.Game(hardware=hardware, clock=clock, rng=rng if rng is not None else random.Random(1),
                         audio=audio, fullscreen=False, idle_video_files=idle_video_files,
                         idle_sound_file=idle_sound_file, show_sound_file=show_sound_file)

    yield make
    pygame.quit()


@pytest.fixture
def snap(request):
    """Saves the game's screen as tests/out/<test name>/<step>.png, for a person or an agent to look at."""
    folder = OUT / request.node.name

    def save(game, step):
        folder.mkdir(parents=True, exist_ok=True)
        pygame.image.save(game.game_canvas, str(folder / f"{step}.png"))

    return save


def screen(game):
    """The name of the screen the game is on: Title, CandyPicker or Winner."""
    return type(game.state_stack[-1]).__name__


def press_space(game):
    """The spacebar: down for one frame, then up for one frame."""
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
    game.step()
    pygame.event.post(pygame.event.Event(pygame.KEYUP, key=pygame.K_SPACE))
    game.step()


def wait(game, clock, seconds):
    """Moves the fake clock on, then runs one frame."""
    clock.advance(seconds)
    game.step()
