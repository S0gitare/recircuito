<script lang="ts">
	import { pontosDeColeta as textos } from '$lib/conteudo/textos';
	import IconeLupa from './IconeLupa.svelte';
	import IconeMira from './IconeMira.svelte';

	interface Props {
		/** Texto digitado. `bind:valor` deixa o componente pai limpar o campo. */
		valor?: string;
		/** Mensagem de erro da busca (CEP não encontrado, localização negada...). */
		mensagem?: string | null;
		/** Enquanto a busca ou a localização estão em andamento. */
		ocupado?: boolean;
		aoBuscar: (texto: string) => void;
		aoUsarLocalizacao: () => void;
	}

	let { valor = $bindable(''), mensagem = null, ocupado = false, aoBuscar, aoUsarLocalizacao }: Props = $props();

	/** O Enter no campo e o clique na lupa disparam o mesmo `submit` do formulário. */
	function enviar(evento: SubmitEvent) {
		evento.preventDefault();
		aoBuscar(valor);
	}
</script>

<div class="busca">
	<form role="search" onsubmit={enviar}>
		<label class="so-leitor" for="campo-busca">{textos.campoBusca}</label>
		<input
			id="campo-busca"
			type="search"
			name="q"
			placeholder={textos.campoBusca}
			autocomplete="postal-code"
			enterkeyhint="search"
			bind:value={valor}
			aria-describedby={mensagem ? 'mensagem-busca' : undefined}
		/>
		<button type="submit" class="lupa" aria-label={textos.botaoBuscar} disabled={ocupado}>
			<IconeLupa />
		</button>
	</form>

	<button type="button" class="localizacao" onclick={aoUsarLocalizacao} disabled={ocupado}>
		<IconeMira />
		{textos.usarLocalizacao}
	</button>

	{#if mensagem}
		<p id="mensagem-busca" class="mensagem" role="alert">{mensagem}</p>
	{/if}
</div>

<style>
	.busca {
		display: grid;
		justify-items: start;
		gap: 12px;
	}

	form {
		position: relative;
		width: 100%;
	}

	/* Escondido da tela, mas lido por leitores de tela: o placeholder some ao digitar e não serve de rótulo. */
	.so-leitor {
		position: absolute;
		width: 1px;
		height: 1px;
		overflow: hidden;
		clip-path: inset(50%);
		white-space: nowrap;
	}

	input {
		width: 100%;
		height: 56px;
		padding: 0 60px 0 16px;
		border: 1px solid var(--line);
		border-radius: 0;
		background: var(--bg);
		font-size: 1rem;
		color: var(--ink);
		appearance: none;
	}

	input::placeholder {
		color: var(--muted);
		opacity: 1;
	}

	/* Remove o "x" nativo do type=search no Chrome/Safari para manter o visual reto do protótipo. */
	input::-webkit-search-cancel-button {
		appearance: none;
	}

	input:focus-visible,
	button:focus-visible {
		outline: 2px solid var(--ink);
		outline-offset: 2px;
	}

	.lupa {
		position: absolute;
		top: 0;
		right: 0;
		width: 56px;
		height: 56px;
		display: grid;
		place-items: center;
		border: 0;
		background: transparent;
		color: var(--ink);
	}

	.lupa:disabled,
	.localizacao:disabled {
		opacity: 0.5;
		cursor: progress;
	}

	.localizacao {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		min-height: 44px; /* área de toque mínima (RNF01) */
		padding: 0;
		border: 0;
		background: none;
		font-size: 0.875rem;
		font-weight: 600;
		/* --green-strong: o --green sobre branco dá só 3,5:1, abaixo do AA para texto pequeno. */
		color: var(--green-strong);
	}

	.mensagem {
		font-family: var(--font-interface);
		font-size: 0.9375rem;
		line-height: 1.4;
		color: var(--ink-2);
		padding-left: 12px;
		border-left: 2px solid var(--green);
	}

	/* Desktop: campo um pouco mais baixo para a seção caber na tela ao lado do mapa. */
	@media (min-width: 768px) {
		input {
			height: 48px;
			padding-right: 52px;
		}

		.lupa {
			width: 48px;
			height: 48px;
		}
	}
</style>
