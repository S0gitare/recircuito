<script lang="ts">
	import { navegacao, sobre } from '$lib/conteudo/textos';
	import { revelar } from '$lib/animacao/revelar';
</script>

<section id="sobre" aria-label={navegacao[0].rotulo}>
	<p class="frase" use:revelar>{sobre.frase}</p>
	<p class="texto" use:revelar={{ atraso: 0.1 }}>{sobre.texto}</p>
</section>

<style>
	section {
		display: grid;
		gap: 24px;
		padding: 56px var(--margem-lateral);
		background: var(--bg-alt);
	}

	.frase {
		font-weight: 500;
		font-size: 30px;
		line-height: 36px;
		letter-spacing: -0.015em;
		color: var(--ink);
	}

	.texto {
		font-size: 18px;
		line-height: 27px;
		color: var(--ink-2);
	}

	@media (min-width: 768px) {
		section {
			grid-template-columns: minmax(0, 780px) 392px;
			justify-content: space-between;
			align-items: end;
			gap: 48px;
			padding-block: 120px;
		}

		.frase {
			font-size: 46px;
			line-height: 54px;
		}

		.texto {
			font-size: 20px;
			line-height: 28px;
		}
	}
</style>
