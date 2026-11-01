// Gera o HTML de todas as páginas no build (exigência do adapter-static).
// Se alguma rota futura precisar de dados só disponíveis no navegador,
// carregue-os no onMount do componente, nunca num load() de servidor.
export const prerender = true;
