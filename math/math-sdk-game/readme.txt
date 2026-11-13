# Wild Respin Chests  (5x4, 1024 ways)

* 5 reels x 4 rows, 1024 ways, wins from left to right (min. 3 reels)
* 13 paying symbols (H1-H5, L1-L8), 1 Wild (reels 2-4 only), 1 Scatter
* Paytable in "x total bet per way", every value is a multiple of 0.1 (RGS payout increments)
* Wincap 50,000x, RTP 96.5 %

# Base game

Wilds carry a multiplier (1x/2x/3x/5x). The multiplier of a board is the SUM of the multipliers of all wilds
that take part in a win (1x wilds add nothing). Scatters pay anywhere (3/4/5 = 1x/5x/25x) on the first board.

WILD RESPIN: a wild that lands NEW and takes part in a win triggers a respin. All wilds (and scatters) stay,
everything else spins again (reel set RR0, no scatters), max. 6 respins in a row.

# Free spins (scatters on the first board)

* 3 scatters  NORMAL  10 spins  Only enhanced wilds (2x/3x/5x/10x) land. They stay sticky until the end.
* 4 scatters  SUPER    7 spins  A landing wild expands over the whole reel (up AND down) and stays sticky.
* 5 scatters  JACKPOT 10 spins  One chest below each reel. Every position that is part of a win is activated.
                                 When all 4 rows of a reel are activated its chest opens (2x-10x).
                                 Chest multipliers are NOT added: they are chained (multiplied) in opening order
                                 (left to right within a spin) and apply to every win from then on.

No retriggers.

# Criteria (see game_config.py / game_optimization.py)

wincap   forced 50,000x rounds (jackpot spins on the wild rich reel set JWC, higher chest weights)
jackpot  5 scatters           super  4 scatters           freegame  3 scatters (normal)
0        no win               basegame  paying spin without feature

# Custom events (game_events.py)

respin, newStickyWilds, expandWilds, activateChestCells, openChest
(+ the standard reveal / winInfo / setWin / setTotalWin / freeSpinTrigger / enterBonus / updateFreeSpin / freeSpinEnd / finalWin)

# Reels

reels/*.csv are exported from the calibration prototype (slot5x4.py): `python slot5x4.py export <folder>`.
