"""Stand-ins for what the game reaches outside itself. Each is passed to Game as a parameter."""
import random


# Two presses of the real button, recorded on the Pi on 2026-10-26 from the game's own log
# (~/.xsession-errors): (seconds after the first edge, pin read high). A press flickers for 0.06-0.23 s.
RECORDED_PRESSES = [
    [(0.0, True), (0.0249, False), (0.0306, False), (0.0309, False), (0.0338, True), (0.0401, False),
     (0.0504, True), (0.0561, False)],
    [(0.0, True), (0.0073, False), (0.0167, True), (0.0253, False), (0.0337, True), (0.0407, False),
     (0.0502, True), (0.0574, False), (0.0668, True), (0.074, False), (0.0835, True), (0.0906, False),
     (0.1001, True), (0.1073, False), (0.1167, True), (0.124, False), (0.1334, True), (0.1406, False),
     (0.15, True), (0.1573, False), (0.1666, True), (0.1739, False), (0.1833, True), (0.1906, False),
     (0.1999, True), (0.2072, False), (0.2167, True), (0.2238, False), (0.2337, False), (0.2339, False)],
]


class FakeClock:
    """A clock that moves only when a test calls advance(). Game calls it like time.time."""

    def __init__(self, start=1000.0):
        self.now = start

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


class FakeHardware:
    """The button and LEDs. Records every call; the button is driven through the game's own callback.

    Same functions as pi2.py and pi_dev2.py, so Game cannot tell it from the real thing.
    """

    def __init__(self):
        self.calls = []
        self.strip = []          # every frame's strip colours, kept apart from calls: there is one each frame
        self.pin_high = False
        self.on_button_edge = None

    # What the game calls
    def gpio_setup(self, on_button_edge):
        self.on_button_edge = on_button_edge
        self.calls.append(("gpio_setup",))

    def is_button_pressed(self):
        return self.pin_high

    def button_state(self):
        return 1 if self.pin_high else 0

    def led_on(self):
        self.calls.append(("led_on",))

    def led_off(self):
        self.calls.append(("led_off",))

    def toggle_led(self):
        self.calls.append(("toggle_led",))

    def set_rgb_leds(self, colors):
        self.calls.append(("set_rgb_leds", [tuple(c) for c in colors]))

    def clear_rgb_leds(self):
        self.calls.append(("clear_rgb_leds",))

    def set_strip(self, colours):
        self.strip.append([tuple(c) for c in colours])

    def clean(self):
        self.calls.append(("clean",))

    # What a test calls
    def edge(self, high):
        """One signal from the button pin, as GPIO reports it: the pin changes, then the callback runs."""
        self.pin_high = high
        self.on_button_edge(None)

    def clean_press(self):
        """A press with no bounce: one rising edge, then one falling edge."""
        self.edge(True)
        self.edge(False)

    def recorded_press(self, clock, edges):
        """A press replayed edge by edge, moving the fake clock to each edge's time (see RECORDED_PRESSES)."""
        start = clock.now
        for seconds, high in edges:
            clock.now = start + seconds
            self.edge(high)

    def count(self, name):
        return sum(1 for call in self.calls if call[0] == name)

    def rgb_patterns(self):
        return [call[1] for call in self.calls if call[0] == "set_rgb_leds"]


class FakeAudio:
    """Sound that records what played. A loaded sound is just its file name."""

    def __init__(self):
        self.played = []
        self.volumes = {}         # each loaded file's volume
        self.looping = None       # the sound looping now, or None
        self.loops_started = 0
        self.show = None          # the show's soundtrack while it plays, or None once stopped
        self.shows_started = 0

    def load(self, path, volume):
        self.volumes[path] = volume
        return path

    def play(self, sound):
        self.played.append(sound)

    def loop(self, sound):
        self.looping = sound
        self.loops_started += 1

    def stop_loop(self):
        self.looping = None

    def play_show(self, sound):
        """A sound that ends by itself stays in `show` until stopped: the fake does not know how long it is."""
        self.show = sound
        self.shows_started += 1

    def stop_show(self):
        self.show = None


class ScriptedPicks(random.Random):
    """A random source whose prize-type picks come from a list; everything else is seeded random."""

    def __init__(self, prize_types):
        super().__init__(0)
        self.prize_types = list(prize_types)

    def choices(self, population, weights=None, k=1):
        prize_type = self.prize_types.pop(0)
        assert prize_type in population, f"{prize_type} is not allowed now; allowed: {population}"
        return [prize_type]
