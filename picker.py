import pygame
import os
import glob
import random
pygame.font.init()
pygame.mixer.init()

FPS = 3
STEP_RATE = 10
MAX_FPS = 15

WINNER_FONT = pygame.font.SysFont('comicsans', 100)
WIDTH, HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

pygame.display.set_caption("First Game!")


images = glob.glob("assets/candy/*.png")
winner_filename = images[0]
BACKGROUND = pygame.image.load("assets/background.jpeg")


def show_image(filename):
    print(f"filename: {filename}")
    image = pygame.image.load(filename)
    
    # pygame.draw.rect(WIN, BLACK, BORDER)
    WIN.blit(image, (0, 0))


def get_new_image(prev_filename):

    next_filename = random.choice(images)
    return next_filename if next_filename != prev_filename else get_new_image(prev_filename)

def check_big_button():
    
    keys_pressed = pygame.key.get_pressed()
    
    return keys_pressed[pygame.K_SPACE]

def clear_screen():
    # WIN.blit(BACKGROUND, (0,0))
    WIN.fill(BLACK)

def try_show_image(filename):
    can_show_image = True
    # filename = None

    if can_show_image:
        filename = get_new_image(filename)
        show_image(filename)

    return filename

def try_button_light():
    can_show_light = False

    if can_show_light:
        light = pygame.Rect(10, 10, 100, 100)
        pygame.draw.rect(WIN, RED, light)
        print("draw light")

    return can_show_light  

def winner(text):

    draw_text = WINNER_FONT.render(text, 1, WHITE)
    WIN.blit(draw_text, (WIDTH/2 - draw_text.get_width() /
                         2, HEIGHT/2 - draw_text.get_height()/2))
    pygame.display.update()
    pygame.time.delay(5000)

def loser(text):

    draw_text = WINNER_FONT.render(text, 1, WHITE)
    WIN.blit(draw_text, (WIDTH/2 - draw_text.get_width() /
                         2, HEIGHT/2 - draw_text.get_height()/2))
    pygame.display.update()
    pygame.time.delay(5000)

def next_fps(current_fps, increment):

    print(f"(current, next): {current_fps}, {increment}")

    next_increase = increment % STEP_RATE
    step = 1 if next_increase == 0 else 0
    current_fps = min( current_fps + step, MAX_FPS)

    return current_fps, increment+1

def main():

    clock = pygame.time.Clock()
    run = True
    filename = None

    current_fps = FPS
    next_increase = 0

    while run:
        print("tick")
        clock.tick(current_fps)
        current_fps, next_increase = next_fps(current_fps, next_increase)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                return

        clear_screen()        
        is_big_button_pressed = check_big_button()
        filename = try_show_image(filename)
        is_phase_1 = (filename)
        is_phase_2 = try_button_light()        

        if is_big_button_pressed:
            clear_screen()
            if filename == winner_filename and is_phase_2:
                winner("FULL SIZE CANDY BAR!")
            else:
                loser("ITTY BITTY!")
            
            current_fps = FPS
            next_increase = 0

        pygame.display.update()


if __name__ == "__main__":
    main()