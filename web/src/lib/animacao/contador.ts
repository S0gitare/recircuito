/**
 * Action Svelte: escreve o número formatado em pt-BR e, ao entrar na tela,
 * conta de 0 até o valor em 1,2s (uma vez).
 * Uso: `<span use:contarAte={{ valor: 1240 }}></span>`.
 */
import { gsap, ScrollTrigger } from './gsap';
import { prefereMovimentoReduzido } from './movimentoReduzido';

export interface OpcoesDeContador {
	valor: number;
}

const formatador = new Intl.NumberFormat('pt-BR');

export function contarAte(no: HTMLElement, opcoes: OpcoesDeContador) {
	// Já escreve o valor final: serve de reserva para movimento reduzido e leitores de tela.
	no.textContent = formatador.format(opcoes.valor);
	if (prefereMovimentoReduzido()) return;

	// Objeto auxiliar: o GSAP anima a propriedade e a gente reescreve o texto a cada quadro.
	const contagem = { atual: 0 };
	no.textContent = formatador.format(0);

	const animacao = gsap.to(contagem, {
		atual: opcoes.valor,
		duration: 1.2,
		ease: 'power1.out',
		paused: true,
		onUpdate: () => {
			no.textContent = formatador.format(Math.round(contagem.atual));
		}
	});

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
