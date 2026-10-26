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
    """The title screen's clips in order: it holds the first frame for hold_before seconds, plays each clip,
    holds the last frame for hold_after seconds, then starts over."""

    def __init__(self, clips, hold_before, hold_after):
        self.clips = clips
        self.hold_before = hold_before
        self.hold_after = hold_after
        self.duration = hold_before + sum(clip.duration for clip in clips) + hold_after

    def frame_at(self, seconds):
        """The frame to show `seconds` after the title screen started."""
        seconds = seconds % self.duration
        if seconds < self.hold_before:
            return self.clips[0].frames[0]
        seconds -= self.hold_before
        for clip in self.clips:
            if seconds < clip.duration:
                return clip.frame_at(seconds)
            seconds -= clip.duration
        return self.clips[-1].frames[-1]


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
