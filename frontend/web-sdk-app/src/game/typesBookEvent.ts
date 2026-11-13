import type { BetType } from 'rgs-requests';

import type {
	SymbolName,
	RawSymbol,
	GameType,
	Position,
	BonusType,
	WildPosition,
	HeldSymbol,
} from './types';

// book events shared with scatter game
type BookEventReveal = {
	index: number;
	type: 'reveal';
	board: RawSymbol[][];
	paddingPositions: number[];
	anticipation: number[];
	gameType: GameType;
};

type BookEventSetTotalWin = {
	index: number;
	type: 'setTotalWin';
	amount: number;
};

type BookEventFinalWin = {
	index: number;
	type: 'finalWin';
	amount: number;
};

type BookEventFreeSpinTrigger = {
	index: number;
	type: 'freeSpinTrigger';
	totalFs: number;
	positions: Position[];
};

type BookEventUpdateFreeSpin = {
	index: number;
	type: 'updateFreeSpin';
	amount: number;
	total: number;
};

type BookEventSetWin = {
	index: number;
	type: 'setWin';
	amount: number;
	winLevel: number;
};

type BookEventFreeSpinEnd = {
	index: number;
	type: 'freeSpinEnd';
	amount: number;
	winLevel: number;
};

type BookEventWinInfo = {
	index: number;
	type: 'winInfo';
	totalWin: number;
	wins: {
		symbol: SymbolName;
		kind: number;
		win: number;
		positions: Position[];
		meta: {
			ways: number;
			globalMult: number;
			winWithoutMult: number;
			symbolMult: number;
		};
	}[];
};

// wild respin game
type BookEventEnterBonus = { index: number; type: 'enterBonus'; reason: BonusType };
type BookEventRespin = {
	index: number;
	type: 'respin';
	respinNumber: number;
	heldSymbols: HeldSymbol[];
};
type BookEventNewStickyWilds = { index: number; type: 'newStickyWilds'; newWilds: WildPosition[] };
type BookEventExpandWilds = { index: number; type: 'expandWilds'; expandingWilds: WildPosition[] };
type BookEventActivateChestCells = {
	index: number;
	type: 'activateChestCells';
	cells: Position[];
	progress: number[];
};
type BookEventOpenChest = {
	index: number;
	type: 'openChest';
	reel: number;
	multiplier: number;
	totalMultiplier: number;
};
type BookEventWincap = { index: number; type: 'wincap'; amount: number };

// customised
type BookEventCreateBonusSnapshot = {
	index: number;
	type: 'createBonusSnapshot';
	bookEvents: BookEvent[];
};

export type BookEvent =
	| BookEventReveal
	| BookEventWinInfo
	| BookEventSetTotalWin
	| BookEventFreeSpinTrigger
	| BookEventUpdateFreeSpin
	| BookEventCreateBonusSnapshot
	| BookEventFinalWin
	| BookEventSetWin
	| BookEventFreeSpinEnd
	| BookEventEnterBonus
	| BookEventRespin
	| BookEventNewStickyWilds
	| BookEventExpandWilds
	| BookEventActivateChestCells
	| BookEventOpenChest
	| BookEventWincap;

export type Bet = BetType<BookEvent>;
export type BookEventOfType<T> = Extract<BookEvent, { type: T }>;
export type BookEventContext = { bookEvents: BookEvent[] };
