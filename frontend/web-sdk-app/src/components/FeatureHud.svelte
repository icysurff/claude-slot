<script lang="ts" module>
	import type { BonusType } from '../game/types';

	export type EmitterEventFeatureHud =
		| { type: 'bannerShow'; text: string; durationMs?: number }
		| { type: 'bonusTypeSet'; bonusType: BonusType | undefined };
</script>

<script lang="ts">
	import { Container, BitmapText, Rectangle } from 'pixi-svelte';
	import { MainContainer } from 'components-layout';
	import { FadeContainer } from 'components-pixi';
	import { waitForTimeout } from 'utils-shared/wait';
	import { stateBet } from 'state-shared';

	import { getContext } from '../game/context';
	import { SYMBOL_SIZE } from '../game/constants';

	const context = getContext();

	const BONUS_LABEL: Record<BonusType, string> = {
		normal: 'FREE SPINS · STICKY WILDS',
		super: 'SUPER FREE SPINS · EXPANDING WILDS',
		jackpot: 'JACKPOT SPINS · CHEST CHAIN',
	};

	let bannerText = $state('');
	let showBanner = $state(false);
	let bonusType = $state<BonusType | undefined>(undefined);

	context.eventEmitter.subscribeOnMount({
		bonusTypeSet: (e) => (bonusType = e.bonusType),
		bannerShow: async ({ text, durationMs }) => {
			bannerText = text;
			showBanner = true;
			await waitForTimeout(stateBet.isTurbo ? 250 : (durationMs ?? 900));
			showBanner = false;
		},
	});

	const top = $derived(
		context.stateGameDerived.boardLayout().y -
			context.stateGameDerived.boardLayout().height * 0.5 -
			SYMBOL_SIZE * 1.02,
	);
	const cx = $derived(context.stateGameDerived.boardLayout().x);
</script>

<FadeContainer show={bonusType !== undefined}>
	<MainContainer>
		<Container x={cx} y={top}>
			<BitmapText
				anchor={0.5}
				text={bonusType ? BONUS_LABEL[bonusType] : ''}
				style={{ fontFamily: 'gold', fontSize: SYMBOL_SIZE * 0.3 }}
			/>
		</Container>
	</MainContainer>
</FadeContainer>

<FadeContainer show={showBanner}>
	<MainContainer>
		<Container x={cx} y={context.stateGameDerived.boardLayout().y}>
			<Rectangle
				anchor={0.5}
				width={SYMBOL_SIZE * 5}
				height={SYMBOL_SIZE * 1.1}
				borderRadius={24}
				backgroundColor={0x000000}
				backgroundAlpha={0.65}
			/>
			<BitmapText
				anchor={0.5}
				text={bannerText}
				style={{ fontFamily: 'gold', fontSize: SYMBOL_SIZE * 0.6 }}
			/>
		</Container>
	</MainContainer>
</FadeContainer>
