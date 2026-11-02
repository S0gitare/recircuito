<script lang="ts">
	import { base } from '$app/paths';
	import { cabecalho, navegacao, rodape } from '$lib/conteudo/textos';
	import { rolarPara } from '$lib/animacao/lenis';
	import IconeMenu from './IconeMenu.svelte';
	import MenuMobile from './MenuMobile.svelte';

	// Referência ao componente do menu para chamar `abrir()` (função exportada por ele).
	let menu: MenuMobile;

	// O `href` é o plano B (sem JavaScript, o navegador já pula para a âncora).
	// Com JavaScript, cancelamos o salto brusco e deixamos o Lenis rolar suave.
	function irPara(evento: MouseEvent, ancora: string) {
		evento.preventDefault();
		rolarPara(`#${ancora}`);
	}
</script>

<div class="cabecalho">
	<a class="logo" href="{base}/" aria-label={cabecalho.nomeDoSite}>
		<img src="{base}/logos/logo-simbolo-no-c-site.svg" alt="" width="172" height="26" />
	</a>

	<nav class="links" aria-label={rodape.tituloNavegacao}>
		{#each navegacao as item (item.ancora)}
			<a href="#{item.ancora}" onclick={(e) => irPara(e, item.ancora)}>{item.rotulo}</a>
		{/each}
	</nav>

	<button class="abrir" type="button" aria-label={cabecalho.abrirMenu} onclick={() => menu.abrir()}>
		<IconeMenu />
	</button>
</div>

<MenuMobile bind:this={menu} />

<style>
	.cabecalho {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 20px var(--margem-lateral) 0;
	}

	.logo {
		display: block;
		line-height: 0;
	}

	.logo img {
		height: 24px;
		width: auto;
	}

	.links {
		display: none;
	}

	.links a {
		font-family: var(--font-interface);
		font-weight: 500;
		font-size: 16px;
		color: var(--ink);
		text-decoration: none;
	}

	.links a:hover {
		text-decoration: underline;
		text-underline-offset: 0.3em;
	}

	/* Botão ☰: alvo de toque de 44×44 (RNF01). */
	.abrir {
		display: grid;
		place-items: center;
		width: 44px;
		height: 44px;
		padding: 0;
		margin-right: -10px; /* alinha o traço do ícone à margem de 20px */
		border: 0;
		background: none;
		color: var(--ink);
	}

	@media (min-width: 768px) {
		.cabecalho {
			padding-top: 32px;
		}

		.logo img {
			height: 26px;
		}

		.links {
			display: flex;
			gap: 48px;
		}

		.abrir {
			display: none;
		}
	}
</style>
