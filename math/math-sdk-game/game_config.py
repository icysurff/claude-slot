"""Configuration for the 5x4 Wild-Respin game with Normal / Super / Jackpot free spins."""

import os
from src.config.config import Config
from src.config.distributions import Distribution
from src.config.betmode import BetMode


class GameConfig(Config):
    """Game specific configuration class."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.game_id = "0_0_wildrespin"
        self.provider_number = 0
        self.working_name = "Wild Respin Chests"
        self.wincap = 50000
        self.win_type = "ways"
        self.rtp = 0.965
        self.construct_paths()

        # Game dimensions: 5 reels x 4 rows = 1024 ways
        self.num_reels = 5
        self.num_rows = [4] * self.num_reels

        # Paytable: x total bet PER WAY. All values are multiples of 0.1 (RGS payout increments).
        self.paytable = {
            (5, "H1"): 20.0,
            (4, "H1"): 5.0,
            (3, "H1"): 2.5,
            (5, "H2"): 12.0,
            (4, "H2"): 3.0,
            (3, "H2"): 1.5,
            (5, "H3"): 6.0,
            (4, "H3"): 2.0,
            (3, "H3"): 1.0,
            (5, "H4"): 4.0,
            (4, "H4"): 1.2,
            (3, "H4"): 0.6,
            (5, "H5"): 2.5,
            (4, "H5"): 0.8,
            (3, "H5"): 0.4,
            (5, "L1"): 1.2,
            (4, "L1"): 0.5,
            (3, "L1"): 0.3,
            (5, "L2"): 0.8,
            (4, "L2"): 0.4,
            (3, "L2"): 0.2,
            (5, "L3"): 0.6,
            (4, "L3"): 0.3,
            (3, "L3"): 0.2,
            (5, "L4"): 0.5,
            (4, "L4"): 0.3,
            (3, "L4"): 0.1,
            (5, "L5"): 0.3,
            (4, "L5"): 0.2,
            (3, "L5"): 0.1,
            (5, "L6"): 0.3,
            (4, "L6"): 0.2,
            (3, "L6"): 0.1,
            (5, "L7"): 0.2,
            (4, "L7"): 0.1,
            (3, "L7"): 0.1,
            (5, "L8"): 0.2,
            (4, "L8"): 0.1,
            (3, "L8"): 0.1,
        }
        # Scatter pays anywhere (x total bet). Only evaluated on the first board of a base spin.
        self.scatter_pay = {3: 1.0, 4: 5.0, 5: 25.0}

        self.include_padding = True
        self.special_symbols = {"wild": ["W"], "scatter": ["S"], "multiplier": []}

        # Scatter count on the first board -> number of free spins (3 = normal, 4 = super, 5 = jackpot)
        self.freespin_triggers = {
            self.basegame_type: {3: 10, 4: 7, 5: 10},
            self.freegame_type: {},  # no retriggers
        }
        self.bonus_type_by_scatters = {3: "normal", 4: "super", 5: "jackpot"}
        self.anticipation_triggers = {self.basegame_type: 2, self.freegame_type: 99}

        # Wild respins in the base game
        self.max_respins = 6
        # Chests: one chest per reel, all rows of a reel must have been part of a win
        self.chest_rows_required = self.num_rows[0]

        # Reels
        reels = {
            "BR0": "BR0.csv",  # base game first board
            "RR0": "RR0.csv",  # base game respin boards (no scatters)
            "NFR": "NFR.csv",  # normal free spins (sticky enhanced wilds)
            "SFR": "SFR.csv",  # super free spins (expanding sticky wilds)
            "JFR": "JFR.csv",  # jackpot free spins (chests)
            "JWC": "JWC.csv",  # jackpot free spins, wild rich (used for max-win rounds)
        }
        self.reels = {}
        for r, f in reels.items():
            self.reels[r] = self.read_reels_csv(os.path.join(self.reels_path, f))

        # Wild multiplier weights per game phase. Win multiplier of a board = SUM of the multipliers
        # of all wilds that take part in a win (1x wilds add nothing).
        mult_values = {
            "basegame": {1: 60, 2: 24, 3: 10, 5: 6},
            "normal": {2: 60, 3: 25, 5: 12, 10: 3},
            "super": {1: 35, 2: 35, 3: 20, 5: 10},
            "jackpot": {1: 60, 2: 24, 3: 10, 5: 6},
            # the two forced full wild reels of the "wild reels" buy: every wild is at least 10x
            "wildreels": {10: 60, 15: 25, 25: 12, 50: 3},
        }
        # Chest multipliers 2x-10x. They are applied one after another (multiplied, never added).
        chest_values = {2: 10, 3: 12, 4: 14, 5: 14, 6: 14, 7: 12, 8: 10, 9: 8, 10: 6}
        chest_values_wincap = {2: 2, 3: 4, 4: 6, 5: 9, 6: 12, 7: 15, 8: 17, 9: 17, 10: 18}

        mode_maxwins = {"base": 50000}

        def cond(reels, mult_tbl=None, **extra):
            """Distribution conditions shared by all modes."""
            c = {
                "reel_weights": reels,
                "force_wincap": False,
                "force_freegame": False,
                "mult_values": mult_values,
                "chest_values": chest_values,
            }
            c.update(extra)
            return c

        bg = {self.basegame_type: {"BR0": 1}}

        def bonus_dist(kind, quota):
            """Distribution that forces a bonus of a given kind (used by base mode, enhancer and buys)."""
            table = {
                "freegame": ("NFR", 3, False),
                "super": ("SFR", 4, False),
                "jackpot": ("JFR", 5, False),
                "wincap": ("JWC", 5, True),
            }
            fg_reel, scatters, wincap = table[kind]
            return Distribution(
                criteria=kind,
                quota=quota,
                win_criteria=mode_maxwins["base"] if wincap else None,
                conditions=cond(
                    {self.basegame_type: {"BR0": 1}, self.freegame_type: {fg_reel: 1}},
                    force_wincap=wincap,
                    force_freegame=True,
                    scatter_triggers={scatters: 1},
                    chest_values=chest_values_wincap if wincap else chest_values,
                ),
            )

        def plain_dists(q0, qbase):
            return [
                Distribution(criteria="0", quota=q0, win_criteria=0.0, conditions=cond(bg)),
                Distribution(criteria="basegame", quota=qbase, conditions=cond(bg)),
            ]

        self.mode_names = {
            "base": "base",
            "enhancer": "enhancer",
            "buy_normal": "buy_normal",
            "buy_super": "buy_super",
            "buy_jackpot": "buy_jackpot",
            "buy_wildreels": "buy_wildreels",
        }
        self.wildreels_mode = "buy_wildreels"

        # Prices of the buys = average win of the bought feature / 0.965 (see game_optimization.py).
        self.bet_modes = [
            BetMode(
                name="base",
                cost=1.0,
                rtp=self.rtp,
                max_win=mode_maxwins["base"],
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    bonus_dist("wincap", 0.002),
                    bonus_dist("jackpot", 0.04),
                    bonus_dist("super", 0.06),
                    bonus_dist("freegame", 0.15),
                    *plain_dists(0.3, 0.448),
                ],
            ),
            # Bonus enhancer: costs 1.5x, bonuses come ~2.3x as often. Same books, different weights.
            BetMode(
                name="enhancer",
                cost=1.5,
                rtp=self.rtp,
                max_win=mode_maxwins["base"],
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    bonus_dist("wincap", 0.002),
                    bonus_dist("jackpot", 0.04),
                    bonus_dist("super", 0.06),
                    bonus_dist("freegame", 0.15),
                    *plain_dists(0.2, 0.548),
                ],
            ),
            BetMode(
                name="buy_normal",
                cost=31.0,
                rtp=self.rtp,
                max_win=mode_maxwins["base"],
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[bonus_dist("freegame", 1.0)],
            ),
            BetMode(
                name="buy_super",
                cost=104.0,
                rtp=self.rtp,
                max_win=mode_maxwins["base"],
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[bonus_dist("super", 1.0)],
            ),
            BetMode(
                name="buy_jackpot",
                cost=1700.0,
                rtp=self.rtp,
                max_win=mode_maxwins["base"],
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[bonus_dist("wincap", 0.004), bonus_dist("jackpot", 0.996)],
            ),
            # Two random full wild reels (reels 2-4) with wilds of at least 10x on the first board.
            BetMode(
                name="buy_wildreels",
                cost=2600.0,
                rtp=self.rtp,
                max_win=mode_maxwins["base"],
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="wincap",
                        quota=0.02,
                        win_criteria=mode_maxwins["base"],
                        conditions=cond(bg, force_wincap=True),
                    ),
                    Distribution(criteria="wildreels", quota=0.98, conditions=cond(bg)),
                ],
            ),
        ]
