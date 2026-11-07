/**
 * Combinação entre a abertura do site (Abertura.svelte) e a cascata de entrada
 * do Hero (CelularExplodido.svelte).
 *
 * A cascata do Hero não pode começar enquanto a cortina da abertura ainda
 * cobre a tela, senão a pessoa perde a animação. Esta promessa é o "sinal
 * verde": a abertura chama `liberarHero()` quando a cortina começa a subir
 * (ou na hora, quando não há abertura), e o Hero espera por `aguardarAbertura()`.
 */

let resolver: () => void = () => {};
let liberado = false;

const promessa = new Promise<void>((resolve) => {
	resolver = resolve;
});

/** Resolve quando o Hero já pode começar a sua animação de entrada. */
export function aguardarAbertura(): Promise<void> {
	return promessa;
}

/** Dá o sinal verde para o Hero. Chamar mais de uma vez não tem efeito. */
export function liberarHero(): void {
	if (liberado) return;
	liberado = true;
	resolver();
}
