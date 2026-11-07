<!--
  Casca comum dos modais de formulário do site (avaliação, sugestão de ponto).

  Cuida de tudo que não é o formulário em si:
  - <dialog> nativo (foco preso, Esc, leitor de tela) com abertura e
    fechamento animados (SPEC §7, "Modal de avaliação");
  - fechar pelo X, por Esc e por clique fora do cartão, mas nunca no meio de
    um envio (`bloqueado`);
  - a troca para a tela de sucesso: o formulário esmaece, entra a confirmação
    e o cartão encolhe suave até a nova altura (sem "pulo" nem cartão vazio);
  - os estilos dos controles usados dentro dos formulários (rótulos, chips,
    campos, botões), para os modais ficarem iguais entre si.

  Uso:
    <ModalBase bind:this={modal} bind:aberto titulo=… tituloSucesso=… …>
      <form>…</form>   ← ao enviar com sucesso, chame modal.mostrarSucesso()
    </ModalBase>
-->
<script lang="ts">
	import { onDestroy, tick, type Snippet } from 'svelte';
	import { prefereMovimentoReduzido } from '$lib/animacao/movimentoReduzido';
	import { CURVA_CSS, MODAL } from '$lib/animacao/movimento';
	import IconeFechar from './IconeFechar.svelte';

	interface Props {
		aberto?: boolean;
		/** id do <h2>, usado no aria-labelledby. Único por modal. */
		idTitulo: string;
		titulo: string;
		tituloSucesso: string;
		mensagemSucesso: string;
		/** Rótulo do X (lido por leitores de tela). */
		rotuloFechar: string;
		/** Texto do botão da tela de sucesso. */
		rotuloBotaoFechar: string;
		/** true durante um envio: impede fechar o modal no meio da requisição. */
		bloqueado?: boolean;
		/** true quando o envio demorou e o "Enviando…" está visível: os campos esmaecem. */
		esperando?: boolean;
		/** Chamado quando o modal termina de fechar depois de um envio com sucesso (limpar o formulário). */
		aoLimpar?: () => void;
		/** Chamado sempre que o modal termina de fechar (limpar mensagens de erro etc.). */
		aoFechar?: () => void;
		children: Snippet;
	}

	let {
		aberto = $bindable(false),
		idTitulo,
		titulo,
		tituloSucesso,
		mensagemSucesso,
		rotuloFechar,
		rotuloBotaoFechar,
		bloqueado = false,
		esperando = false,
		aoLimpar,
		aoFechar,
		children
	}: Props = $props();

	let elementoDialog: HTMLDialogElement | undefined = $state();
	let elementoCartao: HTMLDivElement | undefined = $state();
	let elementoBotaoFecharSucesso: HTMLButtonElement | undefined = $state();

	let sucesso = $state(false);
	let esmaecendo = $state(false);
	// `ativo` liga a transição de entrada; `fechando`, a de saída.
	let ativo = $state(false);
	let fechando = $state(false);
	let clicouForaNoPointerDown = false;
	let temporizadorFechamento: ReturnType<typeof setTimeout> | undefined;
	let temporizadorTroca: ReturnType<typeof setTimeout> | undefined;

	const travado = $derived(bloqueado || fechando || esmaecendo);

	$effect(() => {
		if (!elementoDialog) return;

		if (aberto) {
			// Reaberto durante o fechamento: cancela o fechamento.
			if (temporizadorFechamento) {
				clearTimeout(temporizadorFechamento);
				temporizadorFechamento = undefined;
			}
			fechando = false;

			if (!elementoDialog.open) {
				elementoDialog.showModal();
				elementoCartao?.focus({ preventScroll: true });
				ativo = false;

				if (prefereMovimentoReduzido()) {
					ativo = true;
				} else {
					// Dois quadros: o primeiro pinta o estado inicial, o segundo dispara a
					// transição. O setTimeout é a rede de segurança caso o navegador
					// segure os quadros (aba em segundo plano): o modal nunca fica invisível.
					const ligar = () => {
						if (aberto && !fechando) ativo = true;
					};
					requestAnimationFrame(() => requestAnimationFrame(ligar));
					setTimeout(ligar, 120);
				}
			} else {
				elementoCartao?.focus({ preventScroll: true });
				ativo = true;
			}
		} else if (elementoDialog.open && !fechando) {
			// Fechado de fora (bind:aberto = false): fecha com animação.
			fechar();
		}
	});

	$effect(() => {
		if (sucesso && elementoBotaoFecharSucesso) {
			elementoBotaoFecharSucesso.focus();
		}
	});

	onDestroy(() => {
		clearTimeout(temporizadorFechamento);
		clearTimeout(temporizadorTroca);
	});

	function limparAoFechar() {
		esmaecendo = false;
		if (sucesso) {
			sucesso = false;
			aoLimpar?.();
		}
		aoFechar?.();
	}

	export function fechar() {
		if (bloqueado || fechando) return;
		if (!elementoDialog || !elementoDialog.open) {
			aberto = false;
			return;
		}

		fechando = true;
		ativo = false;
		aberto = false;

		const finalizar = () => {
			if (elementoDialog?.open) elementoDialog.close();
			aberto = false;
			fechando = false;
			limparAoFechar();
		};

		if (prefereMovimentoReduzido()) {
			finalizar();
		} else {
			clearTimeout(temporizadorFechamento);
			temporizadorFechamento = setTimeout(finalizar, MODAL.saida);
		}
	}

	/**
	 * Troca o formulário pela tela de sucesso. Chame depois que o envio deu certo.
	 *
	 * O cartão é mais alto com o formulário do que com a confirmação. Guardamos
	 * a altura antes da troca e animamos até a nova; sem isso o cartão ficaria
	 * branco e vazio na altura antiga e depois "pularia" de uma vez.
	 */
	export function mostrarSucesso() {
		if (prefereMovimentoReduzido()) {
			sucesso = true;
			return;
		}

		const alturaAnterior = elementoCartao?.offsetHeight ?? 0;
		esmaecendo = true;
		clearTimeout(temporizadorTroca);
		temporizadorTroca = setTimeout(async () => {
			sucesso = true;
			esmaecendo = false;
			await tick();
			animarAltura(alturaAnterior);
		}, MODAL.trocaDeConteudo);
	}

	// Web Animations API: não deixa estilo inline para trás; ao terminar, o
	// cartão volta a ter altura automática.
	function animarAltura(alturaAnterior: number) {
		if (!elementoCartao || alturaAnterior === 0) return;
		const alturaNova = elementoCartao.offsetHeight;
		if (alturaNova === alturaAnterior) return;
		elementoCartao.animate(
			[{ height: `${alturaAnterior}px` }, { height: `${alturaNova}px` }],
			{ duration: MODAL.altura, easing: CURVA_CSS.saida }
		);
	}

	function aoFecharNativo() {
		// O navegador fechou o <dialog> por conta própria: sincroniza o estado.
		if (!fechando) {
			aberto = false;
			ativo = false;
			limparAoFechar();
		}
	}

	function foraDoCartao(evento: MouseEvent) {
		if (!elementoDialog) return false;
		const caixa = elementoDialog.getBoundingClientRect();
		const fora =
			evento.clientX < caixa.left ||
			evento.clientX > caixa.right ||
			evento.clientY < caixa.top ||
			evento.clientY > caixa.bottom;
		return evento.target === elementoDialog && fora;
	}

	// Fecha no clique fora só se o clique COMEÇOU fora: arrastar a seleção de
	// texto de dentro para fora do cartão não pode fechar o modal.
	function aoPressionarDialog(evento: MouseEvent) {
		if (travado) return;
		clicouForaNoPointerDown = foraDoCartao(evento);
	}

	function aoClicarNoDialog(evento: MouseEvent) {
		if (travado) return;
		if (clicouForaNoPointerDown && foraDoCartao(evento)) fechar();
		clicouForaNoPointerDown = false;
	}

	function aoCancelar(evento: Event) {
		// Esc: troca o fechamento seco do navegador pelo animado.
		evento.preventDefault();
		if (!travado) fechar();
	}
</script>

<dialog
	bind:this={elementoDialog}
	class="modal"
	class:ativo={ativo && !fechando}
	class:fechando
	aria-labelledby={idTitulo}
	aria-modal="true"
	onpointerdown={aoPressionarDialog}
	onclick={aoClicarNoDialog}
	oncancel={aoCancelar}
	onclose={aoFecharNativo}
>
	<div bind:this={elementoCartao} class="cartao" tabindex="-1">
		<header class="cabecalho">
			<h2 id={idTitulo} class:trocando={esmaecendo}>
				{sucesso ? tituloSucesso : titulo}
			</h2>
			<button
				type="button"
				class="botao-fechar"
				onclick={fechar}
				aria-label={rotuloFechar}
				disabled={travado}
			>
				<IconeFechar tamanho={20} />
			</button>
		</header>

		{#if sucesso}
			<div class="sucesso" role="status">
				<div class="sucesso-icone" aria-hidden="true">
					<!-- pathLength="1": o traço vai de 0 a 1, então o desenho é animado
					     só com stroke-dashoffset, sem medir o comprimento real. -->
					<svg
						width="44"
						height="44"
						viewBox="0 0 44 44"
						fill="none"
						stroke="var(--green-strong)"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
						focusable="false"
					>
						<circle class="aro" cx="22" cy="22" r="18" pathLength="1" transform="rotate(-90 22 22)" />
						<path class="visto" d="M14 22.5L19.5 28L30 16.5" pathLength="1" />
					</svg>
				</div>
				<p class="mensagem-sucesso">{mensagemSucesso}</p>
				<div class="acoes acoes-sucesso">
					<button
						bind:this={elementoBotaoFecharSucesso}
						type="button"
						class="botao-principal"
						onclick={fechar}
						disabled={fechando}
					>
						{rotuloBotaoFechar}
					</button>
				</div>
			</div>
		{:else}
			<div class="corpo" class:esmaecendo class:esperando>
				{@render children()}
			</div>
		{/if}
	</div>
</dialog>

<style>
	/* ── Diálogo, fundo e cartão ─────────────────────────────────────────── */

	dialog.modal {
		position: fixed;
		inset: 0;
		margin: auto;
		width: calc(100% - 32px);
		max-width: 540px;
		height: fit-content;
		max-height: calc(100dvh - 32px);
		padding: 0;
		border: none;
		outline: none;
		background: transparent;
		color: var(--ink);
		box-shadow: none;
		overflow: visible;
	}

	/* Fundo: escurece junto com a entrada do cartão e clareia mais rápido na saída. */
	dialog.modal::backdrop {
		background: rgba(15, 26, 20, 0.4);
		opacity: 0;
		transition: opacity var(--dur-entrada) var(--curva-saida);
	}

	dialog.modal.ativo::backdrop {
		opacity: 1;
	}

	dialog.modal.fechando::backdrop {
		opacity: 0;
		transition-duration: var(--dur-rapida);
	}

	dialog.modal.fechando {
		pointer-events: none;
	}

	.cartao {
		background: var(--bg);
		border: 1px solid var(--line);
		padding: 24px;
		display: flex;
		flex-direction: column;
		max-height: calc(100dvh - 32px);
		overflow-y: auto;
		box-sizing: border-box;
		box-shadow:
			0 20px 48px rgba(15, 26, 20, 0.16),
			0 4px 12px rgba(15, 26, 20, 0.08);
		/* Entrada: surge 8px abaixo e 3% menor, já transparente (nunca "pisca"
		   opaco antes de animar). Origem no centro: modal não nasce de um botão. */
		opacity: 0;
		transform: translateY(8px) scale(0.97);
		transition:
			opacity var(--dur-base) var(--curva-saida),
			transform var(--dur-entrada) var(--curva-saida);
		will-change: transform, opacity;
		scrollbar-width: thin;
		scrollbar-color: var(--line) transparent;
	}

	.cartao:focus {
		outline: none;
	}

	dialog.modal.ativo .cartao {
		opacity: 1;
		transform: none;
	}

	/* Saída: mais curta e com metade do movimento da entrada. */
	dialog.modal.fechando .cartao {
		opacity: 0;
		transform: translateY(4px) scale(0.98);
		transition-duration: var(--dur-rapida);
	}

	/* O conteúdo do formulário chega logo atrás do cartão, em cascata curta
	   (30ms entre blocos, no máximo ~200ms). Só na entrada: na saída tudo
	   sai junto com o cartão. */
	.corpo :global(form > *) {
		opacity: 0;
		transform: translateY(6px);
		transition:
			opacity var(--dur-base) var(--curva-saida),
			transform var(--dur-entrada) var(--curva-saida);
	}

	dialog.modal.ativo .corpo :global(form > *),
	dialog.modal.fechando .corpo :global(form > *) {
		opacity: 1;
		transform: none;
	}

	dialog.modal.fechando .corpo :global(form > *) {
		transition: none;
	}

	.corpo :global(form > :nth-child(1)) { transition-delay: 40ms; }
	.corpo :global(form > :nth-child(2)) { transition-delay: 70ms; }
	.corpo :global(form > :nth-child(3)) { transition-delay: 100ms; }
	.corpo :global(form > :nth-child(4)) { transition-delay: 130ms; }
	.corpo :global(form > :nth-child(5)) { transition-delay: 160ms; }
	.corpo :global(form > :nth-child(n + 6)) { transition-delay: 190ms; }

	/* ── Cabeçalho ───────────────────────────────────────────────────────── */

	.cabecalho {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 12px;
	}

	.cabecalho h2 {
		margin: 0;
		font-family: var(--font-leitura);
		font-size: 24px;
		font-weight: 500;
		line-height: 1.2;
		color: var(--ink);
		transition: opacity var(--dur-rapida) var(--curva-saida);
	}

	.cabecalho h2.trocando {
		opacity: 0;
	}

	.botao-fechar {
		flex-shrink: 0;
		width: 44px;
		height: 44px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: transparent;
		border: none;
		color: var(--muted);
		cursor: pointer;
		padding: 0;
		transition:
			color var(--dur-base) ease,
			background-color var(--dur-base) ease;
	}

	.botao-fechar:hover:not(:disabled) {
		color: var(--ink);
		background: var(--bg-alt);
	}

	.botao-fechar:focus-visible {
		outline: 2px solid var(--green-strong);
		outline-offset: 2px;
	}

	.botao-fechar:disabled {
		opacity: 0.4;
		cursor: not-allowed;
	}

	/* ── Troca formulário → sucesso ──────────────────────────────────────── */

	.corpo {
		transition:
			opacity var(--dur-rapida) var(--curva-saida),
			transform var(--dur-rapida) var(--curva-saida);
	}

	.corpo.esmaecendo {
		opacity: 0;
		transform: translateY(-4px) scale(0.99);
		pointer-events: none;
	}

	/* Tela de sucesso: o aro se desenha, o visto "assina" logo depois e o
	   texto sobe por último. É o momento de recompensa do fluxo, então pode
	   durar um pouco mais que o resto (~600ms no total). */
	.sucesso {
		animation: surgir-sucesso var(--dur-base) var(--curva-saida) both;
	}

	.mensagem-sucesso,
	.acoes-sucesso {
		animation: surgir-sucesso var(--dur-entrada) var(--curva-saida) 220ms both;
	}

	@keyframes surgir-sucesso {
		from {
			opacity: 0;
			transform: translateY(6px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.sucesso-icone {
		display: flex;
		margin: 16px 0 8px;
	}

	.sucesso-icone .aro,
	.sucesso-icone .visto {
		stroke-dasharray: 1;
		stroke-dashoffset: 1;
	}

	.sucesso-icone .aro {
		animation: desenhar 420ms var(--curva-saida) 60ms forwards;
	}

	.sucesso-icone .visto {
		animation: desenhar 260ms var(--curva-saida) 320ms forwards;
	}

	@keyframes desenhar {
		to {
			stroke-dashoffset: 0;
		}
	}

	.mensagem-sucesso {
		margin: 12px 0 24px;
		font-family: var(--font-interface);
		font-size: 15px;
		line-height: 1.5;
		color: var(--muted);
	}

	/* ── Controles dos formulários (classes usadas pelos modais filhos) ──── */

	.cartao :global(.apoio) {
		margin: 8px 0 20px;
		font-family: var(--font-interface);
		font-size: 14px;
		line-height: 1.4;
		color: var(--muted);
	}

	.cartao :global(fieldset.campo) {
		border: none;
		padding: 0;
		margin: 0 0 16px;
		min-width: 0;
	}

	.cartao :global(div.campo) {
		margin: 0 0 16px;
	}

	.cartao :global(.label) {
		display: block;
		margin-bottom: 8px;
		padding: 0;
		font-family: var(--font-interface);
		font-size: 14px;
		font-weight: 500;
		color: var(--ink);
	}

	.cartao :global(.opcional) {
		font-weight: 400;
		color: var(--muted);
	}

	.cartao :global(.chips) {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
	}

	.cartao :global(.chip) {
		min-height: 40px;
		padding: 0 16px;
		background: var(--bg);
		border: 1px solid var(--line);
		font-family: var(--font-interface);
		font-size: 14px;
		font-weight: 500;
		color: var(--ink);
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		transition:
			border-color var(--dur-base) ease,
			background-color var(--dur-base) ease,
			color var(--dur-base) ease,
			opacity var(--dur-base) ease,
			transform var(--dur-toque) var(--curva-saida);
	}

	/* Toque: o controle afunda 3% na hora do clique, antes de qualquer resposta. */
	.cartao :global(:is(.chip, .botao-principal, .botao-cancelar):active:not(:disabled)) {
		transform: scale(0.97);
	}

	.cartao :global(.chip:hover:not(.selecionado):not(:disabled)) {
		border-color: var(--ink);
	}

	.cartao :global(.chip.selecionado) {
		background: var(--green-strong);
		border-color: var(--green-strong);
		color: #fff;
		font-weight: 600;
	}

	.cartao :global(.chip:focus-visible) {
		outline: 2px solid var(--green-strong);
		outline-offset: 2px;
	}

	/* Durante o envio os controles ficam desativados, mas só esmaecem se a
	   espera for longa (`esperando`): numa resposta rápida nada pisca. */
	.cartao :global(.chip:disabled) {
		cursor: progress;
	}

	.corpo.esperando :global(:is(.chip, input.texto, textarea, .botao-cancelar):disabled) {
		opacity: 0.55;
	}

	.cartao :global(input.texto),
	.cartao :global(textarea) {
		width: 100%;
		border: 1px solid var(--line);
		padding: 12px;
		font-family: var(--font-interface);
		font-size: 14px;
		color: var(--ink);
		background: var(--bg);
		box-sizing: border-box;
	}

	.cartao :global(input.texto) {
		height: 44px;
	}

	.cartao :global(textarea) {
		resize: vertical;
	}

	.cartao :global(input.texto::placeholder),
	.cartao :global(textarea::placeholder) {
		color: #8e9e93;
	}

	.cartao :global(input.texto:focus-visible),
	.cartao :global(textarea:focus-visible) {
		outline: 2px solid var(--green-strong);
		outline-offset: 1px;
	}

	.cartao :global(input.texto),
	.cartao :global(textarea) {
		transition:
			border-color var(--dur-base) ease,
			opacity var(--dur-base) ease;
	}

	.cartao :global(input.texto[aria-invalid='true']) {
		border-color: #c5221f;
	}

	.cartao :global(input.texto:disabled),
	.cartao :global(textarea:disabled) {
		cursor: progress;
	}

	.cartao :global(.contador) {
		display: block;
		margin-top: 4px;
		font-size: 12px;
		color: var(--muted);
		text-align: right;
	}

	/* Erro é informação, não susto: entra suave, sem tremer nem piscar. */
	.cartao :global(.erro) {
		margin: 8px 0;
		font-size: 13px;
		color: #c5221f;
		animation: surgir-erro var(--dur-base) var(--curva-saida) both;
	}

	@keyframes surgir-erro {
		from {
			opacity: 0;
			transform: translateY(-4px);
		}
	}

	.acoes,
	.cartao :global(.acoes) {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 12px;
		margin-top: 20px;
	}

	.acoes-sucesso {
		justify-content: flex-end;
	}

	.cartao :global(.botao-cancelar) {
		height: 44px;
		padding: 0 16px;
		background: transparent;
		border: none;
		font-family: var(--font-interface);
		font-size: 15px;
		font-weight: 500;
		color: var(--muted);
		cursor: pointer;
		transition:
			color var(--dur-base) ease,
			transform var(--dur-toque) var(--curva-saida);
	}

	.cartao :global(.botao-cancelar:hover:not(:disabled)) {
		color: var(--ink);
	}

	.cartao :global(.botao-cancelar:disabled) {
		cursor: progress;
	}

	.botao-principal,
	.cartao :global(.botao-principal) {
		height: 44px;
		padding: 0 24px;
		background: var(--green-strong);
		border: none;
		font-family: var(--font-interface);
		font-size: 15px;
		font-weight: 600;
		color: #fff;
		cursor: pointer;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		gap: 8px;
		transition:
			opacity var(--dur-base) ease,
			transform var(--dur-toque) var(--curva-saida);
		white-space: nowrap;
	}

	.cartao :global(.botao-principal:focus-visible) {
		outline: 2px solid var(--ink);
		outline-offset: 2px;
	}

	/* Enviando: o botão continua cheio (não "apaga" no clique); só o cursor muda. */
	.cartao :global(.botao-principal:disabled) {
		cursor: progress;
	}

	/* O "Enviando…" entra com um leve crescimento, sem empurrar o botão. */
	.cartao :global(.botao-principal .spinner),
	.cartao :global(.botao-principal .rotulo-espera) {
		animation: surgir-espera var(--dur-base) var(--curva-saida) both;
	}

	@keyframes surgir-espera {
		from {
			opacity: 0;
			transform: scale(0.9);
		}
	}

	.cartao :global(.botao-enviar) {
		min-width: 180px;
	}

	/* Duas animações: a entrada (uma vez) e o giro contínuo (linear, sem fim). */
	.cartao :global(.botao-principal .spinner) {
		flex-shrink: 0;
		animation:
			surgir-espera var(--dur-base) var(--curva-saida) both,
			girar 0.8s linear infinite;
	}

	@keyframes girar {
		to {
			transform: rotate(360deg);
		}
	}

	/* ── Movimento reduzido (RNF02) ──────────────────────────────────────── */

	@media (prefers-reduced-motion: reduce) {
		/* Sem movimento: fica só a troca de opacidade, e o ícone já aparece pronto. */
		.cartao,
		.corpo,
		.corpo :global(form > *),
		.cartao :global(:is(.chip, .botao-principal, .botao-cancelar)) {
			transform: none !important;
			transition-delay: 0s !important;
		}

		.sucesso-icone .aro,
		.sucesso-icone .visto {
			stroke-dashoffset: 0;
			animation: none;
		}

		.cartao :global(.botao-principal .spinner) {
			animation: none;
		}
	}

	/* ── Celular ─────────────────────────────────────────────────────────── */

	@media (max-width: 480px) {
		.cartao {
			padding: 20px;
		}

		.cabecalho h2 {
			font-size: 22px;
		}

		.cartao :global(.apoio),
		.cartao :global(.label) {
			font-size: 13px;
		}

		.cartao :global(.chip) {
			min-height: 38px;
			padding: 0 14px;
			font-size: 13px;
		}

		.botao-principal,
		.cartao :global(.botao-principal),
		.cartao :global(.botao-cancelar) {
			font-size: 14px;
		}

		.cartao :global(.botao-enviar) {
			min-width: 170px;
		}
	}
</style>
