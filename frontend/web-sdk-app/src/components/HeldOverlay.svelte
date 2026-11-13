<script lang="ts" module>
	import type { HeldSymbol } from '../game/types';

	export type EmitterEventHeldOverlay =
		| { type: 'heldSet'; symbols: HeldSymbol[] }
		| { type: 'heldClear' };
</script>

<script lang="ts">
	import { Container, Rectangle } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { SYMBOL_SIZE } from '../game/constants';
	import { getSymbolX } from '../game/utils';
	import BoardContainer from './BoardContainer.svelte';
	import Symbol from './Symbol.svelte';

	const context = getContext();

	let symbols = $state<HeldSymbol[]>([]);

	context.eventEmitter.subscribeOnMount({
		heldSet: (e) => (symbols = e.symbols),
		heldClear: () => (symbols = []),
	});
</script>

<!-- Held wilds / scatters stay in place while the other symbols spin (rows 1-4, row 0 is padding) -->
<BoardContainer>
	{#each symbols as held (`${held.reel}-${held.row}`)}
		<Container x={getSymbolX(held.reel)} y={(held.row - 0.5) * SYMBOL_SIZE}>
			<Rectangle
				anchor={0.5}
				width={SYMBOL_SIZE * 0.98}
				height={SYMBOL_SIZE * 0.98}
				borderRadius={14}
				backgroundColor={0x0b1020}
				borderColor={0xffd54f}
				borderWidth={3}
			/>
			<Symbol
				state="static"
				rawSymbol={{ name: held.name, multiplier: held.multiplier, wild: held.name === 'W' }}
			/>
		</Container>
	{/each}
</BoardContainer>
