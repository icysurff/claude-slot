"""Set conditions/parameters for optimization program program"""

from optimization_program.optimization_config import (
    ConstructScaling,
    ConstructParameters,
    ConstructConditions,
    ConstructFenceBias,
    verify_optimization_input,
)


class OptimizationSetup:
    """Game specific optimization setup.
    Amends game_config.opt_params, which is required to setup maths configuration file.

    The order of the conditions matters: every simulation is assigned to the FIRST criteria that
    matches it. Max wins (jackpot rounds) must therefore be listed before the jackpot criteria.

    RTP split (sums to the bet mode RTP of 0.965):
        wincap     0.005   50,000x
        jackpot    0.070   5 scatters, ~1 in 22,000 spins
        super      0.100   4 scatters, ~1 in 1,000 spins
        freegame   0.200   3 scatters, ~1 in 150 spins (normal free spins)
        basegame   0.590   paying spins without a feature (incl. wild respins), ~1 in 2.8 spins
    """

    def __init__(self, game_config):
        self.game_config = game_config
        wincaps = {}
        for bm in game_config.bet_modes:
            wincaps[bm.get_name()] = bm.get_wincap()

        def params_buy(min_m2m, max_m2m):
            return ConstructParameters(
                num_show=5000,
                num_per_fence=10000,
                min_m2m=min_m2m,
                max_m2m=max_m2m,
                pmb_rtp=1.0,
                sim_trials=5000,
                test_spins=[10, 20, 50],
                test_weights=[0.3, 0.4, 0.3],
                score_type="rtp",
            ).return_dict()

        self.game_config.opt_params = {
            "base": {
                "conditions": {
                    "wincap": ConstructConditions(
                        rtp=0.005, av_win=wincaps["base"], search_conditions=wincaps["base"]
                    ).return_dict(),
                    "jackpot": ConstructConditions(
                        rtp=0.07, hr=22000, search_conditions={"symbol": "scatter", "kind": "5"}
                    ).return_dict(),
                    "super": ConstructConditions(
                        rtp=0.10, hr=1000, search_conditions={"symbol": "scatter", "kind": "4"}
                    ).return_dict(),
                    "freegame": ConstructConditions(
                        rtp=0.20, hr=150, search_conditions={"symbol": "scatter", "kind": "3"}
                    ).return_dict(),
                    "0": ConstructConditions(rtp=0, av_win=0, search_conditions=0).return_dict(),
                    "basegame": ConstructConditions(hr=2.8, rtp=0.59).return_dict(),
                },
                # Without scaling the optimizer favours tiny wins (<1x) and 5-100x wins and leaves a gap at 1-5x.
                # These factors give the paying base spins a smoother shape (tested on 100,000 books).
                "scaling": ConstructScaling(
                    [
                        {"criteria": "basegame", "scale_factor": 0.6, "win_range": (0.1, 0.5), "probability": 1.0},
                        {"criteria": "basegame", "scale_factor": 14.0, "win_range": (1, 2), "probability": 1.0},
                        {"criteria": "basegame", "scale_factor": 10.0, "win_range": (2, 5), "probability": 1.0},
                        {"criteria": "basegame", "scale_factor": 1.2, "win_range": (5, 20), "probability": 1.0},
                        {"criteria": "basegame", "scale_factor": 0.3, "win_range": (20, 100), "probability": 1.0},
                    ]
                ).return_dict(),
                "parameters": ConstructParameters(
                    num_show=5000,
                    num_per_fence=10000,
                    min_m2m=2,
                    max_m2m=14,
                    pmb_rtp=1.0,
                    sim_trials=5000,
                    test_spins=[50, 100, 200],
                    test_weights=[0.3, 0.4, 0.3],
                    score_type="rtp",
                ).return_dict(),
            },

            # Bonus enhancer (cost 1.5x): bonuses ~2.3x as frequent. RTP shares are relative to the cost.
            "enhancer": {
                "conditions": {
                    "wincap": ConstructConditions(
                        rtp=0.0076, av_win=wincaps["enhancer"], search_conditions=wincaps["enhancer"]
                    ).return_dict(),
                    "jackpot": ConstructConditions(
                        rtp=0.1067, hr=9600, search_conditions={"symbol": "scatter", "kind": "5"}
                    ).return_dict(),
                    "super": ConstructConditions(
                        rtp=0.1524, hr=437, search_conditions={"symbol": "scatter", "kind": "4"}
                    ).return_dict(),
                    "freegame": ConstructConditions(
                        rtp=0.3049, hr=66, search_conditions={"symbol": "scatter", "kind": "3"}
                    ).return_dict(),
                    "0": ConstructConditions(rtp=0, av_win=0, search_conditions=0).return_dict(),
                    "basegame": ConstructConditions(hr=2.8, rtp=0.3934).return_dict(),
                },
                "scaling": ConstructScaling(
                    [
                        {"criteria": "basegame", "scale_factor": 0.6, "win_range": (0.1, 0.5), "probability": 1.0},
                        {"criteria": "basegame", "scale_factor": 14.0, "win_range": (1, 2), "probability": 1.0},
                        {"criteria": "basegame", "scale_factor": 10.0, "win_range": (2, 5), "probability": 1.0},
                        {"criteria": "basegame", "scale_factor": 1.2, "win_range": (5, 20), "probability": 1.0},
                        {"criteria": "basegame", "scale_factor": 0.3, "win_range": (20, 100), "probability": 1.0},
                    ]
                ).return_dict(),
                "parameters": ConstructParameters(
                    num_show=5000,
                    num_per_fence=10000,
                    min_m2m=2,
                    max_m2m=14,
                    pmb_rtp=1.0,
                    sim_trials=5000,
                    test_spins=[50, 100, 200],
                    test_weights=[0.3, 0.4, 0.3],
                    score_type="rtp",
                ).return_dict(),
            },
            "buy_normal": {
                "conditions": {"freegame": ConstructConditions(rtp=0.965, hr="x").return_dict()},
                "scaling": ConstructScaling([]).return_dict(),
                "parameters": params_buy(1.1, 6),
            },
            "buy_super": {
                "conditions": {"super": ConstructConditions(rtp=0.965, hr="x").return_dict()},
                "scaling": ConstructScaling([]).return_dict(),
                "parameters": params_buy(1.1, 8),
            },
            "buy_jackpot": {
                "conditions": {
                    "wincap": ConstructConditions(
                        rtp=0.06, av_win=wincaps["buy_jackpot"], search_conditions=wincaps["buy_jackpot"]
                    ).return_dict(),
                    "jackpot": ConstructConditions(rtp=0.905, hr="x").return_dict(),
                },
                "scaling": ConstructScaling([]).return_dict(),
                "parameters": params_buy(1.2, 14),
            },
            "buy_wildreels": {
                "conditions": {
                    "wincap": ConstructConditions(
                        rtp=0.02, av_win=wincaps["buy_wildreels"], search_conditions=wincaps["buy_wildreels"]
                    ).return_dict(),
                    "wildreels": ConstructConditions(rtp=0.945, hr="x").return_dict(),
                },
                "scaling": ConstructScaling([]).return_dict(),
                "parameters": params_buy(1.1, 10),
            },
        }

        verify_optimization_input(self.game_config, self.game_config.opt_params)
