#!/usr/bin/env python3
import time

import logging
logger = logging.getLogger()


LED_PIN = 21
BUTTON_PIN = 27
BUZZER_PIN = 25
SWITCH_PIN = 13
FLASH_FREQ = 0.1
LED_ON = True

button_event = None

def gpio_setup(button_press):

    logging.info("***Setting up FAKE GPIO")

    global button_event, switch_on

    button_event = button_press
def is_button_pressed(test = False):
    return test
def is_switch_on(test = False):
    return test


def toggle_led():
    global LED_ON
    LED_ON = not LED_ON
    # logger.debug(f"LED: {LED_ON}")

    logger.info(f"LED {LED_ON}")

    return LED_ON

def play_winner():
    logger.info("Winner Sound")
    return

def play_loser():
    logger.info("Lower Sound")
    return

def play_beep(current_tick_rate):
    # if current_tick_rate <= 10:
    #     sound = pi_sound.tick_sounds[-1]
    # elif current_tick_rate <= 10:
        
    sound_index = 0 #int(current_tick_rate/len(pi_sound.tick_sounds))-1
    logger.debug(f"current_tick_rate: {current_tick_rate} sound_index {sound_index}")

    logger.info("Beep")

def clean():

    return