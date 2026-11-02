<script lang="ts">
	// A ordem importa: fontes e tokens primeiro, porque base.css usa as variáveis
	// e as famílias declaradas neles.
	import '$lib/estilos/fontes.css';
	import '$lib/estilos/tokens.css';
	import '$lib/estilos/base.css';
	import { onMount } from 'svelte';
	import { iniciarLenis } from '$lib/animacao/lenis';

	let { children } = $props();

	// A rolagem suave só existe no navegador. `iniciarLenis()` devolve a função
	// que a desliga; o onMount a usa como limpeza quando o layout é destruído.
	onMount(() => iniciarLenis());
</script>

{@render children()}
