# docs

Facts about this project that the code does not say, kept true in the same commit as the code they
describe. The first reader is a coding agent, which reads the note for a subject before it changes code
there; Drew is the second. `AGENTS.md` and `CLAUDE.md` in this folder are symlinks to this file.

| File | Holds |
|---|---|
| [raspberry-pi.md](raspberry-pi.md) | The Pi itself: how to reach it, what it runs, how code gets onto it |
| [testing.md](testing.md) | The scripted test suite: how it runs, its fakes, and how to add a test |
| [light-strip.md](light-strip.md) | The LED strip behind the screen: its scenes, wiring, and how the Pi sends it colours |
| [prize-stock.md](prize-stock.md) | The prizes left: `stock.yaml` on the Pi, how the game counts down in it, and restocking |
| [decisions.md](decisions.md) | Each decision Drew made, with its date; appended, never rewritten |

## Where a new fact goes

1. **A decision Drew made**: a new entry at the end of `decisions.md`, then state its effect where it now
   belongs (`AGENTS.md`, a note here, or the code).
2. **A fact about a subject a note already covers**: update that note.
3. **A new subject**: a new note, one subject per file, with its line in the table above.
