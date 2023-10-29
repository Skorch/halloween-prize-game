from states.state import State
from states.candy_picker import CandyPicker
from colors import *
import pygame

class Title(State):
    def __init__(self, game) -> None:
        super().__init__(game)

    def update(self, delta_time, actions):
        if actions["space"] or actions["button"]:
            new_state = CandyPicker(self.game)
            new_state.enter_state()
        self.game.reset_keys()

    def render1(self, surface):
        text_color = TEXT_COLOR_1
        fill_color = TEXT_BG_1
        # fill_color = (255, 255, 255)
        alpha = 255
        self.game.draw_text( surface, "Press the BIG BUTTON to start!", text_color, self.game.GAME_W/2, self.game.GAME_H/2, self.game.GAME_DIMENSIONS, fill_color=fill_color, fill_alpha=alpha )
        
            
    def render(self, surface):
        # 1. Loading and displaying the background image
        bg_image_filename = "assets/background1.png"  # Update this with your image's path
        bg_image = pygame.image.load(bg_image_filename)
        bg_image = pygame.transform.scale(bg_image, self.game.GAME_DIMENSIONS)
        surface.blit(bg_image, (0, 0))

        # 2 & 3. Displaying the text with a contrasting background
        text_color = TEXT_COLOR_1
        fill_color = TEXT_BG_1  # This color will be behind your text
        alpha = 150  # Making it semi-transparent for contrast

        text_msg = "Press the BIG BUTTON to start!"

        # Assuming your draw_text method creates a filled rectangle behind the text if fill_color and fill_alpha are provided
        self.game.draw_text(surface, text_msg, text_color, self.game.GAME_W/2, self.game.GAME_H/2, self.game.GAME_DIMENSIONS, fill_color=fill_color, fill_alpha=alpha)
        