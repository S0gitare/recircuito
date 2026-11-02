<script lang="ts">
	import { onMount } from 'svelte';
	import { bannerCookies } from '$lib/conteudo/textos';
	import {
		carregarGoogleAnalytics,
		guardarConsentimento,
		lerConsentimento,
		type Consentimento
	} from '$lib/analytics';

	// Começa escondido: o servidor (build estático) não sabe se a pessoa já
	// escolheu, então só o navegador decide se o banner aparece.
	let visivel = $state(false);

	onMount(() => {
		const escolha = lerConsentimento();
		if (escolha === null) visivel = true;
		// Quem já aceitou numa visita anterior volta a ter o Analytics ligado.
		if (escolha === 'aceito') carregarGoogleAnalytics();
	});

	function escolher(escolha: Consentimento) {
		guardarConsentimento(escolha);
		if (escolha === 'aceito') carregarGoogleAnalytics();
		visivel = false;
	}
</script>

<!-- <section> com `aria-label` é anunciada como região (landmark). Não é um
     diálogo modal: não prende o foco, e fica no início da ordem de tabulação. -->
{#if visivel}
	<section class="banner" aria-label={bannerCookies.rotuloDaRegiao}>
		<p class="titulo">{bannerCookies.titulo}</p>
		<p class="texto">{bannerCookies.texto}</p>
		<!-- Os dois botões têm o mesmo tamanho e a mesma cor: recusar não pode ser mais difícil (RF10). -->
		<div class="botoes">
			<button type="button" onclick={() => escolher('recusado')}>{bannerCookies.recusar}</button>
			<button type="button" onclick={() => escolher('aceito')}>{bannerCookies.aceitar}</button>
		</div>
	</section>
{/if}

<style>
	/* Mobile: barra fixa na base, em largura total. */
	.banner {
		position: fixed;
		inset: auto 0 0 0;
		z-index: 50;
		display: flex;
		flex-direction: column;
		gap: 12px;
		padding: 20px 20px 24px;
		background: var(--bg);
		border-top: 1px solid var(--line);
	}

	.titulo {
		font-weight: 500;
		font-size: 22px;
		line-height: 1.2;
	}

	.texto {
		font-family: var(--font-interface);
		font-size: 15px;
		line-height: 22px;
		color: var(--ink);
	}

	.botoes {
		display: flex;
		gap: 12px;
	}

	button {
		flex: 1;
		height: 44px;
		border: 0;
		background: var(--green-strong);
		color: #fff;
		font-weight: 600;
		font-size: 15px;
	}

	button:focus-visible {
		outline-color: var(--ink);
	}

	@media (min-width: 768px) {
		/* Desktop: cartão no canto inferior esquerdo. */
		.banner {
			inset: auto auto 24px 24px;
			width: 520px;
			border: 1px solid var(--line);
			padding: 24px;
		}
	}
</style>
