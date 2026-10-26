# halloween-prize-game

A pygame game on a Raspberry Pi 5 that hands out Halloween candy: a child presses a big button, prize
cards spin with beeps and LEDs, and the card it stops on is the prize. This file is the source; `CLAUDE.md`
is a symlink to it, so Claude Code and Codex read the same instructions.

## Before you change anything

1. **Read [docs/README.md](docs/README.md)**, then every note it lists for the subject you are touching: the
   Pi, deploying, or a past decision.
2. **Load the `pygame-core` skill** before you write or change pygame code (`game.py`, `states/`, drawing,
   sound, input).
3. **Load each other skill in `.agents/skills/`** whose description matches the task.

The task starts once each note and skill it touches is in your context.

## Layout

| Path | Holds |
|---|---|
| `game.py` | The `Game` class: the loop, input, drawing helpers, and the switch between real and fake hardware |
| `states/` | One class per screen: `title.py` → `candy_picker.py` (spinning) → `winner.py` → back to title |
| `config.py` | Every setting a person tunes: pins, prize stock, odds, text, timer, sounds |
| `pi2.py`, `buttonhandler.py`, `pi_sound.py` | Real GPIO on the Pi (button, LEDs) through `RPi.GPIO` from `rpi-lgpio` |
| `pi_dev2.py` | Fake GPIO: logs LED changes; the spacebar stands in for the button |
| `picker.py`, `pi.py`, `pi_dev.py` | The first version of the game. `states/candy_picker.py:3` still imports `picker.py`, which opens a fullscreen window as it loads |
| `assets/`, `sounds/` | Prize card images, backgrounds, the font, and sound effects |
| `docs/` | Facts the code does not say: the Pi, decisions. Start at [docs/README.md](docs/README.md) |

## Running it

**On a Mac**, from the repo folder, with dev mode switched on in memory only:

```bash
uv run --no-project --python 3.13 --with pygame==2.6.1 python -c "import config; config.GAME.DEV_MODE = True; config.GAME.FULLSCREEN = False; import game; game.main()"
```

Spacebar is the button; Esc quits. `--no-project` skips `pyproject.toml`, whose `rpi-lgpio` installs only on
the Pi. Add `SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy` in front to run with no window and no sound.

**On the Pi**, `launch.sh` runs `/usr/bin/python3 game.py`: the system Python and Debian's `python3-pygame`,
not `uv` or `pyproject.toml`. Reaching the Pi and deploying to it: [docs/raspberry-pi.md](docs/raspberry-pi.md).

## Rules

- **`config.py` keeps `DEV_MODE = False` and `FULLSCREEN = True` in every commit.** The Pi reads them as
  committed; dev mode there ignores the real button. Switch them in memory, as the Mac command above does.
- **pygame is 2.6.1, not pygame-ce** (Drew, 2026-10-26). The `pygame-core` skill recommends pygame-ce; follow
  its game-loop advice and keep the library this project runs.
- **Drew approves every commit and push.**
- **Size work by complexity and scope**, never by time.
- **Straightforward, not clever**: plain Python a hobbyist can read on the Pi.
- **A fake is passed in as a parameter**, never swapped in by replacing a module. This is the direction for
  hardware, clock, prize pick and sound as tests arrive ([docs/decisions.md](docs/decisions.md)).
- **The Pi's password never goes in the repo.** Agents reach the Pi by SSH key.
- **Docs change in the same commit as the code they describe.** `plan/`, when it exists, holds only what is
  not built yet; a plan's items move into `docs/` or this file as they are built, and the plan is deleted.

## Skills

Project skills live in `.agents/skills/<name>/` (Codex reads them there), with a symlink at
`.claude/skills/<name>` for Claude Code. `skills-lock.json` records each one's source. Add one with
`npx skills add <github-url> --skill <name> -a claude-code -a codex -y`, and read its `SKILL.md` in full first:
a skill runs with the agent's full permissions.
