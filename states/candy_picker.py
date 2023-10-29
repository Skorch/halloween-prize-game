import pygame, os, glob, random
from time import time
from picker import get_new_image
from states.state import State
from states.winner import Winner
from colors import *
from asyncio.log import logger

PLAYDOUGH_FOLDER = "assets/playdough/*"
CANDY_FOLDER = "assets/candy/*"
FULL_SIZE_FOLDER = "assets/skull/*"

default_volume = 0.05

titles = {
    "playdough": "Playdough",
    "full_size": "3d Skull",
    "mini": "Mini Candy"
}

sounds = {
    "playdough": pygame.mixer.Sound("sounds/small_prize.wav"),
    "full_size": pygame.mixer.Sound("sounds/big_prize.wav"),
    "mini": pygame.mixer.Sound("sounds/small_prize.wav"),
    "beep": pygame.mixer.Sound("sounds/beep.wav")
}

prize_probability = {
    "playdough": 0.3,
    "full_size": 0.3,
    "mini": 0.4
}

assets = {
    "playdough": glob.glob(PLAYDOUGH_FOLDER),
    "full_size": glob.glob(FULL_SIZE_FOLDER),
    "mini": glob.glob(CANDY_FOLDER)
}

cached_assets = {}



STEP_RATE_CURVE = [0.75, 0.75, 0.75, 0.5, 0.5, 0.5, 0.5, 0.25, 0.25, 0.25, 0.25, 0.2, 0.2, 0.2, 0.15, 0.15, 0.15, 0.15, 0.1]
MIN_FULL_SIZE_TICK = 5

class CandyPicker(State):

    def __init__(self, game) -> None:
        super().__init__(game)

        self.current_prize = None
        self.current_tick = 0

        self.get_new_image()
        self.last_image_update = time()

        for sound_key in sounds:
            sounds[sound_key].set_volume(default_volume)
        
        
        
        
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
            dt_led = self.next_led_time - now
            # print(f"candy picker update dt={dt}")
            # logger.debug(f"dt_led: {dt_led}; dt: {dt}")    

            if dt <= 0:
                self.get_new_image()
                # logger.debug(f"turning LED off for {dt_led}")
                self.led_on()
                self.play_beep()
            elif dt_led <=0:
                # logger.debug(f"turning LED off after {dt_led}")
                self.led_off()
            
            # pass
                
    def render(self, surface, limit_vertical=False):
        global cached_assets
        # Clearing the screen by filling with a background color
        BLACK = (0, 0, 0)  # RGB value for black
        surface.fill(BLACK)

        if self.current_prize:
            filename = self.current_prize["filename"]
            prize_text = self.current_prize["title"]

            if filename in cached_assets:
                image = cached_assets[filename]
            else:
                image = pygame.image.load(filename)
                image_width, image_height = image.get_size()
                aspect_ratio = image_width / image_height

                if limit_vertical:
                    # Scale based on the game's height
                    new_height = self.game.GAME_H
                    new_width = int(new_height * aspect_ratio)
                else:
                    # Scale based on the game's width
                    new_width = self.game.GAME_W
                    new_height = int(new_width / aspect_ratio)

                
                image = pygame.transform.smoothscale(image, (new_width, new_height))

                # Clipping (for width only)
                if new_width > self.game.GAME_W:
                    x_offset = (new_width - self.game.GAME_W) // 2
                    image = image.subsurface(pygame.Rect(x_offset, 0, self.game.GAME_W, new_height))

                cached_assets[filename] = image
            # Blit the image and text overlay
            surface.blit(image, (0, 0))

            fill_rect = (self.game.GAME_W, self.game.GAME_H/4)
            fill_position = (0, self.game.GAME_H*3/4)
            text_color = TEXT_COLOR_1
            fill_color = TEXT_BG_1
            fill_alpha = 200
            self.game.draw_text(surface, prize_text, text_color, self.game.GAME_W/2, self.game.GAME_H*7/8, fill_rect=fill_rect, fill_position=fill_position, fill_color=fill_color, fill_alpha=fill_alpha)



    def render1(self, surface):
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
            "title": titles[pick],
            "sound": sounds[pick]
        }


    def get_step_rate(self):
        return STEP_RATE_CURVE[self.current_tick] if self.current_tick < len(STEP_RATE_CURVE) else STEP_RATE_CURVE[-1]

    def get_new_image(self):

        next_step = self.get_step_rate()
        self.next_image_time = time() + next_step
        self.next_beep_time = time() + next_step/2.0
        self.next_led_time = time() + next_step/2.0
        self.current_tick += 1
        # print(f"next tick time: {self.next_image_time}")
        # print(f"next beep time: {self.next_beep_time}")

        self.current_prize = self.pick_prize()


    def led_on(self):
        self.game.led_on()

    def led_off(self):
        self.game.led_off()
        
    def play_beep(self):
        beep = sounds["beep"]
        self.game.play_sound(beep)

        
        # self.game.beep_on(self.current_tick)
        # self.game.led_on()

