from asyncio.log import logger
import os
import time
import pygame

from states.title import Title

dev = True
if not dev:
    import pi2 as pi
else:
    import pi_dev2 as pi

BUTTONS_SPACE = "space"
BUTTONS_BUTTON = "button"
BUTTONS_ESCAPE = "escape"

class Game():
    def __init__(self) -> None:
        pygame.init()
        self.GAME_W, self.GAME_H = 480,270
        self.GAME_DIMENSIONS = (self.GAME_W,self.GAME_H)
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = 960, 540
        self.SCREEN_DIMENSIONS = (self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.pi = pi

        # print("setting canvas")
        self.game_canvas = pygame.Surface(self.GAME_DIMENSIONS)
        # print("setting screen")
        self.screen = pygame.display.set_mode(self.SCREEN_DIMENSIONS)
        # print("variables")

        self.running, self.playing = True, True
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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_SPACE:
            #         self.actions[BUTTONS_SPACE] = True

            # is this the best way to detect?
            if self.pi.is_button_pressed(event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                self.actions[BUTTONS_SPACE] = True

            if event.type == pygame.KEYUP:
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
        now = time.time()
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
        for action in self.actions:
            self.actions[action] = False

    def beep_on(self):
        logger.debug("beep on")

    def beep_off(self):
        logger.debug("beep off")

    def led_on(self):
        logger.debug("led on")

    def led_off(self):
        logger.debug("led off")

if __name__ == '__main__':
    g = Game()
    print("starting")
    while g.running:
        g.game_loop()