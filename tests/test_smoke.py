"""One round of the game as it stands, on the real clock: title, spin, winner, back to title."""
import time

import pygame

import config

config.GAME.DEV_MODE = True      # fake GPIO; set before game.py is imported
config.GAME.FULLSCREEN = False

import game as game_module


def run_for(g, seconds):
    end = time.time() + seconds
    while time.time() < end:
        g.get_dt()
        g.get_events()
        g.update()
        g.render()
        time.sleep(1 / 60)


def press_space(g):
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
    run_for(g, 0.1)
    pygame.event.post(pygame.event.Event(pygame.KEYUP, key=pygame.K_SPACE))
    run_for(g, 0.1)


def screen_name(g):
    return type(g.state_stack[-1]).__name__


def test_one_round_on_the_real_clock():
    g = game_module.Game()
    run_for(g, 0.2)
    assert screen_name(g) == "Title"

    press_space(g)
    run_for(g, 1)
    assert screen_name(g) == "CandyPicker"

    press_space(g)
    assert screen_name(g) == "Winner"

    run_for(g, 5.5)
    assert screen_name(g) == "Title"
