from asyncio.log import logger
import os
from time import time
import pygame

from states.title import Title

dev = True
if not dev:
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
BUTTON_DELAY = 1.3

class Game():
    def __init__(self) -> None:
        pygame.init()
        display_info = pygame.display.Info()
        self.GAME_W, self.GAME_H = 1024,768 
        # display_info.current_w, display_info.current_h #int(480),int(270)
        self.GAME_DIMENSIONS = (self.GAME_W,self.GAME_H)
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = self.GAME_W, self.GAME_H #int(1920), int(1080)
        self.SCREEN_DIMENSIONS = (self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.pi = pi
        
        self.pi.gpio_setup(self.button_press)
        # print("setting canvas")
        self.game_canvas = pygame.Surface(self.GAME_DIMENSIONS)
        # print("setting screen")
        # self.screen = pygame.display.set_mode(self.SCREEN_DIMENSIONS)
        self.screen = pygame.display.set_mode(self.SCREEN_DIMENSIONS, pygame.FULLSCREEN)
        # print("variables")

        self.running, self.playing = True, True
        self.button_pressed = False
        self.button_last_time = time()
        
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

    def draw_text(self, surface, text, color, x, y, fill_rect = None, fill_position = (0,0), fill_color=(255,255,255), fill_alpha=255):
        if fill_rect:
            bg = pygame.Surface(fill_rect)
            bg.set_alpha(fill_alpha)
            bg.fill(fill_color)
            surface.blit(bg, fill_position)

        text_surface = self.font.render(text, True, color)
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
        self.font = pygame.font.SysFont('comicsans', 28)


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

if __name__ == '__main__':
    g = Game()
    print("starting")
    while g.running:
        g.game_loop()
        
    g.quit_game()