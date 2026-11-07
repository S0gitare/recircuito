<!--
  "Avaliar o site" (RF11): nota de 1 a 5, se encontrou o ponto e comentário.
  A abertura, o fechamento e a tela de sucesso vêm do ModalBase.
-->
<script lang="ts">
	import { modalAvaliacao as textos } from '$lib/conteudo/textos';
	import { enviarAvaliacao } from '$lib/api/pontos';
	import ModalBase from './ModalBase.svelte';
	import IconeCarregando from './IconeCarregando.svelte';
	import { aguardarComIndicador } from '$lib/animacao/espera';

	type Objetivo = 'sim' | 'parcialmente' | 'nao';

	let { aberto = $bindable(false) }: { aberto?: boolean } = $props();

	let modal: ModalBase | undefined = $state();
	let formulario: HTMLFormElement | undefined = $state();

	let nota: number | null = $state(null);
	let encontrouPonto: Objetivo | null = $state(null);
	let comentario = $state('');
	let enviando = $state(false);
	/** "Enviando…" visível: só quando o envio passa de ~300ms (ver espera.ts). */
	let esperando = $state(false);
	let erro: string | null = $state(null);

	const NOTAS = [1, 2, 3, 4, 5];

	function limpar() {
		esperando = false;
		nota = null;
		encontrouPonto = null;
		comentario = '';
	}

	// Setas movem a seleção dentro do grupo, como num grupo de rádios nativo.
	function proximoComSetas<T>(evento: KeyboardEvent, opcoes: readonly T[], atual: T): T | null {
		const i = opcoes.indexOf(atual);
		if (evento.key === 'ArrowRight' || evento.key === 'ArrowDown') {
			return opcoes[(i + 1) % opcoes.length];
		}
		if (evento.key === 'ArrowLeft' || evento.key === 'ArrowUp') {
			return opcoes[(i - 1 + opcoes.length) % opcoes.length];
		}
		return null;
	}

	function focar(seletor: string) {
		formulario?.querySelector<HTMLButtonElement>(seletor)?.focus();
	}

	function aoTeclarNota(evento: KeyboardEvent, atual: number) {
		const proxima = proximoComSetas(evento, NOTAS, atual);
		if (proxima === null) return;
		evento.preventDefault();
		nota = proxima;
		erro = null;
		focar(`[data-nota="${proxima}"]`);
	}

	function aoTeclarObjetivo(evento: KeyboardEvent, atual: Objetivo) {
		const valores = textos.opcoesObjetivo.map((o) => o.valor);
		const proximo = proximoComSetas(evento, valores, atual);
		if (proximo === null) return;
		evento.preventDefault();
		encontrouPonto = proximo;
		erro = null;
		focar(`[data-opcao="${proximo}"]`);
	}

	async function submeter(evento: SubmitEvent) {
		evento.preventDefault();
		if (enviando) return;

		if (!nota) {
			erro = textos.avisoSelecaoObrigatoria;
			focar('[data-nota="1"]');
			return;
		}
		if (!encontrouPonto) {
			erro = textos.avisoSelecaoObrigatoria;
			focar(`[data-opcao="${textos.opcoesObjetivo[0].valor}"]`);
			return;
		}

		erro = null;
		enviando = true;
		try {
			await aguardarComIndicador(
				enviarAvaliacao({
					nota,
					encontrou_ponto: encontrouPonto,
					comentario: comentario.trim() || null
				}),
				(visivel) => (esperando = visivel)
			);
			modal?.mostrarSucesso();
		} catch (e) {
			erro = e instanceof Error ? e.message : textos.erroEnvio;
		} finally {
			enviando = false;
		}
	}
</script>

<ModalBase
	bind:this={modal}
	bind:aberto
	idTitulo="modal-avaliacao-titulo"
	titulo={textos.titulo}
	tituloSucesso={textos.tituloSucesso}
	mensagemSucesso={textos.mensagemSucesso}
	rotuloFechar={textos.fechar}
	rotuloBotaoFechar={textos.botaoFechar}
	bloqueado={enviando}
	{esperando}
	aoLimpar={limpar}
	aoFechar={() => {
		erro = null;
		esperando = false;
	}}
>
	<form bind:this={formulario} onsubmit={submeter} novalidate>
		<p class="apoio">{textos.apoio}</p>

		<fieldset class="campo" disabled={enviando}>
			<legend class="label">{textos.perguntaNota}</legend>
			<div class="chips notas" role="radiogroup" aria-label={textos.perguntaNota}>
				{#each NOTAS as n (n)}
					<button
						type="button"
						class="chip"
						class:selecionado={nota === n}
						data-nota={n}
						role="radio"
						aria-checked={nota === n}
						tabindex={nota === n || (nota === null && n === 1) ? 0 : -1}
						onclick={() => {
							nota = n;
							erro = null;
						}}
						onkeydown={(e) => aoTeclarNota(e, n)}
					>
						{n}
					</button>
				{/each}
			</div>
		</fieldset>

		<fieldset class="campo" disabled={enviando}>
			<legend class="label">{textos.perguntaObjetivo}</legend>
			<div class="chips" role="radiogroup" aria-label={textos.perguntaObjetivo}>
				{#each textos.opcoesObjetivo as opcao, i (opcao.valor)}
					<button
						type="button"
						class="chip"
						class:selecionado={encontrouPonto === opcao.valor}
						data-opcao={opcao.valor}
						role="radio"
						aria-checked={encontrouPonto === opcao.valor}
						tabindex={encontrouPonto === opcao.valor || (encontrouPonto === null && i === 0)
							? 0
							: -1}
						onclick={() => {
							encontrouPonto = opcao.valor;
							erro = null;
						}}
						onkeydown={(e) => aoTeclarObjetivo(e, opcao.valor)}
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
			<button type="button" class="botao-cancelar" onclick={() => modal?.fechar()} disabled={enviando}>
				{textos.botaoCancelar}
			</button>
			<button type="submit" class="botao-principal botao-enviar" disabled={enviando}>
				{#if esperando}
					<IconeCarregando />
					<span class="rotulo-espera">{textos.enviando}</span>
				{:else}
					<span>{textos.botaoEnviar}</span>
				{/if}
			</button>
		</div>
	</form>
</ModalBase>

<style>
	/* As 5 notas dividem a largura por igual. */
	.notas .chip {
		flex: 1;
		padding: 0;
		font-size: 15px;
	}
</style>
