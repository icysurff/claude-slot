from src.executables.executables import Executables


class GameCalculations(Executables):
    """Helper functions specific to the wild-respin game: wild multipliers and symbol bookkeeping."""

    def wild_object_key(self, reel: int, row: int):
        """A wild that expands over a whole reel is ONE object (counted once for the multiplier)."""
        if self.gametype == self.config.freegame_type and self.bonus_type == "super":
            return reel
        return (reel, row)

    def get_wild_multiplier(self, win_data: dict) -> int:
        """Board multiplier = SUM of the multipliers of all wilds taking part in a win.
        1x wilds add nothing; without any multiplier wild the board multiplier is 1."""
        seen, total = set(), 0
        for win in win_data["wins"]:
            for pos in win["positions"]:
                sym = self.board[pos["reel"]][pos["row"]]
                if sym.name != "W":
                    continue
                key = self.wild_object_key(pos["reel"], pos["row"])
                if key in seen:
                    continue
                seen.add(key)
                mult = sym.get_attribute("multiplier")
                if mult and mult > 1:
                    total += mult
        return max(total, 1)

    def winning_cells(self, win_data: dict, wild_only: bool = False) -> set:
        """Set of (reel, row) positions that are part of any win."""
        cells = set()
        for win in win_data["wins"]:
            for pos in win["positions"]:
                if wild_only and self.board[pos["reel"]][pos["row"]].name != "W":
                    continue
                cells.add((pos["reel"], pos["row"]))
        return cells

    def collect_held(self) -> dict:
        """Wilds and scatters stay in place during a respin. Returns {(reel, row): Symbol}."""
        held = {}
        for reel in range(self.config.num_reels):
            for row in range(self.config.num_rows[reel]):
                if self.board[reel][row].name in ("W", "S"):
                    held[(reel, row)] = self.board[reel][row]
        return held
