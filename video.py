import pygame


class IdleVideo:
    """Every frame of a video, decoded once and scaled to the game canvas, so the title screen can loop it."""

    def __init__(self, frames, fps, loop_delay):
        self.frames = frames
        self.fps = fps
        self.loop_delay = loop_delay
        self.duration = len(frames) / fps

    def frame_at(self, seconds):
        """The frame to show `seconds` after the video started: it plays, holds its last frame for
        loop_delay seconds, then plays again from the first."""
        seconds_into_loop = seconds % (self.duration + self.loop_delay)
        return self.frames[min(int(seconds_into_loop * self.fps), len(self.frames) - 1)]


def load_video(path, size, loop_delay):
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
    return IdleVideo(frames, fps, loop_delay)
