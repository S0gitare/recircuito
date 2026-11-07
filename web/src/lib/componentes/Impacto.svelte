<script lang="ts">
	import { impacto } from '$lib/conteudo/textos';
	import { revelar } from '$lib/animacao/revelar';
	import { contarAte } from '$lib/animacao/contador';

	// O número já vem escrito no HTML (para quem está sem JavaScript e para o
	// build estático); a action `contarAte` o troca por uma contagem de 0 até o valor.
	const formatar = (valor: number) => new Intl.NumberFormat('pt-BR').format(valor);
</script>

<section id="impacto" aria-labelledby="titulo-impacto">
	<h2 id="titulo-impacto" use:revelar>{impacto.titulo}</h2>

	<ul>
		{#each impacto.numeros as item (item.rotulo)}
			<li>
				<p class="numero">
					<span use:contarAte={{ valor: item.valor }}>{formatar(item.valor)}</span>{#if item.unidade}&nbsp;{item.unidade}{/if}
				</p>
				<p class="rotulo">{item.rotulo}</p>
			</li>
		{/each}
	</ul>
</section>

<style>
	section {
		padding: 56px var(--margem-lateral);
		background: var(--bg-alt);
	}

	h2 {
		font-size: 32px;
		line-height: 36px;
	}

	ul {
		list-style: none;
		padding: 0;
		margin-top: 40px;
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 24px 20px;
	}

	li {
		min-width: 0;
		padding-top: 14px;
		border-top: 1px solid var(--line);
	}

	.numero {
		font-weight: 500;
		/* No celular a coluna tem ~165px: "1.240 kg" a 44px encostava no vizinho.
		   Acompanha a largura da tela, entre 32px e 44px. */
		font-size: clamp(32px, 9vw, 44px);
		line-height: 1.1;
		letter-spacing: -0.02em;
		/* Algarismos de mesma largura: o número não "treme" enquanto conta. */
		font-variant-numeric: tabular-nums;
	}

	.rotulo {
		margin-top: 4px;
		font-family: var(--font-interface);
		font-size: 14px;
		line-height: 1.4;
		color: var(--muted);
	}

	@media (min-width: 768px) {
		section {
			padding-block: 100px;
		}

		h2 {
			font-size: 44px;
			line-height: 50px;
		}

		ul {
			margin-top: 64px;
			grid-template-columns: repeat(4, 1fr);
			gap: 0;
		}

		li {
			padding: 0 0 0 32px;
			border-top: 0;
			border-left: 1px solid var(--line);
		}

		/* A primeira coluna alinha com o título: sem linha e sem recuo. */
		li:first-child {
			padding-left: 0;
			border-left: 0;
		}

		.numero {
			font-size: 64px;
		}

		.rotulo {
			font-size: 15px;
		}
	}
</style>
