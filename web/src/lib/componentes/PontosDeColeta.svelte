<script lang="ts">
	import { tick } from 'svelte';
	import { pontosDeColeta as textos } from '$lib/conteudo/textos';
	import { urlFormularioSugestao } from '$lib/configuracao';
	import { revelar } from '$lib/animacao/revelar';
	import { prefereMovimentoReduzido } from '$lib/animacao/movimentoReduzido';
	import {
		buscarPontos,
		foiCancelado,
		geocodificar,
		type PontoDeColeta
	} from '$lib/api/pontos';
	import Busca from './Busca.svelte';
	import ListaPontos from './ListaPontos.svelte';
	import Mapa from './Mapa.svelte';

	/** Depois deste tempo sem resposta, avisamos que a API gratuita pode estar "acordando" (SPEC §12). */
	const MS_ATE_AVISAR_DEMORA = 4000;

	// ---- Estado da seção ---------------------------------------------------
	let textoDaBusca = $state('');
	/** De onde medir as distâncias. `null` = sem busca: lista alfabética e mapa com todos os pontos. */
	let referencia = $state<{ lat: number; lon: number; rotulo: string } | null>(null);
	let selecionadoId = $state<string | null>(null);

	let pontos = $state<PontoDeColeta[]>([]);
	let carregando = $state(true);
	let demorando = $state(false);
	let erroDaLista = $state<string | null>(null);

	let ocupadoNaBusca = $state(false);
	let mensagemDaBusca = $state<string | null>(null);

	/** Sobe a cada "Tentar de novo" para o efeito de carga rodar outra vez. */
	let tentativa = $state(0);
	let elementoDoMapa = $state<HTMLElement>();

	// ---- Carga dos pontos --------------------------------------------------
	// O efeito roda sempre que a referência ou a tentativa mudam. A função de
	// limpeza (o `return`) cancela a requisição anterior: sem isso, uma resposta lenta de
	// uma busca antiga poderia chegar depois da nova e sobrescrever a lista.
	$effect(() => {
		const lat = referencia?.lat;
		const lon = referencia?.lon;
		void tentativa;

		const controle = new AbortController();
		carregando = true;
		demorando = false;
		erroDaLista = null;
		const aviso = setTimeout(() => (demorando = true), MS_ATE_AVISAR_DEMORA);

		buscarPontos({ lat, lon, sinal: controle.signal })
			.then((resposta) => {
				pontos = resposta.pontos;
				if (selecionadoId && !pontos.some((p) => p.id === selecionadoId)) selecionadoId = null;
				carregando = false;
			})
			.catch((erro) => {
				if (foiCancelado(erro)) return; // outra carga já assumiu: não mexe no estado
				erroDaLista = erro.message;
				carregando = false;
			})
			.finally(() => clearTimeout(aviso));

		return () => {
			controle.abort();
			clearTimeout(aviso);
		};
	});

	// ---- Busca por CEP ou bairro (RF01) ------------------------------------
	let controleDaBusca: AbortController | null = null;

	async function buscarPorTexto(texto: string) {
		const termo = texto.trim();
		if (!termo) return;
		// A API exige ao menos 2 caracteres; avisar aqui evita uma ida à rede à toa.
		if (termo.length < 2) {
			mensagemDaBusca = textos.naoEncontrado;
			return;
		}

		controleDaBusca?.abort();
		controleDaBusca = new AbortController();
		ocupadoNaBusca = true;
		mensagemDaBusca = null;
		try {
			const local = await geocodificar(termo, controleDaBusca.signal);
			referencia = { lat: local.lat, lon: local.lon, rotulo: local.rotulo };
		} catch (erro) {
			if (foiCancelado(erro)) return;
			mensagemDaBusca = (erro as Error).message;
		} finally {
			ocupadoNaBusca = false;
		}
	}

	// ---- "Usar minha localização" (RF02) -----------------------------------
	// A posição vira só os parâmetros `lat`/`lon` da consulta de pontos: não é guardada
	// nem enviada a nenhum outro lugar (RNF06).
	function usarMinhaLocalizacao() {
		if (!('geolocation' in navigator)) {
			mensagemDaBusca = textos.localizacaoIndisponivel;
			return;
		}
		controleDaBusca?.abort();
		ocupadoNaBusca = true;
		mensagemDaBusca = textos.localizando;
		navigator.geolocation.getCurrentPosition(
			(posicao) => {
				referencia = {
					lat: posicao.coords.latitude,
					lon: posicao.coords.longitude,
					rotulo: textos.suaLocalizacao
				};
				mensagemDaBusca = null;
				ocupadoNaBusca = false;
			},
			(erro) => {
				// Código 1 = a pessoa negou a permissão; os demais são falha técnica (sem sinal, tempo esgotado).
				mensagemDaBusca =
					erro.code === erro.PERMISSION_DENIED ? textos.localizacaoNegada : textos.localizacaoIndisponivel;
				ocupadoNaBusca = false;
			},
			{ timeout: 10000, maximumAge: 60000 }
		);
	}

	function limparReferencia() {
		referencia = null;
		textoDaBusca = '';
		mensagemDaBusca = null;
	}

	// ---- Seleção sincronizada entre lista e mapa (RF06) --------------------
	async function selecionarPelaLista(id: string | null) {
		selecionadoId = id;
		if (!id) return;
		// No celular o mapa fica acima da lista e pode estar fora da tela: traz ele para a vista.
		await tick();
		elementoDoMapa?.scrollIntoView({
			block: 'nearest',
			behavior: prefereMovimentoReduzido() ? 'auto' : 'smooth'
		});
	}
</script>

<section id="pontos-de-coleta" aria-labelledby="titulo-pontos">
	<div class="interno">
		<div class="topo">
			<h2 id="titulo-pontos" use:revelar>{textos.titulo}</h2>

			<Busca
				bind:valor={textoDaBusca}
				mensagem={mensagemDaBusca}
				ocupado={ocupadoNaBusca}
				aoBuscar={buscarPorTexto}
				aoUsarLocalizacao={usarMinhaLocalizacao}
			/>
		</div>

		<div class="mapa" bind:this={elementoDoMapa}>
			<Mapa {pontos} {selecionadoId} {referencia} aoSelecionar={(id) => (selecionadoId = id)} />
		</div>

		<div class="lista">
			{#if referencia}
				<p class="referencia">
					{textos.referenciaAtual} <strong>{referencia.rotulo}</strong>
					<button type="button" class="limpar" onclick={limparReferencia}>
						{textos.limparReferencia}
					</button>
				</p>
			{/if}

			<!-- aria-live: leitores de tela anunciam quando a lista muda ou aparece um aviso. -->
			<div class="estado" aria-live="polite" aria-busy={carregando}>
				{#if erroDaLista}
					<p class="aviso">{erroDaLista}</p>
					<button type="button" class="tentar" onclick={() => tentativa++}>{textos.tentarDeNovo}</button>
				{:else if carregando && pontos.length === 0}
					<p class="aviso">{textos.carregando}</p>
					{#if demorando}<p class="aviso suave">{textos.primeiraBuscaDemora}</p>{/if}
				{:else if !carregando && pontos.length === 0}
					<p class="aviso">{textos.semResultados}</p>
				{:else if carregando}
					<!-- Recarregando com uma lista antiga na tela: mantém a lista, só avisa. -->
					<p class="aviso suave">{textos.carregando}</p>
					{#if demorando}<p class="aviso suave">{textos.primeiraBuscaDemora}</p>{/if}
				{/if}
			</div>

			{#if pontos.length > 0 && !erroDaLista}
				<div class="itens" class:atualizando={carregando}>
					<ListaPontos {pontos} {selecionadoId} aoSelecionar={selecionarPelaLista} />
				</div>
			{/if}

			<p class="sugerir">
				{textos.sugerirPergunta}
				{#if urlFormularioSugestao}
					<a href={urlFormularioSugestao} target="_blank" rel="noopener noreferrer">{textos.sugerirLink}</a>
				{:else}
					<!-- Sem link ainda (SPEC §14): texto apagado em vez de um link quebrado. -->
					<span class="em-breve">{textos.sugerirLink} {textos.sugerirEmBreve}</span>
				{/if}
			</p>
		</div>
	</div>
</section>

<style>
	section {
		background: var(--bg);
		padding: 56px var(--margem-lateral);
		font-family: var(--font-interface);
	}

	/* Mobile: uma coluna na ordem título, busca, filtro, mapa, lista (guia §2). */
	.interno {
		display: grid;
		gap: 24px;
		max-width: 1344px;
		margin: 0 auto;
	}

	.topo {
		display: grid;
		gap: 16px;
		align-content: start;
	}

	h2 {
		font-family: var(--font-leitura);
		font-weight: 500;
		font-size: 2.125rem;
		line-height: 38px;
		letter-spacing: -0.02em;
		color: var(--ink);
		margin-bottom: 8px;
	}

	.lista {
		min-width: 0;
	}

	/* ---- Estados e textos de apoio ---- */
	.referencia {
		margin-bottom: 8px;
		font-size: 0.9375rem;
		color: var(--ink-2);
	}

	.limpar,
	.tentar {
		padding: 0;
		border: 0;
		background: none;
		min-height: 44px;
		margin-left: 8px;
		font-size: 0.875rem;
		font-weight: 600;
		color: var(--green-strong);
		text-decoration: underline;
		text-underline-offset: 3px;
	}

	.tentar {
		margin-left: 0;
	}

	.limpar:focus-visible,
	.tentar:focus-visible,
	.sugerir a:focus-visible {
		outline: 2px solid var(--ink);
		outline-offset: 3px;
	}

	.aviso {
		padding: 16px 0;
		font-size: 0.9375rem;
		line-height: 1.5;
		color: var(--ink-2);
		border-bottom: 1px solid var(--line-soft);
	}

	.aviso.suave {
		color: var(--muted);
	}

	.itens {
		transition: opacity 0.2s;
	}

	.itens.atualizando {
		opacity: 0.55;
	}

	.sugerir {
		margin-top: 24px;
		font-size: 0.9375rem;
		color: var(--muted);
	}

	.sugerir a {
		font-weight: 600;
		color: var(--green-strong);
		text-decoration: underline;
		text-underline-offset: 3px;
	}

	.em-breve {
		font-weight: 600;
	}

	/* ---- Desktop: coluna de 460px + mapa de 832x570 (guia §2) ---- */
	@media (min-width: 768px) {
		section {
			padding-top: 100px;
			padding-bottom: 100px;
		}

		.interno {
			grid-template-columns: minmax(0, 460px) minmax(0, 1fr);
			grid-template-areas:
				'topo mapa'
				'lista mapa';
			grid-template-rows: auto 1fr;
			column-gap: 52px;
			row-gap: 24px;
		}

		.topo {
			grid-area: topo;
			gap: 16px;
		}

		.mapa {
			grid-area: mapa;
			/* O mapa acompanha a rolagem enquanto a lista (que pode ser longa) passa ao lado. */
			position: sticky;
			top: 24px;
			align-self: start;
		}

		.lista {
			grid-area: lista;
		}

		h2 {
			font-size: 3.25rem;
			line-height: 56px;
			margin-bottom: 32px; /* 48px do protótipo até a busca, menos o gap de 16px */
		}
	}
</style>
