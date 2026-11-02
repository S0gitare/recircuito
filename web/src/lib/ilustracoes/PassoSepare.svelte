<!--
  Passo 01: itens caem dentro da caixa e a seta aparece (loop).
  Geometria e tempos: guia de implementação §3.
-->
<script lang="ts">
	import { onMount } from 'svelte';
	import { gsap } from '$lib/animacao/gsap';
	import { tocarSoQuandoVisivel } from '$lib/animacao/pausarForaDaTela';

	let {
		titulo = 'Celular, pilha e cabo caindo dentro de uma caixa para serem separados'
	}: { titulo?: string } = $props();

	let svg: SVGSVGElement;
	let itens: SVGGElement;
	let seta: SVGPathElement;

	onMount(() => {
		// O markup já é o estado de repouso = estado estático. A timeline nasce pausada
		// (e nem toca com movimento reduzido), então o desenho fica como está.
		let desligar = () => {};
		const contexto = gsap.context(() => {
			const linha = gsap.timeline({ repeat: -1 });
			linha
				// Início do ciclo: itens 60px acima e seta apagada.
				.set(itens, { y: -60, opacity: 0 })
				.set(seta, { opacity: 0 })
				.to(itens, { opacity: 1, duration: 0.2, ease: 'none' }, 0)
				.to(itens, { y: 0, duration: 0.9, ease: 'power2.in' }, 0)
				.to(seta, { opacity: 1, duration: 0.2 }, 0.9)
				// Pausa de 1,8s com tudo à mostra; depois some (0,3s) e reinicia.
				.to([itens, seta], { opacity: 0, duration: 0.3 }, 0.9 + 1.8);
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
	viewBox="0 0 300 300"
	role="img"
	aria-label={titulo}
	fill="none"
	stroke="var(--ink)"
	stroke-width="2"
	stroke-linecap="round"
	stroke-linejoin="round"
>
	<g bind:this={itens}>
		<!-- Cada item tem a própria rotação fixa; o grupo externo é quem cai. -->
		<rect x="84" y="66" width="46" height="84" rx="9" transform="rotate(-12 107 108)" />
		<circle cx="148" cy="104" r="20" stroke-width="1.5" />
		<circle cx="148" cy="104" r="9" stroke-width="1.5" />
		<rect x="180" y="86" width="28" height="62" rx="6" transform="rotate(10 194 117)" />
	</g>
	<!-- A caixa tem fundo branco para cobrir a base dos itens (eles "entram" nela). -->
	<rect x="75" y="140" width="150" height="96" fill="var(--bg)" />
	<path d="M75 140 L53 114 M225 140 L247 114" />
	<path bind:this={seta} d="M150 172 V204 M138 192 L150 204 L162 192" />
</svg>

<style>
	svg {
		width: 100%;
		height: auto;
	}
</style>
