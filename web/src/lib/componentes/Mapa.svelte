<script lang="ts">
	import { onMount } from 'svelte';
	import type { Map as MapaMapLibre, Marker, Popup } from 'maplibre-gl';
	import { pontosDeColeta as textos } from '$lib/conteudo/textos';
	import { prefereMovimentoReduzido } from '$lib/animacao/movimentoReduzido';
	import { CURVA_CSS, PONTOS, atrasoEmCascata } from '$lib/animacao/movimento';
	import { estilizarMapa } from '$lib/mapa/estiloDoMapa';
	import type { PontoDeColeta } from '$lib/api/pontos';

	interface Props {
		pontos: PontoDeColeta[];
		selecionadoId: string | null;
		/** Posição buscada (CEP, bairro ou aparelho). Sem ela, o mapa mostra todos os pontos. */
		referencia: { lat: number; lon: number; rotulo: string } | null;
		aoSelecionar: (id: string | null) => void;
	}

	let { pontos, selecionadoId, referencia, aoSelecionar }: Props = $props();

	// Lido fora de um efeito (no evento de resize): com um ponto selecionado, o
	// mapa está centrado nele e reenquadrar tudo tiraria a pessoa de lá.
	const selecionadoAtual = () => selecionadoId;

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
	/** Último enquadramento pedido, para refazer quando a tela muda de tamanho. */
	let ultimosLimites: import('maplibre-gl').LngLatBounds | null = null;

	const margemDoEnquadramento = () => (window.innerWidth < 768 ? 36 : 56);

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

		// Girar o celular ou redimensionar a janela muda o tamanho do mapa: sem
		// reenquadrar, os pinos podiam ficar fora da área visível. Espera a
		// pessoa parar de redimensionar (200ms) e reenquadra sem animação.
		let temporizadorDoTamanho: ReturnType<typeof setTimeout> | undefined;
		const aoMudarTamanho = () => {
			clearTimeout(temporizadorDoTamanho);
			temporizadorDoTamanho = setTimeout(() => {
				if (!instancia || !ultimosLimites || selecionadoAtual()) return;
				// Atualiza o tamanho do mapa antes de calcular o enquadramento novo.
				instancia.resize();
				instancia.fitBounds(ultimosLimites, {
					padding: margemDoEnquadramento(),
					maxZoom: 15,
					duration: 0
				});
			}, 200);
		};
		window.addEventListener('resize', aoMudarTamanho);

		return () => {
			cancelado = true;
			window.removeEventListener('resize', aoMudarTamanho);
			clearTimeout(temporizadorDoTamanho);
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
		for (const classe of ['anel', 'ping', 'circulo']) {
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

	/**
	 * Pino novo: o círculo cresce de 50% e um anel fino se abre uma vez em volta
	 * ("ping"), marcando onde ele apareceu. As animações rodam nos filhos do
	 * botão, porque o próprio botão é posicionado pelo MapLibre com `transform`.
	 */
	function animarEntrada(botao: HTMLButtonElement, ordem: number) {
		const atraso = atrasoEmCascata(ordem);
		botao.querySelector('.circulo')?.animate(
			[
				{ opacity: 0, transform: 'scale(0.5)' },
				{ opacity: 1, transform: 'scale(1)' }
			],
			{ duration: PONTOS.entrada, delay: atraso, easing: CURVA_CSS.saida, fill: 'backwards' }
		);
		botao.querySelector('.ping')?.animate(
			[
				{ opacity: 0.45, transform: 'scale(1)' },
				{ opacity: 0, transform: 'scale(2.2)' }
			],
			{ duration: PONTOS.ping, delay: atraso + 60, easing: CURVA_CSS.saida, fill: 'backwards' }
		);
	}

	/** Pino que saiu do filtro: encolhe um pouco e some; só então sai do mapa. */
	function animarSaida(marcador: Marker, botao: HTMLButtonElement) {
		botao.disabled = true; // não pode ser clicado enquanto some
		const circulo = botao.querySelector('.circulo');
		if (!circulo) {
			marcador.remove();
			return;
		}
		circulo.animate(
			[
				{ opacity: 1, transform: 'scale(1)' },
				{ opacity: 0, transform: 'scale(0.6)' }
			],
			{ duration: PONTOS.saida, easing: CURVA_CSS.saida, fill: 'forwards' }
		);
		// Remove pelo relógio, não pelo fim da animação: com a aba em segundo plano
		// o navegador pausa as animações, e o pino ficaria preso no mapa.
		setTimeout(() => marcador.remove(), PONTOS.saida);
	}

	// 1) Marcadores: ao mudar a lista (filtro, busca), compara pelos ids. Quem
	// continua fica parado; quem saiu some animado; quem chegou entra em cascata.
	$effect(() => {
		if (!mapa || !biblioteca) return;
		const { Marker } = biblioteca;
		const atual = mapa;
		const animar = !prefereMovimentoReduzido();
		const idsAtuais = new Set(pontos.map((p) => p.id));

		for (const [id, { marcador, botao }] of marcadores) {
			if (idsAtuais.has(id)) continue;
			marcadores.delete(id);
			if (animar) animarSaida(marcador, botao);
			else marcador.remove();
		}

		let novos = 0;
		for (const ponto of pontos) {
			if (marcadores.has(ponto.id)) continue;
			const botao = criarBotao(ponto);
			const marcador = new Marker({ element: botao, anchor: 'center' })
				.setLngLat([ponto.coordenadas.lon, ponto.coordenadas.lat])
				.addTo(atual);
			marcadores.set(ponto.id, { marcador, botao });
			if (animar) animarEntrada(botao, novos++);
		}
	});

	/**
	 * Texto da etiqueta do ponto de partida. Localização do aparelho vira
	 * "Você está aqui"; uma busca mostra só a primeira parte do rótulo da API
	 * ("Nazaré, Belém - PA" → "Nazaré"), que é o que a pessoa digitou.
	 */
	function textoDaEtiqueta(rotulo: string): string {
		if (rotulo === textos.suaLocalizacao) return textos.voceEstaAqui;
		return rotulo.split(',')[0].trim() || rotulo;
	}

	/**
	 * Marcador do ponto de partida. Precisa ser impossível de confundir com um
	 * ponto de coleta (círculo branco de contorno preto), por isso não depende
	 * só da forma: tem TEXTO. São três camadas, de fora para dentro:
	 * - halo: área clara em volta, que destaca o lugar sem esconder as ruas;
	 * - ponto: preto com anel branco e contorno fino, visível sobre qualquer fundo;
	 * - etiqueta: plaquinha escura acima, com "Você está aqui" ou o bairro buscado.
	 */
	function criarMarcadorDaReferencia(rotulo: string): HTMLDivElement {
		const texto = textoDaEtiqueta(rotulo);
		const elemento = document.createElement('div');
		elemento.className = 'marcador-referencia';
		elemento.setAttribute('role', 'img');
		elemento.setAttribute('aria-label', `${textos.pontoDePartida}: ${texto}`);
		if (prefereMovimentoReduzido()) elemento.classList.add('sem-movimento');

		const halo = document.createElement('span');
		halo.className = 'halo';
		const ponto = document.createElement('span');
		ponto.className = 'ponto';
		const etiqueta = document.createElement('span');
		etiqueta.className = 'etiqueta';
		etiqueta.textContent = texto; // textContent: o rótulo vem da API, nunca vira HTML

		elemento.append(halo, ponto, etiqueta);
		return elemento;
	}

	// 2) Marcador da posição buscada (CEP, bairro ou aparelho).
	$effect(() => {
		if (!mapa || !biblioteca || !referencia) return;
		const elemento = criarMarcadorDaReferencia(referencia.rotulo);
		marcadorDaReferencia = new biblioteca.Marker({ element: elemento, anchor: 'center' })
			.setLngLat([referencia.lon, referencia.lat])
			.addTo(mapa);
		// Por cima dos pinos de coleta (que usam 1 e 2).
		elemento.style.zIndex = '3';
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
		ultimosLimites = limites;
		mapa.fitBounds(limites, {
			padding: margemDoEnquadramento(),
			maxZoom: 15,
			duration: animar ? 600 : 0
		});
	});
</script>

<div class="mapa" role="region" aria-label={textos.rotuloDoMapa} data-lenis-prevent>
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

	/* Anel do "ping" de entrada: invisível parado; só aparece durante a animação. */
	:global(.marcador-ponto .ping) {
		position: absolute;
		top: 50%;
		left: 50%;
		width: 22px;
		height: 22px;
		margin: -11px 0 0 -11px;
		border: 1.5px solid var(--ink);
		border-radius: 50%;
		opacity: 0;
		pointer-events: none;
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

	/* ---- Ponto de partida (posição buscada ou do aparelho) ----
	   O elemento tem 44×44 com o ponto no centro (é o centro que o MapLibre
	   prende na coordenada); halo e etiqueta saem dele com position: absolute.
	   É decorativo para o clique: os pinos de coleta embaixo continuam clicáveis. */
	:global(.marcador-referencia) {
		position: relative;
		width: 44px;
		height: 44px;
		pointer-events: none;
	}

	:global(.marcador-referencia .halo),
	:global(.marcador-referencia .ponto) {
		position: absolute;
		top: 50%;
		left: 50%;
		border-radius: 50%;
	}

	/* Área clara e fina em volta: marca o lugar sem apagar o mapa. */
	:global(.marcador-referencia .halo) {
		width: 56px;
		height: 56px;
		margin: -28px 0 0 -28px;
		background: rgba(15, 26, 20, 0.08);
		border: 1px solid rgba(15, 26, 20, 0.28);
	}

	/* Ponto preto com anel branco e contorno fino por fora: contraste sobre
	   ruas claras, áreas verdes e rótulos do mapa. */
	:global(.marcador-referencia .ponto) {
		width: 18px;
		height: 18px;
		margin: -9px 0 0 -9px;
		background: var(--ink);
		border: 3px solid var(--bg);
		box-shadow: 0 0 0 1px var(--ink);
	}

	/* Plaquinha acima do ponto, com a ponta apontando para ele. */
	:global(.marcador-referencia .etiqueta) {
		position: absolute;
		bottom: calc(50% + 18px);
		left: 50%;
		transform: translateX(-50%);
		max-width: 180px;
		padding: 5px 10px;
		background: var(--ink);
		color: #fff;
		font-family: var(--font-interface);
		font-size: 12px;
		font-weight: 600;
		line-height: 1.2;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	:global(.marcador-referencia .etiqueta::after) {
		content: '';
		position: absolute;
		top: 100%;
		left: 50%;
		margin-left: -5px;
		border: 5px solid transparent;
		border-top-color: var(--ink);
	}

	/* Chegada (uma vez): o ponto "pousa", o halo se abre e a etiqueta desce no lugar.
	   Curta e com pouca amplitude: informa onde é, sem chamar mais atenção que os pinos. */
	:global(.marcador-referencia .ponto) {
		animation: referencia-pousar var(--dur-entrada) var(--curva-saida) both;
	}

	:global(.marcador-referencia .halo) {
		animation: referencia-halo 480ms var(--curva-saida) 80ms both;
	}

	:global(.marcador-referencia .etiqueta) {
		animation: referencia-etiqueta var(--dur-entrada) var(--curva-saida) 140ms both;
	}

	@keyframes referencia-pousar {
		from {
			opacity: 0;
			transform: translateY(-10px) scale(0.7);
		}
	}

	@keyframes referencia-halo {
		from {
			opacity: 0;
			transform: scale(0.4);
		}
	}

	@keyframes referencia-etiqueta {
		from {
			opacity: 0;
			transform: translate(-50%, 6px);
		}
	}

	:global(.marcador-referencia.sem-movimento :is(.halo, .ponto, .etiqueta)) {
		animation: none;
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
