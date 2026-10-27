"""Each frame reaches the display once, scaled to the display's size, and drawing a frame loads nothing."""
import random

import pygame

from config import VISUAL
from conftest import press_space, wait
from fakes import FakeAudio, FakeClock, FakeHardware


def fullscreen_game(clock):
    """Fullscreen on the dummy driver is 1024x768, the size the Pi's display gives, so the canvas is scaled."""
    import game
    return game.Game(hardware=FakeHardware(), clock=clock, rng=random.Random(1), audio=FakeAudio(),
                     fullscreen=True, idle_video_files=None)


def test_the_screen_shows_the_canvas_scaled_to_the_display():
    clock = FakeClock()
    g = fullscreen_game(clock)
    press_space(g)
    wait(g, clock, VISUAL.TIMER_START_SECONDS - VISUAL.TIMER_SHOW_AT_SECONDS + 0.1)   # spinning, countdown up

    expected = pygame.transform.scale(g.game_canvas, g.SCREEN_DIMENSIONS)
    assert g.screen.get_size() == (1024, 768)
    assert pygame.image.tobytes(g.screen, "RGB") == pygame.image.tobytes(expected, "RGB")
    pygame.quit()


def test_each_frame_reaches_the_display_once(make_game, monkeypatch):
    game = make_game()
    presents = []
    monkeypatch.setattr(pygame.display, "flip", lambda: presents.append("flip"))
    monkeypatch.setattr(pygame.display, "update", lambda *args: presents.append("update"))

    game.step()

    assert presents == ["flip"]


def test_the_countdown_loads_no_font_while_it_shows(make_game, clock, monkeypatch):
    game = make_game()
    game.step()
    press_space(game)
    wait(game, clock, VISUAL.TIMER_START_SECONDS - VISUAL.TIMER_SHOW_AT_SECONDS + 0.1)
    assert game.state_stack[-1].timer_remaining <= VISUAL.TIMER_SHOW_AT_SECONDS   # the countdown is up

    loads = []
    font, sys_font = pygame.font.Font, pygame.font.SysFont
    monkeypatch.setattr(pygame.font, "Font", lambda *args: loads.append(args) or font(*args))
    monkeypatch.setattr(pygame.font, "SysFont", lambda *args: loads.append(args) or sys_font(*args))
    for _ in range(30):
        wait(game, clock, 1 / 30)

    assert loads == []
