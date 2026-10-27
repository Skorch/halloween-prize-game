import pygame


class Clip:
    """Every frame of one video, decoded once and scaled to the game canvas."""

    def __init__(self, frames, fps):
        self.frames = frames
        self.fps = fps
        self.duration = len(frames) / fps

    def frame_at(self, seconds):
        return self.frames[min(int(seconds * self.fps), len(self.frames) - 1)]


class IdleVideo:
    """The title screen's video: the curtain clip repeats for `wait` seconds, the show plays once, then it
    starts over."""

    def __init__(self, curtain, show, wait):
        self.curtain = curtain
        self.show = show
        self.wait = wait
        self.duration = wait + show.duration

    def frame_at(self, seconds):
        """The frame to show `seconds` after the title screen started."""
        seconds = seconds % self.duration
        if seconds < self.wait:
            return self.curtain.frame_at(seconds % self.curtain.duration)
        return self.show.frame_at(seconds - self.wait)

    def shows_started(self, seconds):
        """How many times the show has started by `seconds` after the title screen started: 0 during the first
        wait, 1 from the first show's first frame, and so on."""
        return int((seconds + self.show.duration) // self.duration)


def load_clip(path, size):
    """Decodes every frame of the video at `path` into a pygame Surface of `size`. Raises if it cannot."""
    import av   # PyAV: python3-av on the Pi. Imported here so a missing package falls back like a missing file

    frames = []
    with av.open(path) as container:
        stream = container.streams.video[0]
        fps = float(stream.average_rate)
        for frame in container.decode(stream):
            rgb = frame.to_ndarray(format="rgb24")
            surface = pygame.image.frombuffer(rgb.tobytes(), (frame.width, frame.height), "RGB")
            frames.append(pygame.transform.smoothscale(surface, size).convert())
    if not frames:
        raise ValueError(f"no frames in {path}")
    return Clip(frames, fps)
