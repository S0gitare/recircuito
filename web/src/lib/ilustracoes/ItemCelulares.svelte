<!--
  Item "celulares e tablets": aparelhos flutuando em sentidos opostos (loop).
  Geometria e tempos: guia de implementação §3.
-->
<script lang="ts">
	import { onMount } from 'svelte';
	import { gsap } from '$lib/animacao/gsap';
	import { tocarSoQuandoVisivel } from '$lib/animacao/pausarForaDaTela';

	let {
		titulo = 'Celular e tablet flutuando'
	}: { titulo?: string } = $props();

	let svg: SVGSVGElement;
	let celular: SVGGElement;
	let tablet: SVGGElement;

	onMount(() => {
		let desligar = () => {};
		const contexto = gsap.context(() => {
			// yoyo: vai e volta sozinho. Um corpo sobe 12px enquanto o outro desce 8px.
			const linha = gsap.timeline({ repeat: -1, yoyo: true });
			linha
				.to(celular, { y: -12, duration: 1.4, ease: 'sine.inOut' }, 0)
				.to(tablet, { y: 8, duration: 1.4, ease: 'sine.inOut' }, 0);
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
	<g bind:this={celular}>
		<rect x="143" y="30" width="100" height="200" rx="20" />
		<rect x="178" y="44" width="30" height="6" rx="3" fill="var(--green)" stroke="none" />
	</g>
	<!-- O tablet tem fundo da seção para cobrir parte do celular que está atrás. -->
	<g bind:this={tablet}>
		<rect x="96" y="80" width="120" height="150" rx="12" fill="var(--bg-alt)" />
		<circle cx="155" cy="92" r="4" stroke-width="1.5" />
	</g>
</svg>

<style>
	svg {
		width: 100%;
		height: auto;
	}
</style>
