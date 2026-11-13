<script lang="ts" module>
	import { defineMeta } from '@storybook/addon-svelte-csf';

	const { Story } = defineMeta({
		title: 'WILD_RESPIN/books',
	});
</script>

<script lang="ts">
	import {
		StoryGameTemplate,
		StoryLocale,
		type TemplateArgs,
		templateArgs,
	} from 'components-storybook';

	import Game from '../components/Game.svelte';
	import { setContext } from '../game/context';
	import { playBet } from '../game/utils';
	import books from './data/books';

	setContext();
</script>

{#snippet template(args: TemplateArgs<any>)}
	<StoryGameTemplate
		skipLoadingScreen={args.skipLoadingScreen}
		action={async () => {
			await args.action?.(args.data);
		}}
	>
		<StoryLocale lang="en">
			<Game />
		</StoryLocale>
	</StoryGameTemplate>
{/snippet}

<Story
	name="base"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => {
			const data = books.find((b) => b.label === 'base');
			if (!data) return;
			await playBet({ ...data, state: data.events });
		},
	})}
	{template}
/>

<Story
	name="respin"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => {
			const data = books.find((b) => b.label === 'respin');
			if (!data) return;
			await playBet({ ...data, state: data.events });
		},
	})}
	{template}
/>

<Story
	name="normal"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => {
			const data = books.find((b) => b.label === 'normal');
			if (!data) return;
			await playBet({ ...data, state: data.events });
		},
	})}
	{template}
/>

<Story
	name="super"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => {
			const data = books.find((b) => b.label === 'super');
			if (!data) return;
			await playBet({ ...data, state: data.events });
		},
	})}
	{template}
/>

<Story
	name="jackpot"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => {
			const data = books.find((b) => b.label === 'jackpot');
			if (!data) return;
			await playBet({ ...data, state: data.events });
		},
	})}
	{template}
/>

<Story
	name="wincap"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => {
			const data = books.find((b) => b.label === 'wincap');
			if (!data) return;
			await playBet({ ...data, state: data.events });
		},
	})}
	{template}
/>

<Story
	name="wildreels"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => {
			const data = books.find((b) => b.label === 'wildreels');
			if (!data) return;
			await playBet({ ...data, state: data.events });
		},
	})}
	{template}
/>
