<script lang="ts">
	import { base } from '$app/paths';
	import { cabecalho, hero, navegacao, rodape } from '$lib/conteudo/textos';
	import { rolarPara } from '$lib/animacao/lenis';
	import IconeFechar from './IconeFechar.svelte';
	import IconeSeta from './IconeSeta.svelte';

	let janela: HTMLDialogElement;

	/**
	 * Abre o menu. `showModal()` (e não `show()`) faz o navegador cuidar do foco
	 * preso dentro do diálogo, do restante da página inerte e do Esc para fechar.
	 */
	export function abrir() {
		janela.showModal();
	}

	function fechar() {
		janela.close();
	}

	// Fecha o menu e só então rola: com o diálogo aberto, a página fica inerte.
	function escolher(evento: MouseEvent, ancora: string) {
		evento.preventDefault();
		fechar();
		rolarPara(`#${ancora}`);
	}

	// Se a tela crescer até o desktop com o menu aberto, fecha: senão a página
	// ficaria inerte atrás de um diálogo escondido.
	function aoRedimensionar() {
		if (janela?.open && window.innerWidth >= 768) fechar();
	}
</script>

<svelte:window onresize={aoRedimensionar} />

<dialog bind:this={janela} class="menu" aria-label={rodape.tituloNavegacao}>
	<div class="topo">
		<img src="{base}/logos/logo-horizontal-site.svg" alt={cabecalho.nomeDoSite} width="175" height="28" />
		<button class="fechar" type="button" aria-label={cabecalho.fecharMenu} onclick={fechar}>
			<IconeFechar />
		</button>
	</div>

	<nav aria-label={rodape.tituloNavegacao}>
		<ul>
			{#each navegacao as item (item.ancora)}
				<li>
					<a href="#{item.ancora}" onclick={(e) => escolher(e, item.ancora)}>{item.rotulo}</a>
				</li>
			{/each}
		</ul>
	</nav>

	<a class="botao" href="#pontos-de-coleta" onclick={(e) => escolher(e, 'pontos-de-coleta')}>
		{hero.botao}
		<IconeSeta />
	</a>
</dialog>

<style>
	/* O <dialog> vem com margem, borda e tamanho próprios: aqui vira tela cheia. */
	.menu {
		width: 100%;
		max-width: none;
		height: 100dvh;
		max-height: none;
		margin: 0;
		padding: 20px 20px 24px;
		border: 0;
		background: var(--bg-hero);
		color: var(--ink);
	}

	/* Só `[open]` define display: com `display: flex` direto o menu apareceria fechado. */
	.menu[open] {
		display: flex;
		flex-direction: column;
	}

	.topo {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.topo img {
		height: 28px;
		width: auto;
	}

	.fechar {
		display: grid;
		place-items: center;
		width: 44px;
		height: 44px;
		padding: 0;
		margin-right: -10px;
		border: 0;
		background: none;
		color: var(--ink);
	}

	nav {
		margin-top: 24px;
	}

	ul {
		list-style: none;
		padding: 0;
	}

	li {
		border-bottom: 1px solid var(--line);
	}

	li a {
		display: block;
		padding: 18px 0;
		font-family: var(--font-leitura);
		font-weight: 500;
		font-size: 34px;
		line-height: 1.15;
		color: var(--ink);
		text-decoration: none;
	}

	.botao {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 10px;
		height: 52px;
		margin-top: auto;
		background: var(--green-strong);
		color: #fff;
		font-family: var(--font-interface);
		font-weight: 600;
		font-size: 17px;
		text-decoration: none;
	}

	.botao:focus-visible {
		outline-color: var(--ink);
	}
</style>
