"""The game takes its hardware, clock, random source and sound as parameters."""
import os
import random
import subprocess
import sys

from conftest import REPO
from fakes import FakeAudio, FakeClock, FakeHardware


IMPORT_CHECK = """
import sys, pygame, game
assert "pi2" not in sys.modules, "pi2 imported"
assert not pygame.display.get_init(), "display started on import"
assert pygame.mixer.get_init() is None, "mixer started on import"
"""


def test_importing_the_game_touches_no_hardware():
    env = dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy")
    result = subprocess.run([sys.executable, "-c", IMPORT_CHECK], cwd=REPO, env=env,
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_game_runs_a_frame_on_fakes():
    import game

    hardware, audio = FakeHardware(), FakeAudio()
    g = game.Game(hardware=hardware, clock=FakeClock(), rng=random.Random(1), audio=audio,
                  fullscreen=False)
    g.step()

    assert type(g.state_stack[-1]).__name__ == "Title"
    assert hardware.count("gpio_setup") == 1


def test_fullscreen_scales_to_the_size_the_display_gives():
    """Fullscreen asks for GAME.FULLSCREEN_MODE; the display picks its nearest mode, and the game scales to that.

    The dummy driver has one mode (1024x768), so this cannot show which size was asked for. On the Pi on
    2026-10-26 the game printed "Screen: 1024x768" for the 1000x666 asked.
    """
    import game
    import pygame

    g = game.Game(hardware=FakeHardware(), clock=FakeClock(), rng=random.Random(1), audio=FakeAudio(),
                  fullscreen=True)

    assert g.screen.get_flags() & pygame.FULLSCREEN
    assert g.SCREEN_DIMENSIONS == g.screen.get_size()
    pygame.quit()
