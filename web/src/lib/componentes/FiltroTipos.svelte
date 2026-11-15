<script lang="ts">
	import { pontosDeColeta as textos } from '$lib/conteudo/textos';
	import type { TipoResiduo } from '$lib/api/pontos';

	interface Props {
		/** Tipos marcados. Lista vazia = "Todos" (RF04). */
		selecionados: TipoResiduo[];
		/** `null` significa o botão "Todos". */
		aoAlternar: (tipo: TipoResiduo | null) => void;
	}

	let { selecionados, aoAlternar }: Props = $props();

	/**
	 * Quantas das 6 colunas cada chip ocupa: Todos/Cabos/Pilhas dividem a 1ª linha
	 * (2+2+2) e Computadores/Celulares a 2ª (3+3). Mesma ordem de `textos.filtro`.
	 */
	const colunas = [2, 2, 2, 3, 3];
</script>

<div class="filtro" role="group" aria-label={textos.rotuloDoFiltro}>
	{#each textos.filtro as opcao, i (opcao.rotulo)}
		{@const marcado = opcao.tipo === null ? selecionados.length === 0 : selecionados.includes(opcao.tipo)}
		<button
			type="button"
			class="chip"
			style:grid-column="span {colunas[i]}"
			aria-pressed={marcado}
			onclick={() => aoAlternar(opcao.tipo)}
		>
			{opcao.rotulo}
		</button>
	{/each}
</div>

<style>
	.filtro {
		display: grid;
		grid-template-columns: repeat(6, 1fr);
		gap: 8px;
	}

	.chip {
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 44px;
		padding: 0 8px;
		border: 1px solid var(--line);
		border-radius: 0;
		background: var(--bg);
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--ink);
		text-align: center;
	}

	/* RNF01: área de toque mínima de 44px mantida em todos os tamanhos de tela. */

	.chip[aria-pressed='true'] {
		background: var(--ink);
		border-color: var(--ink);
		color: #fff;
	}

	.chip:focus-visible {
		outline: 2px solid var(--green-strong);
		outline-offset: 2px;
	}
</style>
