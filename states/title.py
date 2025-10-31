from states.state import State
from states.candy_picker import CandyPicker
from colors import *
from config import MESSAGES
import pygame
from time import time

class Title(State):
    def __init__(self, game) -> None:
        super().__init__(game)
        self.next_led_time = time() + 1

    def update(self, delta_time, actions):
        if actions["space"] or actions["button"]:
            new_state = CandyPicker(self.game)
            new_state.enter_state()
        else:

            now = time()
            dt_led = self.next_led_time - now
            # print(f"candy picker update dt={dt}")
            # logger.debug(f"dt_led: {dt_led}; dt: {dt}")    

            if dt_led <= 0:
                # logger.debug(f"turning LED off for {dt_led}")
                self.toggle_led()
                self.next_led_time = time() + 1

        self.game.reset_keys()

    def toggle_led(self):

        self.game.toggle_led()

    def render1(self, surface):
        text_color = TEXT_COLOR_1
        fill_color = TEXT_BG_1
        # fill_color = (255, 255, 255)
        alpha = 255
        font = self.game.get_font_by_size(MESSAGES.TITLE_MESSAGE_FONT_SIZE)
        self.game.draw_text(surface, MESSAGES.TITLE_MESSAGE, text_color, self.game.GAME_W/2, self.game.GAME_H/2,
                          self.game.GAME_DIMENSIONS, fill_color=fill_color, fill_alpha=alpha, font=font)
        
            
    def render(self, surface):
        # 1. Loading and displaying the background image
        bg_image_filename = "assets/backgrounds/background2.png"  # Update this with your image's path
        bg_image = pygame.image.load(bg_image_filename)
        bg_image = pygame.transform.smoothscale(bg_image, self.game.GAME_DIMENSIONS)
        surface.blit(bg_image, (0, 0))

        # 2 & 3. Displaying the text with a contrasting background
        text_color = TEXT_COLOR_1
        fill_color = TEXT_BG_1  # This color will be behind your text
        alpha = 0  # Making it semi-transparent for contrast

        # Use configurable message and font size from MESSAGES config
        font = self.game.get_font_by_size(MESSAGES.TITLE_MESSAGE_FONT_SIZE)
        self.game.draw_text(surface, MESSAGES.TITLE_MESSAGE, text_color, self.game.GAME_W/2, self.game.GAME_H/1.05,
                          self.game.GAME_DIMENSIONS, fill_color=fill_color, fill_alpha=alpha, font=font)
        