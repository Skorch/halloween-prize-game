"""The light strip behind the screen: five effects, the scene showing now, and the bytes that carry it to the strip.

A scene (LIGHTS.SCENES in config.py) is one of the effects below with its colours, speed and brightness. Each screen
picks its scene with Lights.show(); the game sends Lights.colours() to the strip once a frame.
"""
import math

from config import LIGHTS

DARK = (0, 0, 0)

# The strip reads each bit from how long the data line stays high. At HW.STRIP_SPI_HZ one SPI byte lasts one strip
# bit (1.25 us), so each strip bit goes out as one SPI byte: 2 of 8 high (about 0.3 us) for a 0, 5 of 8 (about
# 0.8 us) for a 1, as the WS2812B datasheet asks
SPI_ZERO = 0b11000000
SPI_ONE = 0b11111000
LOW_BYTES = 240                         # 300 us of low line either side, so the strip knows where a frame starts


def mix(a, b, amount):
    """The colour `amount` of the way from a to b: 0.0 is a, 1.0 is b."""
    return tuple(a[i] + (b[i] - a[i]) * amount for i in range(3))


def dim(colour, amount):
    return tuple(c * amount for c in colour)


# Each effect takes t, the effect's own clock (seconds since its scene started, times the scene's speed), the number
# of LEDs, and the scene's colours, and returns one (r, g, b) for each LED at full brightness. None of them uses
# random numbers, so the same t always gives the same colours.

def flicker(t, n, colors):
    """Each LED drifts between the two colours and dims and brightens, at its own uneven pace, like firelight."""
    out = []
    for i in range(n):
        # Three waves at rates that never line up, and a different start for each LED: -1.0 to 1.0
        wobble = (math.sin(t * 7.0 + i * 1.7) + math.sin(t * 11.3 + i * 2.9) + math.sin(t * 3.1 + i * 0.6)) / 3
        amount = (wobble + 1) / 2
        out.append(dim(mix(colors[-1], colors[0], amount), 0.5 + 0.5 * amount))
    return out


def heartbeat(t, n, colors):
    """All LEDs thump twice, then rest at a faint glow: one beat a second."""
    beat = t % 1.0
    if beat < 0.15:
        level = math.sin(math.pi * beat / 0.15)
    elif 0.25 <= beat < 0.4:
        level = 0.7 * math.sin(math.pi * (beat - 0.25) / 0.15)
    else:
        level = 0.0
    level = max(level, 0.08)
    return [dim(colors[0], level)] * n


def pulse(t, n, colors):
    """All LEDs swell and fade together: one swell every two seconds."""
    level = 0.15 + 0.85 * (1 - math.cos(math.pi * t)) / 2
    return [dim(colors[0], level)] * n


def wave(t, n, colors):
    """A band of the first colour travels along the strip over the second, 6 LEDs a second."""
    width = 3
    centre = (t * 6) % (n + 2 * width) - width
    return [mix(colors[-1], colors[0], max(0.0, 1 - abs(i - centre) / width)) for i in range(n)]


def chase(t, n, colors):
    """The colours repeat along the strip in pairs of LEDs, and move along it 8 LEDs a second."""
    step = int(t * 8)
    return [colors[((i - step) // 2) % len(colors)] for i in range(n)]


EFFECTS = {
    "flicker": flicker,
    "heartbeat": heartbeat,
    "pulse": pulse,
    "wave": wave,
    "chase": chase,
}


class Lights:
    """The scene the strip shows now.

    pace (0.0 to 1.0) speeds the scene up, to LIGHTS.SPIN_FASTEST_SPEED times its speed at 1.0; boost (0.0 to 1.0)
    lifts its brightness up to LIGHTS.MAX_BRIGHTNESS. The spin sets both every frame; show() puts them back to 0.
    """

    def __init__(self):
        self.scene_name = None
        self.scene = None
        self.pace = 0
        self.boost = 0
        self.effect_time = 0.0
        self.last_time = 0.0

    def show(self, scene_name, now):
        """Start a scene from its beginning."""
        self.scene_name = scene_name
        self.scene = LIGHTS.SCENES[scene_name]
        self.pace = 0
        self.boost = 0
        self.effect_time = 0.0
        self.last_time = now

    def colours(self, now):
        """The strip's colours at `now`, as whole numbers. Call once a frame: it moves the effect's clock on."""
        if self.scene is None:
            return [DARK] * LIGHTS.NUM_LEDS

        # The effect's clock runs at the scene's speed, sped up by pace. Adding up each frame's share keeps the beat
        # smooth while pace changes; multiplying the whole time by a new speed would jump the beat
        speed = self.scene["speed"] * (1 + (LIGHTS.SPIN_FASTEST_SPEED - 1) * self.pace)
        self.effect_time += max(0.0, now - self.last_time) * speed
        self.last_time = now

        brightness = self.scene["brightness"] + (LIGHTS.MAX_BRIGHTNESS - self.scene["brightness"]) * self.boost
        brightness = min(brightness, LIGHTS.MAX_BRIGHTNESS)
        effect = EFFECTS[self.scene["effect"]]
        colours = effect(self.effect_time, LIGHTS.NUM_LEDS, self.scene["colors"])
        return [tuple(round(min(255, max(0, c)) * brightness) for c in colour) for colour in colours]


def strip_bytes(colours):
    """The SPI bytes that send `colours` to the strip: each LED as green, red, blue, 8 bits each, highest bit first."""
    out = bytearray(LOW_BYTES)
    for red, green, blue in colours:
        for value in (green, red, blue):
            for bit in range(7, -1, -1):
                out.append(SPI_ONE if (value >> bit) & 1 else SPI_ZERO)
    out += bytes(LOW_BYTES)
    return bytes(out)
