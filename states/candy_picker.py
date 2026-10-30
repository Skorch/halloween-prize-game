import pygame, math
from states.state import State
from states.winner import Winner
from colors import *
from config import LIGHTS, MESSAGES, VISUAL
from asyncio.log import logger

# Game timing and LED settings
STEP_RATE_CURVE = [0.75, 0.75, 0.75, 0.5, 0.5, 0.5, 0.5, 0.25, 0.25, 0.25, 0.25, 0.2, 0.2, 0.2, 0.15, 0.15, 0.15, 0.15, 0.1]
GREEN = (0, 255, 0)
OFF = (0, 0, 0)
RGB_COLOR_SEQUENCE = [[GREEN, OFF, OFF, OFF], [OFF, GREEN, OFF, OFF], [OFF, OFF, GREEN, OFF], [OFF, OFF, OFF, GREEN]]
class CandyPicker(State):

    def __init__(self, game) -> None:
        super().__init__(game)

        self.current_prize = None
        self.current_tick = 0
        self.current_rgb_index = 0

        # Timer initialization
        if VISUAL.TIMER_ENABLED:
            self.timer_start_time = self.game.now()
            self.timer_remaining = VISUAL.TIMER_START_SECONDS
            print(f"[TIMER] Initialized: duration={VISUAL.TIMER_START_SECONDS}s, show_at={VISUAL.TIMER_SHOW_AT_SECONDS}s")
            logger.info(f"Timer initialized: start_time={self.timer_start_time}, duration={VISUAL.TIMER_START_SECONDS}s")
        else:
            self.timer_start_time = None
            self.timer_remaining = None

        self.get_new_image()
        self.last_image_update = self.game.now()

        # Trigger LED and beep for the first image (subsequent images triggered in update())
        self.led_on()
        self.play_beep()

        # Sound volumes are already set at module level
        
        
        
        
    def update(self, delta_time, actions):
        # Update timer if enabled
        timer_expired = False
        if VISUAL.TIMER_ENABLED and self.timer_start_time is not None:
            elapsed = self.game.now() - self.timer_start_time
            self.timer_remaining = VISUAL.TIMER_START_SECONDS - elapsed

            if self.timer_remaining <= 0:
                self.timer_remaining = 0
                timer_expired = True
                print(f"[TIMER] EXPIRED! Auto-triggering winner screen")
                logger.info("Timer expired! Auto-triggering winner screen")
            elif self.timer_remaining <= VISUAL.TIMER_SHOW_AT_SECONDS:
                # Only print every second to avoid spam
                if int(self.timer_remaining) != getattr(self, '_last_printed_second', -1):
                    self._last_printed_second = int(self.timer_remaining)
                    print(f"[TIMER] Visible: {self.timer_remaining:.1f}s remaining")
                logger.debug(f"Timer visible: {self.timer_remaining:.1f}s remaining")

        self.set_light_boost()

        if actions["space"] or actions["button"] or timer_expired:
            # self.stop_sound()
            new_state = Winner(self.game, self.current_prize)
            self.game.reset_keys()
            new_state.enter_state()
        else:

            now = self.game.now()
            dt = self.next_image_time - now
            dt_rgb = self.next_rgb_time - now
            dt_led = self.next_led_time - now
            # print(f"candy picker update dt={dt}")
            # logger.debug(f"dt_led: {dt_led}; dt: {dt}")

            if dt_rgb <= 0:
                self.update_rgb()
                self.next_rgb_time = self.game.now() + self.get_step_rate()/4.0

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
        cached_assets = self.game.image_cache
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

            # Only show text if enabled in config
            if VISUAL.SHOW_PRIZE_TEXT:
                # Configure text background from VISUAL config
                text_color = TEXT_COLOR_1
                font = self.game.get_font_by_size(MESSAGES.PICKER_MESSAGE_FONT_SIZE)

                if VISUAL.SHOW_TEXT_BACKGROUND:
                    # Background is enabled - use configured opacity and height
                    fill_rect = (self.game.GAME_W, self.game.GAME_H * VISUAL.TEXT_BG_HEIGHT_FRACTION)
                    fill_position = (0, self.game.GAME_H * (1 - VISUAL.TEXT_BG_HEIGHT_FRACTION))
                    fill_color = VISUAL.TEXT_BG_1
                    fill_alpha = VISUAL.TEXT_BG_OPACITY
                    self.game.draw_text(surface, prize_text, text_color, self.game.GAME_W/2, self.game.GAME_H*7/8,
                                      fill_rect=fill_rect, fill_position=fill_position, fill_color=fill_color, fill_alpha=fill_alpha,
                                      font=font)
                else:
                    # No background - just draw text
                    self.game.draw_text(surface, prize_text, text_color, self.game.GAME_W/2, self.game.GAME_H*7/8,
                                      font=font)

        # Draw countdown timer if enabled and visible
        if VISUAL.TIMER_ENABLED and self.timer_remaining is not None:
            if self.timer_remaining <= VISUAL.TIMER_SHOW_AT_SECONDS:
                self.draw_timer(surface)



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

    
    def set_light_boost(self):
        """The strip brightens as the countdown runs down."""
        if self.timer_remaining is not None and self.timer_remaining <= VISUAL.TIMER_SHOW_AT_SECONDS:
            self.game.lights.boost = 1 - self.timer_remaining / VISUAL.TIMER_SHOW_AT_SECONDS

    def pick_prize(self):
        """Pick a prize based on configured probabilities and inventory"""
        prev_filename = self.current_prize["filename"] if self.current_prize else ''
        return self.game.prizes.pick(self.current_tick, prev_filename)


    def get_step_rate(self):
        return STEP_RATE_CURVE[self.current_tick] if self.current_tick < len(STEP_RATE_CURVE) else STEP_RATE_CURVE[-1]

    def get_new_image(self):

        next_step = self.get_step_rate()
        now = self.game.now()
        self.next_rgb_time = now + next_step/4.0
        self.next_image_time = now + next_step
        self.next_beep_time = now + next_step/2.0
        self.next_led_time = now + next_step/2.0
        self.current_tick += 1
        # print(f"next tick time: {self.next_image_time}")
        # print(f"next beep time: {self.next_beep_time}")

        self.current_prize = self.pick_prize()


    def led_on(self):
        self.game.led_on()

    def led_off(self):
        self.game.led_off()
        
    def play_beep(self):
        beep = self.game.prizes.sounds["beep"]
        self.game.audio.play_beep(beep)
        self.beat_lights()

    def beat_lights(self):
        """The strip thumps on every beep, for as long as this card shows: twice while the cards are slow, one flash
        once a card lasts less than LIGHTS.SPIN_FAST_SECONDS."""
        now = self.game.now()
        seconds = self.next_image_time - now
        scene = LIGHTS.SPIN if seconds >= LIGHTS.SPIN_FAST_SECONDS else LIGHTS.SPIN_FAST
        self.game.lights.beat(scene, now, seconds)

    #cycle through a sequence of 4 turning each LED on with a spooky green RGB color
    
    
    def update_rgb(self):
        #show the LED then increment the index looping back to 0 when it reaches 4
        colors = RGB_COLOR_SEQUENCE[self.current_rgb_index]
        self.game.set_rgb_leds(colors)
        self.current_rgb_index = (self.current_rgb_index + 1) % self.game.rgb_count
        # print(f"current_rgb_index: {self.current_rgb_index}")

    def draw_timer(self, surface):
        """Draw countdown timer as text in a circle"""
        # Calculate seconds remaining (round up to show whole seconds)
        seconds = math.ceil(self.timer_remaining)

        # Create a surface for the circle with alpha channel
        circle_surface = pygame.Surface((VISUAL.TIMER_CIRCLE_RADIUS * 2, VISUAL.TIMER_CIRCLE_RADIUS * 2), pygame.SRCALPHA)

        # Draw filled circle
        pygame.draw.circle(
            circle_surface,
            (*VISUAL.TIMER_CIRCLE_COLOR, VISUAL.TIMER_CIRCLE_OPACITY),
            (VISUAL.TIMER_CIRCLE_RADIUS, VISUAL.TIMER_CIRCLE_RADIUS),
            VISUAL.TIMER_CIRCLE_RADIUS
        )

        # Render the countdown number, in the font the game loaded once for it
        timer_text = self.game.font_timer.render(str(seconds), True, VISUAL.TIMER_TEXT_COLOR)
        text_rect = timer_text.get_rect(center=(VISUAL.TIMER_CIRCLE_RADIUS, VISUAL.TIMER_CIRCLE_RADIUS))

        # Draw text on circle surface
        circle_surface.blit(timer_text, text_rect)

        # Position the circle on the main surface (top-left corner by default)
        circle_pos = (
            VISUAL.TIMER_POSITION_X - VISUAL.TIMER_CIRCLE_RADIUS,
            VISUAL.TIMER_POSITION_Y - VISUAL.TIMER_CIRCLE_RADIUS
        )

        # Blit the circle surface to the main surface
        surface.blit(circle_surface, circle_pos)




