<!--
  Passo 04: lixeira e uma fileira de pontos acendendo em "esteira" (loop).
  Geometria e tempos: guia de implementação §3.
-->
<script lang="ts">
	import { onMount } from 'svelte';
	import { gsap } from '$lib/animacao/gsap';
	import { tocarSoQuandoVisivel } from '$lib/animacao/pausarForaDaTela';

	let {
		titulo = 'Lixeira de coleta com uma fileira de pontos acendendo em sequência'
	}: { titulo?: string } = $props();

	let svg: SVGSVGElement;

	// `fase` (t no guia) vale 0, 1 ou 2. t = 0 também é o estado estático.
	let fase = $state(0);
	const pontos = Array.from({ length: 9 }, (_, i) => ({ i, x: 70 + 20 * i }));
	// Aceso quando (i − t) mod 3 == 0; o `+ 3` evita resto negativo em JavaScript.
	const aceso = (i: number) => (i - fase + 3) % 3 === 0;

	onMount(() => {
		let desligar = () => {};
		const contexto = gsap.context(() => {
			const linha = gsap.timeline({ repeat: -1 });
			linha
				.call(() => (fase = 0), [], 0)
				.call(() => (fase = 1), [], 0.3)
				.call(() => (fase = 2), [], 0.6)
				.to({}, { duration: 0.5 }, 0.9); // pausa de 0,5s antes de recomeçar
			desligar = tocarSoQuandoVisivel(svg, linha);
		}, svg);
		return () => {
			desligar();
			contexto.revert();
			fase = 0;
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
	<path
		d="M90 70 H210 M100 70 L110 210 H190 L200 70 M135 70 V56 H165 V70 M135 100 V185 M150 100 V185 M165 100 V185"
	/>
	{#each pontos as p (p.i)}
		{#if aceso(p.i)}
			<circle cx={p.x} cy="244" r="6" fill="var(--green)" stroke="var(--green)" stroke-width="1.5" />
		{:else}
			<circle cx={p.x} cy="244" r="6" stroke-width="1.5" />
		{/if}
	{/each}
</svg>

<style>
	svg {
		width: 100%;
		height: auto;
	}
</style>
