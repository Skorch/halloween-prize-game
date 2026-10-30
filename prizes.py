import glob
from asyncio.log import logger

import stock
from config import PRIZES


def calculate_probabilities(inventory):
    """Calculate probabilities based on remaining inventory"""
    if not PRIZES.USE_INVENTORY_PROBABILITIES:
        # Use fixed probabilities
        return PRIZES.FIXED_PROBABILITIES.copy()

    # Calculate inventory-based probabilities
    total = sum(inventory.values())
    if total == 0:
        # Fallback if somehow all inventory is zero
        logger.warning("All prize inventory is zero! Using equal probabilities")
        return {key: 1.0 / len(inventory) for key in inventory.keys()}

    # Probability proportional to inventory
    probabilities = {key: count / total for key, count in inventory.items()}
    logger.debug(f"Calculated probabilities from inventory: {probabilities}")
    return probabilities


class Prizes:
    """The prizes for one game: titles, sounds, images, stock and odds, built from PRIZES config.

    stock_file: the YAML file that keeps the stock (stock.py); None keeps it in memory only, from PRIZES config
    """

    def __init__(self, audio, rng, stock_file=None):
        self.rng = rng
        self.stock_file = stock_file
        self.titles = {}
        self.sounds = {}
        self.assets = {}
        self.inventory = {}

        # Every prize stays in the game at 0, so it can be restocked
        self._add(audio, "mini", "mini", PRIZES.MINI_CANDY_INVENTORY)
        self._add(audio, "playdough", "playdough", PRIZES.PLAYDOUGH_INVENTORY)
        # Big prize uses the configured type: skull or full_size
        self._add(audio, "big_prize", PRIZES.BIG_PRIZE_TYPE, PRIZES.BIG_PRIZE_INVENTORY)
        self.sounds["beep"] = audio.load(PRIZES.BEEP_SOUND_FILE, PRIZES.DEFAULT_SOUND_VOLUME)

        self.refresh()

    def refresh(self):
        """Read the stock file again, so a number set by hand counts, and work the odds out from it."""
        if self.stock_file:
            self.inventory = stock.read(self.stock_file, self.inventory)
        self.probability = calculate_probabilities(self.inventory)

    def out_of_stock(self):
        return sum(self.inventory.values()) == 0

    def take(self, prize_type):
        """One `prize_type` was won: take it off the stock, and off the file."""
        self.refresh()   # read first, so a number set by hand during the spin is kept
        self.inventory[prize_type] = max(0, self.inventory[prize_type] - 1)
        if self.stock_file:
            stock.write(self.stock_file, self.inventory)
        self.probability = calculate_probabilities(self.inventory)
        logger.info(f"Won {prize_type}; stock now {self.inventory}")

    def _add(self, audio, key, category_name, stock):
        category = PRIZES.PRIZE_CATEGORIES[category_name]
        self.titles[key] = category["title"]
        self.sounds[key] = audio.load(category["sound_file"], PRIZES.DEFAULT_SOUND_VOLUME)
        self.assets[key] = glob.glob(category["folder"])
        self.inventory[key] = stock

    def pick(self, current_tick, prev_filename):
        """Pick a prize based on configured probabilities and inventory"""

        # Only prizes in stock, and no big_prize before the minimum spins, unless big prizes are all that is left
        in_stock = [prize for prize in self.probability if self.inventory[prize] > 0]
        prize_types = [prize for prize in in_stock
                       if prize != 'big_prize' or current_tick >= PRIZES.MIN_SPINS_FOR_BIG_PRIZE]
        if not prize_types:
            prize_types = in_stock

        # Get weights for filtered prize types
        weights = [self.probability[prize] for prize in prize_types]

        # Pick a prize type
        pick = self.rng.choices(prize_types, weights=weights)[0]
        logger.info(f"Prize picked: {pick} (tick {current_tick})")

        # Select a random image file for this prize type
        next_filename = None
        while not next_filename:
            file_choice = self.rng.choice(self.assets[pick])
            if file_choice and file_choice != prev_filename:
                next_filename = file_choice

        return {
            "type": pick,
            "filename": next_filename,
            "title": self.titles[pick],
            "sound": self.sounds[pick]
        }
