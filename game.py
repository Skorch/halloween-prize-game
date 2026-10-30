from asyncio.log import logger
import logging
import os
import random
from time import time
import pygame

from audio import PygameAudio
from prizes import Prizes
from states.title import Title
from video import IdleVideo, load_clip
from config import GAME, HW, VISUAL, MESSAGES

BUTTONS_SPACE = "space"
BUTTONS_BUTTON = "button"
BUTTONS_ESCAPE = "escape"

BUTTON_PRESS_EVENT = pygame.USEREVENT + 1
BUTTON_RELEASE_EVENT = pygame.USEREVENT + 2
BUTTON_DELAY = HW.BUTTON_DELAY
RGB_COUNT = GAME.RGB_COUNT

class Game():
    def __init__(self, hardware, clock=time, rng=None, audio=None, fullscreen=GAME.FULLSCREEN,
                 idle_video_files=(VISUAL.IDLE_CURTAIN_FILE, VISUAL.IDLE_SHOW_FILE),
                 idle_sound_file=VISUAL.IDLE_SOUND_FILE, show_sound_file=VISUAL.IDLE_SHOW_SOUND_FILE) -> None:
        """
        Args:
            hardware: the button and LEDs: the pi2 module on the Pi, pi_dev2 on a Mac, a fake in tests
            clock: returns the time in seconds, like time.time
            rng: random source for prize picks; a new random.Random() if None
            audio: loads and plays sounds; PygameAudio() if None
            fullscreen: fill the display, or open a window of the game's size
            idle_video_files: (curtain clip, show clip) for the title screen; None shows the still background instead
            idle_sound_file: the sound the title screen loops; None leaves it silent
            show_sound_file: the sound that plays with each show on the title screen; None leaves the show silent
        """
        self.idle_video_files = idle_video_files
        self.idle_sound_file = idle_sound_file
        self.show_sound_file = show_sound_file
        self.clock = clock
        self.rng = rng if rng is not None else random.Random()
        self.fullscreen = fullscreen
        pygame.init()
        self.audio = audio if audio is not None else PygameAudio()
        self.prizes = Prizes(self.audio, self.rng)
        self.image_cache = {}
        display_info = pygame.display.Info()

        # Game canvas size (internal rendering resolution)
        self.GAME_W, self.GAME_H = GAME.GAME_WIDTH, GAME.GAME_HEIGHT
        self.GAME_DIMENSIONS = (self.GAME_W, self.GAME_H)

        # Screen size (actual display resolution)
        # Fullscreen asks for GAME.FULLSCREEN_MODE and takes the size the display gives back
        if self.fullscreen:
            self.screen = pygame.display.set_mode(GAME.FULLSCREEN_MODE, pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(self.GAME_DIMENSIONS)
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = self.screen.get_size()

        self.SCREEN_DIMENSIONS = (self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        print(f"Display: {display_info.current_w}x{display_info.current_h}, Game canvas: {self.GAME_W}x{self.GAME_H}, Screen: {self.SCREEN_WIDTH}x{self.SCREEN_HEIGHT}")
        self.hardware = hardware

        self.hardware.gpio_setup(self.button_press)
        # print("setting canvas")
        self.game_canvas = pygame.Surface(self.GAME_DIMENSIONS)
        # print("variables")

        self.running, self.playing = True, True
        self.button_pressed = False
        self.button_last_time = self.now()
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

    def now(self):
        return self.clock()

    def quit_game(self):
        self.hardware.clean()
        
    def button_press(self, ev):
        
        gpio_value = self.hardware.is_button_pressed()
        
        now = self.now()

        button_dt = now - self.button_last_time

        logger.debug(f"button_pressed: {self.button_pressed} GPIO: {gpio_value} / {self.hardware.button_state()} butonDT {button_dt}")
        
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
        frame_limiter = pygame.time.Clock()
        while self.playing:
            self.step()
            frame_limiter.tick(GAME.MAX_FPS)   # sleeps out the rest of the frame, so the Pi is not drawing flat out

    def step(self):
        """One frame: time, events, update, draw."""
        self.get_dt()
        self.get_events()
        self.update()
        self.render()

    def get_events(self) -> None:
        # print("get events")
        # logger.debug(self.hardware.button_state())
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

        # The display surface pygame shows now: on the Pi, the window events at startup make pygame swap it for a
        # new one, so the one set_mode gave cannot be kept. Scaling straight into it makes no new surface each frame
        screen = pygame.display.get_surface()
        # The picture fills GAME.SCREEN_SCALE of the screen's width and height, centred left to right and against
        # the top edge (Drew's frame around the screen covers the top), in a black mat
        w, h = screen.get_size()
        picture = pygame.Rect(0, 0, round(w * GAME.SCREEN_SCALE), round(h * GAME.SCREEN_SCALE))
        picture.midtop = (w // 2, 0)
        screen.fill((0, 0, 0))
        pygame.transform.scale(self.game_canvas, picture.size, screen.subsurface(picture))
        pygame.display.flip()   # once: display.update() with no arguments would send the same frame again

    def get_dt(self):
        # print("get_dt")
        now = self.now()
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
        self.audio.play(sound)
        
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

        # Countdown timer font, sized to its circle (about 60% of the diameter); loaded once here, not every frame
        timer_font_size = int(VISUAL.TIMER_CIRCLE_RADIUS * 1.2)
        try:
            if VISUAL.FONT_USE_TTF:
                self.font_timer = pygame.font.Font(VISUAL.FONT_TTF_PATH, timer_font_size)
            else:
                self.font_timer = pygame.font.SysFont(VISUAL.FONT_NAME, timer_font_size)
        except Exception:
            self.font_timer = pygame.font.SysFont(VISUAL.FONT_NAME, timer_font_size)

        # Title screen background, loaded once here because the title screen is made again after every round
        title_background = pygame.image.load(VISUAL.TITLE_BACKGROUND_FILE)
        self.title_background = pygame.transform.smoothscale(title_background, self.GAME_DIMENSIONS).convert()
        # Idle video: the curtain clip and the show; if either fails to load, the title shows the still background
        self.idle_video = None
        if self.idle_video_files:
            curtain_file, show_file = self.idle_video_files
            try:
                curtain = load_clip(curtain_file, self.GAME_DIMENSIONS)
                show = load_clip(show_file, self.GAME_DIMENSIONS)
                self.idle_video = IdleVideo(curtain, show, VISUAL.IDLE_WAIT_SECONDS)
                logger.info(f"Loaded idle video: {len(curtain.frames)} curtain frames, {len(show.frames)} show frames")
            except Exception as e:
                logger.error(f"Failed to load the idle video, falling back to the still background "
                             f"{VISUAL.TITLE_BACKGROUND_FILE}: {e}")
        # Idle sounds: the title loops the crackle and plays the soundtrack with each show; one that fails to
        # load is left out
        self.idle_sound = None
        if self.idle_sound_file:
            try:
                self.idle_sound = self.audio.load(self.idle_sound_file, VISUAL.IDLE_SOUND_VOLUME)
            except Exception as e:
                logger.error(f"Failed to load idle sound '{self.idle_sound_file}', the title will be silent: {e}")
        self.show_sound = None
        if self.show_sound_file:
            try:
                self.show_sound = self.audio.load(self.show_sound_file, VISUAL.IDLE_SHOW_SOUND_VOLUME)
            except Exception as e:
                logger.error(f"Failed to load show sound '{self.show_sound_file}', the show will be silent: {e}")

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
        self.hardware.start_beep(ticker_index)

    def beep_off(self):
        # logger.debug("beep off")
        self.hardware.stop_beep()

        
    def toggle_led(self):
        # logger.debug("led on")
        self.hardware.toggle_led()
    def led_on(self):
        # logger.debug("led on")
        self.hardware.led_on()

    def led_off(self):
        # logger.debug("led off")
        self.hardware.led_off()

    def set_rgb_leds(self, colors):
        # logger.debug("set rgb leds")
        self.hardware.set_rgb_leds(colors)
    
    def clear_rgb_leds(self):
        # logger.debug("clear rgb leds")
        self.hardware.clear_rgb_leds()
        
def main():
    """Main entry point for the Halloween Prize Game"""
    logging.basicConfig(level=logging.DEBUG)  # picker.py set this when it was imported

    # Dev mode: fake GPIO (spacebar is the button) in a window. HALLOWEEN_DEV=1 turns it on
    # without editing config.py, which the Pi reads as committed.
    dev_mode = GAME.DEV_MODE or os.environ.get("HALLOWEEN_DEV") == "1"
    if dev_mode:
        import pi_dev2 as hardware
        print("dev")
    else:
        import pi2 as hardware
        print("prod")

    g = Game(hardware, fullscreen=GAME.FULLSCREEN and not dev_mode)
    print("starting")
    while g.running:
        g.game_loop()

    g.quit_game()

if __name__ == '__main__':
    main()