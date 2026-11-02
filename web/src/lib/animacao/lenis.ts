/**
 * Rolagem suave com Lenis, sincronizada com o GSAP.
 *
 * O ScrollTrigger lê a posição da página; o Lenis "empurra" a rolagem com
 * inércia. Para os dois não brigarem, o Lenis avisa o ScrollTrigger a cada
 * passo (`lenis.on('scroll', ScrollTrigger.update)`) e é o ticker do GSAP quem
 * dá o compasso (em vez de um `requestAnimationFrame` próprio).
 */
import Lenis from 'lenis';
import { gsap, ScrollTrigger } from './gsap';
import { prefereMovimentoReduzido } from './movimentoReduzido';

let lenis: Lenis | null = null;

/** Liga a rolagem suave. Devolve a função que desliga (use no onMount/onDestroy). */
export function iniciarLenis(): () => void {
	// Movimento reduzido: rolagem nativa, sem inércia.
	if (prefereMovimentoReduzido() || lenis) return () => {};

	const instancia = new Lenis();
	lenis = instancia;

	instancia.on('scroll', ScrollTrigger.update);

	// O ticker entrega o tempo em segundos; o Lenis espera milissegundos.
	const aCadaQuadro = (tempo: number) => instancia.raf(tempo * 1000);
	gsap.ticker.add(aCadaQuadro);
	// Sem isto o GSAP "compensa" quadros perdidos e a rolagem dá soluços.
	gsap.ticker.lagSmoothing(0);

	return () => {
		gsap.ticker.remove(aCadaQuadro);
		gsap.ticker.lagSmoothing(500, 33); // volta ao padrão do GSAP
		instancia.destroy();
		if (lenis === instancia) lenis = null;
	};
}

/** Rola até uma âncora (ex.: '#sobre'). Com Lenis ligado, rola suave. */
export function rolarPara(alvo: string): void {
	if (lenis) {
		lenis.scrollTo(alvo, { duration: 1.2 });
		return;
	}
	const elemento = document.querySelector(alvo);
	elemento?.scrollIntoView({ behavior: prefereMovimentoReduzido() ? 'auto' : 'smooth' });
}
