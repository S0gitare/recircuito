/**
 * Ponto único de entrada do GSAP no site.
 *
 * Os plugins só precisam ser registrados uma vez; centralizar aqui evita
 * registrar de novo em cada componente e garante que todo mundo use a mesma
 * instância do `gsap`. Importe sempre daqui: `import { gsap } from '$lib/animacao/gsap'`.
 */
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { DrawSVGPlugin } from 'gsap/DrawSVGPlugin';

// No build (SSR) não existe `window`; os plugins dependem do navegador.
if (typeof window !== 'undefined') {
	gsap.registerPlugin(ScrollTrigger, DrawSVGPlugin);
}

export { gsap, ScrollTrigger, DrawSVGPlugin };
