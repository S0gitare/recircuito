<script lang="ts">
	import type { Snippet } from 'svelte';
	import { revelar } from '$lib/animacao/revelar';

	// `children` é a ilustração do passo (um dos componentes PassoXxx).
	let {
		numero,
		nome,
		descricao,
		children
	}: { numero: string; nome: string; descricao: string; children: Snippet } = $props();
</script>

<li class="passo">
	<div class="topo">
		<h3 class="faixa" use:revelar>{nome}</h3>
		<!-- O número é só enfeite: a ordem já está na lista numerada. -->
		<span class="numero" aria-hidden="true">{numero}</span>
	</div>

	<div class="ilustracao">
		{@render children()}
	</div>

	<p class="descricao" use:revelar>{descricao}</p>
</li>

<style>
	.passo {
		display: flex;
		flex-direction: column;
	}

	/* Mobile: a faixa verde ocupa a largura toda e o número fica dentro dela. */
	.topo {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 14px 16px;
		background: var(--green);
	}

	.faixa {
		font-weight: 500;
		font-size: 24px;
		line-height: 1.15;
		color: #fff;
	}

	.numero {
		font-family: var(--font-interface);
		font-weight: 500;
		font-size: 14px;
		color: #dff3e5;
	}

	.ilustracao {
		width: 210px;
		max-width: 100%;
		margin: 24px auto 0;
	}

	.ilustracao :global(svg) {
		width: 100%;
		height: auto;
	}

	.descricao {
		margin-top: 16px;
		font-size: 17px;
		line-height: 25px;
		color: var(--muted);
		text-align: center;
	}

	@media (min-width: 768px) {
		/* Cada coluna tem uma linha à esquerda, menos a primeira. */
		.passo:not(:first-child) {
			border-left: 1px solid var(--line-soft);
		}

		/* Desktop: a faixa deixa 66px livres à direita para o número. */
		.topo {
			height: 72px;
			padding: 0;
			background: none;
		}

		.faixa {
			display: flex;
			align-items: center;
			flex: 0 0 calc(100% - 66px);
			height: 100%;
			padding-left: 24px;
			background: var(--green);
			font-size: 26px;
		}

		.numero {
			flex: 1;
			text-align: center;
			font-size: 16px;
			color: var(--muted);
		}

		.ilustracao {
			width: 300px;
			margin-top: 48px;
		}

		.descricao {
			margin-top: 24px;
			padding: 0 24px;
			text-align: left;
		}
	}
</style>
