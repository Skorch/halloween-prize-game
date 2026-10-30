# Prize stock

The game keeps the count of prizes left in `stock.yaml`, in the game folder. It reads the file at the start of
every spin and takes one off each win, so the odds follow what is really left, and a number changed in the file counts
from the next spin with no restart. Facts below are from 2026-10-30.

```yaml
# Prizes left. The game reads this at the start of every spin and takes one off each win.
# Change a number and it counts from the next spin; no restart needed.
mini: 200
playdough: 42
big_prize: 48
```

`big_prize` is whichever prize `PRIZES.BIG_PRIZE_TYPE` names in `config.py` (full-size candy, on 2026-10-30).

## How the game uses it

| When | What happens (`prizes.py`, `stock.py`) |
|---|---|
| The title screen starts, and every press on it | The file is read again (`Prizes.refresh`). With every count at 0, the title shows `MESSAGES.OUT_OF_STOCK_MESSAGE` ("Out of candy!") and the button does nothing until a count goes up |
| Each card of a spin | Only prizes with stock above 0 can be picked, each weighted by its count (`USE_INVENTORY_PROBABILITIES`). No big prize before card `MIN_SPINS_FOR_BIG_PRIZE` (5), unless big prizes are all that is left |
| The winner screen starts | The file is read again and the prize won is taken off (`Prizes.take`), so a number set by hand during the spin is kept |
| The file is missing | It is written from the starting stock in `config.py` (`MINI_CANDY_INVENTORY`, `PLAYDOUGH_INVENTORY`, `BIG_PRIZE_INVENTORY`) |
| The file will not read (a typo, a missing prize, a count below 0) | The error is logged and the game keeps the last counts it read; the file is left as it is |

The game writes to `stock.yaml.tmp` and then renames it over `stock.yaml`, so a power cut never leaves half a file.

Git ignores both files: the count belongs to the Pi, and a `git pull` never changes it.

## Restocking

On the Pi, from the Mac:

```sh
ssh pi@halloween.local 'cd ~/Documents/halloween-prize-game && cat stock.yaml'
ssh pi@halloween.local 'cd ~/Documents/halloween-prize-game && sed -i "s/^big_prize: .*/big_prize: 60/" stock.yaml'
```

The game's log (`~/.xsession-errors`, or `~/game.log` when started over SSH) records each win as
`Won <prize>; stock now {...}`.

In tests, `Game(stock_file=None)` keeps the stock in memory only; `tests/test_stock.py` passes a file in a temporary
folder. Only `main()` passes `PRIZES.STOCK_FILE`.
