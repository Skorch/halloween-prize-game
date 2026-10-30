"""The prizes left, kept in a YAML file so the count lasts across restarts and can be changed by hand while the game
runs (docs/prize-stock.md)."""
import logging
import os

import yaml

logger = logging.getLogger()

HEADER = ("# Prizes left. The game reads this at the start of every spin and takes one off each win.\n"
          "# Change a number and it counts from the next spin; no restart needed.\n")


def read(path, last):
    """The stock in the file at `path`, as {prize type: count}, for the prize types in `last`.

    A missing file is written from `last`. A file that will not read (a typo, a missing prize, a negative number) is
    logged and left alone, and `last` is used, so the game plays on.
    """
    if not os.path.exists(path):
        write(path, last)
        return dict(last)
    try:
        with open(path) as f:
            data = yaml.safe_load(f)
        stock = {prize_type: int(data[prize_type]) for prize_type in last}
        if any(count < 0 for count in stock.values()):
            raise ValueError("a count is below 0")
        return stock
    except Exception as e:
        logger.error(f"Stock file {path} will not read, keeping the last stock {last}: {e}")
        return dict(last)


def write(path, stock):
    """Write `stock` to `path`. It goes to a second file first and then replaces the first in one step, so a power cut
    never leaves half a file."""
    part_written = path + ".tmp"
    with open(part_written, "w") as f:
        f.write(HEADER)
        yaml.safe_dump(stock, f, sort_keys=False)
    os.replace(part_written, path)
