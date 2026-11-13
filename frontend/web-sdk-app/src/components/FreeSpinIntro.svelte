<script lang="ts" module>
	import type { BonusType } from '../game/types';

	export type EmitterEventFreeSpinIntro =
		| { type: 'freeSpinIntroShow' }
		| { type: 'freeSpinIntroHide' }
		| { type: 'freeSpinIntroUpdate'; totalFreeSpins: number; bonusType?: BonusType };
</script>

<script lang="ts">
	import { CanvasSizeRectangle, MainContainer } from 'components-layout';
	import { stateUrlDerived } from 'state-shared';
	import { FadeContainer } from 'components-pixi';
	import { waitForResolve } from 'utils-shared/wait';
	import { BitmapText, Container, SpineProvider, SpineSlot, SpineTrack, Sprite } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import PressToContinue from './PressToContinue.svelte';
	import FreeSpinAnimation from './FreeSpinAnimation.svelte';

	type AnimationName = 'intro' | 'idle';

	const context = getContext();

	let show = $state(false);
	let animationName = $state<AnimationName>('intro');
	let freeSpinsFromEvent = $state(0);
	let bonusTitle = $state('');
	let bonusSubtitle = $state('');
	let oncomplete = $state(() => {});

	context.eventEmitter.subscribeOnMount({
		freeSpinIntroShow: () => (show = true),
		freeSpinIntroHide: () => (show = false),
		freeSpinIntroUpdate: async (emitterEvent) => {
			// if (emitterEvent.extraSpins) {
			// 	context.eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_fs_respins' });
			// }
			// freeSpinsFromEvent = emitterEvent.extraSpins ?? emitterEvent.totalFreeSpins;
			freeSpinsFromEvent = emitterEvent.totalFreeSpins;
			const info = {
				normal: ['FREE SPINS', 'Sticky wilds 2x-10x'],
				super: ['SUPER FREE SPINS', 'Wilds expand over the whole reel and stay'],
				jackpot: ['JACKPOT SPINS', 'Win a full reel to open its chest - multipliers chain'],
			} as const;
			[bonusTitle, bonusSubtitle] = emitterEvent.bonusType ? info[emitterEvent.bonusType] : ['', ''];
			await waitForResolve((resolve) => (oncomplete = resolve));
		},
	});
</script>

<FadeContainer {show}>
	<CanvasSizeRectangle backgroundColor={0x000000} backgroundAlpha={0.5} />

	<FreeSpinAnimation>
		{#snippet children({ sizes })}
			<Sprite
				anchor={{ x: 0.5, y: 1.2 }}
				width={500 * 2.2}
				height={156 * 2.2}
				key="freespins_{stateUrlDerived.lang()}.png"
			/>

			<SpineProvider key="fsIntroNumber" width={sizes.width * 0.3}>
				<SpineTrack
					trackIndex={0}
					{animationName}
					loop={animationName === 'idle'}
					listener={{
						complete: () => (animationName = 'idle'),
					}}
				/>
				<SpineSlot slotName="slot_number">
					<BitmapText
						anchor={{ x: 0.5, y: 0.5 }}
						text={freeSpinsFromEvent}
						style={{
							fontFamily: 'gold',
							fontSize: sizes.width * 0.1,
							fontWeight: 'bold',
						}}
					/>
				</SpineSlot>
			</SpineProvider>

			<Sprite anchor={{ x: 0.5, y: -3 }} width={183 * 2.2} height={42 * 2.2} key="freespins.png" />
		{/snippet}
	</FreeSpinAnimation>

	<MainContainer>
		<Container x={context.stateGameDerived.boardLayout().x} y={context.stateGameDerived.boardLayout().y - 330}>
			<BitmapText anchor={0.5} text={bonusTitle} style={{ fontFamily: 'gold', fontSize: 70 }} />
			<BitmapText anchor={0.5} y={60} text={bonusSubtitle} style={{ fontFamily: 'gold', fontSize: 34 }} />
		</Container>
	</MainContainer>

	<PressToContinue onpress={() => oncomplete()} />
</FadeContainer>
