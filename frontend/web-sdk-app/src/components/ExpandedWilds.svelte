<script lang="ts" module>
	export type EmitterEventExpandedWilds =
		| { type: 'expandedAdd'; reels: { reel: number; multiplier: number }[] }
		| { type: 'expandedClear' };
</script>

<script lang="ts">
	import { Container, Sprite, Rectangle, BitmapText } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { SYMBOL_SIZE } from '../game/constants';
	import { getSymbolX } from '../game/utils';
	import BoardContainer from './BoardContainer.svelte';

	const context = getContext();

	// W_expanded.png is 512x2048; its gold frame is 466x2002 and starts at (23, 23)
	const ART = { width: 512, height: 2048, frameWidth: 466 };
	const scale = (SYMBOL_SIZE * 0.92) / ART.frameWidth;
	// the big badge of the art sits at (261, 1884): we cover it with our own multiplier badge
	const badgeY = (1884 - ART.height / 2) * scale;

	let reels = $state<{ reel: number; multiplier: number }[]>([]);

	context.eventEmitter.subscribeOnMount({
		expandedAdd: (e) => {
			const known = new Set(reels.map((r) => r.reel));
			reels = [...reels, ...e.reels.filter((r) => !known.has(r.reel))];
		},
		expandedClear: () => (reels = []),
	});
</script>

<!-- A wild that expanded: the whole reel (rows 1-4) is one tall wild with a single multiplier -->
<BoardContainer>
	{#each reels as item (item.reel)}
		<Container x={getSymbolX(item.reel)} y={2 * SYMBOL_SIZE}>
			<Sprite
				anchor={0.5}
				key="W_expanded"
				width={ART.width * scale}
				height={ART.height * scale}
			/>
			<Container y={badgeY}>
				<Rectangle
					anchor={0.5}
					width={SYMBOL_SIZE * 0.6}
					height={SYMBOL_SIZE * 0.34}
					backgroundColor={0x111111}
					borderRadius={12}
					borderColor={0xffd54f}
					borderWidth={3}
				/>
				<BitmapText
					anchor={0.5}
					text={`${item.multiplier}X`}
					style={{ fontFamily: 'gold', fontSize: SYMBOL_SIZE * 0.28 }}
				/>
			</Container>
		</Container>
	{/each}
</BoardContainer>
