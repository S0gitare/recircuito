<script lang="ts">
	import { oQueDescartar } from '$lib/conteudo/textos';
	import { revelar } from '$lib/animacao/revelar';
	import ItemCelulares from '$lib/ilustracoes/ItemCelulares.svelte';
	import ItemPilhas from '$lib/ilustracoes/ItemPilhas.svelte';
	import ItemComputadores from '$lib/ilustracoes/ItemComputadores.svelte';
	import ItemCabos from '$lib/ilustracoes/ItemCabos.svelte';
	import Item from './Item.svelte';

	// Mesma ordem de `oQueDescartar.itens`: o índice liga texto e desenho.
	const ilustracoes = [ItemCelulares, ItemPilhas, ItemComputadores, ItemCabos];
</script>

<section id="o-que-descartar" aria-labelledby="titulo-o-que-descartar">
	<h2 id="titulo-o-que-descartar" use:revelar>{oQueDescartar.titulo}</h2>
	<p class="texto" use:revelar={{ atraso: 0.1 }}>{oQueDescartar.texto}</p>

	<ul>
		{#each oQueDescartar.itens as item, i (item.tipo)}
			{@const Ilustracao = ilustracoes[i]}
			<Item nome={item.nome} descricao={item.descricao}>
				<Ilustracao />
			</Item>
		{/each}
	</ul>
</section>

<style>
	section {
		padding: 56px var(--margem-lateral);
		background: var(--bg-alt);
		text-align: center;
	}

	h2 {
		font-size: 38px;
		line-height: 42px;
		letter-spacing: -0.02em;
	}

	.texto {
		max-width: 560px;
		margin: 16px auto 0;
		font-size: 18px;
		line-height: 27px;
		color: var(--ink-2);
	}

	ul {
		list-style: none;
		padding: 0;
		margin-top: 40px;
		display: grid;
		grid-template-columns: 1fr 1fr;
	}

	@media (min-width: 768px) {
		section {
			padding-block: 120px;
		}

		h2 {
			font-size: 72px;
			line-height: 76px;
		}

		.texto {
			margin-top: 24px;
			font-size: 20px;
			line-height: 28px;
		}

		ul {
			margin-top: 80px;
		}
	}
</style>
