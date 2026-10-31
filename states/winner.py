from states.state import State
import pygame
from colors import *
from config import LIGHTS, MESSAGES, PRIZES, VISUAL

RESET_DELAY = 5

class Winner(State):
    def __init__(self, game, prize) -> None:
        super().__init__(game)
        self.prize = prize
        self.win_time = self.game.now()
        self.has_rendered = False
        self.game.lights.show(LIGHTS.WINNER[prize["type"]], self.win_time)   # the strip's scene is the prize's
        self.game.prizes.take(prize["type"])
        # The beep stops at once; the prize sound comes after a gap of PRIZES.WIN_SOUND_DELAY, which a stop sound can open
        self.game.audio.stop_beep()
        if self.game.stop_sound is not None:
            self.game.play_sound(self.game.stop_sound)
        self.prize_sound_played = False


    def update(self, delta_time, actions):
        now = self.game.now()
        if not self.prize_sound_played and now - self.win_time >= PRIZES.WIN_SOUND_DELAY:
            self.game.play_sound(self.prize["sound"])
            self.prize_sound_played = True
        if actions["space"] or actions["button"]:
            self.game.reset_states()
        if now - self.win_time >= RESET_DELAY:
            self.game.reset_states()
        self.game.clear_rgb_leds()
        self.game.reset_keys()

    def render(self, surface):
        # surface.set_alpha(0.6)

        if not self.has_rendered:
            filename = self.prize["filename"]
            prize_text = self.prize["title"]

            # Scale the card to the whole canvas, as the spin does (candy_picker.py)
            image = pygame.transform.smoothscale(pygame.image.load(filename), self.game.GAME_DIMENSIONS)
            surface.blit(image, (0, 0))


            # Only show winner text if enabled in config
            if VISUAL.SHOW_WINNER_TEXT:
                text_color = TEXT_COLOR_1
                fill_color = TEXT_BG_1
                fill_alpha = VISUAL.WINNER_BG_OPACITY
                # Use configurable message with prize name
                message = MESSAGES.WINNER_MESSAGE.format(prize=self.prize['title'])
                fill_rect = (self.game.GAME_W, self.game.GAME_H)
                fill_position = (0, 0)
                # Use configurable font size from MESSAGES config
                font = self.game.get_font_by_size(MESSAGES.WINNER_MESSAGE_FONT_SIZE)
                # Calculate Y position based on configured fraction
                text_y = self.game.GAME_H * VISUAL.WINNER_TEXT_Y_FRACTION
                self.game.draw_text(surface, message, text_color, self.game.GAME_W/2, text_y,
                                  fill_rect=self.game.GAME_DIMENSIONS, fill_color=fill_color, fill_alpha=fill_alpha,
                                  font=font)

            self.has_rendered = True