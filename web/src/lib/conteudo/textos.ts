/**
 * Todos os textos visíveis do site, num lugar só.
 *
 * Por que centralizar: corrigir uma frase vira editar uma linha aqui, sem
 * procurar o texto dentro dos componentes. Também facilita revisar a escrita
 * do site inteiro antes de publicar.
 *
 * Origem: protótipo "ReCircuito - Prototipo.figcraft" (frames Home — Desktop,
 * Home — Mobile, Menu aberto — Mobile e Banner de cookies). Se mudar um texto
 * aqui, mude também no protótipo, para os dois continuarem iguais.
 *
 * Dica: o `as const` no fim de cada objeto faz o TypeScript tratar os textos
 * como valores fixos. Assim o editor avisa se algum componente pedir uma chave
 * que não existe (por exemplo, `textos.hero.titlo` com erro de digitação).
 */

/** Links de navegação. O `ancora` é o `id` da seção que o link rola até. */
export const navegacao = [
	{ rotulo: 'O projeto', ancora: 'sobre' },
	{ rotulo: 'Como descartar', ancora: 'como-descartar' },
	{ rotulo: 'O que descartar', ancora: 'o-que-descartar' },
	{ rotulo: 'Pontos de coleta', ancora: 'pontos-de-coleta' }
] as const;

export const cabecalho = {
	nomeDoSite: 'ReCircuito',
	// Rótulos lidos por leitores de tela nos botões de ícone (☰ e X).
	abrirMenu: 'Abrir menu',
	fecharMenu: 'Fechar menu'
} as const;

export const hero = {
	titulo: 'Seu lixo eletrônico tem destino.',
	texto: 'Saiba o que fazer com celulares, pilhas e cabos velhos, e onde entregar cada um.',
	botao: 'Ver pontos de coleta',
	// Anotações da vista explodida do celular, de cima para baixo.
	// No mobile elas ficam ocultas (falta espaço), então o `descricaoDoDesenho`
	// abaixo repete a ideia para leitores de tela.
	camadas: [
		{ nome: 'Vidro', destino: 'Separado na triagem' },
		{ nome: 'Tela', destino: 'Tem metais que não vão pro lixo comum' },
		{ nome: 'Bateria', destino: 'Risco de incêndio: coleta especial' },
		{ nome: 'Placa', destino: 'Ouro, prata e cobre recuperáveis' },
		{ nome: 'Carcaça', destino: 'Plástico e alumínio recicláveis' }
	],
	descricaoDoDesenho:
		'Celular desmontado em cinco camadas, cada uma com o destino do seu material: vidro, tela, bateria, placa e carcaça.'
} as const;

export const sobre = {
	frase:
		'Celulares, pilhas e cabos esquecidos na gaveta viram risco quando vão para o lixo comum. A gente mostra o caminho certo.',
	texto:
		'Uma iniciativa de extensão universitária que leva informação a escolas, bairros e comércios, e mapeia onde cada resíduo pode ser entregue.'
} as const;

export const comoDescartar = {
	titulo: 'Quatro passos até o descarte certo',
	texto:
		'Descartar certo é simples quando você sabe a ordem. Siga os passos e leve tudo para um ponto de coleta.',
	passos: [
		{ numero: '01', nome: 'Separe', descricao: 'Junte aparelhos, pilhas e cabos que você não usa mais.' },
		{
			numero: '02',
			nome: 'Apague os dados',
			descricao: 'Faça backup e restaure celulares e computadores para o padrão de fábrica.'
		},
		{ numero: '03', nome: 'Ache um ponto', descricao: 'Use o mapa abaixo para achar o ecoponto mais perto de você.' },
		{
			numero: '04',
			nome: 'Entregue',
			descricao: 'Leve tudo junto. Pilhas e baterias vão em um saquinho separado.'
		}
	]
} as const;

/**
 * Os `tipo` batem com o enum `TipoResiduo` da API (api/aplicacao/modelos.py).
 * Cuidado: se renomear um tipo lá, renomeie aqui também, senão o filtro para
 * de encontrar os pontos.
 */
export const oQueDescartar = {
	titulo: 'Nem tudo vai no mesmo lugar',
	texto:
		'Cada tipo de resíduo tem um destino. Pilhas, por exemplo, nunca devem ir junto com o lixo orgânico ou reciclável comum.',
	itens: [
		{ tipo: 'celulares_tablets', nome: 'Celulares e tablets', descricao: 'Inclusive quebrados ou sem bateria.' },
		{ tipo: 'pilhas_baterias', nome: 'Pilhas e baterias', descricao: 'Separe em saquinho e isole os polos.' },
		{
			tipo: 'computadores_perifericos',
			nome: 'Computadores e periféricos',
			descricao: 'Notebooks, teclados, mouses e monitores.'
		},
		{ tipo: 'cabos_carregadores', nome: 'Cabos e carregadores', descricao: 'Fios, fontes, fones e adaptadores.' }
	]
} as const;

export const pontosDeColeta = {
	titulo: 'Onde descartar perto de você',
	campoBusca: 'Digite seu CEP ou bairro',
	usarLocalizacao: 'Usar minha localização',
	// Ordem do filtro definida no protótipo: as palavras curtas ficam na linha
	// de cima (3 botões) e as longas na de baixo (2 botões mais largos).
	filtro: [
		{ tipo: null, rotulo: 'Todos' },
		{ tipo: 'cabos_carregadores', rotulo: 'Cabos' },
		{ tipo: 'pilhas_baterias', rotulo: 'Pilhas' },
		{ tipo: 'computadores_perifericos', rotulo: 'Computadores' },
		{ tipo: 'celulares_tablets', rotulo: 'Celulares' }
	],
	abertoAgora: 'Aberto agora',
	fechadoAgora: 'Fechado agora',
	comoChegar: 'Como chegar',
	sugerirPergunta: 'Conhece um ponto que não está aqui?',
	sugerirLink: 'Sugerir um ponto',
	// Mensagens de estado (RF12): nunca deixar a pessoa diante de uma lista vazia sem explicação.
	carregando: 'Buscando pontos de coleta…',
	semResultados: 'Nenhum ponto encontrado com esses filtros. Tente marcar outros tipos de resíduo.',
	naoEncontrado: 'Não encontramos esse CEP ou bairro em Belém. Confira e tente de novo.',
	erroDeRede: 'Não foi possível carregar os pontos agora. Verifique sua conexão e tente de novo.',
	localizacaoNegada:
		'Sem permissão para usar sua localização. Você ainda pode buscar pelo CEP ou pelo bairro.'
} as const;

/** Os `valor` são FICTÍCIOS: trocar pelos dados reais antes de publicar (SPEC §14). */
export const impacto = {
	titulo: 'O que já tiramos do lixo comum',
	numeros: [
		{ valor: 1240, unidade: 'kg', rotulo: 'de eletrônicos coletados' },
		{ valor: 18, unidade: '', rotulo: 'escolas visitadas' },
		{ valor: 32, unidade: '', rotulo: 'pontos de coleta mapeados' },
		{ valor: 4500, unidade: '', rotulo: 'pessoas alcançadas' }
	]
} as const;

export const rodape = {
	frase: 'Descarte certo de lixo eletrônico.',
	tituloNavegacao: 'Navegação',
	tituloContato: 'Contato',
	// Contatos ainda provisórios (SPEC §14).
	email: 'contato@recircuito.org',
	redeSocial: '@recircuito',
	instituicao: '[Nome da instituição]',
	avaliarSite: 'Avaliar o site',
	creditos: 'Projeto de Extensão II · 2026'
} as const;

export const bannerCookies = {
	// Rótulo da região para leitores de tela (RF10).
	rotuloDaRegiao: 'Aviso de cookies',
	titulo: 'Sua privacidade importa',
	texto:
		'Usamos cookies para entender como o site é usado e melhorar a sua experiência. Ao clicar em “Aceitar”, você concorda com o uso de cookies.',
	recusar: 'Recusar',
	aceitar: 'Aceitar'
} as const;
