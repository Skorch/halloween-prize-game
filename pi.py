#!/usr/bin/env python3
import RPi.GPIO as GPIO 
import time
import pi_sound

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

    logging.info("***Setting up GPIO")

    global button_event, switch_on

    button_event = button_press
    # Set the GPIO modes to BCM Numbering
    GPIO.setmode(GPIO.BCM)
    # Set LedPin's mode to output,and initial level to High(3.3v)

    GPIO.setup(LED_PIN, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(SWITCH_PIN, GPIO.OUT)
    GPIO.setup(BUTTON_PIN, GPIO.IN)
    pi_sound.setup_buzzer(pin=BUZZER_PIN, mute=False)

    GPIO.add_event_detect(BUTTON_PIN, GPIO.BOTH, callback=button_event)

def is_switch_on():
    return True
    switch_on = GPIO.input(SWITCH_PIN)
    logger.debug(f"== switch state {switch_on}")

    return switch_on


def toggle_led():
    global LED_ON
    LED_ON = not LED_ON
    # logger.debug(f"LED: {LED_ON}")
    GPIO.output(LED_PIN, LED_ON)
    return LED_ON

def play_winner():
    pi_sound.play_sounds(pi_sound.winning_sound)

def play_loser():
    pi_sound.play_sounds(pi_sound.losing_sound)

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
    GPIO.cleanup()