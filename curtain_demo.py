"""Test: draw the green-screen curtain clips on top of the current title show.

Checks that the two-layer plan works in pygame: a theme video at the bottom, and the shared curtain
on top with its green background made see-through. The show used by default
(assets/idle/main-animation.mp4) has its own curtain painted in, so you will see two curtains.
That is expected: this only tests that the layering works.

Before running, download the two curtain clips from Runway into assets/curtain/ as
curtain_open.mp4 and curtain_close.mp4.

Run from the repo folder:   uv run python curtain_demo.py
Keys:  Space = skip to the next step    B = swap the show for flat magenta (left-over green at the
       curtain's edges stands out against it)    P = pause    H = hide the text    Esc = quit

The game does not import this file.
"""
import argparse
import os
import sys

import av
import numpy as np
import pygame

SIZE = (1024, 768)   # the Pi's screen, and the size of the title videos
FPS = 30

IDLE, OPENING, SHOW, CLOSING = "idle", "opening", "show", "closing"
STEPS = [IDLE, OPENING, SHOW, CLOSING]


def key_green(rgb, soft, hard):
    """Makes the green background of one frame see-through.

    rgb: a height x width x 3 array of 0-255 values. Returns height x width x 4 (red, green, blue, opacity).
    For each pixel, "spill" is how much its green is above the larger of its red and blue. A pixel with
    spill at or below `soft` stays solid, at or above `hard` it becomes fully see-through, and in between
    it fades. On every pixel, green is then cut down to the larger of red and blue, so the curtain's
    edges do not glow green.
    """
    rgb = rgb.astype(np.int32)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    limit = np.maximum(r, b)
    spill = g - limit
    out = np.empty(rgb.shape[:2] + (4,), np.uint8)
    out[..., 0] = r
    out[..., 1] = np.minimum(g, limit)
    out[..., 2] = b
    out[..., 3] = np.clip((hard - spill) * 255 // (hard - soft), 0, 255)
    return out


def scaled_rgb(frame):
    """One decoded video frame, scaled to SIZE, as a height x width x 3 array."""
    return frame.reformat(width=SIZE[0], height=SIZE[1], format="rgb24").to_ndarray()


def rgb_surface(rgb):
    return pygame.image.frombuffer(rgb.tobytes(), SIZE, "RGB").convert()


def load_curtain(path, soft, hard):
    """Decodes every frame of a curtain clip, keys out its green, and returns (frames, fps)."""
    frames = []
    with av.open(path) as container:
        stream = container.streams.video[0]
        fps = float(stream.average_rate)
        for frame in container.decode(stream):
            rgba = key_green(scaled_rgb(frame), soft, hard)
            frames.append(pygame.image.frombuffer(rgba.tobytes(), SIZE, "RGBA").convert_alpha())
    if not frames:
        raise ValueError(f"no frames in {path}")
    return frames, fps


class ThemeVideo:
    """The bottom layer. Decoded while it plays rather than all at once, so it does not fill memory."""

    def __init__(self, path):
        self.path = path
        count, first, last = 0, None, None
        with av.open(path) as container:
            stream = container.streams.video[0]
            self.fps = float(stream.average_rate)
            for frame in container.decode(stream):
                rgb = scaled_rgb(frame)
                if first is None:
                    first = rgb
                last = rgb
                count += 1
        if count == 0:
            raise ValueError(f"no frames in {path}")
        self.count = count
        self.duration = count / self.fps
        self.first = rgb_surface(first)   # held still while the curtain opens
        self.last = rgb_surface(last)     # held still while the curtain closes
        self.container = None

    def start(self):
        """Rewinds to the first frame."""
        if self.container:
            self.container.close()
        self.container = av.open(self.path)
        self.decoder = self.container.decode(self.container.streams.video[0])
        self.index = 0
        self.current = self.first

    def frame_at(self, seconds):
        """The frame `seconds` after start(), decoding forward as far as needed."""
        wanted = min(int(seconds * self.fps), self.count - 1)
        rgb = None
        while self.index < wanted:
            rgb = scaled_rgb(next(self.decoder))
            self.index += 1
        if rgb is not None:
            self.current = rgb_surface(rgb)
        return self.current


def clip_frame(frames, fps, seconds):
    return frames[min(int(seconds * fps), len(frames) - 1)]


def main():
    parser = argparse.ArgumentParser(description="Draw the green-screen curtain over the title show.")
    parser.add_argument("--theme", default="assets/idle/main-animation.mp4", help="the bottom-layer video")
    parser.add_argument("--open", default="assets/curtain/curtain_open.mp4", help="curtain opening clip")
    parser.add_argument("--close", default="assets/curtain/curtain_close.mp4", help="curtain closing clip")
    parser.add_argument("--idle", type=float, default=2.0, help="seconds the closed curtain stays up")
    parser.add_argument("--soft", type=int, default=40, help="green spill at or below which a pixel stays solid")
    parser.add_argument("--hard", type=int, default=100, help="green spill at or above which a pixel is see-through")
    parser.add_argument("--fullscreen", action="store_true")
    args = parser.parse_args()

    missing = [p for p in (args.theme, args.open, args.close) if not os.path.exists(p)]
    if missing:
        sys.exit("Missing: " + ", ".join(missing) + "\nDownload the curtain clips from Runway into assets/curtain/.")
    if args.hard <= args.soft:
        sys.exit("--hard must be larger than --soft")

    pygame.init()
    flags = pygame.FULLSCREEN | pygame.SCALED if args.fullscreen else 0
    screen = pygame.display.set_mode(SIZE, flags)
    pygame.display.set_caption("Curtain layer test")
    font = pygame.font.Font(None, 26)

    print("Loading clips...")
    open_frames, open_fps = load_curtain(args.open, args.soft, args.hard)
    close_frames, close_fps = load_curtain(args.close, args.soft, args.hard)
    theme = ThemeVideo(args.theme)
    lengths = {
        IDLE: args.idle,
        OPENING: len(open_frames) / open_fps,
        SHOW: theme.duration,
        CLOSING: len(close_frames) / close_fps,
    }
    print("Seconds per step:", {k: round(v, 2) for k, v in lengths.items()})

    magenta = pygame.Surface(SIZE)
    magenta.fill((255, 0, 255))

    step, step_time = IDLE, 0.0
    paused, show_magenta, show_text = False, False, True
    clock = pygame.time.Clock()
    running = True
    while running:
        dt = min(clock.tick(FPS) / 1000, 0.1)
        skip = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    skip = True
                elif event.key == pygame.K_b:
                    show_magenta = not show_magenta
                elif event.key == pygame.K_p:
                    paused = not paused
                elif event.key == pygame.K_h:
                    show_text = not show_text

        if not paused:
            step_time += dt
        if skip or step_time >= lengths[step]:
            step = STEPS[(STEPS.index(step) + 1) % len(STEPS)]
            step_time = 0.0
            if step == SHOW:
                theme.start()

        if step == IDLE:
            bottom, top = theme.first, open_frames[0]   # the closed curtain covers the whole frame
        elif step == OPENING:
            bottom, top = theme.first, clip_frame(open_frames, open_fps, step_time)
        elif step == SHOW:
            bottom, top = theme.frame_at(step_time), open_frames[-1]   # open curtain held on top
        else:
            bottom, top = theme.last, clip_frame(close_frames, close_fps, step_time)

        screen.blit(magenta if show_magenta else bottom, (0, 0))
        screen.blit(top, (0, 0))
        if show_text:
            label = f"{step} {step_time:4.1f}s  {clock.get_fps():3.0f} fps" + ("  PAUSED" if paused else "")
            label += "   Space next  B magenta  P pause  H hide  Esc quit"
            text = font.render(label, True, (255, 255, 255))
            box = pygame.Surface((text.get_width() + 16, text.get_height() + 10))
            box.set_alpha(170)
            screen.blit(box, (8, SIZE[1] - box.get_height() - 8))
            screen.blit(text, (16, SIZE[1] - box.get_height() - 3))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
