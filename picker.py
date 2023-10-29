dev = True
if not dev:
    import pi
else:
    import pi_dev as pi

import pygame
import glob
import random
import logging

logging.basicConfig(level=logging.DEBUG if dev else logging.INFO)
logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)

pygame.font.init()
pygame.mixer.init()

FPS = 20 if dev else 60
TICK_RATE = 10
STEP_RATE_CURVE = [4, 4, 2, 0, 0, 2, 0, 2, 2, 0, 2]
MIN_TICK = 2

CANDY_FOLDER = "assets/candy/*"
FULL_SIZE_FOLDER = "assets/skull/*"

START_TEXT = "PRESS BUTTON TO START"

WINNER_FONT = pygame.font.SysFont('comicsans', 100)
WIDTH, HEIGHT = 1000, 666
WIN = pygame.display.set_mode((WIDTH, HEIGHT) , pygame.FULLSCREEN)
# WIN = pygame.display.set_mode((WIDTH, HEIGHT) )
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

pygame.display.set_caption("First Game!")


candy_assets = glob.glob(CANDY_FOLDER)
fullsize_assets = glob.glob(FULL_SIZE_FOLDER)

images = []
is_big_button_pressed = False
is_starting = False
is_playing = False

def setup_images():
    global images

    images = candy_assets

    if pi.is_switch_on():
        images += fullsize_assets

    logger.debug(f"images: {images}")

def button_press(ev):
    global is_big_button_pressed
    logger.debug(f"button pressed: {ev}")
    is_big_button_pressed = True

def show_image(filename):
    logger.debug(f"filename: {filename}")
    image = pygame.image.load(filename)
    image = pygame.transform.scale(image, (WIDTH, HEIGHT))    
    # pygame.draw.rect(WIN, BLACK, BORDER)
    WIN.blit(image, (0, 0))


def get_new_image(prev_filename):

    next_filename = random.choice(images)
    return next_filename if next_filename != prev_filename else get_new_image(prev_filename)

def check_big_button():

    global is_big_button_pressed, is_starting

    if dev and not is_starting:

        keys_pressed = pygame.key.get_pressed()

    
        is_big_button_pressed = keys_pressed[pygame.K_SPACE]

        if is_big_button_pressed:   
            logger.info(f"space {keys_pressed[pygame.K_SPACE]}")

    return is_big_button_pressed

def reset_big_button():
    global is_big_button_pressed
    is_big_button_pressed = False


def clear_screen():
    # WIN.blit(BACKGROUND, (0,0))
    WIN.fill(BLACK)

def try_show_image(filename):
    can_show_image = True
    # filename = None

    if can_show_image:
        filename = get_new_image(filename)
        show_image(filename)
        logger.debug(f"showing {filename}")
    else:
        logger.debug("can't show image")

    return filename

def try_button_light():
    can_show_light = False

    if can_show_light:
        light = pygame.Rect(10, 10, 100, 100)
        pygame.draw.rect(WIN, RED, light)
        logger.debug("draw light")

    return can_show_light  

def end_game(text, winning):

    if text:
        draw_text = WINNER_FONT.render(text, 1, WHITE)
        WIN.blit(draw_text, (WIDTH/2 - draw_text.get_width() /
                            2, HEIGHT/2 - draw_text.get_height()/2))
    if winning:
        pi.play_winner() 
    else:
        pi.play_loser()

    pygame.display.update()
    pygame.time.delay(5000)

def reset_game():
    global is_big_button_pressed, is_playing

    is_big_button_pressed = False
    is_playing = False
    clear_screen()
    draw_text = WINNER_FONT.render(START_TEXT, 1, WHITE)
    WIN.blit(draw_text, (WIDTH/2 - draw_text.get_width() /
                         2, HEIGHT/2 - draw_text.get_height()/2))

    pygame.display.update()

def start_game():
    global is_big_button_pressed, is_playing

    logger.debug(f"starting game")
    is_big_button_pressed = False
    is_playing = True

    setup_images()


def exit():
    pi.clean()
    run = False
    pygame.quit()

def main():

    global is_big_button_pressed, is_starting

    pi.gpio_setup(button_press)
    reset_game()

    clock = pygame.time.Clock()
    run = True
    filename = None

    step_index = 0
    current_tick = 0
    current_tick_rate = TICK_RATE

    while run:
        logger.debug(f"tick {current_tick}")  
        logger.debug(f"clofk fps {FPS}")  
        clock.tick(FPS)

        current_tick += 1


        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                exit()
                return

        if not is_playing:
            logger.debug("not is_playing")
            if check_big_button():
                is_starting = True
                start_game()
                reset_big_button()
                pygame.time.delay(1000)
                current_tick = 0
        else:
            is_starting = False


        global is_big_button_pressed

        if is_playing and check_big_button():
            logger.debug("is_playing and check_big_button")
            
            end_game(None, filename in fullsize_assets)

            current_tick_rate = TICK_RATE
            current_tick = 0
            reset_game()


        # toggle LED twice as fast
        if current_tick % (current_tick_rate/2) == 0:
            logger.debug("double time LED")
            is_on = pi.toggle_led()
            if is_playing:
                pi.play_beep(is_on, current_tick_rate)

        if is_playing and current_tick % current_tick_rate == 0:
            is_starting = False
            logger.debug("screen update")

            current_tick = 0
            rate = STEP_RATE_CURVE[step_index]
            step_index = min(step_index + 1, len(STEP_RATE_CURVE) - 1)
            current_tick_rate = max( current_tick_rate - rate, MIN_TICK)

            clear_screen()        
            filename = try_show_image(filename)
            

        pygame.display.update()


if __name__ == "__main__":
    main()