"""The game takes its hardware, clock, random source and sound as parameters."""
import os
import random
import subprocess
import sys

from conftest import REPO
from fakes import FakeAudio, FakeClock, FakeHardware


def test_importing_the_game_touches_no_hardware():
    env = dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy")
    result = subprocess.run([sys.executable, "-c", "import game"], cwd=REPO, env=env,
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
