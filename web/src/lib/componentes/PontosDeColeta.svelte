<script lang="ts">
	import { tick } from 'svelte';
	import { pontosDeColeta as textos } from '$lib/conteudo/textos';
	import { revelar } from '$lib/animacao/revelar';
	import { prefereMovimentoReduzido } from '$lib/animacao/movimentoReduzido';
	import {
		buscarPontos,
		foiCancelado,
		geocodificar,
		type PontoDeColeta,
		type TipoResiduo
	} from '$lib/api/pontos';
	import Busca from './Busca.svelte';
	import FiltroTipos from './FiltroTipos.svelte';
	import ListaPontos from './ListaPontos.svelte';
	import Mapa from './Mapa.svelte';
	import ModalSugestao from './ModalSugestao.svelte';

	/** Depois deste tempo sem resposta, avisamos que a API gratuita pode estar "acordando" (SPEC §12). */
	const MS_ATE_AVISAR_DEMORA = 4000;

	// ---- Estado da seção ---------------------------------------------------
	let sugestaoAberta = $state(false);
	let textoDaBusca = $state('');
	/** Lista vazia = "Todos" (RF04). */
	let tiposSelecionados = $state<TipoResiduo[]>([]);
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
	/** Contêiner da lista com janela de rolagem própria (evita alongar a página). */
	let elementoItens = $state<HTMLDivElement>();

	// ---- Carga dos pontos --------------------------------------------------
	// O efeito roda sempre que o filtro, a referência ou a tentativa mudam. A função de
	// limpeza (o `return`) cancela a requisição anterior: sem isso, uma resposta lenta de
	// uma busca antiga poderia chegar depois da nova e sobrescrever a lista.
	$effect(() => {
		const tipos = [...tiposSelecionados];
		const lat = referencia?.lat;
		const lon = referencia?.lon;
		void tentativa;

		const controle = new AbortController();
		carregando = true;
		demorando = false;
		erroDaLista = null;
		const aviso = setTimeout(() => (demorando = true), MS_ATE_AVISAR_DEMORA);

		buscarPontos({ lat, lon, tipos, sinal: controle.signal })
			.then((resposta) => {
				pontos = resposta.pontos;
				// Se o ponto selecionado saiu da lista (por causa do filtro), desfaz a seleção.
				if (selecionadoId && !pontos.some((p) => p.id === selecionadoId)) selecionadoId = null;
				carregando = false;
				// Ao carregar uma nova lista de pontos, reseta a rolagem para o topo
				// para que o usuário visualize os resultados mais relevantes primeiro.
				if (elementoItens) {
					elementoItens.scrollTop = 0;
				}
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
			mensagemDaBusca = textos.buscaCurta;
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

	// ---- Filtro (RF04) -----------------------------------------------------
	function alternarTipo(tipo: TipoResiduo | null) {
		if (tipo === null) {
			tiposSelecionados = []; // "Todos" limpa os tipos
			return;
		}
		// Desmarcar o último tipo volta para "Todos": a lista vazia é exatamente isso.
		tiposSelecionados = tiposSelecionados.includes(tipo)
			? tiposSelecionados.filter((t) => t !== tipo)
			: [...tiposSelecionados, tipo];
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

	/**
	 * Ao clicar em um pino no mapa, seleciona o ponto e rola a janela interna
	 * da lista até que ele fique visível, sem deslocar a página inteira.
	 */
	async function selecionarPeloMapa(id: string | null) {
		selecionadoId = id;
		if (!id || !elementoItens) return;

		await tick();
		const idEscapado = typeof CSS !== 'undefined' && CSS.escape ? CSS.escape(id) : id;
		const item = elementoItens.querySelector<HTMLElement>(`[data-ponto-id="${idEscapado}"]`);
		if (!item) return;

		// Calcula a posição do item relativa ao topo da área interna rolável (descontando o border-top)
		const rectConteiner = elementoItens.getBoundingClientRect();
		const rectItem = item.getBoundingClientRect();
		const topoItem =
			rectItem.top - (rectConteiner.top + elementoItens.clientTop) + elementoItens.scrollTop;
		const alturaItem = rectItem.height;

		const topoVisivel = elementoItens.scrollTop;
		const baseVisivel = topoVisivel + elementoItens.clientHeight;

		// Rola suavemente apenas se o item não estiver totalmente dentro da janela (com tolerância para subpixels)
		const estaVisivel = topoItem >= topoVisivel - 1 && topoItem + alturaItem <= baseVisivel + 1;
		if (!estaVisivel) {
			elementoItens.scrollTo({
				top: topoItem,
				behavior: prefereMovimentoReduzido() ? 'auto' : 'smooth'
			});
		}
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

			<FiltroTipos selecionados={tiposSelecionados} aoAlternar={alternarTipo} />
		</div>

		<div class="mapa" bind:this={elementoDoMapa}>
			<Mapa {pontos} {selecionadoId} {referencia} aoSelecionar={selecionarPeloMapa} />
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
				<div
					class="itens"
					class:atualizando={carregando}
					bind:this={elementoItens}
					data-lenis-prevent
				>
					<ListaPontos {pontos} {selecionadoId} aoSelecionar={selecionarPelaLista} />
				</div>
			{/if}

			<p class="sugerir">
				{textos.sugerirPergunta}
				<button type="button" class="link-sugerir" onclick={() => (sugestaoAberta = true)}>
					{textos.sugerirLink}
				</button>
			</p>
		</div>
	</div>
</section>

<ModalSugestao bind:aberto={sugestaoAberta} />

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
	.link-sugerir:focus-visible {
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
		/* Não duplica a linha divisória com o topo de .itens logo abaixo */
		border-bottom: 0;
	}

	.itens {
		position: relative;
		/* Limita a altura para exibir ~2,5 a 3 itens, com corte que sinaliza haver mais conteúdo */
		max-height: 380px;
		overflow-x: hidden;
		overflow-y: auto;
		overscroll-behavior: contain;
		border-top: 1px solid var(--line-soft);
		border-bottom: 1px solid var(--line-soft);
		padding-right: 10px;
		transition: opacity 0.2s;
		/* Barra de rolagem fina e discreta nos tokens do site */
		scrollbar-width: thin;
		scrollbar-color: var(--line) transparent;
	}

	.itens::-webkit-scrollbar {
		width: 6px;
	}

	.itens::-webkit-scrollbar-track {
		background: transparent;
	}

	.itens::-webkit-scrollbar-thumb {
		background: var(--line);
		border-radius: 0;
	}

	.itens::-webkit-scrollbar-thumb:hover {
		background: var(--ink-2);
	}

	.itens.atualizando {
		opacity: 0.55;
	}

	.sugerir {
		margin-top: 24px;
		font-size: 0.9375rem;
		color: var(--muted);
	}

	/* Botão com cara de link: abre o modal, não leva a outra página. */
	.link-sugerir {
		padding: 0;
		background: none;
		border: none;
		font: inherit;
		font-weight: 600;
		color: var(--green-strong);
		text-decoration: underline;
		text-underline-offset: 3px;
		cursor: pointer;
	}

	.link-sugerir:hover {
		text-decoration-thickness: 2px;
	}

	/* ---- Desktop: coluna de 460px + mapa, os dois com a mesma altura ----
	   A seção cabe numa tela: o painel (título, busca, filtro, lista | mapa) tem
	   a altura da janela menos as margens, entre 480px e 640px. A lista ocupa o
	   que sobra na coluna da esquerda e rola por dentro; o mapa preenche a
	   coluna da direita inteira, sem ser cortado embaixo. */
	@media (min-width: 768px) {
		section {
			padding-top: 56px;
			padding-bottom: 56px;
		}

		.interno {
			grid-template-columns: minmax(0, 460px) minmax(0, 1fr);
			grid-template-areas:
				'topo mapa'
				'lista mapa';
			grid-template-rows: auto minmax(0, 1fr);
			column-gap: 48px;
			row-gap: 16px;
			height: clamp(480px, calc(100svh - 112px), 640px);
		}

		.topo {
			grid-area: topo;
			gap: 12px;
		}

		.mapa {
			grid-area: mapa;
			min-height: 0;
		}

		/* O componente Mapa tem 570px fixos; aqui ele acompanha a altura do painel. */
		.mapa :global(.mapa) {
			height: 100%;
		}

		.lista {
			grid-area: lista;
			display: flex;
			flex-direction: column;
			min-height: 0;
		}

		/* A lista cresce até o fim da coluna e rola por dentro. */
		.itens {
			flex: 1 1 auto;
			min-height: 0;
			max-height: none;
		}

		.aviso {
			padding: 12px 0;
		}

		.sugerir {
			flex-shrink: 0;
			margin-top: 12px;
		}

		h2 {
			font-size: 2.75rem;
			line-height: 48px;
			margin-bottom: 12px;
		}
	}
</style>
