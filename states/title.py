from states.state import State
from states.candy_picker import CandyPicker
from colors import *

class Title(State):
    def __init__(self, game) -> None:
        super().__init__(game)

    def update(self, delta_time, actions):
        if actions["space"] or actions["button"]:
            new_state = CandyPicker(self.game)
            new_state.enter_state()
        self.game.reset_keys()

    def render(self, surface):
        text_color = TEXT_COLOR_1
        fill_color = TEXT_BG_1
        # fill_color = (255, 255, 255)
        alpha = 255
        self.game.draw_text( surface, "Press the BIG BUTTON to start!", text_color, self.game.GAME_W/2, self.game.GAME_H/2, self.game.GAME_DIMENSIONS, fill_color=fill_color, fill_alpha=alpha )