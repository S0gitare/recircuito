<!--
  Passo 03: radar. Um anel verde se expande a partir do centro e some (loop).
  Geometria e tempos: guia de implementação §3.
-->
<script lang="ts">
	import { onMount } from 'svelte';
	import { gsap } from '$lib/animacao/gsap';
	import { tocarSoQuandoVisivel } from '$lib/animacao/pausarForaDaTela';

	let {
		titulo = 'Radar com círculos concêntricos mostrando os pontos de coleta mais próximos'
	}: { titulo?: string } = $props();

	let svg: SVGSVGElement;
	let pulso: SVGCircleElement;

	onMount(() => {
		let desligar = () => {};
		const contexto = gsap.context(() => {
			// Tween que repete: a cada volta volta ao começo instantaneamente.
			const anel = gsap.fromTo(
				pulso,
				{ attr: { r: 12 }, opacity: 1 },
				{
					attr: { r: 110 },
					opacity: 0,
					duration: 1.6,
					ease: 'power2.out',
					delay: 0.2,
					repeat: -1,
					repeatDelay: 0.2
				}
			);
			desligar = tocarSoQuandoVisivel(svg, anel);
		}, svg);
		return () => {
			desligar();
			contexto.revert();
		};
	});
</script>

<svg
	bind:this={svg}
	viewBox="0 0 300 300"
	role="img"
	aria-label={titulo}
	fill="none"
	stroke="var(--ink)"
	stroke-width="2"
	stroke-linecap="round"
	stroke-linejoin="round"
>
	<circle cx="150" cy="150" r="110" stroke="var(--verde-guia)" stroke-width="1" />
	<circle cx="150" cy="150" r="80" />
	<circle cx="150" cy="150" r="40" stroke-width="1.5" />
	<circle cx="150" cy="150" r="12" fill="var(--green)" stroke="none" />
	<circle cx="219" cy="190" r="7" fill="var(--bg)" />
	<circle cx="81" cy="190" r="7" fill="var(--bg)" />
	<circle cx="150" cy="70" r="7" fill="var(--green)" stroke="var(--green)" />
	<circle bind:this={pulso} cx="150" cy="150" r="12" stroke="var(--green)" />
</svg>

<style>
	svg {
		width: 100%;
		height: auto;
	}
</style>
