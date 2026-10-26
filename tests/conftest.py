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
