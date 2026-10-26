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
