<script lang="ts">
	import { onMount } from 'svelte';
	import { Container, Sprite, Rectangle, BitmapText } from 'pixi-svelte';
	import { stateBet } from 'state-shared';

	import { getSymbolInfo } from '../game/utils';
	import { SYMBOL_SIZE } from '../game/constants';
	import type { SymbolState, RawSymbol } from '../game/types';

	type Props = {
		x?: number;
		y?: number;
		state: SymbolState;
		rawSymbol: RawSymbol;
		oncomplete?: () => void;
		loop?: boolean;
	};

	const props: Props = $props();
	const symbolInfo = $derived(getSymbolInfo({ rawSymbol: props.rawSymbol, state: props.state }));
	const isWild = $derived(props.rawSymbol.name === 'W');
	const isWin = $derived(props.state === 'win');
	const scale = $derived(isWin ? 1.12 : 1);
	const showMultiplier = $derived(
		props.rawSymbol.name === 'W' && (props.rawSymbol.multiplier ?? 1) > 1,
	);

	// symbols have no spine animations: "win" and "land" end after a short pulse
	$effect(() => {
		if (props.state !== 'win' && props.state !== 'land') return;
		const timer = setTimeout(() => props.oncomplete?.(), stateBet.isTurbo ? 120 : 520);
		return () => clearTimeout(timer);
	});

	onMount(() => {
		if (props.state !== 'win' && props.state !== 'land') props.oncomplete?.();
	});
</script>

<Container x={props.x} y={props.y} scale={scale}>
	<Sprite
		anchor={0.5}
		key={symbolInfo.assetKey}
		width={SYMBOL_SIZE * symbolInfo.sizeRatios.width * (isWild ? 1.176 : 1)}
		height={SYMBOL_SIZE * symbolInfo.sizeRatios.height * (isWild ? 1.176 : 1)}
	/>
	{#if showMultiplier}
		<Rectangle
			anchor={0.5}
			x={SYMBOL_SIZE * 0.26}
			y={SYMBOL_SIZE * 0.3}
			width={SYMBOL_SIZE * 0.5}
			height={SYMBOL_SIZE * 0.3}
			backgroundColor={0x111111}
			borderRadius={12}
			borderColor={0xffd54f}
			borderWidth={3}
		/>
		<BitmapText
			anchor={0.5}
			x={SYMBOL_SIZE * 0.26}
			y={SYMBOL_SIZE * 0.3}
			text={`${props.rawSymbol.multiplier}X`}
			style={{ fontFamily: 'gold', fontSize: SYMBOL_SIZE * 0.24 }}
		/>
	{/if}
</Container>
