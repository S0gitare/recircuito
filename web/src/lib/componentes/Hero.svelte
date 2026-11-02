<script lang="ts">
	import { hero } from '$lib/conteudo/textos';
	import { rolarPara } from '$lib/animacao/lenis';
	import CelularExplodido from '$lib/ilustracoes/CelularExplodido.svelte';
	import Cabecalho from './Cabecalho.svelte';
	import IconeSeta from './IconeSeta.svelte';

	// No desktop o título quebra em duas linhas fixas ("Seu lixo eletrônico" /
	// "tem destino."). Separamos as duas últimas palavras do resto para não
	// escrever o texto fora do textos.ts. No mobile as linhas fluem normalmente.
	const palavras = hero.titulo.split(' ');
	const linhaUm = palavras.slice(0, -2).join(' ');
	const linhaDois = palavras.slice(-2).join(' ');

	function aoClicarNoBotao(evento: MouseEvent) {
		evento.preventDefault();
		rolarPara('#pontos-de-coleta');
	}
</script>

<!-- O <header> da página: logo e menu ficam dentro do topo (hero). -->
<header class="hero">
	<Cabecalho />

	<div class="arte">
		<CelularExplodido titulo={hero.descricaoDoDesenho} />
	</div>

	<div class="base">
		<h1>
			<span class="linha">{linhaUm}</span>
			<span class="linha">{linhaDois}</span>
		</h1>

		<div class="apoio">
			<p>{hero.texto}</p>
			<a class="botao" href="#pontos-de-coleta" onclick={aoClicarNoBotao}>
				{hero.botao}
				<IconeSeta />
			</a>
		</div>
	</div>
</header>

<style>
	.hero {
		display: flex;
		flex-direction: column;
		min-height: 100svh;
		background: var(--bg-hero);
	}

	/* O desenho ocupa o espaço que sobra e fica centralizado. */
	.arte {
		flex: 1;
		display: grid;
		place-items: center;
		padding: 24px var(--margem-lateral);
	}

	/* Mobile: 257px de largura (390×491 de proporção do desenho = 257×324). */
	.arte :global(> *) {
		width: 257px;
		max-width: 100%;
	}

	.base {
		display: flex;
		flex-direction: column;
		gap: 24px;
		padding: 0 var(--margem-lateral) 32px;
	}

	h1 {
		font-size: 50px;
		line-height: 50px;
		letter-spacing: -0.025em;
	}

	/* Mobile: as duas partes correm como texto comum, com espaço entre elas. */
	.linha {
		display: inline;
	}

	.linha + .linha::before {
		content: ' ';
	}

	.apoio {
		display: flex;
		flex-direction: column;
		gap: 24px;
	}

	.apoio p {
		font-size: 18px;
		line-height: 26px;
		color: var(--ink-2);
	}

	.botao {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 10px;
		height: 52px;
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

	@media (min-width: 768px) {
		.arte {
			padding-top: 32px;
			padding-bottom: 32px;
		}

		/* Desktop: o bloco da vista explodida tem 1212px de largura (proporção 1212×491). */
		.arte :global(> *) {
			width: 1212px;
		}

		.base {
			display: grid;
			grid-template-columns: 1fr 392px;
			align-items: end;
			gap: 48px;
			padding-bottom: 48px;
		}

		h1 {
			font-size: 100px;
			line-height: 96px;
		}

		.linha {
			display: block;
		}

		.linha + .linha::before {
			content: none;
		}

		.apoio {
			gap: 20px;
		}

		.apoio p {
			font-size: 20px;
			line-height: 27px;
		}

		.botao {
			width: 300px;
		}
	}
</style>
