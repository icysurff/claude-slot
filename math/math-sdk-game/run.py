"""Main file for generating results for the 5x4 wild-respin game."""
from gamestate import GameState
from game_config import GameConfig
from game_optimization import OptimizationSetup
from optimization_program.run_script import OptimizationExecution
from utils.game_analytics.run_analysis import create_stat_sheet
from utils.rgs_verification import execute_all_tests
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs

if __name__ == "__main__":

    num_threads = 2
    rust_threads = 2
    batching_size = 50000
    compression = True
    profiling = False

    num_sim_args = {
        "base": int(1e5),
        "enhancer": int(1e5),
        "buy_normal": int(2e4),
        "buy_super": int(2e4),
        "buy_jackpot": int(5e4),
        "buy_wildreels": int(3e4),
    }

    run_conditions = {
        "run_sims": True,
        "run_optimization": True,
        "run_analysis": True,
        "run_format_checks": True,
    }
    target_modes = ["base", "enhancer", "buy_normal", "buy_super", "buy_jackpot", "buy_wildreels"]

    config = GameConfig()
    gamestate = GameState(config)
    if run_conditions["run_optimization"] or run_conditions["run_analysis"]:
        optimization_setup_class = OptimizationSetup(config)

    if run_conditions["run_sims"]:
        create_books(
            gamestate,
            config,
            num_sim_args,
            batching_size,
            num_threads,
            compression,
            profiling,
        )

    generate_configs(gamestate)

    if run_conditions["run_optimization"]:
        OptimizationExecution().run_all_modes(config, target_modes, rust_threads)
        generate_configs(gamestate)

    if run_conditions["run_analysis"]:
        custom_keys = [
            {"symbol": "scatter", "kind": "3"},
            {"symbol": "scatter", "kind": "4"},
            {"symbol": "scatter", "kind": "5"},
        ]
        create_stat_sheet(gamestate, custom_keys=custom_keys)

    if run_conditions["run_format_checks"]:
        execute_all_tests(config)
