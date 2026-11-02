<!--
  Arte do topo: celular em 5 camadas (vista explodida) + linhas-guia + chamadas + rótulos.
  Bloco de 1212×491 (guia de implementação §3). No mobile (< 768px) só aparece a pilha.

  Como funciona a animação:
  - O markup já descreve o estado FINAL (explodido, com tudo visível). É o que vê quem
    prefere movimento reduzido, e o que o HTML pré-renderizado guarda.
  - No `onMount`, o GSAP volta as camadas para "montado", esconde guias, chamadas e
    rótulos, e depois de 0,5s espalha tudo.
-->
<script lang="ts">
	import { onMount } from 'svelte';
	import { gsap, DrawSVGPlugin } from '$lib/animacao/gsap';
	import { prefereMovimentoReduzido } from '$lib/animacao/movimentoReduzido';
	import { hero } from '$lib/conteudo/textos';

	let { titulo = hero.descricaoDoDesenho }: { titulo?: string } = $props();

	let bloco: HTMLDivElement;
	// Fica falso até o JS preparar o estado inicial: evita o "pisca" do estado final.
	let pronto = $state(false);

	// Deslocamento vertical de cada camada, índice 0 = Vidro (topo) … 4 = Carcaça (base).
	const yMontado = (i: number) => 100 + 14 * i;
	const yExplodido = (i: number) => 64 * i;

	// Chamadas: `y` no espaço de 1212×491; `camada` indexa `hero.camadas`.
	const chamadasDireita = [
		{ camada: 0, y: 75, verde: false },
		{ camada: 2, y: 203, verde: true },
		{ camada: 4, y: 331, verde: false }
	];
	const chamadasEsquerda = [
		{ camada: 1, y: 214, verde: false },
		{ camada: 3, y: 342, verde: true }
	];

	// Posição dos rótulos HTML em porcentagem do bloco (acompanha o redimensionamento).
	const pct = (valor: number, total: number) => `${(valor / total) * 100}%`;

	onMount(() => {
		const reduzido = prefereMovimentoReduzido();
		if (reduzido) {
			pronto = true;
			return;
		}

		gsap.registerPlugin(DrawSVGPlugin);

		// Camadas e guias (valem para mobile e desktop).
		const contexto = gsap.context(() => {
			const camadas = gsap.utils.toArray<SVGGElement>('.camada');
			// A ordem no DOM é Carcaça…Vidro; o índice vem do atributo data-i.
			const indice = (c: SVGGElement) => Number(c.dataset.i);

			gsap.set(camadas, { y: (_i: number, c: SVGGElement) => yMontado(indice(c)) });
			gsap.set('.guia', { opacity: 0 });

			const linha = gsap.timeline({ delay: 0.5 });
			linha
				.to(camadas, { y: (_i: number, c: SVGGElement) => yExplodido(indice(c)), duration: 1.4, ease: 'power2.out' }, 0)
				.to('.guia', { opacity: 1, duration: 0.7, stagger: 0.15, ease: 'power1.out' }, 0.6);
		}, bloco);

		// Chamadas e rótulos: só existem de verdade no desktop.
		const midia = gsap.matchMedia();
		midia.add('(min-width: 768px)', () => {
			gsap.set('.chamada-linha', { drawSVG: '0%' });
			gsap.set('.chamada-ponto', { opacity: 0, scale: 0, transformOrigin: '50% 50%' });
			gsap.set('.rotulo', { opacity: 0, y: 8 });

			const linha = gsap.timeline({ delay: 0.5 });
			linha
				.to('.chamada-linha', { drawSVG: '100%', duration: 0.7, stagger: 0.12, ease: 'power2.out' }, 0.8)
				.to('.chamada-ponto', { opacity: 1, scale: 1, duration: 0.4, stagger: 0.12, ease: 'back.out(2)' }, 1.2)
				.to('.rotulo', { opacity: 1, y: 0, duration: 0.6, stagger: 0.12, ease: 'power2.out' }, 1.0);
		}, bloco);

		pronto = true;
		return () => {
			midia.revert();
			contexto.revert();
		};
	});
</script>

{#snippet espessuraEForma()}
	<!-- Lateral da camada (verde-claro) e face de cima (branca), ambas com traço de 2px. -->
	<path d="M0 150 L130 225 L390 75 L390 85 L130 235 L0 160 Z" fill="var(--verde-espessura)" />
	<path d="M260 0 L390 75 L130 225 L0 150 Z" fill="var(--bg)" />
{/snippet}

<div
	class="bloco"
	class:pronto
	bind:this={bloco}
	role="img"
	aria-label={titulo}
>
	<!-- Pilha de camadas: ordem no DOM de baixo para cima (Vidro fica por cima). -->
	<svg
		class="pilha"
		viewBox="0 0 390 491"
		fill="none"
		stroke="var(--ink)"
		stroke-width="2"
		stroke-linecap="round"
		stroke-linejoin="round"
		aria-hidden="true"
	>
		<!-- Linhas-guia tracejadas: aparecem só na vista explodida. -->
		<g stroke="var(--verde-guia)" stroke-width="1" stroke-dasharray="4 4">
			<line class="guia" x1="0" y1="150" x2="0" y2="406" />
			<line class="guia" x1="390" y1="75" x2="390" y2="331" />
			<line class="guia" x1="130" y1="225" x2="130" y2="481" />
		</g>

		<!-- Carcaça (i = 4) -->
		<g class="camada" data-i="4" transform="translate(0 {yExplodido(4)})">
			{@render espessuraEForma()}
			<path d="M78.1 125 L112.8 145 L60.8 175 L26 155 Z" stroke-width="1.5" />
			<path d="M69.3 144 L79.7 150 L69.3 156 L58.9 150 Z" fill="var(--green)" stroke-width="1.5" />
		</g>

		<!-- Placa (i = 3) -->
		<g class="camada" data-i="3" transform="translate(0 {yExplodido(3)})">
			{@render espessuraEForma()}
			<path d="M147.4 155 L190.7 180 L147.4 205 L104.1 180 Z" fill="var(--green)" stroke-width="1.5" />
			<path d="M190.7 180 L250 146 L280 150 M104.1 180 L70 160 M169 192.5 L190 205" stroke-width="1.5" />
			<path d="M34.8 145 L60.8 160 L43.5 170 L17.3 155 Z" stroke-width="1.5" />
		</g>

		<!-- Bateria (i = 2) -->
		<g class="camada" data-i="2" transform="translate(0 {yExplodido(2)})">
			{@render espessuraEForma()}
			<path d="M229.7 42.5 L316.3 92.5 L160.4 182.5 L73.9 132.5 Z" fill="var(--green)" stroke-width="1.5" />
		</g>

		<!-- Tela (i = 1) -->
		<g class="camada" data-i="1" transform="translate(0 {yExplodido(1)})">
			{@render espessuraEForma()}
			<path d="M260 10 L372.6 75 L130.2 215 L17.5 150 Z" stroke-width="1" />
		</g>

		<!-- Vidro (i = 0) -->
		<g class="camada" data-i="0" transform="translate(0 {yExplodido(0)})">
			{@render espessuraEForma()}
			<path d="M297.3 33.5 L332 53.5 L326.8 56.5 L292.1 36.5 Z" fill="var(--green)" stroke="none" />
			<path d="M286 75 L225.4 90 L216.7 125 L129.9 135 M225.4 90 L180.3 77.5" stroke-width="1.5" />
		</g>
	</svg>

	<!-- Linhas e bolinhas das chamadas, no mesmo espaço de coordenadas do bloco. -->
	<svg class="chamadas" viewBox="0 0 1212 491" fill="none" stroke="var(--ink)" stroke-width="1" aria-hidden="true">
		{#each chamadasDireita as c (c.camada)}
			<line class="chamada-linha" x1="837" y1={c.y} x2="957" y2={c.y} />
			<circle class="chamada-ponto" cx="957" cy={c.y} r="3.5" fill={c.verde ? 'var(--green)' : 'var(--ink)'} stroke="none" />
		{/each}
		{#each chamadasEsquerda as c (c.camada)}
			<line class="chamada-linha" x1="315" y1={c.y} x2="435" y2={c.y} />
			<circle class="chamada-ponto" cx="314.5" cy={c.y} r="3.5" fill={c.verde ? 'var(--green)' : 'var(--ink)'} stroke="none" />
		{/each}
	</svg>

	<!-- Rótulos em HTML (texto de verdade, vindo de textos.hero.camadas). -->
	{#each chamadasDireita as c (c.camada)}
		<p
			class="rotulo direita"
			style:top={pct(c.y - 11, 491)}
			style:left={pct(972, 1212)}
			style:width={pct(240, 1212)}
			aria-hidden="true"
		>
			<strong>{hero.camadas[c.camada].nome}</strong>
			<span>{hero.camadas[c.camada].destino}</span>
		</p>
	{/each}
	{#each chamadasEsquerda as c (c.camada)}
		<p
			class="rotulo esquerda"
			style:top={pct(c.y - 11, 491)}
			style:left="0"
			style:width={pct(300, 1212)}
			aria-hidden="true"
		>
			<strong>{hero.camadas[c.camada].nome}</strong>
			<span>{hero.camadas[c.camada].destino}</span>
		</p>
	{/each}
</div>

<style>
	.bloco {
		position: relative;
		width: 100%;
		/* Mobile: só a pilha, ≈ 257×324. */
		max-width: 257px;
		margin-inline: auto;
		/* Com `container-type` os rótulos escalam junto com o bloco (unidade cqw). */
		container-type: inline-size;
		/* Escondido até o JS armar a animação; sem JS (ou sem script), aparece direto. */
		opacity: 0;
	}

	.bloco.pronto {
		opacity: 1;
	}

	@media (scripting: none) {
		.bloco {
			opacity: 1;
		}
	}

	.pilha {
		display: block;
		width: 100%;
		height: auto;
		overflow: visible;
	}

	.chamadas,
	.rotulo {
		display: none;
	}

	@media (min-width: 768px) {
		.bloco {
			max-width: 1212px;
			aspect-ratio: 1212 / 491;
		}

		/* 441/1212 = 36,39%; 390/1212 = 32,18% (guia §3). */
		.pilha {
			position: absolute;
			top: 0;
			left: 36.39%;
			width: 32.18%;
		}

		.chamadas {
			display: block;
			position: absolute;
			inset: 0;
			width: 100%;
			height: 100%;
			overflow: visible;
		}

		.rotulo {
			display: block;
			position: absolute;
			font-family: var(--font-interface);
			/* 24px de linha em 1212px de largura = 1,98cqw; nunca menor que 18px. */
			line-height: clamp(18px, 1.98cqw, 24px);
			color: var(--ink);
		}

		.rotulo.esquerda {
			text-align: right;
		}

		.rotulo strong,
		.rotulo span {
			display: block;
		}

		.rotulo strong {
			font-weight: 600;
			font-size: clamp(12px, 1.24cqw, 15px);
		}

		.rotulo span {
			font-weight: 400;
			font-size: clamp(11px, 1.155cqw, 14px);
			color: var(--ink-2);
		}
	}
</style>
