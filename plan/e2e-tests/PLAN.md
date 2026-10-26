# Plan: a scripted end-to-end test suite (what is left)

Built on branch `e2e-tests`: the suite (`uv run pytest`, 23 tests and 1 known failure), the parameters it
needs, and its docs ([docs/testing.md](../../docs/testing.md), decisions 5-9 in
[docs/decisions.md](../../docs/decisions.md)). It passes on the Mac and on the Pi. Two items need Drew at the Pi.

## 1. Run the new code on the real hardware

Phase 2 changed how `Game` reaches the button, LEDs and sound; no test touches the real pins or speaker.

1. Merge `e2e-tests` into `main` and push (Drew approves).
2. On the Pi: `git pull --ff-only` in `/home/pi/Documents/halloween-prize-game`, then restart the game.
3. Drew plays two rounds: one stopped by the button, one by the timer.

*Done when* both rounds play with the beeps, the prize sound, the status LED and the four-LED chase.

## 2. Measure the real button's edges (decision 7)

A small script on the Pi logs each edge on the button pin (`config.HW.BUTTON_PIN`) and its time while Drew
presses a few times, with the game stopped so the pin is free. `FakeHardware` then gets a `real_press()` that
makes the same edges, and `tests/test_button.py` records what the game does with them, in place of
`test_every_second_clean_press_is_read_as_a_release`.

*Done when* the fake presses the way the real button does, and the button tests say whether every press
starts or stops a round.

When both are done, this plan is deleted.
