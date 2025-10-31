#!/bin/bash
# Halloween Game Launcher Script
# Ensures proper environment for pygame

# Set working directory
cd /home/pi/Documents/halloween-prize-game

# Set display
export DISPLAY=:0

# Set SDL video driver explicitly
export SDL_VIDEODRIVER=x11

# Disable screen saver during game
xset s off -display :0 2>/dev/null
xset -dpms -display :0 2>/dev/null

# Launch the game
/usr/bin/python3 game.py

# Re-enable screen saver after game
xset s on -display :0 2>/dev/null
xset +dpms -display :0 2>/dev/null
