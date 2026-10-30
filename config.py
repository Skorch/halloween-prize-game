#!/usr/bin/env python3
"""
Centralized configuration for Halloween Prize Game
Edit this file to customize hardware pins, game settings, and visual preferences
"""

# =============================================================================
# HARDWARE CONFIGURATION
# =============================================================================

class HardwareConfig:
    """GPIO pin assignments and hardware settings"""

    # GPIO Pin Numbers (BCM numbering)
    LED_PIN = 27            # Standard LED output
    BUTTON_PIN = 4         # Button input
    BUZZER_PIN = 25         # Buzzer/sound output
    SWITCH_PIN = 18         # Switch input (currently unused)

    # Regular LED Configuration (not NeoPixels)
    # Multiple individual LEDs controlled via GPIO
    RGB_LED_PINS = [6, 13, 19, 26]      # BCM pin numbers for individual LEDs (pins 31, 33, 35, 37)
    NUM_RGB_LEDS = 4                    # Number of individual LEDs

    # Timing
    FLASH_FREQ = 0.1                    # LED flash frequency in seconds
    BUTTON_COOLDOWN = 0.1               # Button debounce/cooldown time in seconds
    BUTTON_DELAY = 1.3                  # Delay before button actions in seconds

    # Initial States
    LED_ON = True                       # Initial LED state


# =============================================================================
# GAME CONFIGURATION
# =============================================================================

class GameConfig:
    """Game display and behavior settings"""

    # Display Settings
    GAME_WIDTH = 1024                   # Game canvas width
    GAME_HEIGHT = 1024                   # Game canvas height
    FULLSCREEN = True                   # Run in fullscreen mode
    FULLSCREEN_MODE = (1000, 666)       # Fullscreen size asked of the display; it picks the nearest mode (1024x768 on the Pi)
    SCREEN_SCALE = 0.91                 # Picture's share of the display's width and height, centred; the rest is a black mat. 0.91 takes about 2 cm off the width of a 10.1" screen
    MAX_FPS = 30                        # Frames drawn per second at most; the idle clips play at 30

    # Game Mechanics
    RGB_COUNT = 4                       # Number of RGB LEDs used in game

    # Dev/Prod Mode
    DEV_MODE = False                    # Set to True for development mode (uses pi_dev2)


# =============================================================================
# VISUAL CONFIGURATION
# =============================================================================

class VisualConfig:
    """Colors and visual styling"""

    # Text Colors (RGB tuples)
    TEXT_COLOR_1 = (138, 3, 3)          # Primary text color (dark red)
    TEXT_BG_1 = (0, 0, 0)               # Primary text background (black)

    # Title Screen Background
    # The title screen repeats the curtain clip for IDLE_WAIT_SECONDS, plays the show once, then starts over, with no text
    IDLE_CURTAIN_FILE = "assets/idle/idle-curtains-2s.mp4"  # 2 s of closed curtains with the red lamp pulsing once a second
    IDLE_SHOW_FILE = "assets/idle/main-animation.mp4"       # the 12 s show: curtains open, the automaton plays, curtains close
    IDLE_WAIT_SECONDS = 10              # Seconds of curtains between shows; a whole number keeps the lamp in step with the show
    IDLE_SOUND_FILE = "sounds/crackle-loop.wav"  # Loops the whole time the title screen is up, curtains and show alike; None = silent
    IDLE_SOUND_VOLUME = 0.50            # 0.0 to 1.0
    IDLE_SHOW_SOUND_FILE = "sounds/show-soundtrack.wav"  # Plays with each show, over the crackle; None = the show is silent
    IDLE_SHOW_SOUND_VOLUME = 0.50       # 0.0 to 1.0; the same as the crackle matches the mix the video was approved with
    TITLE_BACKGROUND_FILE = "assets/backgrounds/background2.png"  # Shown with the title message when there is no video, or it fails to load

    # Text Background Configuration (for candy picker screen)
    SHOW_PRIZE_TEXT = False              # Show prize text during candy flipping (True/False)
    SHOW_TEXT_BACKGROUND = False         # Show background behind prize text (True/False)
    TEXT_BG_OPACITY = 200               # Background opacity (0-255, 0=transparent, 255=opaque)
    TEXT_BG_HEIGHT_FRACTION = 0.25      # Background height as fraction of screen (0.25 = 1/4 of screen)

    # Winner Screen Configuration
    SHOW_WINNER_TEXT = False             # Show winner text on result screen (True/False)
    WINNER_BG_OPACITY = 100             # Winner screen background opacity (0-255, 0=transparent, 255=opaque)
    WINNER_TEXT_Y_FRACTION = 0.75        # Winner text Y position as fraction of screen height (0.5 = center)

    # Countdown Timer Configuration (for candy picker screen)
    TIMER_ENABLED = True               # Enable countdown timer (True/False)
    TIMER_START_SECONDS = 10            # Total seconds before auto-triggering button press
    TIMER_SHOW_AT_SECONDS = 5          # When to show the timer (seconds remaining)
    TIMER_CIRCLE_RADIUS = 100            # Radius of the circle background in pixels
    TIMER_POSITION_X = 200              # X position of timer center (pixels from left)
    TIMER_POSITION_Y = 200              # Y position of timer center (pixels from top)
    TIMER_TEXT_COLOR = (255, 255, 255)  # Timer text color (white)
    TIMER_CIRCLE_COLOR = (0, 0, 0)      # Timer circle background color (black)
    TIMER_CIRCLE_OPACITY = 200          # Timer circle opacity (0-255)

    # Font Configuration
    FONT_USE_TTF = True                 # True = use TTF file, False = use system font
    FONT_TTF_PATH = "assets/fonts/Creepster-Regular.ttf"  # Path to TTF font file
    FONT_NAME = 'comicsans'             # Font family name (system font, used if FONT_USE_TTF=False)

    FONT_SIZE_SMALL = 28                # Small text (default/legacy)
    FONT_SIZE_MEDIUM = 48               # Medium text (instructions)
    FONT_SIZE_LARGE = 72                # Large text (prize names during picker)
    FONT_SIZE_XLARGE = 96               # Extra large text (winner announcement)


# =============================================================================
# TEXT MESSAGES CONFIGURATION
# =============================================================================

class MessagesConfig:
    """Configurable text messages displayed in the game"""

    # Title Screen
    TITLE_MESSAGE = "Press the BIG BUTTON to start!"
    TITLE_MESSAGE_FONT_SIZE = VisualConfig.FONT_SIZE_MEDIUM

    # Candy Picker Screen (prize text while spinning)
    PICKER_MESSAGE_FONT_SIZE = VisualConfig.FONT_SIZE_LARGE

    # Winner Screen
    # Use {prize} as a placeholder for the prize name
    WINNER_MESSAGE = "{prize}!"
    WINNER_MESSAGE_FONT_SIZE = VisualConfig.FONT_SIZE_XLARGE

    # Add more custom messages here as needed


# =============================================================================
# PRIZES CONFIGURATION
# =============================================================================

class PrizesConfig:
    """Prize categories, inventory, and probability settings"""

    # =============================================================================
    # PRIZE INVENTORY - Set how many of each prize you have this year
    # =============================================================================
    MINI_CANDY_INVENTORY = 80          # How many mini candies you have
    PLAYDOUGH_INVENTORY = 50            # How many playdough prizes (set to 0 if none)
    BIG_PRIZE_INVENTORY = 20            # How many big prizes you have

    # =============================================================================
    # BIG PRIZE TYPE - What is your "big prize" this year?
    # =============================================================================
    # Options: "full_size" or "skull"
    BIG_PRIZE_TYPE = "full_size"            # Change to "full_size" for full-sized candy bars

    # =============================================================================
    # PRIZE DEFINITIONS - Customize folders, titles, and sounds
    # =============================================================================
    PRIZE_CATEGORIES = {
        "mini": {
            "folder": "assets/candy/*",
            "title": "Mini Candy",
            "sound_file": "sounds/small_prize_candy.wav",
        },
        "playdough": {
            "folder": "assets/playdough/*",
            "title": "Playdough",
            "sound_file": "sounds/small_prize_play.wav",
        },
        "skull": {
            "folder": "assets/skull/*",
            "title": "3d Skull",
            "sound_file": "sounds/big_prize_new.wav",
        },
        "full_size": {
            "folder": "assets/fullsize/*",  # Update this path if you have full-size candy
            "title": "Full Size Candy",
            "sound_file": "sounds/big_prize_new.wav",
        }
    }

    # =============================================================================
    # PROBABILITY SETTINGS
    # =============================================================================
    # Use inventory-based probabilities (recommended)
    # If True: probabilities adjust based on inventory counts above
    # If False: uses fixed probabilities below
    USE_INVENTORY_PROBABILITIES = True

    # Fixed probabilities (only used if USE_INVENTORY_PROBABILITIES = False)
    FIXED_PROBABILITIES = {
        "mini": 0.4,
        "playdough": 0.3,
        "big_prize": 0.3,
    }

    # Minimum number of spins before big prize is allowed
    MIN_SPINS_FOR_BIG_PRIZE = 5

    # =============================================================================
    # OTHER PRIZE SETTINGS
    # =============================================================================
    BEEP_SOUND_FILE = "sounds/prize-game-sound-2.wav"
    DEFAULT_SOUND_VOLUME = 0.50


# =============================================================================
# AUDIO CONFIGURATION
# =============================================================================

class AudioConfig:
    """Sound and buzzer settings"""

    MUTE_BUZZER = False                 # Set to True to disable buzzer sounds


# =============================================================================
# CONVENIENCE EXPORTS
# =============================================================================
# Import these directly: from config import HW, GAME, VISUAL, AUDIO, MESSAGES, PRIZES

HW = HardwareConfig
GAME = GameConfig
VISUAL = VisualConfig
AUDIO = AudioConfig
MESSAGES = MessagesConfig
PRIZES = PrizesConfig
