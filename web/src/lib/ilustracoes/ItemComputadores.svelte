<!--
  Item "computadores": a rodinha do mouse rola (loop).
  Geometria e tempos: guia de implementação §3.
-->
<script lang="ts">
	import { onMount } from 'svelte';
	import { gsap } from '$lib/animacao/gsap';
	import { tocarSoQuandoVisivel } from '$lib/animacao/pausarForaDaTela';

	let {
		titulo = 'Monitor com teclado e mouse'
	}: { titulo?: string } = $props();

	let svg: SVGSVGElement;
	let rodinha: SVGRectElement;

	onMount(() => {
		let desligar = () => {};
		const contexto = gsap.context(() => {
			// A rodinha do mouse desce 14px e volta (yoyo).
			const linha = gsap.timeline({ repeat: -1, yoyo: true });
			linha.to(rodinha, { y: 14, duration: 0.7, ease: 'sine.inOut' });
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
	<rect x="78" y="40" width="230" height="150" rx="10" />
	<rect x="90" y="52" width="206" height="126" rx="3" stroke-width="1" />
	<path d="M58 190 H328 L314 206 H72 Z" />
	<rect x="300" y="168" width="26" height="40" rx="13" fill="var(--bg-alt)" />
	<rect bind:this={rodinha} x="311" y="176" width="4" height="8" rx="2" fill="var(--green)" stroke="none" />
</svg>

<style>
	svg {
		width: 100%;
		height: auto;
	}
</style>
