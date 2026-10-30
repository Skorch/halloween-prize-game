# The light strip

An addressable LED strip behind the screen throws a coloured glow onto the wall around it. `config.py`
(`LightsConfig`) says what each screen lights it with; `lights.py` holds the effects; `pi2.py` sends the colours.
Facts below are from 2026-10-30.

## What each screen shows

| Screen | Scene (`config.py`) | What it looks like |
|---|---|---|
| Title | `LIGHTS.TITLE`, `fire` | Each LED flares orange and drops nearly dark in deep red, about five flares a second, each LED at its own pace, like flames |
| Spin | `LIGHTS.SPIN`, `dread`, then `LIGHTS.SPIN_FAST`, `panic` | A red thump on every beep, brightest on the beep's own frame. While a card lasts `SPIN_FAST_SECONDS` (0.4 s) or more, a double thump (`dread`); on quicker cards, one flash (`panic`), since a second thump would last under 2 frames. Brightens to `MAX_BRIGHTNESS` as the countdown runs down |
| Winner | `LIGHTS.WINNER`, by the prize won | `mini`: `ember`, an orange swell. `playdough`: `toxic`, a green band travelling along the strip. `big_prize`: `jackpot`, red, orange, green and purple racing along it |

A scene is one effect plus its colours, speed and brightness, so a new scene is a few lines of `config.py`. A new
kind of movement is a new function in `lights.py`, added to `EFFECTS`. No scene goes past `MAX_BRIGHTNESS` (0.4).

On every beep the spin calls `game.lights.beat(scene, now, seconds)`, which starts the scene from its beginning with
one round of its effect lasting until the next card (`states/candy_picker.py`, `beat_lights`); the spin scenes'
`speed` is not used. Every frame it sets `game.lights.boost` from the countdown once it shows (`set_light_boost`).

## The hardware

| Fact | Value |
|---|---|
| Strip | 18 LEDs of a 5 V strip with one data wire (pads `GND`, `Din`, `5V`), the WS2812B family, in a silicone sleeve; red, green and blue, no white LED (from Drew's photo) |
| `Din` | GPIO10 (physical pin 19), the Pi's SPI data output, through a 330 or 470 Ω resistor soldered at the strip's `Din` pad. No other pin can carry the signal the game sends |
| `5V` | a 5 V header pin (pin 2 or 4; both are the same supply) |
| `GND` | a GND header pin, such as pin 20 |
| Wire | 22 AWG solid core, 30 to 60 cm from Drew's hat to the strip, data and ground twisted together the whole way |
| Level shifter | None. The Pi's 3.3 V data goes to the strip direct; the WS2812B datasheet asks for at least 0.7 × its supply (3.5 V at 5 V), so this often works but is not certain |
| Power | 18 LEDs at `MAX_BRIGHTNESS` draw about 0.2 to 0.5 A from the Pi's 5 V pins |

The strip's arrows point the way data flows; `Din` is the end they point away from.

**If the strip flickers or shows wrong colours**, the first fix is a silicon diode (such as a 1N4001) in the strip's
5 V wire, stripe toward the strip: the strip then runs on about 4.3 V and needs only about 3.0 V on `Din`. A level
shifter (a 74AHCT125 powered from 5 V) is the fix with no trade-off.

## How the colours reach it

The strip reads each bit from how long the data line stays high: about 0.4 µs for a 0 and 0.8 µs for a 1, in
1.25 µs. Python cannot switch a pin that precisely under Linux, and `rpi_ws281x`, the usual library, does not work on
the Pi 5. So `lights.strip_bytes` turns each strip bit into one SPI byte (`0b11000000` for a 0, `0b11111000` for a
1), and at `HW.STRIP_SPI_HZ` (6.4 MHz) the SPI hardware sends each byte in 1.25 µs. Each LED goes as green, red,
blue, highest bit first, and 240 zero bytes either side hold the line low between frames.

`pi2.py` opens `/dev/spidev0.0` through `spidev` (Debian's `python3-spidev`) when the game starts, and sends one
frame for each game frame. If SPI will not open, it logs `Light strip off: ...` once and the game plays on with the
strip dark; the same if a send fails. The game sends a dark frame when it quits.

SPI on the header must be switched on: `dtparam=spi=on` in `/boot/firmware/config.txt`, then a reboot.
`ls /dev/spidev0.0` shows whether it is on.

**Test pattern**: with the game stopped, `python3 pi2.py` on the Pi blinks the cabinet LEDs in turn, then lights the
whole strip red, then green, then blue, then one LED at a time along it. The right colours in that order show the
strip reads the colours as sent; the walk shows all 18 answer. The game running at the same time also sends to the
strip, and the two mix.

## On a Mac

Dev mode (`HALLOWEEN_DEV=1`) draws every output in the black mat under the picture: the 18 strip LEDs, a gap, the
four cabinet LEDs, a gap, the LED on GPIO 27 (`Game(show_outputs=True)`). The strip's dots are drawn at full
brightness, divided by `MAX_BRIGHTNESS`, because the real cap looks dull on a screen.
