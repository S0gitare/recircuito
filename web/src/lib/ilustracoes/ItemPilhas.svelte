<!--
  Item "pilhas e baterias": uma pilha sobe e a outra desce devagar (loop).
  Geometria e tempos: guia de implementação §3.
-->
<script lang="ts">
	import { onMount } from 'svelte';
	import { gsap } from '$lib/animacao/gsap';
	import { tocarSoQuandoVisivel } from '$lib/animacao/pausarForaDaTela';

	let {
		titulo = 'Duas pilhas de tamanhos diferentes'
	}: { titulo?: string } = $props();

	let svg: SVGSVGElement;
	let pilha1: SVGGElement;
	let pilha2: SVGGElement;

	onMount(() => {
		let desligar = () => {};
		const contexto = gsap.context(() => {
			const linha = gsap.timeline({ repeat: -1, yoyo: true });
			linha
				.to(pilha1, { y: -10, duration: 1.4, ease: 'sine.inOut' }, 0)
				.to(pilha2, { y: 6, duration: 1.4, ease: 'sine.inOut' }, 0);
			desligar = tocarSoQuandoVisivel(svg, linha);
		}, svg);
		return () => {
			desligar();
			contexto.revert();
		};
	});
</script>

<svg
	bind:this={svg}
	viewBox="0 0 386 260"
	role="img"
	aria-label={titulo}
	fill="none"
	stroke="var(--ink)"
	stroke-width="2"
	stroke-linecap="round"
	stroke-linejoin="round"
>
	<g bind:this={pilha1}>
		<rect x="159" y="40" width="16" height="10" fill="var(--ink)" />
		<rect x="147" y="48" width="40" height="170" rx="8" />
		<rect x="148" y="90" width="38" height="18" fill="var(--green)" stroke="none" />
	</g>
	<g bind:this={pilha2}>
		<rect x="213" y="70" width="16" height="10" fill="var(--ink)" />
		<rect x="201" y="78" width="40" height="140" rx="8" />
		<path d="M221 130 V146 M213 138 H229" />
	</g>
</svg>

<style>
	svg {
		width: 100%;
		height: auto;
	}
</style>
