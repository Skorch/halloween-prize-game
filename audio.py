import pygame

LOOP_CHANNEL = 0   # kept for the looping sound: no other sound plays there, so starting the loop cuts none off


class PygameAudio:
    """Loads and plays the game's sounds through pygame.mixer. Game takes it as a parameter."""

    def __init__(self):
        pygame.mixer.init()
        pygame.mixer.set_reserved(1)   # Sound.play() skips reserved channels: channel 0 is LOOP_CHANNEL's alone

    def load(self, path, volume):
        sound = pygame.mixer.Sound(path)
        sound.set_volume(volume)
        return sound

    def play(self, sound):
        sound.play()
        pygame.mixer.music.stop()

    def loop(self, sound):
        """Plays `sound` over and over, mixed with every other sound, until stop_loop()."""
        pygame.mixer.Channel(LOOP_CHANNEL).play(sound, loops=-1)

    def stop_loop(self):
        pygame.mixer.Channel(LOOP_CHANNEL).stop()
