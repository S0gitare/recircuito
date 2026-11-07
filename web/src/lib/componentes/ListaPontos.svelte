<script lang="ts">
	import { pontosDeColeta as textos } from '$lib/conteudo/textos';
	import type { PontoDeColeta } from '$lib/api/pontos';
	import { flip } from 'svelte/animate';
	import { quintOut } from 'svelte/easing';
	import { PONTOS, atrasoEmCascata } from '$lib/animacao/movimento';
	import { prefereMovimentoReduzido } from '$lib/animacao/movimentoReduzido';

	interface Props {
		pontos: PontoDeColeta[];
		selecionadoId: string | null;
		/** Clicar de novo no ponto já selecionado envia `null` (desmarca). */
		aoSelecionar: (id: string | null) => void;
	}

	let { pontos, selecionadoId, aoSelecionar }: Props = $props();

	/** "850 m" abaixo de 1 km, "1,2 km" acima. `toLocaleString` já usa a vírgula do pt-BR. */
	function formatarDistancia(km: number): string {
		if (km < 1) return `${Math.round((km * 1000) / 10) * 10} m`;
		return `${km.toLocaleString('pt-BR', { maximumFractionDigits: 1 })} km`;
	}

	function enderecoEmUmaLinha(ponto: PontoDeColeta): string {
		const { logradouro, numero, bairro } = ponto.endereco;
		return `${logradouro}${numero ? `, ${numero}` : ''} · ${bairro}`;
	}

	/**
	 * Link de rota do Google Maps (RF07). O destino por coordenadas evita ambiguidade
	 * de endereço; a pessoa escolhe a origem e o meio de transporte no app.
	 */
	function linkDeRota(ponto: PontoDeColeta): string {
		const { lat, lon } = ponto.coordenadas;
		return `https://www.google.com/maps/dir/?api=1&destination=${lat},${lon}`;
	}

	// ---- Animação ao filtrar ----
	// `quintOut` é a curva de saída do Svelte mais próxima de --curva-saida.
	// Só os itens que entram ou saem se animam; os que ficam deslizam (FLIP)
	// para o novo lugar. No primeiro carregamento nada se anima: o Svelte só
	// roda `in:` em itens adicionados depois que a lista já existe.
	const semMovimento = () => prefereMovimentoReduzido();

	/** Item novo: sobe 8px enquanto aparece, em cascata curta com os outros novos. */
	function entrar(_no: Element, { ordem }: { ordem: number }) {
		if (semMovimento()) return { duration: 0 };
		return {
			duration: PONTOS.entrada,
			delay: atrasoEmCascata(ordem),
			easing: quintOut,
			css: (t: number) => `opacity: ${t}; transform: translateY(${(1 - t) * 8}px)`
		};
	}

	/** Item que saiu do filtro: só esmaece, rápido, sem se deslocar. */
	function sair(_no: Element) {
		if (semMovimento()) return { duration: 0 };
		return { duration: PONTOS.saida, easing: quintOut, css: (t: number) => `opacity: ${t}` };
	}

	function nomesDosTipos(ponto: PontoDeColeta): string {
		return ponto.tipos_aceitos.map((tipo) => textos.nomesDosTipos[tipo]).join(', ');
	}
</script>

<ul aria-label={textos.rotuloDaLista}>
	{#each pontos as ponto, i (ponto.id)}
		{@const selecionado = ponto.id === selecionadoId}
		<li
			class:selecionado
			data-ponto-id={ponto.id}
			in:entrar={{ ordem: i }}
			out:sair
			animate:flip={{ duration: semMovimento() ? 0 : PONTOS.reorganizar, easing: quintOut }}
		>
			<button
				type="button"
				class="corpo"
				aria-pressed={selecionado}
				aria-label="{ponto.nome}. {textos.selecionar}"
				onclick={() => aoSelecionar(selecionado ? null : ponto.id)}
			>
				<span class="bolinha" aria-hidden="true"></span>
				<span class="texto">
					<span class="nome">{ponto.nome}</span>
					<span class="endereco">{enderecoEmUmaLinha(ponto)}</span>
					<span class="detalhes">
						<span class="status" class:aberto={ponto.aberto_agora === true}>
							{#if ponto.aberto_agora === null}
								{textos.horarioNaoInformado}
							{:else}
								{ponto.aberto_agora ? textos.abertoAgora : textos.fechadoAgora}
							{/if}
						</span>
						<span class="tipos">{nomesDosTipos(ponto)}</span>
					</span>
				</span>
				{#if ponto.distancia_km !== null}
					<!-- O primeiro da lista (mais perto) e o selecionado ganham o verde. -->
					<span class="distancia" class:destaque={i === 0 || selecionado}>
						{formatarDistancia(ponto.distancia_km)}
					</span>
				{/if}
			</button>
			<a
				class="rota"
				href={linkDeRota(ponto)}
				target="_blank"
				rel="noopener noreferrer"
				aria-label="{textos.comoChegarAte} {ponto.nome}"
			>
				{textos.comoChegar}
			</a>
		</li>
	{/each}
</ul>

<style>
	ul {
		list-style: none;
		padding: 0;
		font-family: var(--font-interface);
	}

	li {
		padding: 20px 4px 12px;
		border-bottom: 1px solid var(--line-soft);
	}

	li:last-child {
		/* O contêiner pai (.itens) já possui borda inferior; remove do último item para não duplicar traços. */
		border-bottom: 0;
	}

	.corpo {
		display: grid;
		grid-template-columns: 12px 1fr auto;
		gap: 0 14px;
		align-items: start;
		width: 100%;
		padding: 0;
		border: 0;
		background: none;
		text-align: left;
	}

	.corpo:focus-visible,
	.rota:focus-visible {
		outline: 2px solid var(--ink);
		outline-offset: 4px;
	}

	.bolinha {
		width: 12px;
		height: 12px;
		margin-top: 6px;
		border-radius: 50%;
		background: #a3afa7;
	}

	.selecionado .bolinha {
		background: var(--green);
	}

	.texto {
		display: grid;
		gap: 4px;
	}

	.nome {
		font-size: 1.0625rem;
		font-weight: 600;
		line-height: 1.3;
		color: var(--ink);
	}

	.endereco {
		font-size: 0.9375rem;
		line-height: 1.4;
		color: var(--muted);
	}

	.detalhes {
		display: flex;
		flex-wrap: wrap;
		gap: 2px 12px;
		font-size: 0.875rem;
		line-height: 1.4;
	}

	.status {
		color: var(--muted);
	}

	.status.aberto {
		color: var(--green-strong);
		font-weight: 600;
	}

	.tipos {
		color: var(--muted);
	}

	.distancia {
		font-size: 0.9375rem;
		font-weight: 600;
		color: var(--muted);
		white-space: nowrap;
	}

	.distancia.destaque {
		color: var(--green-strong);
	}

	.rota {
		display: inline-flex;
		align-items: center;
		min-height: 44px;
		margin-left: 26px; /* alinha com o texto: bolinha (12) + espaço (14) */
		font-size: 0.875rem;
		font-weight: 600;
		color: var(--green-strong);
		text-decoration: underline;
		text-underline-offset: 3px;
	}

	/* Desktop com mouse: itens mais baixos para caber mais pontos ao lado do mapa.
	   No toque, o "Como chegar" mantém os 44px de área (RNF01). */
	@media (min-width: 768px) {
		li {
			padding: 14px 4px 4px;
		}

		.nome {
			font-size: 1rem;
		}

		.endereco {
			font-size: 0.875rem;
		}

		.detalhes {
			font-size: 0.8125rem;
		}
	}

	@media (min-width: 768px) and (pointer: fine) {
		.rota {
			min-height: 32px;
		}
	}
</style>
