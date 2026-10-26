import glob
from asyncio.log import logger

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
    """The prizes for one game: titles, sounds, images, stock and odds, built from PRIZES config."""

    def __init__(self, audio, rng):
        self.rng = rng
        self.titles = {}
        self.sounds = {}
        self.assets = {}
        self.inventory = {}

        self._add(audio, "mini", "mini", PRIZES.MINI_CANDY_INVENTORY)
        if PRIZES.PLAYDOUGH_INVENTORY > 0:
            self._add(audio, "playdough", "playdough", PRIZES.PLAYDOUGH_INVENTORY)
        # Big prize uses the configured type: skull or full_size
        self._add(audio, "big_prize", PRIZES.BIG_PRIZE_TYPE, PRIZES.BIG_PRIZE_INVENTORY)
        self.sounds["beep"] = audio.load(PRIZES.BEEP_SOUND_FILE, PRIZES.DEFAULT_SOUND_VOLUME)

        self.probability = calculate_probabilities(self.inventory)

    def _add(self, audio, key, category_name, stock):
        category = PRIZES.PRIZE_CATEGORIES[category_name]
        self.titles[key] = category["title"]
        self.sounds[key] = audio.load(category["sound_file"], PRIZES.DEFAULT_SOUND_VOLUME)
        self.assets[key] = glob.glob(category["folder"])
        self.inventory[key] = stock

    def pick(self, current_tick, prev_filename):
        """Pick a prize based on configured probabilities and inventory"""

        # Filter out big_prize if minimum spins not reached
        prize_types = list(filter(
            lambda prize: prize != 'big_prize' or current_tick >= PRIZES.MIN_SPINS_FOR_BIG_PRIZE,
            self.probability.keys()
        ))

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
