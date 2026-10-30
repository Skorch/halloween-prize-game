"""Every file config.py and the screens name exists, and every light scene they name is complete, so the game finds
them on the night."""
import glob
import random
from pathlib import Path

import pytest

from config import LIGHTS, PRIZES, VISUAL
from fakes import FakeAudio
from lights import EFFECTS
from prizes import Prizes

@pytest.mark.parametrize("name", PRIZES.PRIZE_CATEGORIES)
def test_each_prize_category_has_its_sound_and_cards(name):
    category = PRIZES.PRIZE_CATEGORIES[name]

    assert Path(category["sound_file"]).is_file()
    assert glob.glob(category["folder"]), f"no cards in {category['folder']}"


@pytest.mark.parametrize("path", [PRIZES.BEEP_SOUND_FILE, VISUAL.FONT_TTF_PATH, VISUAL.TITLE_BACKGROUND_FILE,
                                  VISUAL.IDLE_CURTAIN_FILE, VISUAL.IDLE_SHOW_FILE, VISUAL.IDLE_SOUND_FILE,
                                  VISUAL.IDLE_SHOW_SOUND_FILE])
def test_each_named_file_exists(path):
    assert Path(path).is_file()


def test_each_scene_the_screens_name_is_in_scenes():
    named = [LIGHTS.TITLE, LIGHTS.SPIN, *LIGHTS.WINNER.values()]

    assert [name for name in named if name not in LIGHTS.SCENES] == []


def test_each_prize_has_a_winner_scene():
    assert set(Prizes(FakeAudio(), random.Random(0)).inventory) <= set(LIGHTS.WINNER)


@pytest.mark.parametrize("name", sorted(LIGHTS.SCENES))
def test_each_scene_uses_an_effect_that_exists_and_stays_under_the_cap(name):
    scene = LIGHTS.SCENES[name]

    assert scene["effect"] in EFFECTS
    assert scene["colors"]
    assert 0 <= scene["brightness"] <= LIGHTS.MAX_BRIGHTNESS
