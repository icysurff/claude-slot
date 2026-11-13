<script lang="ts" module>
	export type EmitterEventChestBar =
		| { type: 'chestBarShow' }
		| { type: 'chestBarHide' }
		| { type: 'chestBarReset' }
		| { type: 'chestProgress'; progress: number[] }
		| { type: 'chestOpen'; reel: number; multiplier: number; totalMultiplier: number };
</script>

<script lang="ts">
	import { Container, Sprite, BitmapText, Rectangle } from 'pixi-svelte';
	import { MainContainer } from 'components-layout';
	import { FadeContainer } from 'components-pixi';
	import { waitForTimeout } from 'utils-shared/wait';
	import { stateBet } from 'state-shared';

	import { getContext } from '../game/context';
	import { SYMBOL_SIZE, BOARD_DIMENSIONS } from '../game/constants';
	import { getSymbolX } from '../game/utils';

	const context = getContext();
	const REELS = BOARD_DIMENSIONS.x;
	const ROWS = BOARD_DIMENSIONS.y;

	let show = $state(false);
	let progress = $state<number[]>(Array(REELS).fill(0));
	let openedValues = $state<(number | undefined)[]>(Array(REELS).fill(undefined));
	let pulseReel = $state<number | undefined>(undefined);
	let totalMultiplier = $state(1);

	const reset = () => {
		progress = Array(REELS).fill(0);
		openedValues = Array(REELS).fill(undefined);
		pulseReel = undefined;
		totalMultiplier = 1;
	};

	context.eventEmitter.subscribeOnMount({
		chestBarShow: () => (show = true),
		chestBarHide: () => (show = false),
		chestBarReset: () => reset(),
		chestProgress: ({ progress: next }) => {
			progress = [...next];
		},
		chestOpen: async ({ reel, multiplier, totalMultiplier: total }) => {
			pulseReel = reel;
			context.eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_multiplier_landing' });
			await waitForTimeout(stateBet.isTurbo ? 150 : 600);
			openedValues[reel] = multiplier;
			totalMultiplier = total;
			await waitForTimeout(stateBet.isTurbo ? 150 : 700);
			pulseReel = undefined;
		},
	});

	const chestY = $derived(
		context.stateGameDerived.boardLayout().y +
			context.stateGameDerived.boardLayout().height * 0.5 +
			SYMBOL_SIZE * 0.5,
	);
	const boardLeft = $derived(
		context.stateGameDerived.boardLayout().x - context.stateGameDerived.boardLayout().width * 0.5,
	);
</script>

<FadeContainer {show}>
	<MainContainer>
		<Container x={boardLeft} y={chestY}>
			{#each Array(REELS) as _, reel}
				{@const opened = openedValues[reel] !== undefined}
				<Container x={getSymbolX(reel)} scale={pulseReel === reel ? 1.18 : 1}>
					<Sprite
						anchor={0.5}
						key={opened ? 'chest_open' : progress[reel] > 0 ? 'chest_closed' : 'chest_lock'}
						width={SYMBOL_SIZE * 0.72}
						height={SYMBOL_SIZE * 0.72}
					/>
					{#if opened}
						<BitmapText
							anchor={0.5}
							y={-SYMBOL_SIZE * 0.05}
							text={`${openedValues[reel]}X`}
							style={{ fontFamily: 'gold', fontSize: SYMBOL_SIZE * 0.34 }}
						/>
					{:else}
						<!-- one pip per row of the reel: lit when the cell took part in a win -->
						{#each Array(ROWS) as __, row}
							<Rectangle
								anchor={0.5}
								x={(row - (ROWS - 1) / 2) * SYMBOL_SIZE * 0.2}
								y={SYMBOL_SIZE * 0.4}
								width={SYMBOL_SIZE * 0.14}
								height={SYMBOL_SIZE * 0.14}
								borderRadius={SYMBOL_SIZE * 0.07}
								backgroundColor={row < progress[reel] ? 0xffd54f : 0x37474f}
							/>
						{/each}
					{/if}
				</Container>
			{/each}
			<BitmapText
				anchor={{ x: 0, y: 0.5 }}
				x={getSymbolX(REELS - 0.35)}
				text={`CHAIN ${totalMultiplier}X`}
				style={{ fontFamily: 'gold', fontSize: SYMBOL_SIZE * 0.3 }}
			/>
		</Container>
	</MainContainer>
</FadeContainer>
