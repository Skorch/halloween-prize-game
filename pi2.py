#!/usr/bin/env python3
import RPi.GPIO as GPIO 
import time
import pi_sound
import neopixel


import logging
from buttonhandler import ButtonHandler
logger = logging.getLogger()


LED_PIN = 27
BUTTON_PIN = 17
BUZZER_PIN = 25
SWITCH_PIN = 13
FLASH_FREQ = 0.1
LED_ON = True

RGB_LED_PIN = 22
NUM_RGB_LEDS = 4

button_event = None
pixels = None

def gpio_setup(button_press):

    logging.info("***Setting up GPIO")

    global button_event, switch_on, pixels


    # Set the GPIO modes to BCM Numbering
    GPIO.setmode(GPIO.BCM)
    # Set LedPin's mode to output,and initial level to High(3.3v)
    GPIO.setup(LED_PIN, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(BUTTON_PIN, GPIO.IN)

    # Initialize RGB LEDs
    pixels = neopixel.NeoPixel(RGB_LED_PIN, NUM_RGB_LEDS, brightness=0.2, auto_write=False)

    GPIO.add_event_detect(BUTTON_PIN, GPIO.BOTH, callback=button_press)


def button_state():
    return GPIO.input(BUTTON_PIN)

def is_button_pressed():

    button_on = GPIO.input(BUTTON_PIN) == 1

    return button_on 

def led_on():
    global LED_ON
    LED_ON = True
    # logger.debug(f"LED: {LED_ON}")
    GPIO.output(LED_PIN, GPIO.HIGH)
    return LED_ON

def led_off():
    global LED_ON
    LED_ON = False
    # logger.debug(f"LED: {LED_ON}")
    GPIO.output(LED_PIN, GPIO.LOW)
    return LED_ON

def toggle_led():
    global LED_ON
    LED_ON = not LED_ON
    # logger.debug(f"LED: {LED_ON}")
    GPIO.output(LED_PIN, LED_ON)
    return LED_ON

def set_rgb_leds(colors):
    global pixels
    for i in range(min(NUM_RGB_LEDS, len(colors))):
        pixels[i] = colors[i]
    pixels.show()

def clear_rgb_leds():
    global pixels
    pixels.fill((0, 0, 0))
    pixels.show()
    
def play_winner():
    pi_sound.play_sounds(pi_sound.winning_sound)

def play_loser():
    pi_sound.play_sounds(pi_sound.losing_sound)

def start_beep(ticker_index):
    sound_index = ticker_index
    sound_type = pi_sound.tick_sounds[sound_index]
    
    logger.debug(f"beep on of type {sound_type}")
    
    pi_sound.start_sound(sound_type)
def stop_beep():
    pi_sound.stop_sound()

def play_beep(is_on, current_tick_rate):
    # if current_tick_rate <= 10:
    #     sound = pi_sound.tick_sounds[-1]
    # elif current_tick_rate <= 10:
        
    sound_index = 0 #int(current_tick_rate/len(pi_sound.tick_sounds))-1
    logger.debug(f"current_tick_rate: {current_tick_rate} sound_index {sound_index}")

    if is_on:
        pi_sound.start_sound(pi_sound.tick_sounds[sound_index])
    else:
        pi_sound.stop_sound()

def clean():
    logger.info("cleaning GPIO")
    GPIO.cleanup()


def press():
    print("button press")
    pass
# if __name__ == "__main__":
    # print("testing gpio")
    # gpio_setup(press)
    # while True:
    #     print("opn")
    #     led_on()
    #     time.sleep(1)
    #     print("off")
    #     led_off()
        
def test_rgb_leds():
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]  # Red, Green, Blue, Yellow
    for _ in range(10):  # Loop 10 times
        for color in colors:
            set_rgb_leds([color] * NUM_RGB_LEDS)
            time.sleep(0.5)
        clear_rgb_leds()
        time.sleep(0.5)

if __name__ == "__main__":
    print("testing gpio")
    gpio_setup(press)
    test_rgb_leds()        