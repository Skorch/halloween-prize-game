"""Every file config.py and the screens name exists, so the game finds them on the night."""
import glob
from pathlib import Path

import pytest

from config import PRIZES, VISUAL

@pytest.mark.parametrize("name", PRIZES.PRIZE_CATEGORIES)
def test_each_prize_category_has_its_sound_and_cards(name):
    category = PRIZES.PRIZE_CATEGORIES[name]

    assert Path(category["sound_file"]).is_file()
    assert glob.glob(category["folder"]), f"no cards in {category['folder']}"


@pytest.mark.parametrize("path", [PRIZES.BEEP_SOUND_FILE, VISUAL.FONT_TTF_PATH, VISUAL.TITLE_BACKGROUND_FILE,
                                  VISUAL.IDLE_VIDEO_FILE])
def test_each_named_file_exists(path):
    assert Path(path).is_file()
