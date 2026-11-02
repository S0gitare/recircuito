<script lang="ts">
	import { onMount } from 'svelte';
	import type { Map as MapaMapLibre, Marker, Popup } from 'maplibre-gl';
	import { pontosDeColeta as textos } from '$lib/conteudo/textos';
	import { prefereMovimentoReduzido } from '$lib/animacao/movimentoReduzido';
	import { estilizarMapa } from '$lib/mapa/estiloDoMapa';
	import type { PontoDeColeta } from '$lib/api/pontos';

	interface Props {
		pontos: PontoDeColeta[];
		selecionadoId: string | null;
		/** Posição buscada (CEP, bairro ou aparelho). Sem ela, o mapa mostra todos os pontos. */
		referencia: { lat: number; lon: number } | null;
		aoSelecionar: (id: string | null) => void;
	}

	let { pontos, selecionadoId, referencia, aoSelecionar }: Props = $props();

	const URL_DO_ESTILO = 'https://tiles.openfreemap.org/styles/positron';
	const CENTRO_DE_BELEM: [number, number] = [-48.4902, -1.4558]; // [lon, lat]: a ordem do MapLibre
	const LIMITES_DE_BELEM: [[number, number], [number, number]] = [
		[-48.75, -1.65],
		[-48.25, -1.05]
	];

	let conteiner: HTMLDivElement;

	// `$state.raw`: o objeto do MapLibre é enorme e tem vida própria; o Svelte só precisa
	// saber QUANDO ele ficou pronto, não vigiar cada propriedade dele (que é o que `$state` faria).
	let mapa = $state.raw<MapaMapLibre | null>(null);
	let biblioteca: typeof import('maplibre-gl') | null = null;

	// Fora do $state de propósito: são só a "caderneta" de marcadores criados.
	const marcadores = new Map<string, { marcador: Marker; botao: HTMLButtonElement }>();
	let marcadorDaReferencia: Marker | null = null;
	let balao: Popup | null = null;
	let primeiroEnquadramento = true;

	onMount(() => {
		let cancelado = false;
		let instancia: MapaMapLibre | null = null;

		(async () => {
			try {
				// Import dinâmico: o MapLibre depende de `window`/WebGL e quebraria o build estático (SSR).
				const [maplibre] = await Promise.all([
					import('maplibre-gl'),
					import('maplibre-gl/dist/maplibre-gl.css')
				]);
				const resposta = await fetch(URL_DO_ESTILO);
				const estilo = estilizarMapa(await resposta.json());
				if (cancelado) return;

				biblioteca = maplibre;
				instancia = new maplibre.Map({
					container: conteiner,
					style: estilo,
					center: CENTRO_DE_BELEM,
					zoom: 11.5,
					maxBounds: LIMITES_DE_BELEM,
					attributionControl: false,
					cooperativeGestures: false
				});
				// Atribuição compacta e discreta: o crédito ao OpenStreetMap é obrigatório (RNF08).
				instancia.addControl(new maplibre.AttributionControl({ compact: true }), 'bottom-right');
				// O controle compacto nasce aberto e cobriria os pinos no celular: fechamos já na carga.
				// A pessoa ainda abre pelo botão "i" (acessível e discreto).
				instancia.once('load', () => {
					const atribuicao = conteiner.querySelector('.maplibregl-ctrl-attrib');
					atribuicao?.removeAttribute('open');
					atribuicao?.classList.remove('maplibregl-compact-show');
				});
				instancia.on('click', () => aoSelecionar(null));
				mapa = instancia;
			} catch (erro) {
				// Sem WebGL ou sem rede para o estilo: o mapa fica em branco e a lista continua útil.
				console.warn('Mapa indisponível:', erro);
			}
		})();

		return () => {
			cancelado = true;
			marcadores.clear();
			instancia?.remove();
			mapa = null;
		};
	});

	/** Cria o <button> de um ponto. O MapLibre posiciona este elemento com `transform`, por isso o desenho vai num filho. */
	function criarBotao(ponto: PontoDeColeta): HTMLButtonElement {
		const botao = document.createElement('button');
		botao.type = 'button';
		botao.className = 'marcador-ponto';
		botao.setAttribute('aria-label', ponto.nome);
		for (const classe of ['anel', 'circulo']) {
			const parte = document.createElement('span');
			parte.className = classe;
			botao.append(parte);
		}
		botao.addEventListener('click', (evento) => {
			evento.stopPropagation();
			aoSelecionar(ponto.id);
		});
		return botao;
	}

	// 1) Marcadores: refeitos sempre que a lista de pontos muda (filtro, busca).
	$effect(() => {
		if (!mapa || !biblioteca) return;
		const { Marker } = biblioteca;
		const atual = mapa;

		for (const ponto of pontos) {
			const botao = criarBotao(ponto);
			const marcador = new Marker({ element: botao, anchor: 'center' })
				.setLngLat([ponto.coordenadas.lon, ponto.coordenadas.lat])
				.addTo(atual);
			marcadores.set(ponto.id, { marcador, botao });
		}

		return () => {
			for (const { marcador } of marcadores.values()) marcador.remove();
			marcadores.clear();
		};
	});

	// 2) Marcador da posição buscada: um pontinho cheio, só decorativo.
	$effect(() => {
		if (!mapa || !biblioteca || !referencia) return;
		const elemento = document.createElement('div');
		elemento.className = 'marcador-referencia';
		elemento.setAttribute('aria-hidden', 'true');
		marcadorDaReferencia = new biblioteca.Marker({ element: elemento })
			.setLngLat([referencia.lon, referencia.lat])
			.addTo(mapa);
		return () => {
			marcadorDaReferencia?.remove();
			marcadorDaReferencia = null;
		};
	});

	// 3) Seleção: destaca o pino e abre o balão. Lê `pontos` para rodar de novo depois
	// que os marcadores são refeitos (o efeito 1 vem antes e, portanto, termina antes).
	$effect(() => {
		void pontos;
		const id = selecionadoId;
		if (!mapa || !biblioteca) return;

		for (const [idDoMarcador, { botao, marcador }] of marcadores) {
			const ativo = idDoMarcador === id;
			botao.classList.toggle('selecionado', ativo);
			botao.setAttribute('aria-pressed', String(ativo));
			// O selecionado fica por cima dos vizinhos.
			marcador.getElement().style.zIndex = ativo ? '2' : '1';
		}

		const ponto = pontos.find((p) => p.id === id);
		if (!ponto) return;

		const posicao: [number, number] = [ponto.coordenadas.lon, ponto.coordenadas.lat];
		balao = new biblioteca.Popup({
			closeButton: false,
			closeOnClick: false,
			// Sem `anchor`: o MapLibre escolhe sozinho o lado que cabe, evitando o balão cortado na borda.
			offset: 20,
			maxWidth: '240px',
			className: 'balao-ponto'
		})
			.setLngLat(posicao)
			.setDOMContent(montarBalao(ponto))
			.addTo(mapa);

		// Vindo da lista, o ponto pode estar fora da área visível: leva o mapa até ele.
		if (!mapa.getBounds().contains(posicao)) {
			mapa.easeTo({ center: posicao, duration: prefereMovimentoReduzido() ? 0 : 500 });
		}

		return () => {
			balao?.remove();
			balao = null;
		};
	});

	/**
	 * Conteúdo do balão montado com DOM (e não com texto HTML): nome e horário vêm da API,
	 * e `textContent` garante que nenhum caractere vire marcação, mesmo se o dado vier estranho.
	 */
	function montarBalao(ponto: PontoDeColeta): HTMLElement {
		const caixa = document.createElement('div');
		const nome = document.createElement('p');
		nome.className = 'balao-nome';
		nome.textContent = ponto.nome;

		const status = document.createElement('p');
		status.className = 'balao-status';
		// Bolinha verde só para "aberto"; "fechado" e "horário não informado" ficam sem ela.
		if (ponto.aberto_agora === true) {
			const bolinha = document.createElement('span');
			bolinha.className = 'balao-bolinha';
			status.append(bolinha);
		}
		if (ponto.aberto_agora === null) {
			status.append(textos.horarioNaoInformado);
		} else {
			status.append(ponto.aberto_agora ? textos.abertoAgora : textos.fechadoAgora);
		}

		caixa.append(nome, status);
		return caixa;
	}

	// 4) Enquadramento: com busca, a posição e os 3 pontos mais próximos; sem busca, todos os pontos (RF03).
	$effect(() => {
		if (!mapa || !biblioteca) return;
		const { LngLatBounds } = biblioteca;
		const limites = new LngLatBounds();
		let quantidade = 0;

		if (referencia) {
			limites.extend([referencia.lon, referencia.lat]);
			quantidade++;
			// A API já devolve em ordem de distância quando há referência.
			for (const ponto of pontos.slice(0, 3)) {
				limites.extend([ponto.coordenadas.lon, ponto.coordenadas.lat]);
				quantidade++;
			}
		} else {
			for (const ponto of pontos) {
				limites.extend([ponto.coordenadas.lon, ponto.coordenadas.lat]);
				quantidade++;
			}
		}
		if (quantidade === 0) return;

		const animar = !primeiroEnquadramento && !prefereMovimentoReduzido();
		primeiroEnquadramento = false;
		mapa.fitBounds(limites, {
			padding: window.innerWidth < 768 ? 36 : 56,
			maxZoom: 15,
			duration: animar ? 600 : 0
		});
	});
</script>

<div class="mapa" role="region" aria-label={textos.rotuloDoMapa}>
	<div class="tela" bind:this={conteiner}></div>
</div>

<style>
	.mapa {
		width: 100%;
		height: 240px; /* mobile (guia §2) */
		border: 1px solid var(--line-soft);
		background: var(--bg-alt);
	}

	.tela {
		width: 100%;
		height: 100%;
	}

	@media (min-width: 768px) {
		.mapa {
			height: 570px;
		}
	}

	/* Os marcadores e o balão são criados pelo MapLibre, fora do escopo do Svelte: por isso :global. */
	:global(.marcador-ponto) {
		/* 44x44: área de toque mínima (RNF01). O desenho é menor e fica no centro. */
		position: relative;
		width: 44px;
		height: 44px;
		padding: 0;
		border: 0;
		background: none;
		display: grid;
		place-items: center;
	}

	:global(.marcador-ponto .circulo) {
		width: 22px;
		height: 22px;
		border: 2px solid var(--ink);
		border-radius: 50%;
		background: var(--bg);
	}

	:global(.marcador-ponto.selecionado .circulo) {
		width: 28px;
		height: 28px;
		border-color: var(--green);
		background: var(--green);
	}

	:global(.marcador-ponto .anel) {
		display: none;
	}

	/* Anel que cresce de 28px a 108px e some, 1,6s em loop (SPEC §7). */
	:global(.marcador-ponto.selecionado .anel) {
		display: block;
		position: absolute;
		top: 50%;
		left: 50%;
		width: 28px;
		height: 28px;
		margin: -14px 0 0 -14px;
		border: 1.5px solid var(--green);
		border-radius: 50%;
		pointer-events: none;
		animation: pulsar-anel 1.6s ease-out infinite;
	}

	@keyframes pulsar-anel {
		from {
			transform: scale(1);
			opacity: 1;
		}
		to {
			transform: scale(3.86); /* 108 / 28 */
			opacity: 0;
		}
	}

	/* Movimento reduzido (RNF02): o anel fica parado, só marcando o ponto. */
	@media (prefers-reduced-motion: reduce) {
		:global(.marcador-ponto.selecionado .anel) {
			animation: none;
			transform: scale(1.6);
		}
	}

	:global(.marcador-ponto:focus-visible) {
		outline: none;
	}

	:global(.marcador-ponto:focus-visible .circulo) {
		outline: 2px solid var(--ink);
		outline-offset: 3px;
	}

	:global(.marcador-referencia) {
		width: 12px;
		height: 12px;
		border-radius: 50%;
		background: var(--ink);
		border: 2px solid var(--bg);
	}

	/* Balão: caixa branca, borda fina, cantos retos, sem sombra e sem a setinha. */
	:global(.balao-ponto .maplibregl-popup-content) {
		padding: 10px 12px;
		border: 1px solid var(--line);
		border-radius: 0;
		background: var(--bg);
		box-shadow: none;
		font-family: var(--font-interface);
	}

	:global(.balao-ponto .maplibregl-popup-tip) {
		display: none;
	}

	:global(.balao-nome) {
		font-size: 0.875rem;
		font-weight: 600;
		line-height: 1.3;
		color: var(--ink);
	}

	:global(.balao-status) {
		display: flex;
		align-items: center;
		gap: 6px;
		margin-top: 2px;
		font-size: 0.75rem;
		color: var(--muted);
	}

	:global(.balao-bolinha) {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		background: var(--green);
	}

	/* Atribuição discreta, no tom do site. */
	:global(.maplibregl-ctrl-attrib) {
		font-family: var(--font-interface);
		font-size: 0.6875rem;
		background: rgba(255, 255, 255, 0.85);
		border-radius: 0;
	}
</style>
