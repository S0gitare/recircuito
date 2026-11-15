/**
 * Consentimento de cookies e carregamento do Google Analytics (RF10).
 *
 * Regra de ouro: NADA do Google é carregado antes de a pessoa aceitar.
 * Por isso o script do gtag nunca aparece no HTML: ele é injetado aqui, só
 * depois do consentimento e só se houver um ID configurado.
 */
import { idGoogleAnalytics } from '$lib/configuracao';

export type Consentimento = 'aceito' | 'recusado';

/** Chave do localStorage onde a escolha fica guardada. */
const CHAVE = 'recircuito:cookies';

/**
 * Lê a escolha salva. Devolve `null` na primeira visita ou quando o
 * navegador bloqueia o armazenamento (modo privado, cookies desligados):
 * nesse caso o `localStorage` pode até lançar erro só de ser acessado, por
 * isso o try/catch.
 */
export function lerConsentimento(): Consentimento | null {
	try {
		const valor = localStorage.getItem(CHAVE);
		return valor === 'aceito' || valor === 'recusado' ? valor : null;
	} catch {
		return null;
	}
}

/** Salva a escolha. Se o armazenamento estiver bloqueado, só vale até recarregar. */
export function guardarConsentimento(valor: Consentimento): void {
	try {
		localStorage.setItem(CHAVE, valor);
	} catch {
		// Sem armazenamento: o banner volta na próxima visita, o que é aceitável.
	}
}

/**
 * Esquece a escolha (página de privacidade, "Rever minha escolha"): o banner
 * volta a aparecer na próxima vez que a página inicial abrir. Se o Analytics
 * já tinha sido carregado nesta visita, ele só deixa de carregar a partir da
 * próxima página aberta.
 */
export function apagarConsentimento(): void {
	try {
		localStorage.removeItem(CHAVE);
	} catch {
		// Sem armazenamento: não havia escolha guardada.
	}
}

let jaCarregado = false;

type ParametrosEvento = Record<string, string | number | boolean>;

function dispararGtag(..._argumentos: unknown[]): void {
	const janela = window as unknown as { dataLayer?: unknown[] };
	janela.dataLayer = janela.dataLayer ?? [];
	// O gtag.js exige o objeto `arguments` (e não um array) dentro do dataLayer.
	// eslint-disable-next-line prefer-rest-params
	janela.dataLayer.push(arguments);
}

/**
 * Injeta o gtag.js do Google Analytics 4. Só faz algo se a pessoa aceitou os
 * cookies E existe um ID configurado; chamar duas vezes não duplica o script.
 */
export function carregarGoogleAnalytics(): void {
	if (jaCarregado || !idGoogleAnalytics || lerConsentimento() !== 'aceito') return;
	jaCarregado = true;

	dispararGtag('js', new Date());
	dispararGtag('config', idGoogleAnalytics);

	const script = document.createElement('script');
	script.async = true;
	script.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(idGoogleAnalytics)}`;
	document.head.appendChild(script);
}

/**
 * Registra um evento agregado no GA4 (sem dados pessoais, RNF06).
 * Só envia quando o Analytics já foi carregado após consentimento explícito.
 */
export function registrarEvento(nome: string, parametros?: ParametrosEvento): void {
	if (typeof window === 'undefined' || !jaCarregado || !idGoogleAnalytics || lerConsentimento() !== 'aceito') {
		return;
	}
	if (parametros) {
		dispararGtag('event', nome, parametros);
	} else {
		dispararGtag('event', nome);
	}
}
