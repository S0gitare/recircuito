<script lang="ts">
	import { base } from '$app/paths';
</script>

<svelte:head>
	<title>ReCircuito · Descarte de lixo eletrônico em Belém</title>
	<meta
		name="description"
		content="Saiba como descartar lixo eletrônico em Belém e encontre o ponto de coleta mais próximo."
	/>
</svelte:head>

<!-- Página provisória: só confirma que estilos, fontes e logo carregam.
     As seções reais (Hero, Sobre, ComoDescartar...) entram na etapa de estrutura. -->
<main class="provisoria">
	<img src="{base}/logos/logo-horizontal-site.svg" alt="ReCircuito" width="320" height="51" />
	<p>Site em construção.</p>
</main>

<style>
	.provisoria {
		min-height: 100svh;
		display: grid;
		place-content: center;
		gap: 1.5rem;
		justify-items: center;
		background: var(--bg-hero);
	}
</style>
