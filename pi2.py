#!/usr/bin/env python3
# GPIO import - uses rpi-lgpio library for Raspberry Pi 5 compatibility
import RPi.GPIO as GPIO
import time
import pi_sound

import logging
from buttonhandler import ButtonHandler
from config import HW

logger = logging.getLogger()

# Import hardware configuration from centralized config
LED_PIN = HW.LED_PIN
BUTTON_PIN = HW.BUTTON_PIN
BUZZER_PIN = HW.BUZZER_PIN
SWITCH_PIN = HW.SWITCH_PIN
FLASH_FREQ = HW.FLASH_FREQ
LED_ON = HW.LED_ON

# Regular LED configuration (not NeoPixels)
RGB_LED_PINS = HW.RGB_LED_PINS
NUM_RGB_LEDS = HW.NUM_RGB_LEDS

button_event = None

def gpio_setup(button_press):

    logging.info("***Setting up GPIO")

    global button_event, switch_on

    # Set the GPIO modes to BCM Numbering
    GPIO.setmode(GPIO.BCM)
    # Set LedPin's mode to output,and initial level to High(3.3v)
    GPIO.setup(LED_PIN, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(BUTTON_PIN, GPIO.IN)

    # Initialize RGB LED pins as outputs (regular LEDs, not NeoPixels)
    for pin in RGB_LED_PINS:
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
        logging.info(f"Set up RGB LED on GPIO pin {pin}")

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
    """
    Set individual LED states based on color tuples.
    For regular LEDs: any non-zero color turns LED on, (0,0,0) turns it off
    """
    for i in range(min(NUM_RGB_LEDS, len(colors))):
        # Check if color is non-zero (any value other than (0,0,0) means ON)
        if isinstance(colors[i], tuple) and len(colors[i]) == 3:
            is_on = any(colors[i])  # True if any RGB value is non-zero
            GPIO.output(RGB_LED_PINS[i], GPIO.HIGH if is_on else GPIO.LOW)
            logger.debug(f"LED {i} on pin {RGB_LED_PINS[i]}: {'ON' if is_on else 'OFF'} (color={colors[i]})")

def clear_rgb_leds():
    """Turn off all RGB LEDs"""
    for pin in RGB_LED_PINS:
        GPIO.output(pin, GPIO.LOW)
    logger.debug("All RGB LEDs cleared")
    
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
    """Test individual LEDs by turning them on/off in sequence"""
    print(f"Testing {NUM_RGB_LEDS} LEDs on pins: {RGB_LED_PINS}")

    # Test each LED individually
    for i in range(NUM_RGB_LEDS):
        colors = [(0, 0, 0)] * NUM_RGB_LEDS
        colors[i] = (255, 255, 255)  # Turn on LED i
        print(f"Turning on LED {i} (GPIO pin {RGB_LED_PINS[i]})")
        set_rgb_leds(colors)
        time.sleep(0.5)

    # Turn all on
    print("All LEDs ON")
    set_rgb_leds([(255, 255, 255)] * NUM_RGB_LEDS)
    time.sleep(1)

    # Turn all off
    print("All LEDs OFF")
    clear_rgb_leds()
    time.sleep(0.5)

if __name__ == "__main__":
    print("testing gpio")
    gpio_setup(press)
    test_rgb_leds()        