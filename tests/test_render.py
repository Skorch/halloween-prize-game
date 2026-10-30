"""Each frame reaches the display once, scaled to GAME.SCREEN_SCALE of the display's size inside a black mat, and
drawing a frame loads nothing."""
import random

import pygame

from config import GAME, VISUAL
from conftest import press_space, wait
from fakes import FakeAudio, FakeClock, FakeHardware


def fullscreen_game(clock):
    """Fullscreen on the dummy driver is 1024x768, the size the Pi's display gives, so the canvas is scaled."""
    import game
    return game.Game(hardware=FakeHardware(), clock=clock, rng=random.Random(1), audio=FakeAudio(),
                     fullscreen=True, idle_video_files=None)


def matted(canvas, size):
    """What the display should show: black, with the canvas scaled to GAME.SCREEN_SCALE of size in the middle."""
    w, h = size
    picture = pygame.Rect(0, 0, round(w * GAME.SCREEN_SCALE), round(h * GAME.SCREEN_SCALE))
    picture.center = (w // 2, h // 2)
    frame = pygame.Surface(size)
    frame.fill((0, 0, 0))
    frame.blit(pygame.transform.scale(canvas, picture.size), picture)
    return frame


def test_the_screen_shows_the_canvas_inside_a_black_mat():
    clock = FakeClock()
    g = fullscreen_game(clock)
    press_space(g)
    wait(g, clock, VISUAL.TIMER_START_SECONDS - VISUAL.TIMER_SHOW_AT_SECONDS + 0.1)   # spinning, countdown up

    expected = matted(g.game_canvas, g.SCREEN_DIMENSIONS)
    assert g.screen.get_size() == (1024, 768)
    assert pygame.image.tobytes(g.screen, "RGB") == pygame.image.tobytes(expected, "RGB")
    pygame.quit()


def test_a_frame_draws_onto_the_display_surface_pygame_has_now(make_game):
    """On the Pi, the window events at startup make pygame swap the display surface for a new one (2026-10-26,
    measured: the old one's size read (0, 0), then garbage). The game must draw onto the one pygame shows now,
    at its size, not onto the one set_mode gave."""
    game = make_game()
    game.step()
    shown = pygame.display.set_mode((800, 600))   # the display surface changes under the game

    game.step()

    expected = matted(game.game_canvas, (800, 600))
    assert pygame.image.tobytes(shown, "RGB") == pygame.image.tobytes(expected, "RGB")


def test_the_mat_is_black_and_the_picture_keeps_the_display_shape():
    clock = FakeClock()
    g = fullscreen_game(clock)
    g.step()
    w, h = g.SCREEN_DIMENSIONS
    side = (w - round(w * GAME.SCREEN_SCALE)) // 2
    top = (h - round(h * GAME.SCREEN_SCALE)) // 2

    assert GAME.SCREEN_SCALE < 1
    assert g.screen.get_at((side - 1, h // 2))[:3] == (0, 0, 0)   # left edge of the mat
    assert g.screen.get_at((w // 2, top - 1))[:3] == (0, 0, 0)    # top edge of the mat
    assert abs(side / w - top / h) < 0.01                         # the same share off the width and the height
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
