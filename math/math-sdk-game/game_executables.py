"""Executables: ways evaluation with wild multipliers, respin boards, sticky / expanding wilds and chests."""

import random

from game_calculations import GameCalculations
from game_events import (
    activate_chest_cells_event,
    open_chest_event,
    win_info_event,
    set_win_event,
    set_total_event,
)
from src.calculations.ways import Ways
from src.calculations.statistics import get_random_outcome


class GameExecutables(GameCalculations):
    """Game specific actions used by gamestate.py."""

    # ------------------------------------------------------------------ boards
    def draw_reel_set(self, reel_id: str) -> None:
        """Draw a board from a specific reel set, regardless of the criteria's reel weights."""
        conditions = self.get_current_distribution_conditions()
        saved = conditions["reel_weights"]
        conditions["reel_weights"] = {self.gametype: {reel_id: 1}}
        try:
            self.create_board_reelstrips()
        finally:
            conditions["reel_weights"] = saved

    def respin_board(self) -> None:
        """New board from the respin reels (no scatters). Held wilds and scatters are put back."""
        self.draw_reel_set("RR0")
        for (reel, row), sym in self.held.items():
            self.board[reel][row] = sym
        self.get_special_symbols_on_board()

    def overlay_sticky_wilds(self) -> None:
        """Normal free spins: previously landed wilds keep their place and multiplier."""
        for (reel, row), sym in self.sticky_wilds.items():
            self.board[reel][row] = sym
        self.get_special_symbols_on_board()

    def register_new_sticky_wilds(self) -> list:
        """Every wild on the board that is not sticky yet becomes sticky. Returns [(reel, row, mult)]."""
        new = []
        for reel in range(self.config.num_reels):
            for row in range(self.config.num_rows[reel]):
                sym = self.board[reel][row]
                if sym.name == "W" and (reel, row) not in self.sticky_wilds:
                    self.sticky_wilds[(reel, row)] = sym
                    new.append((reel, row, sym.get_attribute("multiplier")))
        return new

    def apply_expanded_reels(self) -> None:
        """Super free spins: expanded reels are completely wild (all rows, same multiplier)."""
        for reel, mult in self.expanded_reels.items():
            for row in range(self.config.num_rows[reel]):
                wild = self.symbol_storage.create_symbol("W")
                wild.assign_attribute({"multiplier": mult})
                self.board[reel][row] = wild
        self.get_special_symbols_on_board()

    def find_new_expansions(self) -> list:
        """A wild on a not yet expanded reel expands. Returns [(reel, landing_row, mult)]."""
        new = []
        for reel in range(self.config.num_reels):
            if reel in self.expanded_reels:
                continue
            for row in range(self.config.num_rows[reel]):
                sym = self.board[reel][row]
                if sym.name == "W":
                    mult = sym.get_attribute("multiplier")
                    self.expanded_reels[reel] = mult
                    new.append((reel, row, mult))
                    break
        return new

    def force_wild_reels(self) -> None:
        """'Wild reels' buy: two random reels out of 2-4 become full wild reels, every wild >= 10x."""
        table = self.get_current_distribution_conditions()["mult_values"]["wildreels"]
        for reel in random.sample([1, 2, 3], 2):
            for row in range(self.config.num_rows[reel]):
                wild = self.symbol_storage.create_symbol("W")
                wild.assign_attribute({"multiplier": get_random_outcome(table)})
                self.board[reel][row] = wild
        self.get_special_symbols_on_board()

    # -------------------------------------------------------------------- wins
    def evaluate_raw(self) -> dict:
        """Ways wins without any multiplier. Used to find the wilds / cells taking part in wins."""
        self.raw_win_data = Ways.get_ways_data(
            self.config, self.board, multiplier_strategy="global", global_multiplier=1
        )
        return self.raw_win_data

    def add_scatter_win(self) -> None:
        """Scatters pay anywhere (not multiplied). Only called for the first board of a base spin."""
        count = self.count_special_symbols("scatter")
        if count < 3:
            return
        pay = self.config.scatter_pay[min(count, 5)]
        self.win_data["wins"].append(
            {
                "symbol": "S",
                "kind": count,
                "win": pay,
                "positions": [dict(p) for p in self.special_syms_on_board["scatter"]],
                "meta": {"ways": 0, "globalMult": 1, "winWithoutMult": pay, "symbolMult": 0},
            }
        )
        self.win_data["totalWin"] += pay

    def finalize_ways_win(self, include_scatter: bool = False, extra_mult: int = 1) -> None:
        """Apply wild (and chest) multipliers, update the win manager and emit the win events."""
        raw = self.raw_win_data
        total_mult = self.get_wild_multiplier(raw) * extra_mult
        if raw["totalWin"] > 0 and total_mult > 1:
            self.win_data = Ways.get_ways_data(
                self.config, self.board, multiplier_strategy="global", global_multiplier=total_mult
            )
        else:
            self.win_data = raw
        self.ways_total = self.win_data["totalWin"]  # ways only (decides respins)
        self.win_wild_cells = self.winning_cells(self.win_data, wild_only=True)
        if self.ways_total > 0:
            Ways.record_ways_wins(self)
        if include_scatter:
            self.add_scatter_win()
        if self.win_data["totalWin"] > 0:
            self.win_manager.update_spinwin(self.win_data["totalWin"])
            win_info_event(self)
            self.evaluate_wincap()
            set_win_event(self)
        set_total_event(self)

    # ------------------------------------------------------------------ chests
    def activate_chest_cells(self, win_data: dict) -> None:
        new_cells = sorted(self.winning_cells(win_data) - self.activated)
        if not new_cells:
            return
        self.activated.update(new_cells)
        progress = [
            sum(1 for row in range(self.config.num_rows[reel]) if (reel, row) in self.activated)
            for reel in range(self.config.num_reels)
        ]
        activate_chest_cells_event(self, new_cells, progress)

    def open_ready_chests(self) -> None:
        """A chest opens as soon as every row of its reel has been part of a win.
        Chests open left to right; their multipliers are chained (multiplied)."""
        for reel in range(self.config.num_reels):
            if reel in self.opened_chests:
                continue
            if all((reel, row) in self.activated for row in range(self.config.num_rows[reel])):
                value = get_random_outcome(self.get_current_distribution_conditions()["chest_values"])
                self.opened_chests.append(reel)
                self.chest_multiplier *= value
                open_chest_event(self, reel, value, self.chest_multiplier)
