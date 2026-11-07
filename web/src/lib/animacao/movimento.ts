/**
 * Fonte única de curvas e durações das animações feitas com GSAP.
 *
 * Componentes não devem escrever `ease: 'power2.out'` ou `duration: 0.9`
 * soltos: importam daqui. Assim, se a "sensação" do site mudar, muda num
 * lugar só, e todas as animações continuam conversando entre si.
 *
 * Regras (curvas):
 * - `saida`: algo entrando ou saindo da tela, ou respondendo a um clique.
 *   Começa rápido e freia no fim, por isso parece responder na hora.
 * - `moverNaTela`: algo que já está na tela e muda de lugar (ex.: a cortina
 *   da abertura subindo). Acelera e freia, como um objeto físico.
 * - `desenhar`: traço sendo desenhado (DrawSVG). Suave nas duas pontas, para
 *   o traço "sair" e "chegar" sem tranco.
 * - Nunca usar curvas `.in` (acelerando até parar de repente) em interface.
 */
export const CURVA = {
	saida: 'power3.out',
	moverNaTela: 'power3.inOut',
	desenhar: 'power2.inOut'
} as const;

/**
 * Mesmas curvas em formato CSS, para animações feitas com a Web Animations API
 * (`elemento.animate`). Espelho dos tokens --curva-* de estilos/tokens.css.
 */
export const CURVA_CSS = {
	saida: 'cubic-bezier(0.23, 1, 0.32, 1)',
	mover: 'cubic-bezier(0.77, 0, 0.175, 1)'
} as const;

/** Durações dos modais, em milissegundos (espelho dos tokens --dur-*). */
export const MODAL = {
	/** Formulário esmaecendo antes da tela de sucesso. */
	trocaDeConteudo: 160,
	/** Fechamento: cartão e fundo saindo. */
	saida: 180,
	/** Cartão ajustando a altura entre formulário e sucesso. */
	altura: 280
} as const;

/**
 * Pontos de coleta entrando e saindo ao mudar o filtro ou a busca (ms).
 * Só se mexe o que mudou: pinos e itens que continuam ficam parados.
 */
export const PONTOS = {
	/** Pino ou item novo surgindo. */
	entrada: 240,
	/** Pino ou item que saiu do filtro sumindo (mais curto que a entrada). */
	saida: 160,
	/** "Ping" que marca no mapa onde um pino novo apareceu. */
	ping: 520,
	/** Atraso entre um pino/item novo e o próximo, em cascata. */
	intervalo: 25,
	/** Teto da cascata: com muitos pontos, o último não pode demorar a chegar. */
	intervaloMaximo: 175,
	/** Vizinhos deslizando para o lugar de quem saiu da lista. */
	reorganizar: 240
} as const;

/** Atraso em cascata do n-ésimo elemento novo, com teto. */
export function atrasoEmCascata(indice: number): number {
	return Math.min(indice * PONTOS.intervalo, PONTOS.intervaloMaximo);
}

/**
 * Espera de um envio (§4 do guia de movimento: "sem piscar").
 * - Respostas rápidas não mostram indicador nenhum: o botão afundando já respondeu.
 * - Se passar de `mostrarApos`, aparece "Enviando…"; uma vez visível, ele fica
 *   pelo menos `manterPor`, para não piscar na tela.
 */
export const ESPERA = {
	mostrarApos: 300,
	manterPor: 500
} as const;

/**
 * Tempos da abertura do site (em segundos). É uma animação rara (uma vez por
 * carregamento), então pode ser mais demorada que um botão: mesmo assim o
 * total fica em ~2,6s para não parecer que o site está "travado".
 */
export const ABERTURA = {
	/** Ponto verde (a "fonte" do sinal) surgindo. */
	ponto: 0.4,
	/** Trilha do circuito se desenhando do ponto verde até o furo. */
	trilha: 0.95,
	/** Furo no topo da trilha acendendo quando o sinal chega. */
	furo: 0.35,
	/** Letras surgindo ao redor do símbolo e o logo se centralizando. */
	letras: 0.7,
	/** Intervalo entre uma letra e a próxima. */
	intervaloLetras: 0.035,
	/** Pausa com o logo completo antes de abrir a cortina. */
	pausa: 0.35,
	/** Logo some antes da cortina subir. */
	logoSaindo: 0.4,
	/** Cortina subindo e revelando o site. */
	cortina: 0.9,
	/** Quanto tempo depois do início da cortina a cascata do Hero começa. */
	atrasoDoHero: 0.3,
	/** Multiplicador de velocidade quando a pessoa clica ou tecla para pular. */
	acelerarAoPular: 4
} as const;
