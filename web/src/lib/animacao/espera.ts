/**
 * Indicador de espera que não pisca (guia de movimento §4).
 *
 * Um "Enviando…" que aparece e some em 80ms parece defeito, não velocidade.
 * Por isso:
 * - se a tarefa termina antes de ESPERA.mostrarApos, o indicador nunca aparece
 *   (o botão afundando no clique já foi a resposta);
 * - se aparece, fica pelo menos ESPERA.manterPor na tela, mesmo que a tarefa
 *   termine logo depois.
 */
import { ESPERA } from './movimento';

/**
 * Espera `tarefa` e liga o indicador pelo `mostrar`. Devolve o resultado da
 * tarefa (ou repassa o erro dela) só depois do tempo mínimo do indicador.
 *
 * Em caso de erro, o indicador é desligado aqui. Em caso de sucesso ele fica
 * ligado: quem chamou vai trocar a tela (ex.: para a confirmação), e desligar
 * antes faria o botão voltar a "Enviar" por um instante. Desligue ao limpar.
 */
export async function aguardarComIndicador<T>(
	tarefa: Promise<T>,
	mostrar: (visivel: boolean) => void
): Promise<T> {
	let visivelDesde: number | null = null;
	const temporizador = setTimeout(() => {
		visivelDesde = performance.now();
		mostrar(true);
	}, ESPERA.mostrarApos);

	const segurarIndicador = async () => {
		clearTimeout(temporizador);
		if (visivelDesde === null) return;
		const falta = ESPERA.manterPor - (performance.now() - visivelDesde);
		if (falta > 0) await new Promise((resolver) => setTimeout(resolver, falta));
	};

	try {
		const resultado = await tarefa;
		await segurarIndicador();
		return resultado;
	} catch (erro) {
		await segurarIndicador();
		mostrar(false);
		throw erro;
	}
}
