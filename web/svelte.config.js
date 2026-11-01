import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/**
 * O site é publicado no GitHub Pages, que só serve arquivos estáticos.
 * Por isso usamos o adapter-static: no build, cada rota vira um arquivo HTML
 * pronto (prerender), sem servidor Node rodando em produção.
 *
 * Dica: se o site for publicado num subcaminho (ex.: usuario.github.io/recircuito),
 * defina a variável BASE_PATH=/recircuito no build. Sem isso, os links para
 * /favicon.svg, /fontes e /logos quebram.
 *
 * @type {import('@sveltejs/kit').Config}
 */
const config = {
	preprocess: vitePreprocess(),
	kit: {
		adapter: adapter({
			pages: 'build',
			assets: 'build',
			// Página de erro servida pelo GitHub Pages quando a URL não existe.
			fallback: '404.html',
			precompress: false,
			strict: true
		}),
		paths: {
			base: process.env.BASE_PATH ?? ''
		}
	}
};

export default config;
