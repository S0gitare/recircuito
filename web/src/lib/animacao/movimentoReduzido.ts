/**
 * Detecta se a pessoa pediu menos animação no sistema (RNF02).
 *
 * Todo código de animação do site deve perguntar isto antes de se mexer: quem
 * tem sensibilidade a movimento (vertigem, enxaqueca) configura o computador
 * ou o celular para reduzir animações, e o site precisa respeitar.
 */

const CONSULTA = '(prefers-reduced-motion: reduce)';

/** true se a pessoa prefere movimento reduzido. No servidor (build), assume false. */
export function prefereMovimentoReduzido(): boolean {
	if (typeof window === 'undefined' || !window.matchMedia) return false;
	return window.matchMedia(CONSULTA).matches;
}
