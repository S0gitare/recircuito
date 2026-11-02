<!--
  Passo 02: a barra de quadrados enche, como num "restaurar dados de fábrica" (loop).
  Geometria e tempos: guia de implementação §3.
-->
<script lang="ts">
	import { onMount } from 'svelte';
	import { gsap } from '$lib/animacao/gsap';
	import { tocarSoQuandoVisivel } from '$lib/animacao/pausarForaDaTela';

	let {
		titulo = 'Celular com o símbolo de restaurar e uma barra de progresso enchendo'
	}: { titulo?: string } = $props();

	// Vários desenhos na página: o id do recorte precisa ser único.
	const uid = $props.id();
	const idRecorte = `recorte-barra-${uid}`;

	let svg: SVGSVGElement;
	let recorte: SVGRectElement;

	// 12 quadrados: 2 linhas × 6 colunas, passo de 14px, a partir de (110, 178).
	const quadrados = Array.from({ length: 12 }, (_, i) => ({
		x: 110 + (i % 6) * 14,
		y: 178 + Math.floor(i / 6) * 14
	}));

	onMount(() => {
		let desligar = () => {};
		const contexto = gsap.context(() => {
			const linha = gsap.timeline({ repeat: -1 });
			linha
				.set(recorte, { attr: { width: 0 } })
				.to(recorte, { attr: { width: 80 }, duration: 1.8, ease: 'none' })
				.to({}, { duration: 0.9 }) // pausa com a barra cheia
				.to(recorte, { attr: { width: 0 }, duration: 0.2 });
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
	<defs>
		<clipPath id={idRecorte}>
			<!-- Largura 80 = barra cheia (estado estático); a animação varia de 0 a 80. -->
			<rect bind:this={recorte} x="110" y="178" width="80" height="24" />
		</clipPath>
	</defs>
	<rect x="95" y="45" width="110" height="210" rx="18" />
	<rect x="135" y="58" width="30" height="4" rx="2" fill="var(--green)" stroke="none" />
	<path d="M172 118 A22 22 0 1 1 165.6 102.4 M165.6 102.4 L166 93 M165.6 102.4 L156 103" />
	<g stroke-width="1.5">
		{#each quadrados as q, i (i)}
			<rect x={q.x} y={q.y} width="10" height="10" />
		{/each}
	</g>
	<g clip-path="url(#{idRecorte})" fill="var(--green)" stroke-width="1.5">
		{#each quadrados as q, i (i)}
			<rect x={q.x} y={q.y} width="10" height="10" />
		{/each}
	</g>
</svg>

<style>
	svg {
		width: 100%;
		height: auto;
	}
</style>
