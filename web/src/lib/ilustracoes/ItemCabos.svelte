<!--
  Item "cabos e carregadores": a luz do carregador pisca (loop).
  Geometria e tempos: guia de implementação §3.
-->
<script lang="ts">
	import { onMount } from 'svelte';
	import { gsap } from '$lib/animacao/gsap';
	import { tocarSoQuandoVisivel } from '$lib/animacao/pausarForaDaTela';

	let {
		titulo = 'Cabo ligado a um carregador com luz piscando'
	}: { titulo?: string } = $props();

	let svg: SVGSVGElement;
	let led: SVGCircleElement;

	onMount(() => {
		let desligar = () => {};
		const contexto = gsap.context(() => {
			// A luz do carregador pisca: opacidade de 1 a 0,15 e volta (yoyo).
			const linha = gsap.timeline({ repeat: -1, yoyo: true });
			linha.to(led, { opacity: 0.15, duration: 0.5, ease: 'sine.inOut' });
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
	<path d="M60 216 C120 106 180 266 230 176 S310 76 265 66" />
	<!-- A fonte tem fundo da seção: esconde a ponta do fio que entra nela. -->
	<rect x="230" y="34" width="70" height="82" rx="12" fill="var(--bg-alt)" />
	<path d="M252 14 V34 M278 14 V34" />
	<circle bind:this={led} cx="265" cy="75" r="6" fill="var(--green)" stroke="none" />
	<circle cx="60" cy="216" r="7" fill="var(--bg-alt)" />
</svg>

<style>
	svg {
		width: 100%;
		height: auto;
	}
</style>
