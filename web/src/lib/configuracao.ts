/**
 * Configuração do site, lida de variáveis de ambiente do Vite.
 *
 * Só variáveis com o prefixo VITE_ chegam ao navegador (o Vite bloqueia as
 * outras de propósito, para você não vazar um segredo sem querer). Aqui NÃO há
 * segredos: tudo o que está neste arquivo vai para o código público do site.
 *
 * Em desenvolvimento, copie .env.example para .env e ajuste.
 */

const ler = (valor: string | undefined, padrao = ''): string => (valor ?? padrao).trim();

/** Endereço da API (FastAPI). Sem barra no final. */
export const urlDaApi = ler(import.meta.env.VITE_URL_DA_API, 'http://localhost:8010').replace(/\/$/, '');

/** Google Forms "Sugerir um ponto" (RF08). Vazio enquanto o formulário não existe (SPEC §14). */
export const urlFormularioSugestao = ler(import.meta.env.VITE_URL_FORMULARIO_SUGESTAO);

/** Google Forms "Avaliar o site" (RF11). Vazio enquanto o formulário não existe (SPEC §14). */
export const urlFormularioAvaliacao = ler(import.meta.env.VITE_URL_FORMULARIO_AVALIACAO);

/** ID do Google Analytics 4 (ex.: G-XXXXXXXXXX). Vazio = o Analytics nunca é carregado. */
export const idGoogleAnalytics = ler(import.meta.env.VITE_ID_GOOGLE_ANALYTICS);
