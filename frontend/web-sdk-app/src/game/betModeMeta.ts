import type { BetModeMeta } from 'state-shared';

// Costs must match the bet modes of the math (games/0_0_wildrespin/game_config.py).
export const BET_MODE_COSTS = {
	enhancer: 1.5,
	buy_normal: 31,
	buy_super: 104,
	buy_jackpot: 1700,
	buy_wildreels: 2600,
} as const;

const NO_ASSETS = { icon: '', dialogImage: '', dialogVolatility: '', volatility: '', button: '' };

const buy = (
	mode: keyof typeof BET_MODE_COSTS,
	title: string,
	description: string,
	dialog: string,
) => ({
	mode,
	costMultiplier: BET_MODE_COSTS[mode],
	type: 'buy' as const,
	parent: '',
	children: '',
	maxWin: 50000,
	assets: NO_ASSETS,
	text: {
		title,
		description,
		dialog,
		button: 'BUY',
		betAmountLabel: title,
		tickerIdle: title,
		tickerSpin: 'GOOD LUCK',
	},
});

export const BET_MODE_META: BetModeMeta = {
	BASE: {
		mode: 'BASE',
		costMultiplier: 1,
		type: 'default',
		parent: '',
		children: '',
		maxWin: 50000,
		assets: NO_ASSETS,
		text: { title: '', dialog: '', button: '', betAmountLabel: '', tickerIdle: '', tickerSpin: '' },
	},
	enhancer: {
		mode: 'enhancer',
		costMultiplier: BET_MODE_COSTS.enhancer,
		type: 'activate',
		parent: '',
		children: '',
		maxWin: 50000,
		assets: NO_ASSETS,
		text: {
			title: 'BONUS ENHANCER',
			description: 'About 2.3x the chance to trigger a bonus. Every spin costs 1.5x your bet.',
			dialog:
				'Activate the BONUS ENHANCER: bonus rounds (free spins, super and jackpot spins) come about 2.3 times as often. Each spin costs 150% of your bet. It stays on until you switch it off.',
			button: 'ACTIVATE',
			betAmountLabel: 'ENHANCER',
			tickerIdle: 'BONUS ENHANCER IS ACTIVE',
			tickerSpin: 'GOOD LUCK',
		},
	},
	buy_normal: buy(
		'buy_normal',
		'BUY FREE SPINS',
		'10 free spins. Enhanced wilds (2x-10x) land and stay.',
		'Buy the normal FREE SPINS round (3 scatters, 10 spins, sticky wilds with 2x-10x).',
	),
	buy_super: buy(
		'buy_super',
		'BUY SUPER SPINS',
		'7 super spins. Wilds expand over the whole reel and stay.',
		'Buy the SUPER FREE SPINS round (4 scatters, 7 spins, expanding sticky wilds).',
	),
	buy_jackpot: buy(
		'buy_jackpot',
		'BUY JACKPOT SPINS',
		'10 jackpot spins. Open chests below the reels for chained 2x-10x multipliers.',
		'Buy the JACKPOT SPINS round (5 scatters, 10 spins). Win every row of a reel to open its chest; chest multipliers are chained.',
	),
	buy_wildreels: buy(
		'buy_wildreels',
		'BUY WILD REELS',
		'Two random reels full of wilds, each at least 10x. Multipliers add up. One board, no respins.',
		'Two random reels (2-4) land full of wilds, every wild at least 10x. The multipliers of all winning wilds are added and apply to every win, to the single board (no respins).',
	),
};
