from game_executables import GameExecutables
from src.calculations.statistics import get_random_outcome


class GameStateOverride(GameExecutables):
    """
    This class is is used to override or extend universal state.py functions.
    e.g: A specific game may have custom book properties to reset
    """

    def reset_book(self):
        # Reset global values used across multiple projects
        super().reset_book()
        # Reset parameters relevant to local game only
        self.bonus_type = None  # "normal" | "super" | "jackpot"
        self.held = {}  # wilds + scatters that stay during base-game respins
        self.sticky_wilds = {}  # normal free spins
        self.expanded_reels = {}  # super free spins: {reel: multiplier}
        self.activated = set()  # jackpot free spins: activated (reel, row) cells
        self.opened_chests = []  # reels whose chest is open, in opening order
        self.chest_multiplier = 1
        self.raw_win_data = {"totalWin": 0, "wins": []}
        self.ways_total = 0
        self.win_wild_cells = set()

    def assign_special_sym_function(self):
        self.special_symbol_functions = {"W": [self.assign_mult_property]}

    def assign_mult_property(self, symbol):
        """Every wild gets a multiplier from the table of the current game phase."""
        phase = "basegame" if self.gametype == self.config.basegame_type else self.bonus_type
        table = self.get_current_distribution_conditions()["mult_values"][phase]
        symbol.assign_attribute({"multiplier": get_random_outcome(table)})

    def check_repeat(self) -> None:
        """Checks if the spin failed a criteria constraint at any point."""
        if self.repeat is False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True

            if self.get_current_distribution_conditions()["force_freegame"] and not (self.triggered_freegame):
                self.repeat = True

            # "basegame" books are the paying spins without a feature
            if self.criteria == "basegame" and self.win_manager.running_bet_win == 0.0:
                self.repeat = True

        self.repeat_count += 1
        self.check_current_repeat_count()
