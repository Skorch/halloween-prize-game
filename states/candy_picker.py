import pygame, os, glob, random
from time import time
from picker import get_new_image
from states.state import State
from states.winner import Winner
from colors import *
from asyncio.log import logger

PLAYDOUGH_FOLDER = "assets/playdough/*"
CANDY_FOLDER = "assets/candy/*"
FULL_SIZE_FOLDER = "assets/fullsize/*"

titles = {
    "playdough": "Playdough",
    "full_size": "Full Sized",
    "mini": "Mini Candy"
}

prize_probability = {
    "playdough": 0.3,
    "full_size": 0.1,
    "mini": 0.6
}

assets = {
    "playdough": glob.glob(PLAYDOUGH_FOLDER),
    "full_size": glob.glob(FULL_SIZE_FOLDER),
    "mini": glob.glob(CANDY_FOLDER)
}


STEP_RATE_CURVE = [1.0, 1.0, 0.75, 0.75, 0.75, 0.5, 0.5, 0.5, 0.5, 0.25, 0.25, 0.25, 0.25, 0.1]
MIN_FULL_SIZE_TICK = 4

class CandyPicker(State):

    def __init__(self, game) -> None:
        super().__init__(game)

        self.current_prize = None
        self.current_tick = 0

        self.get_new_image()
        self.last_image_update = time()

        
    def update(self, delta_time, actions):

        if actions["space"] or actions["button"]:
            # self.stop_sound()
            new_state = Winner(self.game, self.current_prize)
            self.game.reset_keys()
            new_state.enter_state()
        else:

            now = time()
            dt = self.next_image_time - now
            dt_beep = self.next_beep_time - now
            # print(f"candy picker update dt={dt}")
            logger.debug(f"dt_beep: {dt_beep}; dt: {dt}")    

            if dt <= 0:
                self.get_new_image()
                self.play_beep()
            elif dt_beep <= 0:
                self.stop_beep()
            # pass

    def render(self, surface):
        if self.current_prize:
            filename = self.current_prize["filename"]
            prize_text = self.current_prize["title"]
            image = pygame.image.load(filename)
            image = pygame.transform.scale(image, self.game.GAME_DIMENSIONS)    
            # pygame.draw.rect(WIN, BLACK, BORDER)
            # surface.set_alpha(1.0)
            surface.blit(image, (0, 0))

            fill_rect = (self.game.GAME_W, self.game.GAME_H/4)
            fill_position = (0, self.game.GAME_H*3/4)
            text_color = TEXT_COLOR_1
            fill_color = TEXT_BG_1
            fill_alpha = 200
            self.game.draw_text( surface, prize_text, text_color, self.game.GAME_W/2, self.game.GAME_H*7/8, fill_rect=fill_rect, fill_position=fill_position, fill_color=fill_color, fill_alpha=fill_alpha)            

    
    def pick_prize(self):

        prize_types = list(filter(lambda prize: prize != 'full_size' or self.current_tick >= MIN_FULL_SIZE_TICK, prize_probability.keys()))
        weights = map(lambda prize: prize_probability[prize],prize_types )

        pick = random.choices(prize_types, weights=weights)[0]
        print(f"pick: {pick}")

        prev_filename = self.current_prize["filename"] if self.current_prize else ''
        next_filename = None
        while not next_filename:

            file_choice = random.choice(assets[pick])
            if file_choice and file_choice != prev_filename:
                next_filename = file_choice

        return {
            "type": pick,
            "filename": next_filename,
            "title": titles[pick]
        }


    def get_step_rate(self):
        return STEP_RATE_CURVE[self.current_tick] if self.current_tick < len(STEP_RATE_CURVE) else STEP_RATE_CURVE[-1]

    def get_new_image(self):

        next_step = self.get_step_rate()
        self.next_image_time = time() + next_step
        self.next_beep_time = time() + next_step/2.0
        self.current_tick += 1
        print(f"next tick time: {self.next_image_time}")
        print(f"next beep time: {self.next_beep_time}")

        self.current_prize = self.pick_prize()

    def play_beep(self):
        self.game.beep_on()
        self.game.led_on()

    def stop_beep(self):
        self.game.beep_off()
        self.game.led_off()
