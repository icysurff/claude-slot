"""Game logic and event emission for the 5x4 wild-respin game.

Base game   1024 ways, wilds (with multipliers) that take part in a win trigger a respin.
3 scatters  NORMAL  free spins: only enhanced wilds (2x-10x) land and stay sticky.
4 scatters  SUPER   free spins: landing wilds expand over the whole reel and stay.
5 scatters  JACKPOT free spins: chests below the reels, chained 2x-10x multipliers.
"""

from game_override import GameStateOverride
from game_events import (
    respin_event,
    new_sticky_wilds_event,
    expand_wilds_event,
    enter_bonus_event,
    reveal_event,
)


class GameState(GameStateOverride):
    """Handle basegame and freegame logic."""

    def run_spin(self, sim: int, simulation_seed=None) -> None:
        self.reset_seed(sim)
        self.repeat = True
        while self.repeat:
            self.reset_book()
            self.run_base_round()
            self.win_manager.update_gametype_wins(self.gametype)

            # Scatters of the first board (held during respins) decide the bonus type
            if self.check_fs_condition() and self.check_freespin_entry():
                self.bonus_type = self.config.bonus_type_by_scatters[min(self.count_special_symbols("scatter"), 5)]
                self.run_freespin_from_base()

            self.evaluate_finalwin()
            self.check_repeat()

        self.imprint_wins()

    # ------------------------------------------------------------------ base game
    def run_base_round(self) -> None:
        """First board + wild respins. A wild that lands NEW and takes part in a win starts a respin."""
        if self.betmode == self.config.wildreels_mode:
            self.draw_board(emit_event=False)
            self.force_wild_reels()
            reveal_event(self)
        else:
            self.draw_board(emit_event=True)
        self.evaluate_raw()
        self.finalize_ways_win(include_scatter=True)

        self.held = self.collect_held()
        new_wilds = {cell for cell, sym in self.held.items() if sym.name == "W"}
        respins = 0
        while (
            self.ways_total > 0
            and (self.win_wild_cells & new_wilds)
            and respins < self.config.max_respins
            and not self.wincap_triggered
            and self.betmode != self.config.wildreels_mode  # wild reels buy: one board, no respins
        ):
            respins += 1
            before = set(self.held)
            respin_event(self, respins, self.held)
            self.respin_board()
            reveal_event(self)
            self.held = self.collect_held()
            new_wilds = {cell for cell, sym in self.held.items() if sym.name == "W" and cell not in before}
            self.evaluate_raw()
            self.finalize_ways_win(include_scatter=False)

    # ------------------------------------------------------------------ free games
    def run_freespin(self) -> None:
        enter_bonus_event(self)
        self.reset_fs_spin()
        self.sticky_wilds = {}
        self.expanded_reels = {}
        self.activated = set()
        self.opened_chests = []
        self.chest_multiplier = 1

        while self.fs < self.tot_fs and not self.wincap_triggered:
            self.update_freespin()
            if self.bonus_type == "normal":
                self.play_normal_spin()
            elif self.bonus_type == "super":
                self.play_super_spin()
            else:
                self.play_jackpot_spin()
            self.win_manager.update_gametype_wins(self.gametype)
        self.end_freespin()

    def play_normal_spin(self) -> None:
        """Enhanced wilds (2x-10x) land and stay until the end of the bonus."""
        self.create_board_reelstrips()
        self.overlay_sticky_wilds()
        reveal_event(self)
        new = self.register_new_sticky_wilds()
        if new:
            new_sticky_wilds_event(self, new)
        self.evaluate_raw()
        self.finalize_ways_win()

    def play_super_spin(self) -> None:
        """Landing wilds expand over the whole reel (up and down) and stay until the end."""
        self.create_board_reelstrips()
        self.apply_expanded_reels()
        reveal_event(self)
        new = self.find_new_expansions()
        if new:
            self.apply_expanded_reels()
            expand_wilds_event(self, new)
        self.evaluate_raw()
        self.finalize_ways_win()

    def play_jackpot_spin(self) -> None:
        """Winning positions activate chest cells; a full reel opens its chest. Chest multipliers chain."""
        self.create_board_reelstrips()
        reveal_event(self)
        self.evaluate_raw()
        self.activate_chest_cells(self.raw_win_data)
        self.open_ready_chests()
        self.finalize_ways_win(extra_mult=self.chest_multiplier)
