# Decisions

Each decision Drew made, newest last. Entries are appended and never rewritten; a later decision that
changes an earlier one says so.

## 2026-10-26

1. **Stay on pygame 2.6.1; do not switch to pygame-ce.** 2.6.1 is the newest pygame release (2024-09-29) and
   the version the Pi runs from Debian. pygame-ce is worth another look on a move to Python 3.15 or a
   pygame bug.
2. **Test with scripted tests first.** The game takes its hardware, clock, prize pick and sound as
   parameters, so a test passes fakes, runs with no window (SDL's `dummy` drivers), and saves a PNG of each
   screen. An agent playing the live game by commands may come later.
3. **Keep SSH password login on the Pi**, beside key login from Drew's Mac.
4. **Work in any agent tool.** `AGENTS.md` is the source and `CLAUDE.md` a symlink to it; project skills live
   in `.agents/skills/`, symlinked into `.claude/skills/`.
5. **Dev mode is switched on by `HALLOWEEN_DEV=1`**, never by editing `config.py`.
6. **The suite saves screens for review and does not compare them** against approved images: those would
   change with every art or font change, and SDL draws text slightly differently on the Mac and the Pi.
7. **The real button's edges are to be measured on the Pi** so the fake button presses the way the real one
   does. Until then the fake makes one clean edge per press.
8. **Fakes live in `tests/fakes.py`**, so the game's own code holds only what the game runs.
9. **Stock that never goes down is a known bug**, recorded as a test that is expected to fail
   (`test_stock_goes_down_when_a_prize_is_won`); the fix is a change of its own.
10. **The button is measured from the game's own log**, not a separate script (completes decision 7). Two real
    presses recorded on the Pi are replayed by the tests; with them every press starts or stops a round.
11. **The title screen loops a video**, `assets/backgrounds/skeleton.mp4`, with no text over it and no sound. At
    the end it holds its last frame for `IDLE_VIDEO_LOOP_DELAY` (5 s) before it plays again.
    If it fails to load, the title shows `background2.png` with its message, as before. An mp3 played over
    the video may come later.
12. **PyAV decodes the video**, because the Pi already has it (`python3-av`); OpenCV would add 81 packages.
13. **Every frame is decoded once, when the game starts**, and kept in memory, so the loop restarts without
    a pause and the fake clock picks the frame in tests. The cost on the Pi: 3.9 s at startup and about
    600 MB of its 4 GB.
14. **Loading is made efficient where needed**: the title's video and still background load once in
    `Game`, not on every frame or every round. Anything else changes only if measuring on the Pi shows it is needed.
15. **Five clips replace the skeleton video** (changes decisions 11 and 13). They play in the order
    `assets/idle/automaton-1.mp4` to `automaton-5.mp4`; each clip ends on the frame the next begins with, and
    the last ends on the first's opening frame, curtains closed. The first frame holds for
    `IDLE_VIDEO_HOLD_BEFORE` (5 s) before the clips play, and the last for `IDLE_VIDEO_HOLD_AFTER` (5 s) after.
    A clip that fails to load is skipped; with none, the title shows `background2.png`.
16. **All the clips' frames still load at startup**: 12 s of clips fits in the Pi's memory, and decoding
    while playing could pause at the joins between clips. Decoding while playing is worth it if the clips grow
    past about 15 to 20 s in total.
17. **The game loop draws at most `GAME.MAX_FPS` (30) frames a second**; before, it drew as fast as it could
    and kept one processor core busy.
18. **The title screen loops a crackle**, `sounds/idle_crackle.mp3` (changes the "no sound" in decision 11). It
    plays the whole time the title is up, the holds included, on its own 12 s loop rather than in step with the
    clips; a press stops it, and it starts again back at the title. Each clip's own sound, mixed in with it, comes
    later, once a clip has sound.
19. **The title screen plays a 4:3 curtain loop and one show, with a soundtrack** (changes decisions 15 and 18).
    The video was re-rendered at 1024x768, the Pi display's size. `assets/idle/idle-curtains-2s.mp4` repeats
    for `IDLE_WAIT_SECONDS` (10 s), then `assets/idle/main-animation.mp4` (12 s) plays once, and it starts over;
    they replace the five `automaton-*.mp4` clips and the holds. `sounds/show-soundtrack.wav` starts on the show's
    first frame, on a mixer channel of its own, at the crackle's volume (0.50), the mix the video was approved
    with. The crackle is now `sounds/crackle-loop.wav`, cut to loop without a gap, and keeps playing through the
    curtains and the show. A press stops both sounds. If either clip fails to load, the title shows
    `background2.png` with its message.
20. **Every change to what the game does comes with a test that fails without it**, and a test of existing
    behaviour is updated to match, not deleted. Before, the rules asked only that `uv run pytest` pass.
21. **Each frame goes to the display once, and the countdown loads its font once**, ahead of a measured need
    (decision 14 asked for one first). `render()` scales the canvas straight into the screen and calls only
    `display.flip()`; the countdown's font loads in `load_assets`. On the Pi the title screen went from 30% to
    17% of one core. Turning the LEDs off on every frame of the winner screen stays as it is, until LED strip
    work replaces it.
22. **The picture sits in a black mat** (Drew, 2026-10-30): shrunk proportionally so the screen loses about 2 cm
    of width, and the same share of height. `config.GAME.SCREEN_SCALE` sets the picture's share of the display;
    `render()` fills the display black and scales the canvas into the middle.
23. **The picture sits against the top edge** (Drew, 2026-10-30; changes decision 22): Drew's frame around the
    screen needs it top aligned. It stays centred left to right, so the mat runs down both sides and along the
    bottom.

## 2026-10-30

24. **An addressable LED strip glows behind the screen**, 18 LEDs of a 5 V WS2812B-family strip, never at full white.
    `config.py` drives it: `LIGHTS.SCENES` names scenes (an effect from `lights.py` with its colours, speed and
    brightness), and each screen names its scene. The title shows `fire`; the spin shows `dread`, a heartbeat that
    speeds up with the cards and brightens in the countdown; the winner screen's scene is the prize's. The four
    cabinet LEDs and the LED on GPIO 27 keep doing what they did.
25. **The game loop sends the strip its colours**, once a frame, over SPI on GPIO10 through `spidev`, with the
    signal built in `lights.py`. Not a background thread (harder to test and to read), and not Adafruit's
    `neopixel_spi` or `Pi5Neo` (neither is a Debian package). If SPI will not open, the game plays on with the
    strip dark.
26. **The strip is wired with no level shifter**, Drew having none; a diode in its 5 V wire is the first fix if it
    flickers.
27. **Dev mode shows every LED** as a dot in the black mat under the picture, so scenes can be tuned on a Mac.
28. **The spin's strip thumps on every beep** (changes the spin in decision 24): each beep starts a thump, brightest on
    the beep, lasting until the next card. Slow cards get a double thump; cards under `LIGHTS.SPIN_FAST_SECONDS`
    (0.4 s) get one flash, because a double at that speed got in the way of the frames. The heartbeat no longer speeds
    up on its own clock.
29. **The title's fire flickers harder and faster**: flares to orange and drops nearly dark between them, about five
    flares a second, in place of a slow glow.
30. **Fullscreen hides the mouse pointer**, which sat over the picture on the Pi; a window on a Mac keeps it.
31. **The playdough wave runs faster** (speed 0.6 to 1.5): at 0.6 the band took 6.7 s to cross the strip, longer than the
    5 s winner screen; now it crosses in 2.7 s.
