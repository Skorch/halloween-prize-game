from asyncio.log import logger
import os
from time import time
import pygame

from states.title import Title
from config import GAME, HW, VISUAL, MESSAGES

# Dev/Prod mode selection from config
if not GAME.DEV_MODE:
    import pi2 as pi
    print("prod")
else:
    import pi_dev2 as pi
    print("dev")

BUTTONS_SPACE = "space"
BUTTONS_BUTTON = "button"
BUTTONS_ESCAPE = "escape"

BUTTON_PRESS_EVENT = pygame.USEREVENT + 1
BUTTON_RELEASE_EVENT = pygame.USEREVENT + 2
BUTTON_DELAY = HW.BUTTON_DELAY
RGB_COUNT = GAME.RGB_COUNT

class Game():
    def __init__(self) -> None:
        pygame.init()
        display_info = pygame.display.Info()
        self.GAME_W, self.GAME_H = GAME.GAME_WIDTH, GAME.GAME_HEIGHT
        # display_info.current_w, display_info.current_h #int(480),int(270)
        self.GAME_DIMENSIONS = (self.GAME_W,self.GAME_H)
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = self.GAME_W, self.GAME_H #int(1920), int(1080)
        self.SCREEN_DIMENSIONS = (self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.pi = pi

        self.pi.gpio_setup(self.button_press)
        # print("setting canvas")
        self.game_canvas = pygame.Surface(self.GAME_DIMENSIONS)
        # print("setting screen")
        if GAME.FULLSCREEN:
            self.screen = pygame.display.set_mode(self.SCREEN_DIMENSIONS, pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(self.SCREEN_DIMENSIONS)
        # print("variables")

        self.running, self.playing = True, True
        self.button_pressed = False
        self.button_last_time = time()
        self.rgb_count = RGB_COUNT
        self.actions = {
            BUTTONS_SPACE: False, 
            BUTTONS_BUTTON: False,
            BUTTONS_ESCAPE: False
            }
        self.dt = 0
        self.prev_time = 0
        self.state_stack = []
        self.load_assets()
        self.load_states()

    def quit_game(self):
        self.pi.clean()
        
    def button_press(self, ev):
        
        gpio_value = self.pi.is_button_pressed()
        
        now = time()

        button_dt = now - self.button_last_time

        logger.debug(f"button_pressed: {self.button_pressed} GPIO: {gpio_value} / {self.pi.button_state()} butonDT {button_dt}")
        
        if not self.button_pressed and gpio_value and button_dt > BUTTON_DELAY:
            self.button_last_time = now
            logger.debug(f"button press event: GPIO: {gpio_value}")
            self.button_pressed = True
            event = pygame.event.Event(BUTTON_PRESS_EVENT)
            pygame.event.post(event)
        elif self.button_pressed and gpio_value:
            logger.debug(f"button release event: GPIO: {gpio_value}")
            self.button_pressed = False
            event = pygame.event.Event(BUTTON_RELEASE_EVENT)
            pygame.event.post(event)

            

    
    def game_loop(self):
        # print("starting loop")
        while self.playing:
            self.get_dt()
            self.get_events()
            self.update()
            self.render()
            # print("loop")

    def get_events(self) -> None:
        # print("get events")
        # logger.debug(self.pi.button_state())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_SPACE:
            #         self.actions[BUTTONS_SPACE] = True

            # is this the best way to detect?
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.actions[BUTTONS_SPACE] = True
            if event.type == BUTTON_PRESS_EVENT and not self.actions[BUTTONS_SPACE]:
                self.actions[BUTTONS_BUTTON] = True                
            if event.type == BUTTON_RELEASE_EVENT and self.actions[BUTTONS_SPACE]:
                self.actions[BUTTONS_BUTTON] = False                
            if event.type == pygame.KEYUP:
                logger.info(f"KEY UP {event.key}")
                if event.key == pygame.K_ESCAPE:
                    self.playing = False
                    self.running = False
                if event.key == pygame.K_SPACE:
                    self.actions[BUTTONS_SPACE] = False

    def update(self) -> None:
        self.state_stack[-1].update(self.dt, self.actions)

    def render(self) -> None:
        # print("render")
        self.state_stack[-1].render(self.game_canvas)

        self.screen.blit(pygame.transform.scale(self.game_canvas, self.SCREEN_DIMENSIONS), (0, 0))
        pygame.display.flip()
        pygame.display.update()

    def get_dt(self):
        # print("get_dt")
        now = time()
        self.dt = now - self.prev_time
        self.prev_time = now

    def draw_text(self, surface, text, color, x, y, fill_rect = None, fill_position = (0,0), fill_color=(255,255,255), fill_alpha=255, font=None):
        """
        Draw text on the surface with optional background fill.

        Args:
            font: Optional pygame font. If None, uses default font. Can be one of:
                  self.font_small, self.font_medium, self.font_large, self.font_xlarge
        """
        if fill_rect:
            bg = pygame.Surface(fill_rect)
            bg.set_alpha(fill_alpha)
            bg.fill(fill_color)
            surface.blit(bg, fill_position)

        # Use provided font or fall back to default
        active_font = font if font is not None else self.font
        text_surface = active_font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        # text_rect.set_alpha(0.6)

        surface.blit(text_surface, text_rect)

    def play_sound(self, sound):
        pygame.mixer.Sound.play(sound)
        pygame.mixer.music.stop()
        
    def load_assets(self):
        # print("loading assets")
        self.assets_dir = os.path.join("assets")

        # Load multiple font sizes from config
        # Check if using TTF file or system font
        if VISUAL.FONT_USE_TTF:
            # Load custom TTF font file
            try:
                self.font_small = pygame.font.Font(VISUAL.FONT_TTF_PATH, VISUAL.FONT_SIZE_SMALL)
                self.font_medium = pygame.font.Font(VISUAL.FONT_TTF_PATH, VISUAL.FONT_SIZE_MEDIUM)
                self.font_large = pygame.font.Font(VISUAL.FONT_TTF_PATH, VISUAL.FONT_SIZE_LARGE)
                self.font_xlarge = pygame.font.Font(VISUAL.FONT_TTF_PATH, VISUAL.FONT_SIZE_XLARGE)
                logger.info(f"Loaded custom font: {VISUAL.FONT_TTF_PATH}")
            except Exception as e:
                logger.error(f"Failed to load TTF font '{VISUAL.FONT_TTF_PATH}': {e}")
                logger.info(f"Falling back to system font: {VISUAL.FONT_NAME}")
                # Fall back to system font
                self.font_small = pygame.font.SysFont(VISUAL.FONT_NAME, VISUAL.FONT_SIZE_SMALL)
                self.font_medium = pygame.font.SysFont(VISUAL.FONT_NAME, VISUAL.FONT_SIZE_MEDIUM)
                self.font_large = pygame.font.SysFont(VISUAL.FONT_NAME, VISUAL.FONT_SIZE_LARGE)
                self.font_xlarge = pygame.font.SysFont(VISUAL.FONT_NAME, VISUAL.FONT_SIZE_XLARGE)
        else:
            # Use system font
            self.font_small = pygame.font.SysFont(VISUAL.FONT_NAME, VISUAL.FONT_SIZE_SMALL)
            self.font_medium = pygame.font.SysFont(VISUAL.FONT_NAME, VISUAL.FONT_SIZE_MEDIUM)
            self.font_large = pygame.font.SysFont(VISUAL.FONT_NAME, VISUAL.FONT_SIZE_LARGE)
            self.font_xlarge = pygame.font.SysFont(VISUAL.FONT_NAME, VISUAL.FONT_SIZE_XLARGE)

        # Default font for backward compatibility
        self.font = self.font_small

        # Create a mapping of font sizes to font objects for easy lookup
        self.font_size_map = {
            VISUAL.FONT_SIZE_SMALL: self.font_small,
            VISUAL.FONT_SIZE_MEDIUM: self.font_medium,
            VISUAL.FONT_SIZE_LARGE: self.font_large,
            VISUAL.FONT_SIZE_XLARGE: self.font_xlarge,
        }

    def get_font_by_size(self, font_size):
        """Get a font object by its configured size value"""
        return self.font_size_map.get(font_size, self.font)


    def reset_states(self):
        self.state_stack.clear()
        self.reset_keys()
        self.load_states()
        
        
    def load_states(self):
        self.title_screen = Title(self)
        self.state_stack.append(self.title_screen)

    def reset_keys(self):
        # logger.debug("resetting actions")
        for action in self.actions:
            self.actions[action] = False


    def beep_on(self, ticker_index):
        # logger.debug("beep on")
        self.pi.start_beep(ticker_index)

    def beep_off(self):
        # logger.debug("beep off")
        self.pi.stop_beep()

        
    def toggle_led(self):
        # logger.debug("led on")
        self.pi.toggle_led()
    def led_on(self):
        # logger.debug("led on")
        self.pi.led_on()

    def led_off(self):
        # logger.debug("led off")
        self.pi.led_off()

    def set_rgb_leds(self, colors):
        # logger.debug("set rgb leds")
        self.pi.set_rgb_leds(colors)
    
    def clear_rgb_leds(self):
        # logger.debug("clear rgb leds")
        self.pi.clear_rgb_leds()
        
if __name__ == '__main__':
    g = Game()
    print("starting")
    while g.running:
        g.game_loop()
        
    g.quit_game()