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
| Video decoding | PyAV 14.2.0 (`python3-av`) and numpy 2.2.4 (`python3-numpy`), both already installed; `pyproject.toml` pins the same versions for the Mac |
| Memory | 4 GB, 3.3 GB free with the game running (2026-10-26) |
| Idle video's cost | The curtain clip and the show in `assets/idle/` (420 frames: 60 + 360) decode once at startup. The game then holds 1.94 GB, leaving 1.59 GB available (2026-10-26, branch `title-show-v2`). Decoding alone runs at about 70 frames a second (measured on a 960x960 clip), against the 30 the video plays at |
| Processor use | One core at 17% on the title screen, with each frame sent to the display once; 30% before that change, and 105% before the loop was capped at 30 frames a second (2026-10-26; the game's own processor time from `/proc/<pid>/stat` over 66 s, three title loops) |
| Restarting the game over SSH | `XAUTHORITY=/home/pi/.Xauthority WAYLAND_DISPLAY=wayland-0 XDG_RUNTIME_DIR=/run/user/1000 setsid nohup ./launch.sh > ~/game.log 2>&1 < /dev/null &` from the repo folder starts it on the display; the SSH command does not return by itself afterwards, and stopping it leaves the game running |
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

## The button

The big button bounces: each press flickers on and off for 0.06 to 0.23 s (two presses measured on
2026-10-26). The game logs every edge it sees, with the time since the last press, as `button_pressed: ...
butonDT ...` lines in `~/.xsession-errors`; `tests/fakes.py` (`RECORDED_PRESSES`) holds those two presses.
