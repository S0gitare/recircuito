<!--
  Abertura do site: uma cortina verde-escura com o logo se "ligando".

  Sequência (~2,6s, tempos em $lib/animacao/movimento.ts → ABERTURA):
  1. O ponto verde do símbolo surge: é a fonte do sinal.
  2. A trilha octogonal se desenha saindo do ponto verde até o furo, como um
     sinal correndo pela placa de circuito.
  3. O furo no topo acende quando o sinal chega.
  4. As letras "Re" e "ircuito" brotam de trás do símbolo, que estava sozinho
     no centro e desliza para o seu lugar no meio da palavra.
  5. O logo some, a cortina sobe e entrega a tela para a cascata do Hero.

  Regras:
  - Só toca quando o script em app.html marcou <html class="com-abertura">
    (JS ligado, sem movimento reduzido, sem âncora na URL). Sem a classe, a
    cortina nem aparece (display: none) e o Hero é liberado na hora.
  - Clique, tecla ou rolagem aceleram a abertura: ninguém fica preso nela.
  - É decorativa: aria-hidden, sem foco, sem texto para leitores de tela.
-->
<script lang="ts">
	import { onMount } from 'svelte';
	import { gsap } from '$lib/animacao/gsap';
	import { CURVA, ABERTURA } from '$lib/animacao/movimento';
	import { liberarHero } from '$lib/animacao/abertura';
	import { travarRolagem, liberarRolagem } from '$lib/animacao/lenis';
	// O mesmo arquivo do logo do cabeçalho, embutido como texto para que cada
	// letra e cada parte do símbolo possam ser animadas separadamente.
	import logoSvg from '../../../static/logos/logo-simbolo-no-c-site.svg?raw';

	let cortina: HTMLDivElement | undefined = $state();
	let conteudo: HTMLDivElement | undefined = $state();
	let ativa = $state(true);

	const CLASSE = 'com-abertura';

	onMount(() => {
		const html = document.documentElement;

		const encerrar = () => {
			html.classList.remove(CLASSE);
			ativa = false;
			liberarRolagem();
			liberarHero();
		};

		// Sem a classe (movimento reduzido, âncora na URL): o site aparece direto.
		if (!html.classList.contains(CLASSE) || !cortina || !conteudo) {
			encerrar();
			return;
		}

		// Garante o topo mesmo se algo rolou entre o app.html e a montagem.
		window.scrollTo(0, 0);
		travarRolagem();

		const svg = conteudo.querySelector('svg');
		const simbolo = svg?.querySelector<SVGGElement>('g > g');
		const trilha = simbolo?.querySelector<SVGPathElement>('path');
		const [furo, ponto] = simbolo ? [...simbolo.querySelectorAll('circle')] : [];
		if (!svg || !simbolo || !trilha || !furo || !ponto) {
			encerrar();
			return;
		}

		// No arquivo, as letras vêm na ordem: R, e, [símbolo], i, r, c, u, i, t, o.
		const letras = [...svg.querySelectorAll<SVGPathElement>(':scope > g > path')];
		const indiceDoSimbolo = [...svg.firstElementChild!.children].indexOf(simbolo);
		const antes = letras.slice(0, indiceDoSimbolo).reverse(); // "e", "R": de dentro para fora
		const depois = letras.slice(indiceDoSimbolo); // "i", "r", "c"… de dentro para fora

		// Medidas em pixels para centralizar o símbolo sozinho no começo.
		const caixaLogo = svg.getBoundingClientRect();
		const caixaSimbolo = simbolo.getBoundingClientRect();
		const deslocamentoInicial =
			caixaLogo.left + caixaLogo.width / 2 - (caixaSimbolo.left + caixaSimbolo.width / 2);

		// As letras se movem em unidades do desenho (o viewBox é enorme): convertemos
		// ~14px de tela para essas unidades.
		const unidadesPorPixel = svg.viewBox.baseVal.width / caixaLogo.width;
		const afastamento = 14 * unidadesPorPixel;

		// Estado inicial: só a cortina, com o símbolo apagado no centro.
		gsap.set(svg, { x: deslocamentoInicial });
		gsap.set(ponto, { scale: 0.6, opacity: 0, transformOrigin: '50% 50%' });
		gsap.set(furo, { scale: 0.7, opacity: 0, transformOrigin: '50% 50%' });
		gsap.set(trilha, { drawSVG: '0%' });
		gsap.set(antes, { opacity: 0, x: afastamento });
		gsap.set(depois, { opacity: 0, x: -afastamento });
		gsap.set(conteudo, { opacity: 1 });

		const linha = gsap.timeline({ defaults: { ease: CURVA.saida }, onComplete: encerrar });

		// 1. Fonte do sinal.
		linha.to(ponto, { scale: 1, opacity: 1, duration: ABERTURA.ponto }, 0);

		// 2. O traço sai do ponto verde (início do caminho) e vai até o furo.
		linha.to(
			trilha,
			{ drawSVG: '100%', duration: ABERTURA.trilha, ease: CURVA.desenhar },
			ABERTURA.ponto * 0.4
		);

		// 3. O furo acende quando o sinal chega.
		linha.to(furo, { scale: 1, opacity: 1, duration: ABERTURA.furo }, '>-0.12');

		// 4. As letras brotam de trás do símbolo enquanto o logo vai para o centro.
		linha.addLabel('letras', '>-0.15');
		linha.to(svg, { x: 0, duration: ABERTURA.letras, ease: CURVA.moverNaTela }, 'letras');
		linha.to(
			antes,
			{ opacity: 1, x: 0, duration: ABERTURA.letras, stagger: ABERTURA.intervaloLetras },
			'letras+=0.1'
		);
		linha.to(
			depois,
			{ opacity: 1, x: 0, duration: ABERTURA.letras, stagger: ABERTURA.intervaloLetras },
			'letras+=0.1'
		);

		// 5. Logo sobe e some; a cortina sobe logo atrás e entrega a tela ao Hero.
		linha.addLabel('saida', `>+${ABERTURA.pausa}`);
		linha.to(conteudo, { y: -24, opacity: 0, duration: ABERTURA.logoSaindo }, 'saida');
		linha.to(
			cortina,
			{ yPercent: -100, duration: ABERTURA.cortina, ease: CURVA.moverNaTela },
			'saida+=0.1'
		);
		linha.call(liberarHero, [], `saida+=${0.1 + ABERTURA.atrasoDoHero}`);

		// Quem tem pressa pula: clique, tecla ou rolagem aceleram o resto.
		const acelerar = () => linha.timeScale(ABERTURA.acelerarAoPular);
		const eventos = ['pointerdown', 'keydown', 'wheel', 'touchmove'] as const;
		eventos.forEach((nome) => window.addEventListener(nome, acelerar, { passive: true }));

		return () => {
			eventos.forEach((nome) => window.removeEventListener(nome, acelerar));
			linha.kill();
			encerrar();
		};
	});
</script>

{#if ativa}
	<div class="abertura" bind:this={cortina} aria-hidden="true">
		<div class="logo" bind:this={conteudo}>
			{@html logoSvg}
		</div>
	</div>
{/if}

<style>
	/* Escondida por padrão: só aparece quando o app.html marcou o <html>. */
	.abertura {
		display: none;
		position: fixed;
		inset: 0;
		z-index: 1000;
		align-items: center;
		justify-content: center;
		background: var(--footer);
		will-change: transform;
	}

	:global(html.com-abertura) .abertura {
		display: flex;
	}

	/* Enquanto a cortina cobre a tela, a página não rola (o Lenis também para). */
	:global(html.com-abertura) {
		overflow: hidden;
	}

	/* Antes do JS montar a animação, o logo fica invisível (evita ver o logo
	   completo por um instante e depois ele "se desmontar"). */
	.logo {
		opacity: 0;
		width: min(420px, 72vw);
		line-height: 0;
	}

	.logo :global(svg) {
		width: 100%;
		height: auto;
		overflow: visible;
	}

	/* O arquivo do logo é o da versão clara do site; aqui ele vira negativo. */
	.logo :global(path) {
		fill: var(--bg-hero);
	}

	.logo :global(g > g > path) {
		fill: none;
		stroke: var(--bg-hero);
	}

	/* Furo: anel claro com o miolo da cor da cortina (vazado). */
	.logo :global(circle:first-of-type) {
		fill: var(--footer);
		stroke: var(--bg-hero);
	}

	.logo :global(circle:last-of-type) {
		fill: var(--green-dark-mode);
	}
</style>
