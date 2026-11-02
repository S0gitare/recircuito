<script lang="ts">
	import { pontosDeColeta as textos } from '$lib/conteudo/textos';
	import type { PontoDeColeta } from '$lib/api/pontos';

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

	function nomesDosTipos(ponto: PontoDeColeta): string {
		return ponto.tipos_aceitos.map((tipo) => textos.nomesDosTipos[tipo]).join(', ');
	}
</script>

<ul aria-label={textos.rotuloDaLista}>
	{#each pontos as ponto, i (ponto.id)}
		{@const selecionado = ponto.id === selecionadoId}
		<li class:selecionado>
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
						<span class="status" class:aberto={ponto.aberto_agora}>
							{ponto.aberto_agora ? textos.abertoAgora : textos.fechadoAgora}
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
</style>
