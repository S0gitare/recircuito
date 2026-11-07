<script lang="ts">
	import { comoDescartar } from '$lib/conteudo/textos';
	import { revelar } from '$lib/animacao/revelar';
	import PassoSepare from '$lib/ilustracoes/PassoSepare.svelte';
	import PassoApague from '$lib/ilustracoes/PassoApague.svelte';
	import PassoPonto from '$lib/ilustracoes/PassoPonto.svelte';
	import PassoEntregue from '$lib/ilustracoes/PassoEntregue.svelte';
	import Passo from './Passo.svelte';

	// Mesma ordem de `comoDescartar.passos`: o índice liga texto e desenho.
	const ilustracoes = [PassoSepare, PassoApague, PassoPonto, PassoEntregue];
</script>

<section id="como-descartar" aria-labelledby="titulo-como-descartar">
	<div class="cabecalho">
		<h2 id="titulo-como-descartar" use:revelar>{comoDescartar.titulo}</h2>
		<p use:revelar={{ atraso: 0.1 }}>{comoDescartar.texto}</p>
	</div>

	<ol>
		{#each comoDescartar.passos as passo, i (passo.numero)}
			{@const Ilustracao = ilustracoes[i]}
			<Passo numero={passo.numero} nome={passo.nome} descricao={passo.descricao}>
				<Ilustracao />
			</Passo>
		{/each}
	</ol>
</section>

<style>
	section {
		padding: 56px var(--margem-lateral);
		background: var(--bg);
	}

	.cabecalho {
		display: grid;
		gap: 16px;
	}

	h2 {
		font-size: 36px;
		line-height: 1.1;
		letter-spacing: -0.02em;
	}

	.cabecalho p {
		font-size: 18px;
		line-height: 27px;
		color: var(--ink-2);
	}

	ol {
		list-style: none;
		padding: 0;
		margin-top: 40px;
		display: grid;
		gap: 32px;
	}

	@media (min-width: 768px) {
		section {
			padding-block: 120px;
		}

		.cabecalho {
			grid-template-columns: minmax(0, 1fr) 392px;
			align-items: end;
			gap: 48px;
		}

		h2 {
			font-size: 56px;
			line-height: 62px;
		}

		.cabecalho p {
			font-size: 20px;
			line-height: 28px;
		}

		ol {
			margin-top: 64px;
			/* minmax(0, …): a coluna pode ficar menor que o conteúdo, que se ajusta. */
			grid-template-columns: repeat(4, minmax(0, 1fr));
			gap: 0;
		}
	}
</style>
