"""Custom events for wild respins, sticky / expanding wilds and the jackpot chests.

All row indices are shifted by +1 when `include_padding` is on, like the standard events do
(row 0 of a client board is the padding symbol above the visible reels).
"""

from src.events.events import *  # noqa: F401,F403  (re-export the standard events)

RESPIN = "respin"
NEW_STICKY_WILDS = "newStickyWilds"
EXPAND_WILDS = "expandWilds"
ACTIVATE_CHEST_CELLS = "activateChestCells"
OPEN_CHEST = "openChest"


def _row_offset(gamestate) -> int:
    return 1 if gamestate.config.include_padding else 0


def respin_event(gamestate, respin_number: int, held: dict) -> None:
    """A wild took part in a win: all wilds (and scatters) stay, the rest spins again.
    `held` maps (reel, row) -> Symbol."""
    off = _row_offset(gamestate)
    symbols = []
    for (reel, row), sym in sorted(held.items()):
        entry = {"reel": reel, "row": row + off, "name": sym.name}
        if sym.name == "W":
            entry["multiplier"] = sym.get_attribute("multiplier")
        symbols.append(entry)
    gamestate.book.add_event(
        {
            "index": len(gamestate.book.events),
            "type": RESPIN,
            "respinNumber": respin_number,
            "heldSymbols": symbols,
        }
    )


def new_sticky_wilds_event(gamestate, new_cells: list) -> None:
    """Normal free spins: wilds that just landed now stay for the rest of the bonus.
    `new_cells` is a list of (reel, row, multiplier)."""
    off = _row_offset(gamestate)
    gamestate.book.add_event(
        {
            "index": len(gamestate.book.events),
            "type": NEW_STICKY_WILDS,
            "newWilds": [{"reel": r, "row": row + off, "multiplier": m} for r, row, m in new_cells],
        }
    )


def expand_wilds_event(gamestate, new_expansions: list) -> None:
    """Super free spins: a landed wild expands over the whole reel (up and down) and stays.
    `new_expansions` is a list of (reel, landing_row, multiplier)."""
    off = _row_offset(gamestate)
    gamestate.book.add_event(
        {
            "index": len(gamestate.book.events),
            "type": EXPAND_WILDS,
            "expandingWilds": [{"reel": r, "row": row + off, "multiplier": m} for r, row, m in new_expansions],
        }
    )


def activate_chest_cells_event(gamestate, new_cells: list, progress: list) -> None:
    """Jackpot free spins: board positions that were part of a win are activated.
    `progress[reel]` is the number of activated rows on that reel (chest opens at the full row count)."""
    off = _row_offset(gamestate)
    gamestate.book.add_event(
        {
            "index": len(gamestate.book.events),
            "type": ACTIVATE_CHEST_CELLS,
            "cells": [{"reel": r, "row": row + off} for r, row in new_cells],
            "progress": list(progress),
        }
    )


def open_chest_event(gamestate, reel: int, value: int, total_multiplier: int) -> None:
    """A chest opens. Chest multipliers are chained (multiplied), `totalMultiplier` is the running product."""
    gamestate.book.add_event(
        {
            "index": len(gamestate.book.events),
            "type": OPEN_CHEST,
            "reel": reel,
            "multiplier": int(value),
            "totalMultiplier": int(total_multiplier),
        }
    )
