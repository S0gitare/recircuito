<script lang="ts">
	import Abertura from '$lib/componentes/Abertura.svelte';
	import BannerCookies from '$lib/componentes/BannerCookies.svelte';
	import Hero from '$lib/componentes/Hero.svelte';
	import Sobre from '$lib/componentes/Sobre.svelte';
	import ComoDescartar from '$lib/componentes/ComoDescartar.svelte';
	import OQueDescartar from '$lib/componentes/OQueDescartar.svelte';
	import PontosDeColeta from '$lib/componentes/PontosDeColeta.svelte';
	import Impacto from '$lib/componentes/Impacto.svelte';
	import Rodape from '$lib/componentes/Rodape.svelte';
	import { hero } from '$lib/conteudo/textos';

	// Texto do link de atalho. Ainda não está em textos.ts (arquivo de outra frente).
	const pularParaConteudo = 'Pular para o conteúdo';

	const titulo = 'ReCircuito · Descarte de lixo eletrônico em Belém';
	const descricao =
		'Saiba como descartar lixo eletrônico em Belém e encontre o ponto de coleta mais próximo.';
</script>

<svelte:head>
	<title>{titulo}</title>
	<meta name="description" content={descricao} />
	<meta property="og:type" content="website" />
	<meta property="og:locale" content="pt_BR" />
	<meta property="og:site_name" content="ReCircuito" />
	<meta property="og:title" content={titulo} />
	<meta property="og:description" content={hero.texto} />
</svelte:head>

<!-- Ordem de tabulação: atalho, aviso de cookies, depois a página. -->
<a class="pular" href="#conteudo">{pularParaConteudo}</a>

<Abertura />

<BannerCookies />

<Hero />

<main id="conteudo" tabindex="-1">
	<Sobre />
	<ComoDescartar />
	<OQueDescartar />
	<!-- O próprio PontosDeColeta já traz a seção com id="pontos-de-coleta". -->
	<PontosDeColeta />
	<Impacto />
</main>

<Rodape />

<style>
	/* Só aparece quando recebe foco pelo teclado. */
	.pular {
		position: fixed;
		top: 8px;
		left: 8px;
		z-index: 100;
		padding: 12px 16px;
		background: var(--ink);
		color: #fff;
		font-family: var(--font-interface);
		font-weight: 600;
		font-size: 15px;
		transform: translateY(-200%);
	}

	.pular:focus {
		transform: none;
		outline-color: #fff;
	}

	main:focus {
		outline: none;
	}
</style>
