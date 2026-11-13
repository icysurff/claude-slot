import _ from 'lodash';

import type { RawSymbol, SymbolState } from './types';

export const SYMBOL_SIZE = 100;

export const REEL_PADDING = 0.53;

// initial board (padded top and bottom)
export const INITIAL_BOARD: RawSymbol[][] = [
	[{ name: 'L1' }, { name: 'L2' }, { name: 'L3' }, { name: 'L4' }, { name: 'L5' }, { name: 'L6' }],
	[{ name: 'L4' }, { name: 'L5' }, { name: 'L6' }, { name: 'L7' }, { name: 'L8' }, { name: 'H1' }],
	[{ name: 'L7' }, { name: 'L8' }, { name: 'H1' }, { name: 'H2' }, { name: 'H3' }, { name: 'H4' }],
	[{ name: 'H2' }, { name: 'H3' }, { name: 'H4' }, { name: 'H5' }, { name: 'L1' }, { name: 'L2' }],
	[{ name: 'H5' }, { name: 'L1' }, { name: 'L2' }, { name: 'L3' }, { name: 'L4' }, { name: 'L5' }],
];

export const BOARD_DIMENSIONS = { x: INITIAL_BOARD.length, y: INITIAL_BOARD[0].length - 2 };

export const BOARD_SIZES = {
	width: SYMBOL_SIZE * BOARD_DIMENSIONS.x,
	height: SYMBOL_SIZE * BOARD_DIMENSIONS.y,
};

export const BACKGROUND_RATIO = 2039 / 1000;
export const PORTRAIT_BACKGROUND_RATIO = 1242 / 2208;
const PORTRAIT_RATIO = 800 / 1422;
const LANDSCAPE_RATIO = 1600 / 900;
const DESKTOP_RATIO = 1422 / 800;

const DESKTOP_HEIGHT = 800;
const LANDSCAPE_HEIGHT = 900;
const PORTRAIT_HEIGHT = 1422;
export const DESKTOP_MAIN_SIZES = { width: DESKTOP_HEIGHT * DESKTOP_RATIO, height: DESKTOP_HEIGHT };
export const LANDSCAPE_MAIN_SIZES = {
	width: LANDSCAPE_HEIGHT * LANDSCAPE_RATIO,
	height: LANDSCAPE_HEIGHT,
};
export const PORTRAIT_MAIN_SIZES = {
	width: PORTRAIT_HEIGHT * PORTRAIT_RATIO,
	height: PORTRAIT_HEIGHT,
};

export const HIGH_SYMBOLS = ['H1', 'H2', 'H3', 'H4', 'H5'];

export const CHEST_VALUES_TEXT = 'x2 – x10';

export const INITIAL_SYMBOL_STATE: SymbolState = 'static';


const SPIN_OPTIONS_SHARED = {
	reelFallInDelay: 80,
	reelPaddingMultiplierNormal: 1.25,
	reelPaddingMultiplierAnticipated: 18,
	reelFallOutDelay: 145,
};

export const SPIN_OPTIONS_DEFAULT = {
	...SPIN_OPTIONS_SHARED,
	symbolFallInSpeed: 3.5,
	symbolFallInInterval: 30,
	symbolFallInBounceSpeed: 0.15,
	symbolFallInBounceSizeMulti: 0.5,
	symbolFallOutSpeed: 3.5,
	symbolFallOutInterval: 20,
};

export const SPIN_OPTIONS_FAST = {
	...SPIN_OPTIONS_SHARED,
	symbolFallInSpeed: 7,
	symbolFallInInterval: 0,
	symbolFallInBounceSpeed: 0.3,
	symbolFallInBounceSizeMulti: 0.25,
	symbolFallOutSpeed: 7,
	symbolFallOutInterval: 0,
};

export const MOTION_BLUR_VELOCITY = 31;

export const zIndexes = {
	background: {
		backdrop: -3,
		normal: -2,
		feature: -1,
	},
};

const spriteInfo = (name: string) => ({ type: 'sprite', assetKey: `sym_${name}`, sizeRatios: { width: 0.92, height: 0.92 } }) as const;

export const SYMBOL_INFO_MAP = {
	W: {
		explosion: spriteInfo('W'),
		win: spriteInfo('W'),
		postWinStatic: spriteInfo('W'),
		static: spriteInfo('W'),
		spin: spriteInfo('W'),
		land: spriteInfo('W'),
	},
	S: {
		explosion: spriteInfo('S'),
		win: spriteInfo('S'),
		postWinStatic: spriteInfo('S'),
		static: spriteInfo('S'),
		spin: spriteInfo('S'),
		land: spriteInfo('S'),
	},
	H1: {
		explosion: spriteInfo('H1'),
		win: spriteInfo('H1'),
		postWinStatic: spriteInfo('H1'),
		static: spriteInfo('H1'),
		spin: spriteInfo('H1'),
		land: spriteInfo('H1'),
	},
	H2: {
		explosion: spriteInfo('H2'),
		win: spriteInfo('H2'),
		postWinStatic: spriteInfo('H2'),
		static: spriteInfo('H2'),
		spin: spriteInfo('H2'),
		land: spriteInfo('H2'),
	},
	H3: {
		explosion: spriteInfo('H3'),
		win: spriteInfo('H3'),
		postWinStatic: spriteInfo('H3'),
		static: spriteInfo('H3'),
		spin: spriteInfo('H3'),
		land: spriteInfo('H3'),
	},
	H4: {
		explosion: spriteInfo('H4'),
		win: spriteInfo('H4'),
		postWinStatic: spriteInfo('H4'),
		static: spriteInfo('H4'),
		spin: spriteInfo('H4'),
		land: spriteInfo('H4'),
	},
	H5: {
		explosion: spriteInfo('H5'),
		win: spriteInfo('H5'),
		postWinStatic: spriteInfo('H5'),
		static: spriteInfo('H5'),
		spin: spriteInfo('H5'),
		land: spriteInfo('H5'),
	},
	L1: {
		explosion: spriteInfo('L1'),
		win: spriteInfo('L1'),
		postWinStatic: spriteInfo('L1'),
		static: spriteInfo('L1'),
		spin: spriteInfo('L1'),
		land: spriteInfo('L1'),
	},
	L2: {
		explosion: spriteInfo('L2'),
		win: spriteInfo('L2'),
		postWinStatic: spriteInfo('L2'),
		static: spriteInfo('L2'),
		spin: spriteInfo('L2'),
		land: spriteInfo('L2'),
	},
	L3: {
		explosion: spriteInfo('L3'),
		win: spriteInfo('L3'),
		postWinStatic: spriteInfo('L3'),
		static: spriteInfo('L3'),
		spin: spriteInfo('L3'),
		land: spriteInfo('L3'),
	},
	L4: {
		explosion: spriteInfo('L4'),
		win: spriteInfo('L4'),
		postWinStatic: spriteInfo('L4'),
		static: spriteInfo('L4'),
		spin: spriteInfo('L4'),
		land: spriteInfo('L4'),
	},
	L5: {
		explosion: spriteInfo('L5'),
		win: spriteInfo('L5'),
		postWinStatic: spriteInfo('L5'),
		static: spriteInfo('L5'),
		spin: spriteInfo('L5'),
		land: spriteInfo('L5'),
	},
	L6: {
		explosion: spriteInfo('L6'),
		win: spriteInfo('L6'),
		postWinStatic: spriteInfo('L6'),
		static: spriteInfo('L6'),
		spin: spriteInfo('L6'),
		land: spriteInfo('L6'),
	},
	L7: {
		explosion: spriteInfo('L7'),
		win: spriteInfo('L7'),
		postWinStatic: spriteInfo('L7'),
		static: spriteInfo('L7'),
		spin: spriteInfo('L7'),
		land: spriteInfo('L7'),
	},
	L8: {
		explosion: spriteInfo('L8'),
		win: spriteInfo('L8'),
		postWinStatic: spriteInfo('L8'),
		static: spriteInfo('L8'),
		spin: spriteInfo('L8'),
		land: spriteInfo('L8'),
	},
} as const;

export const SCATTER_LAND_SOUND_MAP = {
	1: 'sfx_scatter_stop_1',
	2: 'sfx_scatter_stop_2',
	3: 'sfx_scatter_stop_3',
	4: 'sfx_scatter_stop_4',
	5: 'sfx_scatter_stop_5',
} as const;
