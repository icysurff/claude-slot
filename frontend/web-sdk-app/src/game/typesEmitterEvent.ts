import type { EmitterEventBoard } from '../components/Board.svelte';
import type { EmitterEventBoardFrame } from '../components/BoardFrame.svelte';
import type { EmitterEventFreeSpinIntro } from '../components/FreeSpinIntro.svelte';
import type { EmitterEventFreeSpinCounter } from '../components/FreeSpinCounter.svelte';
import type { EmitterEventFreeSpinOutro } from '../components/FreeSpinOutro.svelte';
import type { EmitterEventWin } from '../components/Win.svelte';
import type { EmitterEventSound } from '../components/Sound.svelte';
import type { EmitterEventChestBar } from '../components/ChestBar.svelte';
import type { EmitterEventHeldOverlay } from '../components/HeldOverlay.svelte';
import type { EmitterEventExpandedWilds } from '../components/ExpandedWilds.svelte';
import type { EmitterEventFeatureHud } from '../components/FeatureHud.svelte';
import type { EmitterEventTransition } from '../components/Transition.svelte';

export type EmitterEventGame =
	| EmitterEventBoard
	| EmitterEventBoardFrame
	| EmitterEventWin
	| EmitterEventFreeSpinIntro
	| EmitterEventFreeSpinCounter
	| EmitterEventFreeSpinOutro
	| EmitterEventSound
	| EmitterEventTransition
	| EmitterEventChestBar
	| EmitterEventFeatureHud
	| EmitterEventHeldOverlay
	| EmitterEventExpandedWilds;
