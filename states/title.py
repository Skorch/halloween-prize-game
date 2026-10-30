from states.state import State
from states.candy_picker import CandyPicker
from colors import *
from config import LIGHTS, MESSAGES
import pygame

class Title(State):
    def __init__(self, game) -> None:
        super().__init__(game)
        self.next_led_time = self.game.now() + 1
        self.video_start = self.game.now()
        self.shows_played = 0   # how many shows this title screen has started the soundtrack for
        self.game.lights.show(LIGHTS.TITLE, self.game.now())
        self.game.prizes.refresh()
        self.out_of_stock = self.game.prizes.out_of_stock()
        # The idle sound loops under the curtains and the show alike, until a press starts a spin
        if self.game.idle_sound is not None:
            self.game.audio.loop(self.game.idle_sound)

    def update(self, delta_time, actions):
        if actions["space"] or actions["button"]:
            # The stock is read again on every press, so a restock lets the next press play
            self.game.prizes.refresh()
            self.out_of_stock = self.game.prizes.out_of_stock()
        if (actions["space"] or actions["button"]) and not self.out_of_stock:
            if self.game.idle_sound is not None:
                self.game.audio.stop_loop()
            self.game.audio.stop_show()
            new_state = CandyPicker(self.game)
            new_state.enter_state()
        else:

            now = self.game.now()
            # The soundtrack starts on the frame the show starts: update runs just before render picks that frame
            if self.game.idle_video is not None:
                shows = self.game.idle_video.shows_started(now - self.video_start)
                if shows > self.shows_played:
                    self.shows_played = shows
                    if self.game.show_sound is not None:
                        self.game.audio.play_show(self.game.show_sound)
            dt_led = self.next_led_time - now
            # print(f"candy picker update dt={dt}")
            # logger.debug(f"dt_led: {dt_led}; dt: {dt}")    

            if dt_led <= 0:
                # logger.debug(f"turning LED off for {dt_led}")
                self.toggle_led()
                self.next_led_time = self.game.now() + 1

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
        # The idle video, when it loaded, fills the screen with no text over it
        if self.game.idle_video is not None:
            surface.blit(self.game.idle_video.frame_at(self.game.now() - self.video_start), (0, 0))
            self.render_out_of_stock(surface)
            return

        # 1. Displaying the background image, loaded once by the game
        surface.blit(self.game.title_background, (0, 0))

        # 2 & 3. Displaying the text with a contrasting background
        text_color = TEXT_COLOR_1
        fill_color = TEXT_BG_1  # This color will be behind your text
        alpha = 0  # Making it semi-transparent for contrast

        # Use configurable message and font size from MESSAGES config; out of candy, the button does nothing
        if not self.out_of_stock:
            font = self.game.get_font_by_size(MESSAGES.TITLE_MESSAGE_FONT_SIZE)
            self.game.draw_text(surface, MESSAGES.TITLE_MESSAGE, text_color, self.game.GAME_W/2, self.game.GAME_H/1.05,
                              self.game.GAME_DIMENSIONS, fill_color=fill_color, fill_alpha=alpha, font=font)
        self.render_out_of_stock(surface)

    def render_out_of_stock(self, surface):
        """With every prize gone, the title says so over the picture."""
        if not self.out_of_stock:
            return
        font = self.game.get_font_by_size(MESSAGES.OUT_OF_STOCK_MESSAGE_FONT_SIZE)
        self.game.draw_text(surface, MESSAGES.OUT_OF_STOCK_MESSAGE, TEXT_COLOR_1, self.game.GAME_W / 2,
                            self.game.GAME_H / 2, (self.game.GAME_W, self.game.GAME_H // 4),
                            fill_position=(0, self.game.GAME_H * 3 // 8), fill_color=TEXT_BG_1, fill_alpha=200,
                            font=font)
