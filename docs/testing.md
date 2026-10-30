# Testing

`uv run pytest` plays whole rounds of the game with no window and no sound, on fakes, and finishes in about
nine seconds on the Mac, most of it decoding the title screen's clips. It also passed on the Pi (2026-10-26,
in a scratch environment with pytest added), before the clips were added.

## How a test controls the game

`Game` takes everything it reaches outside itself as a parameter, so a test passes stand-ins from
`tests/fakes.py`:

| Parameter | On the Pi | In a test | What the test does with it |
|---|---|---|---|
| `hardware` | the `pi2` module | `FakeHardware` | reads `calls` (every LED change) and `strip` (the light strip's colours, one list each frame, kept apart from `calls`); `edge(high)` and `clean_press()` drive the game's button callback |
| `clock` | `time.time` | `FakeClock` | `advance(seconds)`; nothing in the game waits on real time |
| `rng` | `random.Random()` | `random.Random(seed)` or `ScriptedPicks([...])` | a seed gives the same picks every run; `ScriptedPicks` names each prize type in order |
| `audio` | `PygameAudio` | `FakeAudio` | reads `played`, the file name of each sound in order; `looping`, the sound looping now or `None`; and `show`, the show's soundtrack or `None` |
| `fullscreen` | `True` | `False` | |
| `idle_video_files` | `(VISUAL.IDLE_CURTAIN_FILE, VISUAL.IDLE_SHOW_FILE)` | `None`, unless the test passes a pair | `None` shows the still background. Decoding the 12 s show takes seconds, so most video and sound tests pass the 2 s curtain clip as both clips; only `test_title_shows_the_curtains_then_the_show_then_the_curtains` and `test_game_runs_a_frame_on_fakes` decode the real show |
| `idle_sound_file` | `VISUAL.IDLE_SOUND_FILE` | the same, unless the test passes `None` | `FakeAudio` loads it as its file name, so the title's loop shows in `looping` |
| `show_outputs` | `False` (`True` in dev mode) | `False`, unless the test passes `True` | draws every LED as a dot in the mat; `game.output_dot_centres(size)` says where |
| `show_sound_file` | `VISUAL.IDLE_SHOW_SOUND_FILE` | the same, unless the test passes `None` | `FakeAudio` records it in `show` and counts it in `shows_started` each time a show begins |

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
- **Round tests press the spacebar.** The GPIO button path has its own tests in `tests/test_button.py`, which
  replay presses recorded from the real button (`hardware.recorded_press(clock, RECORDED_PRESSES[0])`). A press
  with one clean edge (`clean_press()`) behaves differently: the code reads every second one as a release.
- **Look at the screens** a change affects: `tests/out/` is gitignored and rewritten on each run.
- **A known bug** gets a test marked `@pytest.mark.xfail(strict=True, reason=...)`; it fails the suite once the
  bug is fixed, so the mark comes off with the fix.

## What the suite does not cover

- **The real pins** (`pi2.py`), including the light strip's signal reaching the strip, its timing, and the game
  playing on when SPI will not open (`tests/test_lights.py` checks the bytes `strip_bytes` makes), real sound (`audio.py`'s `PygameAudio`, which SDL's `dummy` driver plays into
  nothing), and `game.main()`. Four tests in `tests/test_idle_sound.py` use `PygameAudio` on that driver to check
  which mixer channel each sound plays on; only the Pi shows how the sounds sound together. The button's
  bounce is covered only as far as the two recorded presses go.
- **The fullscreen size**: the dummy driver has one mode, so only the Pi shows which mode the display picks.

After a change to any of them, deploy to the Pi and play a round ([raspberry-pi.md](raspberry-pi.md)).
`buttonhandler.py`, the buzzer in `pi_sound.py` and `Game.beep_on`/`beep_off` are not used by the game at all.
