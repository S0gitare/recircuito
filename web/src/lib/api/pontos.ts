/**
 * Cliente da API de pontos de coleta (SPEC §9 e §10).
 *
 * Todas as funções aceitam um `AbortSignal`: quando a pessoa digita outra busca
 * ou muda o filtro, o componente cancela a requisição anterior para uma
 * resposta lenta e antiga nunca sobrescrever a nova.
 *
 * Erros viram `ErroDaApi`, sempre com uma mensagem pronta para mostrar à pessoa
 * (em português, vinda de `textos.pontosDeColeta`). Quando a requisição é
 * cancelada, o erro tem `tipo === 'cancelado'` e o componente deve ignorá-lo.
 */
import { urlDaApi } from '$lib/configuracao';
import { pontosDeColeta as textos } from '$lib/conteudo/textos';

export type TipoResiduo =
	| 'celulares_tablets'
	| 'pilhas_baterias'
	| 'computadores_perifericos'
	| 'cabos_carregadores';

export type TipoLocal =
	| 'ecoponto'
	| 'varejo'
	| 'operadora'
	| 'fabricante'
	| 'cooperativa'
	| 'orgao_publico';

export interface FaixaDeHorario {
	/** 0 = domingo ... 6 = sábado (convenção do JavaScript). */
	dias: number[];
	abre: string;
	fecha: string;
}

export interface PontoDeColeta {
	id: string;
	nome: string;
	tipo_local: TipoLocal;
	endereco: { logradouro: string; numero: string | null; bairro: string; cep: string | null };
	coordenadas: { lat: number; lon: number };
	tipos_aceitos: TipoResiduo[];
	horarios: FaixaDeHorario[];
	contato: { telefone: string | null; site: string | null };
	fonte: string;
	verificado_em: string | null;
	observacoes: string | null;
	/** Só vem preenchido quando a busca informa `lat` e `lon`. */
	distancia_km: number | null;
	/** `null` = horário não informado (não é o mesmo que fechado). */
	aberto_agora: boolean | null;
}

export interface RespostaPontos {
	pontos: PontoDeColeta[];
	total: number;
}

export interface Localizacao {
	lat: number;
	lon: number;
	/** Texto curto para mostrar à pessoa, ex.: "Campina, Belém - PA". */
	rotulo: string;
	fonte: string;
}

export type TipoDeErro = 'rede' | 'nao_encontrado' | 'servidor' | 'cancelado';

export class ErroDaApi extends Error {
	readonly tipo: TipoDeErro;

	constructor(tipo: TipoDeErro, mensagem: string) {
		super(mensagem);
		this.name = 'ErroDaApi';
		this.tipo = tipo;
	}
}

/** Verdadeiro quando o erro é só o cancelamento que nós mesmos pedimos. */
export function foiCancelado(erro: unknown): boolean {
	return erro instanceof ErroDaApi && erro.tipo === 'cancelado';
}

/**
 * Faz o GET e devolve o JSON, convertendo qualquer falha em `ErroDaApi`.
 *
 * Dica: `fetch` só rejeita quando não consegue falar com o servidor (sem
 * internet, API fora do ar, CORS). Resposta 404 ou 500 é "sucesso" para o
 * fetch, por isso conferimos `resposta.ok` à mão.
 */
async function pedir<T>(caminho: string, parametros: URLSearchParams, sinal?: AbortSignal): Promise<T> {
	const consulta = parametros.toString();
	const url = `${urlDaApi}${caminho}${consulta ? `?${consulta}` : ''}`;

	let resposta: Response;
	try {
		resposta = await fetch(url, { signal: sinal, headers: { Accept: 'application/json' } });
	} catch (erro) {
		if (erro instanceof DOMException && erro.name === 'AbortError') {
			throw new ErroDaApi('cancelado', 'Requisição cancelada.');
		}
		throw new ErroDaApi('rede', textos.erroDeRede);
	}

	if (resposta.ok) {
		try {
			return (await resposta.json()) as T;
		} catch (erro) {
			// O corpo pode ser cortado se a requisição for cancelada no meio da leitura.
			if (sinal?.aborted) throw new ErroDaApi('cancelado', 'Requisição cancelada.');
			throw new ErroDaApi('servidor', textos.erroDeRede);
		}
	}

	if (resposta.status === 404) throw new ErroDaApi('nao_encontrado', textos.naoEncontrado);

	// A API explica seus erros em { erro, mensagem } (SPEC §10). Se o corpo não
	// vier nesse formato (ex.: página de erro da hospedagem), usamos a mensagem genérica.
	let mensagem: string = textos.erroDeRede;
	try {
		const corpo = (await resposta.json()) as { detail?: { mensagem?: string }; mensagem?: string };
		mensagem = corpo.detail?.mensagem ?? corpo.mensagem ?? mensagem;
	} catch {
		// mantém a mensagem genérica
	}
	throw new ErroDaApi('servidor', mensagem);
}

export interface ParametrosDaBusca {
	lat?: number;
	lon?: number;
	/** Vazio ou ausente = todos os tipos. */
	tipos?: TipoResiduo[];
	sinal?: AbortSignal;
}

/** GET /api/pontos. Com `lat`/`lon` a lista vem ordenada por distância; sem eles, em ordem alfabética. */
export function buscarPontos({ lat, lon, tipos, sinal }: ParametrosDaBusca = {}): Promise<RespostaPontos> {
	const parametros = new URLSearchParams();
	if (lat !== undefined && lon !== undefined) {
		parametros.set('lat', String(lat));
		parametros.set('lon', String(lon));
	}
	if (tipos && tipos.length > 0) parametros.set('tipos', tipos.join(','));
	return pedir<RespostaPontos>('/api/pontos', parametros, sinal);
}

/** GET /api/geocodificar?q=. Transforma CEP ou bairro de Belém em coordenada (RF01). */
export function geocodificar(texto: string, sinal?: AbortSignal): Promise<Localizacao> {
	return pedir<Localizacao>('/api/geocodificar', new URLSearchParams({ q: texto.trim() }), sinal);
}
