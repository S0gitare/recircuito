<script lang="ts">
	import { modalAvaliacao as textos } from '$lib/conteudo/textos';
	import { enviarAvaliacao } from '$lib/api/pontos';

	interface Props {
		aberto?: boolean;
	}

	let { aberto = $bindable(false) }: Props = $props();

	let elementoDialog: HTMLDialogElement | undefined = $state();
	let elementoBotaoFecharSucesso: HTMLButtonElement | undefined = $state();

	let nota: number | null = $state(null);
	let encontrouPonto: 'sim' | 'parcialmente' | 'nao' | null = $state(null);
	let comentario: string = $state('');

	let enviando: boolean = $state(false);
	let sucesso: boolean = $state(false);
	let erro: string | null = $state(null);
	let clicouForaNoPointerDown: boolean = false;

	$effect(() => {
		if (!elementoDialog) return;
		if (aberto) {
			if (!elementoDialog.open) {
				elementoDialog.showModal();
			}
		} else {
			if (elementoDialog.open) {
				elementoDialog.close();
			}
		}
	});

	$effect(() => {
		if (sucesso && elementoBotaoFecharSucesso) {
			elementoBotaoFecharSucesso.focus();
		}
	});

	function fechar() {
		if (enviando) return;
		aberto = false;
		erro = null;
		if (sucesso) {
			nota = null;
			encontrouPonto = null;
			comentario = '';
			sucesso = false;
		}
	}

	function aoPressionarDialog(evento: MouseEvent) {
		if (enviando || !elementoDialog) return;
		const rect = elementoDialog.getBoundingClientRect();
		const foraDosLimites =
			evento.clientX < rect.left ||
			evento.clientX > rect.right ||
			evento.clientY < rect.top ||
			evento.clientY > rect.bottom;
		clicouForaNoPointerDown = evento.target === elementoDialog && foraDosLimites;
	}

	function aoClicarNoDialog(evento: MouseEvent) {
		if (enviando || !elementoDialog) return;
		const rect = elementoDialog.getBoundingClientRect();
		const foraDosLimites =
			evento.clientX < rect.left ||
			evento.clientX > rect.right ||
			evento.clientY < rect.top ||
			evento.clientY > rect.bottom;

		if (clicouForaNoPointerDown && evento.target === elementoDialog && foraDosLimites) {
			fechar();
		}
		clicouForaNoPointerDown = false;
	}

	function aoCancelar(evento: Event) {
		evento.preventDefault();
		if (!enviando) {
			fechar();
		}
	}

	function aoTeclarNota(evento: KeyboardEvent, atual: number) {
		let proxima = atual;
		if (evento.key === 'ArrowRight' || evento.key === 'ArrowDown') {
			proxima = atual < 5 ? atual + 1 : 1;
		} else if (evento.key === 'ArrowLeft' || evento.key === 'ArrowUp') {
			proxima = atual > 1 ? atual - 1 : 5;
		} else {
			return;
		}
		evento.preventDefault();
		nota = proxima;
		erro = null;
		const botao = elementoDialog?.querySelector<HTMLButtonElement>(
			`button[data-nota="${proxima}"]`
		);
		botao?.focus();
	}

	function aoTeclarObjetivo(evento: KeyboardEvent, indiceAtual: number) {
		const opcoes = textos.opcoesObjetivo;
		let proximoIndice = indiceAtual;
		if (evento.key === 'ArrowRight' || evento.key === 'ArrowDown') {
			proximoIndice = (indiceAtual + 1) % opcoes.length;
		} else if (evento.key === 'ArrowLeft' || evento.key === 'ArrowUp') {
			proximoIndice = (indiceAtual - 1 + opcoes.length) % opcoes.length;
		} else {
			return;
		}
		evento.preventDefault();
		encontrouPonto = opcoes[proximoIndice].valor;
		erro = null;
		const botao = elementoDialog?.querySelector<HTMLButtonElement>(
			`button[data-opcao="${opcoes[proximoIndice].valor}"]`
		);
		botao?.focus();
	}

	async function submeter(evento: SubmitEvent) {
		evento.preventDefault();
		if (!nota) {
			erro = textos.avisoSelecaoObrigatoria;
			const primeiroBotaoNota = elementoDialog?.querySelector<HTMLButtonElement>('button[data-nota="1"]');
			primeiroBotaoNota?.focus();
			return;
		}

		if (!encontrouPonto) {
			erro = textos.avisoSelecaoObrigatoria;
			const primeiroBotaoObjetivo = elementoDialog?.querySelector<HTMLButtonElement>(
				`button[data-opcao="${textos.opcoesObjetivo[0].valor}"]`
			);
			primeiroBotaoObjetivo?.focus();
			return;
		}

		erro = null;
		enviando = true;

		try {
			await enviarAvaliacao({
				nota,
				encontrou_ponto: encontrouPonto,
				comentario: comentario.trim() || null
			});
			sucesso = true;
		} catch (e) {
			erro = e instanceof Error ? e.message : textos.erroEnvio;
		} finally {
			enviando = false;
		}
	}
</script>

<dialog
	bind:this={elementoDialog}
	class="modal-avaliacao"
	aria-labelledby="modal-avaliacao-titulo"
	aria-modal="true"
	onpointerdown={aoPressionarDialog}
	onclick={aoClicarNoDialog}
	oncancel={aoCancelar}
>
	<div class="cartao">
		<header class="cabecalho">
			<h2 id="modal-avaliacao-titulo">{sucesso ? textos.tituloSucesso : textos.titulo}</h2>
			<button
				type="button"
				class="botao-fechar"
				onclick={fechar}
				aria-label={textos.fechar}
				disabled={enviando}
			>
				×
			</button>
		</header>

		{#if sucesso}
			<div class="sucesso" role="status">
				<p class="mensagem-sucesso">{textos.mensagemSucesso}</p>
				<div class="acoes sucesso-acoes">
					<button
						bind:this={elementoBotaoFecharSucesso}
						type="button"
						class="botao-principal"
						onclick={fechar}
					>
						{textos.botaoFechar}
					</button>
				</div>
			</div>
		{:else}
			<form onsubmit={submeter}>
				<p class="apoio">{textos.apoio}</p>

				<fieldset class="campo" disabled={enviando}>
					<legend class="label">{textos.perguntaNota}</legend>
					<div class="chips-notas" role="radiogroup" aria-label={textos.perguntaNota}>
						{#each [1, 2, 3, 4, 5] as n}
							<button
								type="button"
								class="chip-nota"
								class:selecionado={nota === n}
								data-nota={n}
								onclick={() => {
									nota = n;
									erro = null;
								}}
								onkeydown={(e) => aoTeclarNota(e, n)}
								role="radio"
								aria-checked={nota === n}
								tabindex={nota === n ? 0 : nota === null && n === 1 ? 0 : -1}
							>
								{n}
							</button>
						{/each}
					</div>
				</fieldset>

				<fieldset class="campo" disabled={enviando}>
					<legend class="label">{textos.perguntaObjetivo}</legend>
					<div class="chips-opcoes" role="radiogroup" aria-label={textos.perguntaObjetivo}>
						{#each textos.opcoesObjetivo as opcao, i}
							<button
								type="button"
								class="chip-opcao"
								class:selecionado={encontrouPonto === opcao.valor}
								data-opcao={opcao.valor}
								onclick={() => {
									encontrouPonto = opcao.valor;
									erro = null;
								}}
								onkeydown={(e) => aoTeclarObjetivo(e, i)}
								role="radio"
								aria-checked={encontrouPonto === opcao.valor}
								tabindex={encontrouPonto === opcao.valor ? 0 : encontrouPonto === null && i === 0 ? 0 : -1}
							>
								{opcao.rotulo}
							</button>
						{/each}
					</div>
				</fieldset>

				<div class="campo">
					<label class="label" for="avaliacao-comentario">{textos.perguntaComentario}</label>
					<textarea
						id="avaliacao-comentario"
						bind:value={comentario}
						maxlength="1000"
						rows="3"
						placeholder={textos.placeholderComentario}
						disabled={enviando}
					></textarea>
					<span class="contador">{comentario.length}/1000</span>
				</div>

				{#if erro}
					<p class="erro" role="alert">{erro}</p>
				{/if}

				<div class="acoes">
					<button type="button" class="botao-cancelar" onclick={fechar} disabled={enviando}>
						{textos.botaoCancelar}
					</button>
					<button
						type="submit"
						class="botao-principal"
						disabled={enviando}
					>
						{enviando ? textos.enviando : textos.botaoEnviar}
					</button>
				</div>
			</form>
		{/if}
	</div>
</dialog>

<style>
	dialog.modal-avaliacao {
		position: fixed;
		inset: 0;
		margin: auto;
		width: calc(100% - 32px);
		max-width: 540px;
		padding: 0;
		border: 1px solid var(--line);
		border-radius: 0;
		background: var(--bg);
		color: var(--ink);
		box-shadow: none;
	}

	dialog.modal-avaliacao::backdrop {
		background: rgba(15, 26, 20, 0.4);
	}

	.cartao {
		padding: 24px;
		display: flex;
		flex-direction: column;
	}

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
	}

	.botao-fechar {
		width: 44px;
		height: 44px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: transparent;
		border: none;
		border-radius: 0;
		font-family: var(--font-interface);
		font-size: 24px;
		line-height: 1;
		color: var(--muted);
		cursor: pointer;
		padding: 0;
	}

	.botao-fechar:hover {
		color: var(--ink);
	}

	.apoio {
		margin: 8px 0 20px;
		font-family: var(--font-interface);
		font-size: 14px;
		line-height: 1.4;
		color: var(--muted);
	}

	fieldset.campo {
		border: none;
		padding: 0;
		margin: 0 0 16px;
	}

	div.campo {
		margin: 0 0 16px;
	}

	.label {
		display: block;
		margin-bottom: 8px;
		font-family: var(--font-interface);
		font-size: 14px;
		font-weight: 500;
		color: var(--ink);
	}

	.chips-notas {
		display: flex;
		gap: 8px;
	}

	.chip-nota {
		flex: 1;
		height: 40px;
		background: var(--bg);
		border: 1px solid var(--line);
		border-radius: 0;
		font-family: var(--font-interface);
		font-size: 15px;
		font-weight: 500;
		color: var(--ink);
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: border-color 0.15s, background-color 0.15s, color 0.15s;
	}

	.chip-nota:hover:not(.selecionado) {
		border-color: var(--ink);
	}

	.chip-nota.selecionado {
		background: var(--green-strong);
		border-color: var(--green-strong);
		color: #ffffff;
		font-weight: 600;
	}

	.chips-opcoes {
		display: flex;
		gap: 8px;
		flex-wrap: wrap;
	}

	.chip-opcao {
		height: 38px;
		padding: 0 16px;
		background: var(--bg);
		border: 1px solid var(--line);
		border-radius: 0;
		font-family: var(--font-interface);
		font-size: 14px;
		font-weight: 500;
		color: var(--ink);
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: border-color 0.15s, background-color 0.15s, color 0.15s;
	}

	.chip-opcao:hover:not(.selecionado) {
		border-color: var(--ink);
	}

	.chip-opcao.selecionado {
		background: var(--green-strong);
		border-color: var(--green-strong);
		color: #ffffff;
		font-weight: 600;
	}

	textarea {
		width: 100%;
		border: 1px solid var(--line);
		border-radius: 0;
		padding: 12px;
		font-family: var(--font-interface);
		font-size: 14px;
		color: var(--ink);
		background: var(--bg);
		box-sizing: border-box;
		resize: vertical;
	}

	textarea::placeholder {
		color: #8e9e93;
	}

	textarea:focus-visible {
		outline: 2px solid var(--green-strong);
		outline-offset: 1px;
	}

	.contador {
		display: block;
		margin-top: 4px;
		font-size: 12px;
		color: var(--muted);
		text-align: right;
	}

	.erro {
		margin: 8px 0;
		font-size: 13px;
		color: #c5221f;
	}

	.acoes {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 12px;
		margin-top: 20px;
	}

	.sucesso-acoes {
		justify-content: flex-end;
	}

	.mensagem-sucesso {
		margin: 16px 0 24px;
		font-family: var(--font-interface);
		font-size: 15px;
		line-height: 1.5;
		color: var(--muted);
	}

	.botao-cancelar {
		height: 44px;
		padding: 0 16px;
		background: transparent;
		border: none;
		border-radius: 0;
		font-family: var(--font-interface);
		font-size: 15px;
		font-weight: 500;
		color: var(--muted);
		cursor: pointer;
	}

	.botao-cancelar:hover:not(:disabled) {
		color: var(--ink);
	}

	.botao-principal {
		height: 44px;
		padding: 0 24px;
		background: var(--green-strong);
		border: none;
		border-radius: 0;
		font-family: var(--font-interface);
		font-size: 15px;
		font-weight: 600;
		color: #ffffff;
		cursor: pointer;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		transition: opacity 0.15s;
	}

	.botao-principal:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	@media (max-width: 480px) {
		.cartao {
			padding: 20px;
		}

		.cabecalho h2 {
			font-size: 22px;
		}

		.apoio {
			font-size: 13px;
		}

		.label {
			font-size: 13px;
		}

		.chip-nota {
			height: 38px;
			font-size: 14px;
		}

		.chip-opcao {
			height: 36px;
			font-size: 13px;
			padding: 0 14px;
		}

		.botao-cancelar,
		.botao-principal {
			font-size: 14px;
		}

		.botao-principal {
			padding: 0 20px;
		}
	}
</style>
