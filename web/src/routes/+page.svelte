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

	// Texto do link de atalho. Ainda não está em textos.ts (arquivo de outra frente).
	const pularParaConteudo = 'Pular para o conteúdo';

	const urlCanonica = 'https://recircuito.info/';
	const urlImagemOg = 'https://recircuito.info/og-image.png';
	const titulo = 'ReCircuito · Onde descartar lixo eletrônico em Belém (PA)';
	const descricao =
		'Encontre 140 pontos de coleta de lixo eletrônico em 32 bairros de Belém (PA). Descarte celulares, pilhas, baterias, computadores e cabos buscando pelo seu CEP ou bairro.';
	const textoAlternativoOg =
		'ReCircuito — Guia gratuito com 140 pontos de coleta de lixo eletrônico em 32 bairros de Belém (PA).';

	// Dados estruturados (Schema.org) para reforçar o contexto local em Belém (PA) no Google Search Console.
	const dadosEstruturados = {
		'@context': 'https://schema.org',
		'@graph': [
			{
				'@type': 'WebSite',
				'@id': `${urlCanonica}#site`,
				url: urlCanonica,
				name: 'ReCircuito',
				inLanguage: 'pt-BR',
				description: descricao
			},
			{
				'@type': 'WebApplication',
				'@id': `${urlCanonica}#guia`,
				url: urlCanonica,
				name: 'ReCircuito — Guia de Descarte de Lixo Eletrônico em Belém',
				applicationCategory: 'UtilitiesApplication',
				operatingSystem: 'Web',
				inLanguage: 'pt-BR',
				isAccessibleForFree: true,
				description: descricao,
				image: urlImagemOg,
				areaServed: {
					'@type': 'City',
					name: 'Belém',
					addressRegion: 'PA',
					addressCountry: 'BR'
				},
				author: {
					'@type': 'Person',
					name: 'Alecsander Henrique da Silva de Lima'
				},
				sameAs: ['https://github.com/S0gitare/recircuito']
			}
		]
	};

	const scriptDadosEstruturados =
		'<script type="application/ld+json">' +
		JSON.stringify(dadosEstruturados).replace(/</g, '\\u003c') +
		'<' +
		'/script>';
</script>

<svelte:head>
	<title>{titulo}</title>
	<meta name="description" content={descricao} />
	<link rel="canonical" href={urlCanonica} />
	<meta property="og:type" content="website" />
	<meta property="og:locale" content="pt_BR" />
	<meta property="og:site_name" content="ReCircuito" />
	<meta property="og:url" content={urlCanonica} />
	<meta property="og:title" content={titulo} />
	<meta property="og:description" content={descricao} />
	<meta property="og:image" content={urlImagemOg} />
	<meta property="og:image:type" content="image/png" />
	<meta property="og:image:width" content="1200" />
	<meta property="og:image:height" content="630" />
	<meta property="og:image:alt" content={textoAlternativoOg} />
	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:title" content={titulo} />
	<meta name="twitter:description" content={descricao} />
	<meta name="twitter:image" content={urlImagemOg} />
	<meta name="twitter:image:alt" content={textoAlternativoOg} />
	<!-- eslint-disable-next-line svelte/no-at-html-tags -->
	{@html scriptDadosEstruturados}
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
