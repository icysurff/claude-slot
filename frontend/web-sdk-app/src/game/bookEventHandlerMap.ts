import _ from 'lodash';

import { recordBookEvent, checkIsMultipleRevealEvents, type BookEventHandlerMap } from 'utils-book';
import { stateBet } from 'state-shared';
import { sequence } from 'utils-shared/sequence';

import { eventEmitter } from './eventEmitter';
import { playBookEvent } from './utils';
import { winLevelMap, type WinLevel, type WinLevelData } from './winLevelMap';
import { stateGame, stateGameDerived } from './stateGame.svelte';
import type { BookEvent, BookEventOfType, BookEventContext } from './typesBookEvent';
import type { Position } from './types';
import { BOARD_DIMENSIONS } from './constants';

const winLevelSoundsPlay = ({ winLevelData }: { winLevelData: WinLevelData }) => {
	if (winLevelData?.alias === 'max') eventEmitter.broadcastAsync({ type: 'uiHide' });
	if (winLevelData?.sound?.sfx) {
		eventEmitter.broadcast({ type: 'soundOnce', name: winLevelData.sound.sfx });
	}
	if (winLevelData?.sound?.bgm) {
		eventEmitter.broadcast({ type: 'soundMusic', name: winLevelData.sound.bgm });
	}
	if (winLevelData?.type === 'big') {
		eventEmitter.broadcast({ type: 'soundLoop', name: 'sfx_bigwin_coinloop' });
	}
};

const winLevelSoundsStop = () => {
	eventEmitter.broadcast({ type: 'soundStop', name: 'sfx_bigwin_coinloop' });
	if (stateBet.activeBetModeKey === 'SUPERSPIN' || stateGame.gameType === 'freegame') {
		// check if SUPERSPIN, when finishing a bet.
		eventEmitter.broadcast({ type: 'soundMusic', name: 'bgm_freespin' });
	} else {
		eventEmitter.broadcast({ type: 'soundMusic', name: 'bgm_main' });
	}
	eventEmitter.broadcastAsync({ type: 'uiShow' });
};

const animateSymbols = async ({ positions }: { positions: Position[] }) => {
	eventEmitter.broadcast({ type: 'boardShow' });
	await eventEmitter.broadcastAsync({
		type: 'boardWithAnimateSymbols',
		symbolPositions: positions,
	});
};

export const bookEventHandlerMap: BookEventHandlerMap<BookEvent, BookEventContext> = {
	reveal: async (bookEvent: BookEventOfType<'reveal'>, { bookEvents }: BookEventContext) => {
		const isBonusGame = checkIsMultipleRevealEvents({ bookEvents });
		if (isBonusGame) {
			eventEmitter.broadcast({ type: 'stopButtonEnable' });
			recordBookEvent({ bookEvent });
		}

		stateGame.gameType = bookEvent.gameType;
		await stateGameDerived.enhancedBoard.spin({ revealEvent: bookEvent });
		eventEmitter.broadcast({ type: 'heldClear' });
		eventEmitter.broadcast({ type: 'soundScatterCounterClear' });

		// "wild reels" buy: two reels land completely wild
		const wildReels = bookEvent.board.filter((reel) =>
			reel.slice(1, 1 + BOARD_DIMENSIONS.y).every((symbol) => symbol.name === 'W'),
		).length;
		if (bookEvent.gameType === 'basegame' && wildReels >= 2) {
			await eventEmitter.broadcastAsync({ type: 'bannerShow', text: `${wildReels} WILD REELS` });
		}
	},
	winInfo: async (bookEvent: BookEventOfType<'winInfo'>) => {
		eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_winlevel_small' });
		await sequence(bookEvent.wins, async (win) => {
			await animateSymbols({ positions: win.positions });
		});
	},
	setTotalWin: async (bookEvent: BookEventOfType<'setTotalWin'>) => {
		stateBet.winBookEventAmount = bookEvent.amount;
	},
	freeSpinTrigger: async (bookEvent: BookEventOfType<'freeSpinTrigger'>) => {
		// animate scatters
		eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_scatter_win_v2' });
		await animateSymbols({ positions: bookEvent.positions });
		// show free spin intro
		eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_superfreespin' });
		await eventEmitter.broadcastAsync({ type: 'uiHide' });
		await eventEmitter.broadcastAsync({ type: 'transition' });
		eventEmitter.broadcast({ type: 'freeSpinIntroShow' });
		eventEmitter.broadcast({ type: 'soundOnce', name: 'jng_intro_fs' });
		eventEmitter.broadcast({ type: 'soundMusic', name: 'bgm_freespin' });
		await eventEmitter.broadcastAsync({
			type: 'freeSpinIntroUpdate',
			totalFreeSpins: bookEvent.totalFs,
			// 3 / 4 / 5 scatters = normal / super / jackpot
			bonusType: ({ 3: 'normal', 4: 'super', 5: 'jackpot' } as const)[
				bookEvent.positions.length as 3 | 4 | 5
			],
		});
		stateGame.gameType = 'freegame';
		eventEmitter.broadcast({ type: 'freeSpinIntroHide' });
		eventEmitter.broadcast({ type: 'boardFrameGlowShow' });
		eventEmitter.broadcast({ type: 'freeSpinCounterShow' });
		eventEmitter.broadcast({
			type: 'freeSpinCounterUpdate',
			current: undefined,
			total: bookEvent.totalFs,
		});
		await eventEmitter.broadcastAsync({ type: 'uiShow' });
		await eventEmitter.broadcastAsync({ type: 'drawerButtonShow' });
		eventEmitter.broadcast({ type: 'drawerFold' });
	},
	updateFreeSpin: async (bookEvent: BookEventOfType<'updateFreeSpin'>) => {
		eventEmitter.broadcast({ type: 'freeSpinCounterShow' });
		eventEmitter.broadcast({
			type: 'freeSpinCounterUpdate',
			current: bookEvent.amount,
			total: bookEvent.total,
		});
	},
	freeSpinEnd: async (bookEvent: BookEventOfType<'freeSpinEnd'>) => {
		const winLevelData = winLevelMap[bookEvent.winLevel as WinLevel];

		await eventEmitter.broadcastAsync({ type: 'uiHide' });
		stateGame.gameType = 'basegame';
		eventEmitter.broadcast({ type: 'expandedClear' });
		eventEmitter.broadcast({ type: 'bonusTypeSet', bonusType: undefined });
		eventEmitter.broadcast({ type: 'chestBarHide' });
		eventEmitter.broadcast({ type: 'boardFrameGlowHide' });
		eventEmitter.broadcast({ type: 'freeSpinOutroShow' });
		eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_youwon_panel' });
		winLevelSoundsPlay({ winLevelData });
		await eventEmitter.broadcastAsync({
			type: 'freeSpinOutroCountUp',
			amount: bookEvent.amount,
			winLevelData,
		});
		winLevelSoundsStop();
		eventEmitter.broadcast({ type: 'freeSpinOutroHide' });
		eventEmitter.broadcast({ type: 'freeSpinCounterHide' });
		await eventEmitter.broadcastAsync({ type: 'transition' });
		await eventEmitter.broadcastAsync({ type: 'uiShow' });
		await eventEmitter.broadcastAsync({ type: 'drawerUnfold' });
		eventEmitter.broadcast({ type: 'drawerButtonHide' });
	},
	setWin: async (bookEvent: BookEventOfType<'setWin'>) => {
		const winLevelData = winLevelMap[bookEvent.winLevel as WinLevel];

		eventEmitter.broadcast({ type: 'winShow' });
		winLevelSoundsPlay({ winLevelData });
		await eventEmitter.broadcastAsync({
			type: 'winUpdate',
			amount: bookEvent.amount,
			winLevelData,
		});
		winLevelSoundsStop();
		eventEmitter.broadcast({ type: 'winHide' });
	},
	finalWin: async (bookEvent: BookEventOfType<'finalWin'>) => {
		// Do nothing
	},
	// wild respin game
	respin: async (bookEvent: BookEventOfType<'respin'>) => {
		eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_multiplier_landing' });
		eventEmitter.broadcast({ type: 'heldSet', symbols: bookEvent.heldSymbols });
		await eventEmitter.broadcastAsync({
			type: 'bannerShow',
			text: `RESPIN ${bookEvent.respinNumber}`,
		});
	},
	enterBonus: async (bookEvent: BookEventOfType<'enterBonus'>) => {
		eventEmitter.broadcast({ type: 'expandedClear' });
		eventEmitter.broadcast({ type: 'bonusTypeSet', bonusType: bookEvent.reason });
		eventEmitter.broadcast({ type: 'chestBarReset' });
		if (bookEvent.reason === 'jackpot') eventEmitter.broadcast({ type: 'chestBarShow' });
		else eventEmitter.broadcast({ type: 'chestBarHide' });
	},
	newStickyWilds: async (bookEvent: BookEventOfType<'newStickyWilds'>) => {
		eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_multiplier_landing' });
		await eventEmitter.broadcastAsync({
			type: 'boardWithAnimateSymbols',
			symbolPositions: bookEvent.newWilds,
		});
	},
	expandWilds: async (bookEvent: BookEventOfType<'expandWilds'>) => {
		eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_multiplier_landing' });
		// every wild that lands turns its whole reel into wilds (rows 1..4, row 0/5 are padding)
		for (const wild of bookEvent.expandingWilds) {
			const reel = stateGame.board[wild.reel].reelState.symbols;
			for (let row = 1; row <= BOARD_DIMENSIONS.y; row++) {
				reel[row].rawSymbol = { name: 'W', wild: true, multiplier: wild.multiplier };
			}
		}
		eventEmitter.broadcast({
			type: 'expandedAdd',
			reels: bookEvent.expandingWilds.map((w) => ({ reel: w.reel, multiplier: w.multiplier })),
		});
		await eventEmitter.broadcastAsync({
			type: 'boardWithAnimateSymbols',
			symbolPositions: bookEvent.expandingWilds.flatMap((wild) =>
				_.range(1, BOARD_DIMENSIONS.y + 1).map((row) => ({ reel: wild.reel, row })),
			),
		});
	},
	activateChestCells: async (bookEvent: BookEventOfType<'activateChestCells'>) => {
		eventEmitter.broadcast({ type: 'chestProgress', progress: bookEvent.progress });
		await eventEmitter.broadcastAsync({
			type: 'boardWithAnimateSymbols',
			symbolPositions: bookEvent.cells,
		});
	},
	openChest: async (bookEvent: BookEventOfType<'openChest'>) => {
		await eventEmitter.broadcastAsync({
			type: 'chestOpen',
			reel: bookEvent.reel,
			multiplier: bookEvent.multiplier,
			totalMultiplier: bookEvent.totalMultiplier,
		});
	},
	wincap: async () => {
		await eventEmitter.broadcastAsync({ type: 'bannerShow', text: 'MAX WIN 50,000X', durationMs: 1800 });
	},
	// customised
	createBonusSnapshot: async (bookEvent: BookEventOfType<'createBonusSnapshot'>) => {
		const { bookEvents } = bookEvent;

		function findLastBookEvent<T>(type: T) {
			return _.findLast(bookEvents, (bookEvent) => bookEvent.type === type) as
				| BookEventOfType<T>
				| undefined;
		}

		const lastFreeSpinTriggerEvent = findLastBookEvent('freeSpinTrigger' as const);
		const lastUpdateFreeSpinEvent = findLastBookEvent('updateFreeSpin' as const);
		const lastSetTotalWinEvent = findLastBookEvent('setTotalWin' as const);
		const lastEnterBonusEvent = findLastBookEvent('enterBonus' as const);

		if (lastFreeSpinTriggerEvent) await playBookEvent(lastFreeSpinTriggerEvent, { bookEvents });
		if (lastUpdateFreeSpinEvent) playBookEvent(lastUpdateFreeSpinEvent, { bookEvents });
		if (lastSetTotalWinEvent) playBookEvent(lastSetTotalWinEvent, { bookEvents });
		if (lastEnterBonusEvent) await playBookEvent(lastEnterBonusEvent, { bookEvents });
	},
};
