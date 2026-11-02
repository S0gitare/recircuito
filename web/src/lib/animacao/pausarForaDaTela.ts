/**
 * Ajuda as ilustrações em loop a gastarem CPU só quando aparecem na tela.
 *
 * `IntersectionObserver` avisa quando o elemento entra ou sai da janela:
 * entrou, a animação toca; saiu, pausa (e retoma do mesmo ponto).
 */
import { prefereMovimentoReduzido } from './movimentoReduzido';

/** Mínimo que precisamos de uma timeline/tween do GSAP. */
interface Tocavel {
	play(): unknown;
	pause(): unknown;
}

/**
 * Toca `animacao` enquanto `no` estiver visível. Devolve a função que desliga o observador.
 * Com movimento reduzido nunca toca (quem chama deve mostrar o estado final estático).
 */
export function tocarSoQuandoVisivel(no: Element, animacao: Tocavel): () => void {
	animacao.pause();
	if (prefereMovimentoReduzido()) return () => {};

	const observador = new IntersectionObserver(
		(entradas) => {
			for (const entrada of entradas) {
				if (entrada.isIntersecting) animacao.play();
				else animacao.pause();
			}
		},
		{ threshold: 0.15 }
	);
	observador.observe(no);
	return () => observador.disconnect();
}
