<script lang="ts" module>
	export type EmitterEventBoardFrame =
		| { type: 'boardFrameGlowShow' }
		| { type: 'boardFrameGlowHide' };
</script>

<script lang="ts">
	import { Rectangle, Sprite } from 'pixi-svelte';

	import { getContext } from '../game/context';

	const context = getContext();
	let glow = $state(false);

	context.eventEmitter.subscribeOnMount({
		boardFrameGlowShow: () => (glow = true),
		boardFrameGlowHide: () => (glow = false),
	});

	// frame.png is 3020x2638; its transparent window starts at (230, 360) and is 2560x2048
	const FRAME = { width: 3020, height: 2638, innerX: 230, innerY: 360, innerWidth: 2560, innerHeight: 2048 };

	const layout = $derived(context.stateGameDerived.boardLayout());
	const scale = $derived((layout.width * 1.02) / FRAME.innerWidth);
	const centerOffsetY = $derived(
		(FRAME.innerY + FRAME.innerHeight / 2 - FRAME.height / 2) * scale,
	);
</script>

<Rectangle
	anchor={0.5}
	x={layout.x}
	y={layout.y}
	width={layout.width + 6}
	height={layout.height + 6}
	backgroundColor={0x10131c}
	backgroundAlpha={0.9}
	borderColor={glow ? 0xffd54f : 0x10131c}
	borderWidth={glow ? 8 : 0}
/>
<Sprite
	anchor={0.5}
	key="frame"
	x={layout.x}
	y={layout.y - centerOffsetY}
	width={FRAME.width * scale}
	height={FRAME.height * scale}
/>
