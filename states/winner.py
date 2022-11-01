from states.state import State
import pygame
from time import time
from colors import *

RESET_DELAY = 5

class Winner(State):
    def __init__(self, game, prize) -> None:
        super().__init__(game)
        self.prize = prize
        self.win_time = time()
        self.has_rendered = False



    def update(self, delta_time, actions):
        now = time()
        if actions["space"] or actions["button"]:
            self.game.reset_states()
        if now - self.win_time >= RESET_DELAY:
            self.game.reset_states()

        self.game.reset_keys()

    def render(self, surface):
        # surface.set_alpha(0.6)

        if not self.has_rendered:
            filename = self.prize["filename"]
            prize_text = self.prize["title"]
            image = pygame.image.load(filename)
            image = pygame.transform.scale(image, self.game.GAME_DIMENSIONS)    
            surface.blit(image, (0, 0))


            text_color = TEXT_COLOR_1
            fill_color = TEXT_BG_1
            fill_alpha = 200
            message = f"You win {self.prize['title']}!"
            sound = self.prize["sound"]
            fill_rect = (self.game.GAME_W, self.game.GAME_H)
            fill_position = (0, 0)
            self.game.draw_text( surface, message, text_color, self.game.GAME_W/2, self.game.GAME_H/2, fill_rect=self.game.GAME_DIMENSIONS, fill_color=fill_color, fill_alpha=fill_alpha)
            self.game.play_sound(sound)
            self.has_rendered = True