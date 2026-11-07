<!--
  "Sugerir um ponto" (RF08): a pessoa indica um local que recebe lixo
  eletrônico e não está no mapa. A sugestão vai para a API (POST /api/sugestoes)
  e só aparece no mapa depois de a equipe conferir.

  Não pede contato (e-mail, telefone): seria dado pessoal (RNF06).
  A abertura, o fechamento e a tela de sucesso vêm do ModalBase.
-->
<script lang="ts">
	import { modalSugestao as textos, pontosDeColeta } from '$lib/conteudo/textos';
	import { enviarSugestao, type TipoResiduo } from '$lib/api/pontos';
	import ModalBase from './ModalBase.svelte';
	import IconeCarregando from './IconeCarregando.svelte';
	import { aguardarComIndicador } from '$lib/animacao/espera';

	let { aberto = $bindable(false) }: { aberto?: boolean } = $props();

	// Mesmos limites da API (NovaSugestao em api/aplicacao/modelos.py).
	const LIMITE_NOME = 120;
	const LIMITE_ENDERECO = 200;
	const LIMITE_OBSERVACAO = 500;

	const TIPOS = Object.entries(pontosDeColeta.nomesDosTipos) as [TipoResiduo, string][];

	let modal: ModalBase | undefined = $state();
	let campoNome: HTMLInputElement | undefined = $state();
	let campoEndereco: HTMLInputElement | undefined = $state();
	let grupoTipos: HTMLDivElement | undefined = $state();

	let nome = $state('');
	let endereco = $state('');
	let tipos = $state<TipoResiduo[]>([]);
	let observacao = $state('');
	let enviando = $state(false);
	/** "Enviando…" visível: só quando o envio passa de ~300ms (ver espera.ts). */
	let esperando = $state(false);
	let erro: string | null = $state(null);
	/** Campo que causou o último erro de validação (para marcar com aria-invalid). */
	let campoComErro: 'nome' | 'endereco' | 'tipos' | null = $state(null);

	function limpar() {
		esperando = false;
		nome = '';
		endereco = '';
		tipos = [];
		observacao = '';
	}

	function alternarTipo(tipo: TipoResiduo) {
		tipos = tipos.includes(tipo) ? tipos.filter((t) => t !== tipo) : [...tipos, tipo];
		if (campoComErro === 'tipos') {
			erro = null;
			campoComErro = null;
		}
	}

	function limparErroDe(campo: 'nome' | 'endereco') {
		if (campoComErro === campo) {
			erro = null;
			campoComErro = null;
		}
	}

	/** Devolve a primeira falha encontrada, na ordem em que os campos aparecem. */
	function validar(): boolean {
		if (nome.trim().length < 2) {
			[erro, campoComErro] = [textos.avisoNome, 'nome'];
			campoNome?.focus();
			return false;
		}
		if (endereco.trim().length < 3) {
			[erro, campoComErro] = [textos.avisoEndereco, 'endereco'];
			campoEndereco?.focus();
			return false;
		}
		if (tipos.length === 0) {
			[erro, campoComErro] = [textos.avisoTipos, 'tipos'];
			grupoTipos?.querySelector('button')?.focus();
			return false;
		}
		[erro, campoComErro] = [null, null];
		return true;
	}

	async function submeter(evento: SubmitEvent) {
		evento.preventDefault();
		if (enviando || !validar()) return;

		enviando = true;
		try {
			await aguardarComIndicador(
				enviarSugestao({
					nome: nome.trim(),
					endereco: endereco.trim(),
					tipos,
					observacao: observacao.trim() || null
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
	idTitulo="modal-sugestao-titulo"
	titulo={textos.titulo}
	tituloSucesso={textos.tituloSucesso}
	mensagemSucesso={textos.mensagemSucesso}
	rotuloFechar={textos.fechar}
	rotuloBotaoFechar={textos.botaoFechar}
	bloqueado={enviando}
	{esperando}
	aoLimpar={limpar}
	aoFechar={() => {
		[erro, campoComErro] = [null, null];
		esperando = false;
	}}
>
	<form onsubmit={submeter} novalidate>
		<p class="apoio">{textos.apoio}</p>

		<div class="campo">
			<label class="label" for="sugestao-nome">{textos.rotuloNome}</label>
			<input
				bind:this={campoNome}
				bind:value={nome}
				oninput={() => limparErroDe('nome')}
				id="sugestao-nome"
				class="texto"
				type="text"
				autocomplete="organization"
				maxlength={LIMITE_NOME}
				placeholder={textos.placeholderNome}
				aria-invalid={campoComErro === 'nome'}
				aria-describedby={campoComErro === 'nome' ? 'sugestao-erro' : undefined}
				disabled={enviando}
			/>
		</div>

		<div class="campo">
			<label class="label" for="sugestao-endereco">{textos.rotuloEndereco}</label>
			<input
				bind:this={campoEndereco}
				bind:value={endereco}
				oninput={() => limparErroDe('endereco')}
				id="sugestao-endereco"
				class="texto"
				type="text"
				autocomplete="off"
				maxlength={LIMITE_ENDERECO}
				placeholder={textos.placeholderEndereco}
				aria-invalid={campoComErro === 'endereco'}
				aria-describedby={campoComErro === 'endereco' ? 'sugestao-erro' : undefined}
				disabled={enviando}
			/>
		</div>

		<fieldset class="campo" disabled={enviando}>
			<legend class="label">
				{textos.perguntaTipos} <span class="opcional">{textos.dicaTipos}</span>
			</legend>
			<!-- Caixas de seleção (pode marcar vários): aria-pressed, não rádio. -->
			<div class="chips tipos" bind:this={grupoTipos}>
				{#each TIPOS as [codigo, rotulo] (codigo)}
					<button
						type="button"
						class="chip"
						class:selecionado={tipos.includes(codigo)}
						aria-pressed={tipos.includes(codigo)}
						onclick={() => alternarTipo(codigo)}
					>
						{rotulo}
					</button>
				{/each}
			</div>
		</fieldset>

		<div class="campo">
			<label class="label" for="sugestao-observacao">
				{textos.rotuloObservacao} <span class="opcional">{textos.opcional}</span>
			</label>
			<textarea
				id="sugestao-observacao"
				bind:value={observacao}
				maxlength={LIMITE_OBSERVACAO}
				rows="3"
				placeholder={textos.placeholderObservacao}
				disabled={enviando}
			></textarea>
			<span class="contador">{observacao.length}/{LIMITE_OBSERVACAO}</span>
		</div>

		{#if erro}
			<p class="erro" id="sugestao-erro" role="alert">{erro}</p>
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
	/* 2×2: os quatro tipos com a mesma largura, como o filtro do mapa. */
	/* `.chips.tipos` (duas classes) para vencer o `display: flex` do ModalBase. */
	.chips.tipos {
		display: grid;
		grid-template-columns: 1fr 1fr;
	}

	.tipos .chip {
		padding: 8px 12px;
		text-align: center;
		line-height: 1.25;
	}
</style>
