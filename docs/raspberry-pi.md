# The Raspberry Pi

The game runs on a Raspberry Pi 5 named `halloween`. Facts below were checked on 2026-10-26.

## Reaching it

| Fact | Value |
|---|---|
| Name on the network | `halloween.local` |
| Address on 2026-10-26 | `192.168.7.231`, given by the router, so it can change; the name does not |
| Hardware address | `2c:cf:67:1a:82:73` (prefix registered to Raspberry Pi Ltd) |
| Login | `ssh pi@halloween.local`; Drew's Mac logs in by its key `~/.ssh/id_ed25519` |
| Password login | Still on, by Drew's choice (see [decisions.md](decisions.md)) |

To find it when the name does not answer: `dns-sd -B _workstation._tcp local.` lists devices by name, and
`arp -a` lists every address the Mac has seen; look for the `2c:cf:67` prefix.

## What it runs

| Fact | Value |
|---|---|
| Operating system | Debian GNU/Linux 13 (trixie) |
| Python | 3.13.5, `/usr/bin/python3` |
| pygame | 2.6.1 from the Debian package `python3-pygame` (SDL 2.32.4) |
| Repo folder | `/home/pi/Documents/halloween-prize-game` |
| Started by | `launch.sh`, from the desktop session: the game's output goes to `~/.xsession-errors`. What starts `launch.sh` at boot is not known: no systemd service names the game and `pi`'s crontab is empty |
| Display | HDMI, "TXD Display"; it prefers 1280x800. The game asks for 1000x666 fullscreen (`config.GAME.FULLSCREEN_MODE`) and gets 1024x768, as `~/.xsession-errors` shows: `Display: 1024x768, Game canvas: 1024x1024, Screen: 1024x768` |

`/home/pi/Documents/halloween-prize-game-backup-20251030-181252` is an old copy whose git history is
damaged (`fatal: bad object HEAD`). Nothing in it is newer than the repo folder.

## Getting code onto it

The Pi has no GitHub login, so it pulls and never pushes:

1. Commit and push from the Mac.
2. On the Pi: `ssh pi@halloween.local 'cd ~/Documents/halloween-prize-game && git pull --ff-only'`.
3. Restart the game, and press the real button to check it.

When the Pi holds commits or edits of its own, carry them to the Mac first: commit on the Pi,
`git bundle create /tmp/x.bundle origin/main..main`, copy the bundle over with `scp`, and
`git pull --ff-only <bundle> main` in the Mac's clone. The commit keeps its id, so the Pi matches GitHub after
the push.

Pins for the button and LEDs are set in `config.py` (`HardwareConfig`).
