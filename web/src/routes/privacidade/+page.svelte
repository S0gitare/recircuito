<!--
  /privacidade: o que o site faz com cada dado (LGPD, RNF06). Linkada pelo
  aviso de cookies e pelo rodapé. Página simples, sem animação de abertura.
-->
<script lang="ts">
	import { base } from '$app/paths';
	import { cabecalho, privacidade as textos, rodape } from '$lib/conteudo/textos';
	import { apagarConsentimento } from '$lib/analytics';

	let escolhaApagada = $state(false);
	const urlCanonica = 'https://recircuito.info/privacidade';
	const urlImagemOg = 'https://recircuito.info/og-image.png';

	function reverEscolha() {
		apagarConsentimento();
		escolhaApagada = true;
	}
</script>

<svelte:head>
	<title>{textos.titulo} · ReCircuito</title>
	<meta name="description" content={textos.descricao} />
	<link rel="canonical" href={urlCanonica} />
	<meta property="og:type" content="website" />
	<meta property="og:locale" content="pt_BR" />
	<meta property="og:site_name" content="ReCircuito" />
	<meta property="og:url" content={urlCanonica} />
	<meta property="og:title" content="{textos.titulo} · ReCircuito" />
	<meta property="og:description" content={textos.descricao} />
	<meta property="og:image" content={urlImagemOg} />
	<meta name="twitter:card" content="summary_large_image" />
</svelte:head>

<header class="topo">
	<a class="logo" href="{base}/" aria-label={cabecalho.nomeDoSite}>
		<img src="{base}/logos/logo-simbolo-no-c-site.svg" alt="" width="172" height="26" />
	</a>
	<a class="voltar" href="{base}/">{textos.voltar}</a>
</header>

<main id="conteudo">
	<h1>{textos.titulo}</h1>
	<p class="resumo">{textos.resumo}</p>

	{#each textos.secoes as secao (secao.titulo)}
		<section>
			<h2>{secao.titulo}</h2>
			<p>{secao.texto}</p>
		</section>
	{/each}

	<section class="escolha">
		<h2>{textos.tituloEscolha}</h2>
		<button type="button" onclick={reverEscolha} disabled={escolhaApagada}>{textos.reverEscolha}</button>
		<!-- role="status": leitores de tela anunciam a confirmação. -->
		<p role="status">{escolhaApagada ? textos.escolhaApagada : ''}</p>
	</section>

	<p class="contato">
		{textos.contato} <a href="mailto:{rodape.email}">{rodape.email}</a>.
	</p>
</main>

<style>
	.topo {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 16px;
		padding: 20px var(--margem-lateral);
		border-bottom: 1px solid var(--line-soft);
		font-family: var(--font-interface);
	}

	.logo {
		display: inline-flex;
		align-items: center;
		min-width: 44px;
		min-height: 44px;
	}

	.logo img {
		display: block;
		height: 24px;
		width: auto;
	}

	.voltar {
		display: inline-flex;
		align-items: center;
		min-height: 44px;
		font-size: 15px;
		font-weight: 600;
		color: var(--green-strong);
	}

	main {
		max-width: 720px;
		margin: 0 auto;
		padding: 48px var(--margem-lateral) 80px;
	}

	h1 {
		font-size: 40px;
		line-height: 1.1;
		letter-spacing: -0.02em;
	}

	.resumo {
		margin-top: 16px;
		font-size: 20px;
		line-height: 1.5;
		color: var(--ink-2);
	}

	section {
		margin-top: 36px;
		padding-top: 24px;
		border-top: 1px solid var(--line-soft);
	}

	h2 {
		font-family: var(--font-interface);
		font-size: 17px;
		font-weight: 600;
		color: var(--ink);
	}

	section p {
		margin-top: 8px;
		font-size: 18px;
		line-height: 1.55;
		color: var(--ink-2);
	}

	.escolha button {
		margin-top: 12px;
		min-height: 44px;
		padding: 0 20px;
		border: 1px solid var(--ink);
		background: var(--bg);
		font-family: var(--font-interface);
		font-size: 15px;
		font-weight: 600;
		color: var(--ink);
		cursor: pointer;
		transition: transform var(--dur-toque) var(--curva-saida);
	}

	.escolha button:active:not(:disabled) {
		transform: scale(0.97);
	}

	.escolha button:disabled {
		color: var(--muted);
		border-color: var(--line);
		cursor: default;
	}

	.escolha p[role='status'] {
		font-family: var(--font-interface);
		font-size: 15px;
		color: var(--green-strong);
	}

	.contato {
		margin-top: 48px;
		font-family: var(--font-interface);
		font-size: 15px;
		color: var(--muted);
	}

	.contato a {
		display: inline-flex;
		align-items: center;
		min-height: 44px;
		color: var(--green-strong);
		font-weight: 600;
	}

	@media (min-width: 768px) {
		main {
			padding-top: 80px;
		}

		h1 {
			font-size: 56px;
		}
	}
</style>
