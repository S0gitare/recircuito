<script lang="ts">
	import type { Snippet } from 'svelte';
	import { revelar } from '$lib/animacao/revelar';

	// `children` é a ilustração do item (um dos componentes ItemXxx).
	let { nome, descricao, children }: { nome: string; descricao: string; children: Snippet } = $props();
</script>

<li class="item">
	<div class="ilustracao">
		{@render children()}
	</div>
	<h3 use:revelar>{nome}</h3>
	<p use:revelar>{descricao}</p>
</li>

<style>
	.item {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 24px 6px;
		text-align: center;
	}

	/* Linhas só entre as células: borda direita na coluna da esquerda e
	   borda inferior na linha de cima (nada nas bordas externas da grade). */
	.item:nth-child(odd) {
		border-right: 1px solid var(--line);
	}

	.item:nth-child(-n + 2) {
		border-bottom: 1px solid var(--line);
	}

	.ilustracao {
		width: 100%;
		max-width: 386px;
	}

	.ilustracao :global(svg) {
		width: 100%;
		height: auto;
	}

	h3 {
		margin-top: 8px;
		font-size: 19px;
		line-height: 23px;
	}

	p {
		margin-top: 4px;
		font-size: 15px;
		line-height: 20px;
		color: var(--muted);
	}

	@media (min-width: 768px) {
		.item {
			padding: 48px 48px 56px;
		}

		h3 {
			margin-top: 12px;
			font-size: 28px;
			line-height: 1.2;
		}

		p {
			margin-top: 8px;
			font-size: 18px;
			line-height: 1.45;
		}
	}
</style>
