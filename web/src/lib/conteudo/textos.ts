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
	fecharMenu: 'Fechar menu',
	// Nomes dos menus para leitores de tela: cada <nav> precisa de um nome próprio.
	menuPrincipal: 'Menu principal'
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
		'Desenvolvido por Alecsander Lima como uma iniciativa de extensão universitária da Uninter que leva informação a escolas, bairros e comércios, e mapeia onde cada resíduo pode ser entregue.'
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
	horarioNaoInformado: 'Horário não informado',
	comoChegar: 'Como chegar',
	sugerirPergunta: 'Conhece um ponto que não está aqui?',
	sugerirLink: 'Sugerir um ponto',
	// Mensagens de estado (RF12): nunca deixar a pessoa diante de uma lista vazia sem explicação.
	carregando: 'Buscando pontos de coleta…',
	semResultados: 'Nenhum ponto encontrado com esses filtros. Tente marcar outros tipos de resíduo.',
	naoEncontrado: 'Não encontramos esse CEP ou bairro em Belém. Confira e tente de novo.',
	buscaCurta: 'Digite pelo menos 2 letras do bairro ou o CEP completo.',
	erroDeRede: 'Não foi possível carregar os pontos agora. Verifique sua conexão e tente de novo.',
	localizacaoNegada:
		'Sem permissão para usar sua localização. Você ainda pode buscar pelo CEP ou pelo bairro.',
	// Textos de apoio (leitores de tela, estados e avisos).
	botaoBuscar: 'Buscar',
	rotuloDoFiltro: 'Filtrar por tipo de resíduo',
	rotuloDaLista: 'Pontos de coleta',
	rotuloDoMapa: 'Mapa dos pontos de coleta',
	primeiraBuscaDemora: 'A primeira busca pode demorar um pouco. Já estamos buscando.',
	tentarDeNovo: 'Tentar de novo',
	localizacaoIndisponivel: 'Não foi possível descobrir sua localização agora. Tente buscar pelo CEP ou pelo bairro.',
	localizando: 'Descobrindo sua localização…',
	referenciaAtual: 'Distâncias a partir de',
	suaLocalizacao: 'sua localização',
	// Etiqueta do marcador da posição no mapa (quando a posição veio do aparelho).
	voceEstaAqui: 'Você está aqui',
	// Leitor de tela: "Ponto de partida: Nazaré".
	pontoDePartida: 'Ponto de partida',
	limparReferencia: 'Limpar busca',
	// Rótulo lido por leitores de tela no "Como chegar" de cada ponto: "Como chegar até <nome>".
	comoChegarAte: 'Como chegar até',
	selecionar: 'Selecionar no mapa',
	// Nomes de exibição dos tipos aceitos (mesmos códigos da API).
	nomesDosTipos: {
		celulares_tablets: 'Celulares e tablets',
		pilhas_baterias: 'Pilhas e baterias',
		computadores_perifericos: 'Computadores e periféricos',
		cabos_carregadores: 'Cabos e carregadores'
	}
} as const;

/** Números reais verificados da base atual (api/dados/pontos.json). */
export const impacto = {
	titulo: 'O que já mapeamos em Belém',
	numeros: [
		{ valor: 140, unidade: '', rotulo: 'pontos de coleta mapeados' },
		{ valor: 32, unidade: '', rotulo: 'bairros de Belém cobertos' },
		{ valor: 119, unidade: '', rotulo: 'pontos confirmados em fontes oficiais' },
		{ valor: 4, unidade: '', rotulo: 'grupos de resíduos aceitos' }
	]
} as const;

export const rodape = {
	frase: 'Descarte certo de lixo eletrônico.',
	tituloNavegacao: 'Navegação',
	menuDoRodape: 'Menu do rodapé',
	privacidade: 'Privacidade',
	tituloContato: 'Contato',
	email: 'alecsander.hslima@gmail.com',
	telefone: '(91) 98805-4024',
	telefoneRaw: '+5591988054024',
	linkedinTexto: 'LinkedIn',
	linkedinUrl: 'https://www.linkedin.com/in/alec-undefined-231a31428/',
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
	aceitar: 'Aceitar',
	saibaMais: 'Saiba mais sobre privacidade'
} as const;

export const modalAvaliacao = {
	rotuloDialogo: 'Avaliação do site',
	titulo: 'Avaliar o ReCircuito',
	fechar: 'Fechar modal',
	apoio: 'Sua opinião ajuda a melhorar o guia de descarte para Belém.',
	perguntaNota: 'Como você avalia a sua experiência?',
	perguntaObjetivo: 'Conseguiu encontrar o ponto de coleta que precisava?',
	opcoesObjetivo: [
		{ valor: 'sim', rotulo: 'Sim' },
		{ valor: 'parcialmente', rotulo: 'Parcialmente' },
		{ valor: 'nao', rotulo: 'Não' }
	],
	perguntaComentario: 'Sugestões, dúvidas ou críticas (opcional)',
	placeholderComentario: 'Deixe aqui seu comentário...',
	botaoCancelar: 'Cancelar',
	botaoEnviar: 'Enviar avaliação',
	enviando: 'Enviando...',
	tituloSucesso: 'Obrigado pela sua avaliação!',
	mensagemSucesso:
		'Sua contribuição ajuda a construir uma Belém mais sustentável e aprimorar o ReCircuito.',
	botaoFechar: 'Fechar',
	erroEnvio: 'Não foi possível enviar a avaliação agora. Verifique sua conexão e tente de novo.',
	avisoSelecaoObrigatoria: 'Selecione uma nota e se encontrou o ponto antes de enviar.'
} as const;


export const modalSugestao = {
	titulo: 'Sugerir um ponto de coleta',
	fechar: 'Fechar',
	apoio:
		'Conhece um lugar em Belém que recebe lixo eletrônico e não está no mapa? Conte pra gente. Vamos conferir antes de publicar.',
	rotuloNome: 'Nome do local',
	placeholderNome: 'Ex.: Loja, supermercado, ecoponto',
	rotuloEndereco: 'Endereço ou bairro',
	placeholderEndereco: 'Ex.: Av. Nazaré, 100, Nazaré',
	perguntaTipos: 'O que o local recebe?',
	dicaTipos: 'Pode marcar mais de um.',
	rotuloObservacao: 'Como você sabe deste ponto?',
	opcional: '(opcional)',
	placeholderObservacao: 'Ex.: vi a caixa de coleta perto do caixa; funciona de segunda a sábado',
	botaoCancelar: 'Cancelar',
	botaoEnviar: 'Enviar sugestão',
	enviando: 'Enviando...',
	tituloSucesso: 'Obrigado pela sugestão!',
	mensagemSucesso:
		'Vamos conferir as informações e, se estiver tudo certo, o ponto aparece no mapa em breve.',
	botaoFechar: 'Fechar',
	erroEnvio: 'Não foi possível enviar a sugestão agora. Verifique sua conexão e tente de novo.',
	avisoNome: 'Informe o nome do local.',
	avisoEndereco: 'Informe o endereço ou o bairro.',
	avisoTipos: 'Marque pelo menos um tipo de resíduo.'
} as const;

/**
 * Página /privacidade (LGPD, RNF06). Cada item descreve o que o código faz
 * de fato: se o tratamento de algum dado mudar, este texto muda junto.
 */
export const privacidade = {
	titulo: 'Privacidade',
	descricao: 'Quais dados o ReCircuito usa, para quê e o que fica guardado.',
	voltar: 'Voltar para o início',
	resumo:
		'O ReCircuito não tem cadastro nem login e não pede seu nome, e-mail ou telefone. Os poucos dados que passam pelo site servem só para mostrar os pontos de coleta e melhorar o projeto.',
	secoes: [
		{
			titulo: 'Busca por CEP ou bairro',
			texto:
				'O que você digita vai para a nossa API, que consulta o ViaCEP e o Nominatim (OpenStreetMap) para descobrir a coordenada do lugar. Guardamos por até 30 dias só o par "texto buscado → coordenada", para não repetir a mesma consulta; nada nesse registro identifica quem buscou.'
		},
		{
			titulo: 'Sua localização',
			texto:
				'Só é usada se você tocar em "Usar minha localização" e o navegador pedir sua permissão. A posição vai para a nossa API apenas para ordenar os pontos pela distância e não é guardada.'
		},
		{
			titulo: 'Mapa',
			texto:
				'As imagens do mapa vêm do OpenFreeMap, com dados do OpenStreetMap. Como em qualquer site que mostra um mapa, esse serviço recebe as requisições do seu navegador (por exemplo, o endereço IP).'
		},
		{
			titulo: 'Google Analytics e cookies',
			texto:
				'Só é carregado se você clicar em "Aceitar" no aviso de cookies. Ele registra de forma estatística quais partes do site são visitadas e por qual tipo de aparelho. Se você recusar, nenhum código do Google é carregado. Sua escolha fica salva apenas no seu navegador.'
		},
		{
			titulo: 'Avaliação do site e sugestão de pontos',
			texto:
				'Guardamos as respostas do formulário e a data do envio, para o relatório do projeto e para conferir os pontos sugeridos. Não pedimos dados pessoais: evite escrever nome, telefone ou e-mail nos campos de texto.'
		},
		{
			titulo: 'Hospedagem',
			texto:
				'O site e a API ficam hospedados na Vercel, que processa e registra dados técnicos de acesso necessários para garantir o funcionamento, a estabilidade e a segurança da plataforma, em conformidade com as políticas de privacidade e segurança digital.'
		}
	],
	tituloEscolha: 'Mudou de ideia sobre os cookies?',
	reverEscolha: 'Rever minha escolha',
	escolhaApagada: 'Pronto. O aviso de cookies vai aparecer de novo quando você voltar para o início.',
	contato: 'Dúvidas ou pedidos sobre seus dados: escreva para'
} as const;
