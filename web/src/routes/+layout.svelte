<script lang="ts">
	// A ordem importa: fontes e tokens primeiro, porque base.css usa as variáveis
	// e as famílias declaradas neles.
	import '$lib/estilos/fontes.css';
	import '$lib/estilos/tokens.css';
	import '$lib/estilos/base.css';

	let { children } = $props();
</script>

{@render children()}
