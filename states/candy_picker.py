import pygame, os, glob, random
from time import time
from picker import get_new_image
from states.state import State
from states.winner import Winner
from colors import *
from config import MESSAGES, PRIZES
from asyncio.log import logger

# =============================================================================
# PRIZE SETUP - Built from config
# =============================================================================

# Build prize data structures from config
def build_prize_data():
    """Build prize structures from PRIZES config"""
    _titles = {}
    _sounds = {}
    _assets = {}
    _inventory = {}

    # Add mini candy
    _titles["mini"] = PRIZES.PRIZE_CATEGORIES["mini"]["title"]
    _sounds["mini"] = pygame.mixer.Sound(PRIZES.PRIZE_CATEGORIES["mini"]["sound_file"])
    _assets["mini"] = glob.glob(PRIZES.PRIZE_CATEGORIES["mini"]["folder"])
    _inventory["mini"] = PRIZES.MINI_CANDY_INVENTORY

    # Add playdough (if available)
    if PRIZES.PLAYDOUGH_INVENTORY > 0:
        _titles["playdough"] = PRIZES.PRIZE_CATEGORIES["playdough"]["title"]
        _sounds["playdough"] = pygame.mixer.Sound(PRIZES.PRIZE_CATEGORIES["playdough"]["sound_file"])
        _assets["playdough"] = glob.glob(PRIZES.PRIZE_CATEGORIES["playdough"]["folder"])
        _inventory["playdough"] = PRIZES.PLAYDOUGH_INVENTORY

    # Add big prize (use configured type: skull or full_size)
    big_prize_key = PRIZES.BIG_PRIZE_TYPE
    _titles["big_prize"] = PRIZES.PRIZE_CATEGORIES[big_prize_key]["title"]
    _sounds["big_prize"] = pygame.mixer.Sound(PRIZES.PRIZE_CATEGORIES[big_prize_key]["sound_file"])
    _assets["big_prize"] = glob.glob(PRIZES.PRIZE_CATEGORIES[big_prize_key]["folder"])
    _inventory["big_prize"] = PRIZES.BIG_PRIZE_INVENTORY

    # Beep sound
    _sounds["beep"] = pygame.mixer.Sound(PRIZES.BEEP_SOUND_FILE)

    return _titles, _sounds, _assets, _inventory

def calculate_probabilities(inventory):
    """Calculate probabilities based on remaining inventory"""
    if not PRIZES.USE_INVENTORY_PROBABILITIES:
        # Use fixed probabilities
        return PRIZES.FIXED_PROBABILITIES.copy()

    # Calculate inventory-based probabilities
    total = sum(inventory.values())
    if total == 0:
        # Fallback if somehow all inventory is zero
        logger.warning("All prize inventory is zero! Using equal probabilities")
        return {key: 1.0 / len(inventory) for key in inventory.keys()}

    # Probability proportional to inventory
    probabilities = {key: count / total for key, count in inventory.items()}
    logger.debug(f"Calculated probabilities from inventory: {probabilities}")
    return probabilities

# Initialize prize data
titles, sounds, assets, inventory = build_prize_data()
prize_probability = calculate_probabilities(inventory)

# Set sound volumes
for sound_key in sounds:
    sounds[sound_key].set_volume(PRIZES.DEFAULT_SOUND_VOLUME)

cached_assets = {}

# Game timing and LED settings
STEP_RATE_CURVE = [0.75, 0.75, 0.75, 0.5, 0.5, 0.5, 0.5, 0.25, 0.25, 0.25, 0.25, 0.2, 0.2, 0.2, 0.15, 0.15, 0.15, 0.15, 0.1]
MIN_FULL_SIZE_TICK = PRIZES.MIN_SPINS_FOR_BIG_PRIZE
GREEN = (0, 255, 0)
OFF = (0, 0, 0)
RGB_COLOR_SEQUENCE = [[GREEN, OFF, OFF, OFF], [OFF, GREEN, OFF, OFF], [OFF, OFF, GREEN, OFF], [OFF, OFF, OFF, GREEN]]
class CandyPicker(State):

    def __init__(self, game) -> None:
        super().__init__(game)

        self.current_prize = None
        self.current_tick = 0
        self.current_rgb_index = 0


        self.get_new_image()
        self.last_image_update = time()

        # Sound volumes are already set at module level
        
        
        
        
    def update(self, delta_time, actions):

        if actions["space"] or actions["button"]:
            # self.stop_sound()
            new_state = Winner(self.game, self.current_prize)
            self.game.reset_keys()
            new_state.enter_state()
        else:

            now = time()
            dt = self.next_image_time - now
            dt_rgb = self.next_rgb_time - now
            dt_led = self.next_led_time - now
            # print(f"candy picker update dt={dt}")
            # logger.debug(f"dt_led: {dt_led}; dt: {dt}")    

            if dt_rgb <= 0:
                self.update_rgb()
                self.next_rgb_time = time() + self.get_step_rate()/4.0
                
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
            # Use configurable font size from MESSAGES config
            font = self.game.get_font_by_size(MESSAGES.PICKER_MESSAGE_FONT_SIZE)
            self.game.draw_text(surface, prize_text, text_color, self.game.GAME_W/2, self.game.GAME_H*7/8,
                              fill_rect=fill_rect, fill_position=fill_position, fill_color=fill_color, fill_alpha=fill_alpha,
                              font=font)



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
        """Pick a prize based on configured probabilities and inventory"""

        # Filter out big_prize if minimum spins not reached
        prize_types = list(filter(
            lambda prize: prize != 'big_prize' or self.current_tick >= MIN_FULL_SIZE_TICK,
            prize_probability.keys()
        ))

        # Get weights for filtered prize types
        weights = [prize_probability[prize] for prize in prize_types]

        # Pick a prize type
        pick = random.choices(prize_types, weights=weights)[0]
        logger.info(f"Prize picked: {pick} (tick {self.current_tick})")

        # Select a random image file for this prize type
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
        self.next_rgb_time = time() + next_step/4.0
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

    #cycle through a sequence of 4 turning each LED on with a spooky green RGB color
    
    
    def update_rgb(self):
        #show the LED then increment the index looping back to 0 when it reaches 4
        colors = RGB_COLOR_SEQUENCE[self.current_rgb_index]
        self.game.set_rgb_leds(colors)
        self.current_rgb_index = (self.current_rgb_index + 1) % self.game.rgb_count
        # print(f"current_rgb_index: {self.current_rgb_index}")
        

        
        

