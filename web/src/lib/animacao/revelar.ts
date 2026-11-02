/**
 * Action Svelte: o elemento sobe 16px enquanto aparece, uma vez, ao entrar na tela.
 * Uso: `<h2 use:revelar>` ou `<p use:revelar={{ atraso: 0.1 }}>`.
 */
import { gsap, ScrollTrigger } from './gsap';
import { prefereMovimentoReduzido } from './movimentoReduzido';

export interface OpcoesDeRevelar {
	/** Atraso em segundos antes de começar. */
	atraso?: number;
}

export function revelar(no: HTMLElement, opcoes: OpcoesDeRevelar = {}) {
	// Movimento reduzido: o elemento fica como está, já visível.
	if (prefereMovimentoReduzido()) return;

	const animacao = gsap.fromTo(
		no,
		{ opacity: 0, y: 16 },
		{
			opacity: 1,
			y: 0,
			duration: 0.6,
			delay: opcoes.atraso ?? 0,
			ease: 'power2.out',
			// Limpa os estilos inline depois, para não interferir no CSS do componente.
			clearProps: 'opacity,transform',
			paused: true
		}
	);

	const gatilho = ScrollTrigger.create({
		trigger: no,
		start: 'top 90%',
		once: true,
		onEnter: () => animacao.play()
	});

	return {
		destroy() {
			gatilho.kill();
			animacao.kill();
		}
	};
}
