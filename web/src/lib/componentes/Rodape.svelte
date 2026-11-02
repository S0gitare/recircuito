<script lang="ts">
	import { base } from '$app/paths';
	import { cabecalho, navegacao, rodape } from '$lib/conteudo/textos';
	import { rolarPara } from '$lib/animacao/lenis';
	import ModalAvaliacao from '$lib/componentes/ModalAvaliacao.svelte';

	let modalAberto = $state(false);

	function abrirModalAvaliacao() {
		modalAberto = true;
	}

	function irPara(evento: MouseEvent, ancora: string) {
		evento.preventDefault();
		rolarPara(`#${ancora}`);
	}
</script>

<footer>
	<div class="conteudo">
		<div class="marca">
			<img src="{base}/logos/logo-simbolo-no-c-escuro-site.svg" alt={cabecalho.nomeDoSite} width="172" height="26" />
			<p>{rodape.frase}</p>
		</div>

		<div class="colunas">
			<nav aria-labelledby="rodape-navegacao">
				<h2 id="rodape-navegacao">{rodape.tituloNavegacao}</h2>
				<ul>
					{#each navegacao as item (item.ancora)}
						<li><a href="#{item.ancora}" onclick={(e) => irPara(e, item.ancora)}>{item.rotulo}</a></li>
					{/each}
				</ul>
			</nav>

			<div>
				<h2>{rodape.tituloContato}</h2>
				<ul>
					<li><a href="mailto:{rodape.email}">{rodape.email}</a></li>
					<li><a href="tel:{rodape.telefoneRaw}">{rodape.telefone}</a></li>
					<li>
						<a href={rodape.linkedinUrl} target="_blank" rel="noopener noreferrer">
							{rodape.linkedinTexto}<span class="visualmente-oculto"> (abre em nova aba)</span>
						</a>
					</li>
					<li>
						<button type="button" class="avaliar" onclick={abrirModalAvaliacao}>
							{rodape.avaliarSite}
						</button>
					</li>
				</ul>
			</div>
		</div>
	</div>

	<p class="creditos">{rodape.creditos}</p>

	<ModalAvaliacao bind:aberto={modalAberto} />
</footer>

<style>
	footer {
		padding: 48px var(--margem-lateral) 32px;
		background: var(--footer);
		color: #dff3e5;
		font-family: var(--font-interface);
	}

	.conteudo {
		display: flex;
		flex-direction: column;
		gap: 40px;
	}

	.marca img {
		height: 24px;
		width: auto;
	}

	.marca p {
		margin-top: 16px;
		font-family: var(--font-leitura);
		font-size: 17px;
		line-height: 1.4;
		color: #a9c7b4;
	}

	.colunas {
		display: flex;
		gap: 40px;
	}

	h2 {
		font-family: var(--font-interface);
		font-weight: 600;
		font-size: 15px;
		line-height: 30px;
		color: #fff;
	}

	ul {
		list-style: none;
		padding: 0;
		font-size: 15px;
		line-height: 30px;
	}

	footer a {
		color: inherit;
		text-decoration: none;
	}

	footer a:hover {
		text-decoration: underline;
	}

	footer button.avaliar {
		font-family: inherit;
		font-size: inherit;
		font-weight: 600;
		text-decoration: underline;
		color: var(--green-dark-mode);
		background: none;
		border: none;
		padding: 0;
		cursor: pointer;
		text-align: left;
	}

	footer button.avaliar:hover {
		color: #fff;
	}

	/* Divisória e créditos. */
	.creditos {
		margin-top: 32px;
		padding-top: 24px;
		border-top: 1px solid rgb(255 255 255 / 0.12);
		font-size: 13px;
		color: #7e9c89;
	}

	footer :focus-visible {
		outline-color: #fff;
	}

	@media (min-width: 768px) {
		footer {
			padding-top: 64px;
		}

		.conteudo {
			flex-direction: row;
			justify-content: space-between;
		}

		.marca img {
			height: 26px;
		}

		.colunas {
			gap: 96px;
		}
	}
</style>
