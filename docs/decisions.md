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
