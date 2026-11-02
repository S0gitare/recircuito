<script lang="ts">
	// Três traços de 2px (☰). Decorativo: quem dá o nome é o aria-label do botão.
	let { tamanho = 24 }: { tamanho?: number } = $props();
</script>

<svg width={tamanho} height={tamanho} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true" focusable="false">
	<path d="M3 6H21M3 12H21M3 18H21" />
</svg>
