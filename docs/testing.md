# Testing

`uv run pytest` plays whole rounds of the game with no window and no sound, on fakes, and finishes in about
two seconds on the Mac. It also passes on the Pi (2026-10-26, in a scratch environment with pytest added).

## How a test controls the game

`Game` takes everything it reaches outside itself as a parameter, so a test passes stand-ins from
`tests/fakes.py`:

| Parameter | On the Pi | In a test | What the test does with it |
|---|---|---|---|
| `hardware` | the `pi2` module | `FakeHardware` | reads `calls` (every LED change); `edge(high)` and `clean_press()` drive the game's button callback |
| `clock` | `time.time` | `FakeClock` | `advance(seconds)`; nothing in the game waits on real time |
| `rng` | `random.Random()` | `random.Random(seed)` or `ScriptedPicks([...])` | a seed gives the same picks every run; `ScriptedPicks` names each prize type in order |
| `audio` | `PygameAudio` | `FakeAudio` | reads `played`, the file name of each sound in order |
| `fullscreen` | `True` | `False` | |

`tests/conftest.py` sets SDL's `dummy` video and audio drivers before pygame starts, and moves into the repo
folder, since the game loads files by relative path.

## Writing a test

The fixtures `make_game`, `clock`, `hardware`, `audio` and `snap`, and the helpers `screen(game)`,
`press_space(game)` and `wait(game, clock, seconds)`, are in `tests/conftest.py`. A round test reads like the
round:

```python
def test_press_starts_a_spin(make_game, hardware, audio, snap):
    game = make_game()
    game.step()
    press_space(game)
    assert screen(game) == "CandyPicker"
    snap(game, "first-card")          # saved to tests/out/test_press_starts_a_spin/first-card.png
```

- **Derive numbers from the code or config** (`STEP_RATE_CURVE`, `VISUAL.TIMER_START_SECONDS`, the stock in
  `config.py`), so a tuning change does not break a test.
- **Round tests press the spacebar.** The GPIO button path has its own tests in `tests/test_button.py`: with one
  clean edge per press, the code reads every second press as a release, so it cannot drive a round until the
  real button's edges are measured (decision 7).
- **Look at the screens** a change affects: `tests/out/` is gitignored and rewritten on each run.
- **A known bug** gets a test marked `@pytest.mark.xfail(strict=True, reason=...)`; it fails the suite once the
  bug is fixed, so the mark comes off with the fix.

## What the suite does not cover

- **The real pins** (`pi2.py`), real sound (`audio.py`'s `PygameAudio`), `game.main()`, and how the real button
  bounces.
- **The fullscreen size**: the dummy driver has one mode, so only the Pi shows which mode the display picks.

After a change to any of them, deploy to the Pi and play a round ([raspberry-pi.md](raspberry-pi.md)).
`buttonhandler.py`, the buzzer in `pi_sound.py` and `Game.beep_on`/`beep_off` are not used by the game at all.
