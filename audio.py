import pygame


class PygameAudio:
    """Loads and plays the game's sounds through pygame.mixer. Game takes it as a parameter."""

    def __init__(self):
        pygame.mixer.init()

    def load(self, path, volume):
        sound = pygame.mixer.Sound(path)
        sound.set_volume(volume)
        return sound

    def play(self, sound):
        sound.play()
        pygame.mixer.music.stop()
