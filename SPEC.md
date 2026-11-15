# ReCircuito — Especificação do projeto

Guia web para o descarte correto de lixo eletrônico em Belém (PA).
Projeto de Atividade Extensionista II (UNINTER, Ciência da Computação).

| | |
|---|---|
| **Status** | Site e API implementados e publicados na Vercel ([recircuito.info](https://recircuito.info) e [recircuito.vercel.app](https://recircuito.vercel.app)); base com 140 pontos em 32 bairros de Belém (119 confirmados e 21 pendentes); resta conferência presencial/telefônica dos 21 pontos pendentes (e 14 grades de horário), configuração opcional do ID real de produção em `VITE_ID_GOOGLE_ANALYTICS` e divulgação contínua em Belém |
| **Protótipo** | `ReCircuito - Prototipo.figcraft` (FigCraft): frames "Home — Desktop", "Home — Mobile", "Menu aberto — Mobile" e "Banner de cookies" (desktop e mobile) |
| **Logo** | Canva, design "Logo ReCircuito"; arquivos em `logos/final/` (ativos do site em `web/static/logos/`) |
| **Proposta enviada** | `Proposta de Tema - Alecsander Lima - Guia de Descarte Eletronico.pdf` |
| **Nome** | "ReCircuito" |

Este documento registra **o que** será construído e **por que** cada decisão foi tomada. Ele é a fonte única para o desenvolvimento: quando o protótipo e este texto divergirem, vale o texto, e o protótipo deve ser corrigido.

---

## 1. Visão geral

**Problema.** Em Belém, a informação sobre onde descartar lixo eletrônico está espalhada entre prefeitura, órgãos ambientais, fabricantes, operadoras, varejistas e cooperativas. Por isso, boa parte da população joga o lixo eletrônico no lixo comum.

**Solução.** Um site de uma página só, gratuito e sem cadastro, que:
1. explica por que o lixo eletrônico não vai no lixo comum;
2. ensina o descarte em 4 passos;
3. mostra o que pode ser descartado;
4. encontra o ponto de coleta mais próximo, com filtro pelo tipo de resíduo.

**Público.** Moradores, pequenos comércios e escritórios de Belém. A maior parte acessa pelo celular, a partir de links compartilhados em grupos de bairro e redes sociais.

**ODS.** 11 (Cidades e comunidades sustentáveis) e 12 (Consumo e produção responsáveis).

**Como saber que deu certo.**
- Uma pessoa encontra o ponto de coleta mais próximo que aceita o que ela quer descartar em menos de 1 minuto, pelo celular.
- O site passa nas validações de acessibilidade (WCAG 2.1 AA, inspeção automatizada em navegador real e navegação por teclado).
- Os acessos e as avaliações podem ser medidos (Google Analytics e formulário de avaliação).

## 2. Escopo

**Dentro do escopo**
- Página única com 6 seções (seção 3), em versões desktop e mobile.
- Busca de pontos de coleta por CEP, bairro ou localização do aparelho.
- Filtro por tipo de resíduo.
- Mapa real estilizado com os pontos de coleta.
- Botão "Como chegar", que abre a rota no aplicativo de mapas da pessoa.
- Link "Sugerir um ponto", que abre um formulário no próprio site (modal) e envia a sugestão para a API.
- Google Analytics, com banner de cookies, e formulário de avaliação.
- Animações de entrada e de rolagem (seção 7).

**Fora do escopo (por enquanto)**
- Área administrativa para editar pontos. Os dados são editados no arquivo JSON e publicados com um novo deploy.
- Cadastro ou login de usuários.
- Cálculo de rotas dentro do site (a rota é delegada ao app de mapas).
- Checklist interativo de remoção de dados. A orientação fica no texto do passo 02.
- Versão em outros idiomas.
- Outras cidades além de Belém.

## 3. Seções da página

A ordem é a mesma no desktop e no mobile. Os itens do menu levam às âncoras com rolagem suave.

| # | Seção | Âncora | Conteúdo | Comportamento |
|---|---|---|---|---|
| 1 | Topo (hero) | — | Logo, menu, vista explodida de um celular com 5 anotações ("Vidro", "Tela", "Bateria", "Placa", "Carcaça"), título "Seu lixo eletrônico tem destino.", texto de apoio e botão "Ver pontos de coleta" | Ocupa a altura da tela (`100svh`). Ao carregar no topo, os elementos entram em cascata descendo do topo: cabeçalho, as 5 camadas em ordem construtiva da base ao topo (Carcaça a Vidro), título e texto com botão (~1,35s). Se o usuário rolar durante a entrada, a cascata é cancelada e o celular assume a posição montada. Ao rolar, o Hero é fixado (`pin: true`) durante 1 tela (`+=100%`); de 0% a 80%, as camadas explodem e as anotações surgem; de 80% a 100%, pausa para leitura antes de desfixar. **Mobile:** menu vira ícone ☰ e as anotações ficam ocultas |
| 2 | O projeto | `#sobre` | Frase de impacto e parágrafo explicando a iniciativa de extensão universitária | Estática, com entrada suave |
| 3 | Como descartar | `#como-descartar` | 4 passos: Separe, Apague os dados, Ache um ponto, Entregue. Cada um com faixa verde, número, ilustração em traço e descrição | Ilustrações em loop. **Desktop:** 4 colunas. **Mobile:** empilhado |
| 4 | O que descartar | `#o-que-descartar` | Título centralizado e grade 2×2: celulares e tablets, pilhas e baterias, computadores e periféricos, cabos e carregadores | Movimento leve em cada ilustração |
| 5 | Pontos de coleta | `#pontos-de-coleta` | Busca, "Usar minha localização", filtro por tipo, mapa, lista de pontos ordenada por distância (cada um com "Como chegar") e link "Sugerir um ponto" | Ver seção 4. O filtro é uma grade de 2 linhas que ocupa a largura toda: "Todos", "Cabos", "Pilhas" / "Computadores", "Celulares". A lista de pontos fica contida em uma janela com rolagem vertical própria (`max-height: 380px`, `overflow-x: hidden`, `data-lenis-prevent`) e linhas delimitadoras, permitindo exibir ~2,5 a 3 itens sem alongar a página. **Mobile:** busca, filtro, mapa e lista, nessa ordem |
| 6 | Impacto | `#impacto` | 4 métricas reais de cobertura do mapeamento: **140** pontos de coleta mapeados, **32** bairros de Belém cobertos, **119** pontos confirmados em fontes oficiais e **4** grupos de resíduos aceitos | Números contam de 0 até o valor real ao entrar na tela (substituindo os valores fictícios iniciais do protótipo) |
| — | Rodapé | — | Logo escuro, frase, navegação, contato, link para `/privacidade`, "Projeto de Extensão II · 2026" e botão "Avaliar o site" (modal de avaliação) | Estático |

Menções a "projeto de extensão": só na seção "O projeto" e nos créditos do rodapé.

## 4. Requisitos funcionais

| ID | Requisito |
|---|---|
| RF01 | A pessoa digita um CEP ou o nome de um bairro de Belém, e o site centraliza o mapa nesse local e ordena os pontos pela distância. |
| RF02 | O botão "Usar minha localização" pede permissão ao navegador e faz o mesmo que o RF01 com a posição do aparelho. A localização nunca é enviada para armazenamento. |
| RF03 | Sem busca, o mapa mostra Belém inteira com todos os pontos, e a lista fica em ordem alfabética. |
| RF04 | O filtro por tipo de resíduo (celulares e tablets, pilhas e baterias, computadores e periféricos, cabos e carregadores) mostra só os pontos que aceitam os tipos marcados. Pode marcar mais de um. "Todos" vem marcado por padrão, e desmarcar todos os tipos volta para "Todos". |
| RF05 | Cada ponto na lista mostra nome, endereço, distância (quando houver busca), tipos aceitos e se está **aberto agora**, calculado pelo horário de funcionamento no fuso de Belém; quando o ponto não tem horário conhecido, mostra **"Horário não informado"** em vez de "Fechado agora". |
| RF06 | Clicar num ponto da lista destaca o ponto no mapa e abre o balão; clicar num pino do mapa destaca o ponto, abre o balão e rola suavemente a janela interna da lista (`data-lenis-prevent`) até o item correspondente. |
| RF07 | O botão "Como chegar" abre a rota até o ponto no Google Maps ou no OpenStreetMap, em nova aba. |
| RF08 | O link "Sugerir um ponto" abre um modal com nome do local, endereço ou bairro, tipos de resíduo aceitos (pelo menos um) e observação opcional. O envio vai para `POST /api/sugestoes`, que grava em `api/dados/sugestoes.json`. A sugestão **não** aparece no mapa sozinha: a equipe confere e cadastra à mão em `pontos.json`. O formulário não pede contato (e-mail, telefone), para não coletar dado pessoal (RNF06). |
| RF09 | Os links do menu rolam suavemente até a seção. No mobile, o menu abre em tela cheia e fecha ao escolher um item. |
| RF10 | Na primeira visita, um **banner de cookies** ("Sua privacidade importa") pede consentimento para o Analytics, com os botões "Recusar" e "Aceitar" do mesmo tamanho e da mesma cor. Ele não prende o foco do teclado, fica no início da ordem de tabulação e é anunciado como região ("Aviso de cookies") para leitores de tela. O Google Analytics só carrega se a pessoa aceitar. A escolha fica salva no navegador, e o banner não volta a aparecer. |
| RF11 | O rodapé tem o botão "Avaliar o site", que abre um modal no próprio site (nota, se encontrou o ponto e comentário opcional) e envia para `POST /api/avaliacoes`, gravando em `api/dados/avaliacoes.json`. |
| RF12 | Busca sem resultado, erro de rede e permissão de localização negada mostram mensagens claras, nunca uma lista vazia sem explicação. |

## 5. Requisitos não funcionais

| ID | Requisito |
|---|---|
| RNF01 | **Acessibilidade:** WCAG 2.1 nível AA, validado via inspeção automatizada em navegador real (contraste e teclado). Contraste mínimo de 4,5:1 em texto normal, navegação completa por teclado com foco visível, textos alternativos nas ilustrações e áreas de toque de pelo menos 44×44px. |
| RNF02 | **Animação acessível:** com `prefers-reduced-motion`, o Lenis fica desligado, as ilustrações aparecem no estado final e os loops param. |
| RNF03 | **Responsivo:** funciona de 360px a 1920px de largura. As referências do protótipo são 390px (mobile) e 1440px (desktop). |
| RNF04 | **Desempenho:** Lighthouse ≥ 90 em desempenho no mobile e LCP abaixo de 2,5s em 4G. |
| RNF05 | **Navegadores:** as duas últimas versões de Chrome, Safari (inclusive iOS), Firefox e Edge. |
| RNF06 | **Privacidade (LGPD):** nenhuma coleta de dado pessoal além do Analytics consentido. CEP e localização são usados só para a busca e não ficam guardados. O cache da API guarda só pares "texto buscado → coordenada". |
| RNF07 | **Custo zero:** todas as ferramentas e serviços em plano gratuito. |
| RNF08 | **Uso justo de serviços públicos:** respeitar as regras do Nominatim (no máximo 1 requisição por segundo, identificação do app e cache) e os créditos do OpenStreetMap no mapa. |

## 6. Identidade visual

**Cores**

| Token | Valor | Uso |
|---|---|---|
| `--ink` | `#0F1A14` | Texto principal e traço das ilustrações |
| `--ink-2` | `#3F4F45` | Texto de apoio |
| `--muted` | `#5B6B61` | Descrições e rótulos (mínimo para contraste AA) |
| `--line` | `#C9D3CC` | Linhas divisórias e contornos |
| `--line-soft` | `#DCE3DD` | Bordas suaves (busca, mapa) |
| `--green` | `#1F9D55` | Detalhes das ilustrações, faixas dos passos (texto ≥ 24px) e links |
| `--green-strong` | `#157A41` | Fundo de botões com texto branco (contraste 5,4:1, AA). O `--green` com texto branco dá só 3,5:1 |
| `--green-dark-mode` | `#3FBF73` | Verde sobre fundo escuro |
| `--bg-hero` | `#E8F1EA` | Fundo do topo |
| `--bg-alt` | `#F5F7F2` | Fundo das seções alternadas |
| `--bg` | `#FFFFFF` | Fundo das seções |
| `--footer` | `#0B2A1A` | Rodapé |

**Tipografia**
- **Newsreader**, para tudo que é **lido**: títulos (Medium), parágrafos e descrições (Regular), logo e números grandes.
- **Plus Jakarta Sans**, para tudo que é **usado**: menu, botões, busca, filtros, lista de pontos, anotações, rótulos e números 01–04.
- Ambas são gratuitas (Google Fonts) e devem ser servidas pelo próprio site, em `woff2` com `font-display: swap`.

**Regras de estilo**
- Ilustrações em traço de 2px na cor `--ink`, com no máximo um detalhe verde por desenho.
- Sem sombras e sem gradientes.
- Cantos retos em botões, cards, busca, mapa e faixas. Só os desenhos de aparelhos têm cantos arredondados.
- Botões com fundo `--green-strong` e texto branco; links em `--green` sublinhado. Filtro selecionado: fundo `--ink` e texto branco.
- Separação entre conteúdos por linhas finas e espaço, nunca por caixas com sombra.
- Fundos alternando entre `--bg` e `--bg-alt`, com o topo em `--bg-hero`.
- Margem lateral de 48px no desktop e de 20px no mobile.

**Logo:** o nome em Newsreader Medium em que o símbolo (trilha de circuito em octógono aberto, com furo vazado em cima e ponto verde embaixo) **substitui o "C"** de Circuito. O símbolo usa o corte grosso (traço 60), que casa com o peso das letras. O símbolo sozinho continua sendo o ícone (favicon, redes sociais), porque em tamanho pequeno o "C" dentro da palavra não se lê. Arquivos em `logos/final/` (fora do repositório; os do site estão em `web/static/logos/`):
- `logo-simbolo-no-c-site.svg` e `logo-simbolo-no-c-escuro-site.svg`: recorte justo, usados no menu e no rodapé (o escuro, sobre o fundo verde-escuro);
- `logo-simbolo-no-c.svg`: com margem, para divulgação (página 5 do design "Logo ReCircuito" no Canva);
- `-site.svg`: sem margem, para menu e rodapé;
- `logo-horizontal`, `logo-vertical` e `-escuro`: para divulgação;
- `simbolo-favicon`: traço grosso, para ícone da aba e redes sociais.

## 7. Animações

Feitas com GSAP (ScrollTrigger, DrawSVG). A rolagem suave é feita com Lenis, sincronizado com o `ScrollTrigger`. Todas respeitam o RNF02.

| Onde | Animação | Disparo | Duração |
|---|---|---|---|
| Topo (entrada) | Cascata do topo: cabeçalho desce (0s), 5 camadas caem em sequência construtiva (Carcaça a Vidro, stagger 0,12s) montando o aparelho, seguidas pelo título e texto com botão; guias e chamadas ocultas | Ao carregar no topo (`window.scrollY <= 5`) | ~1,35s no total, `power2.out` |
| Topo (scroll) | Hero fixado (`pin: true`, scrub 0,6). De 0% a 80%: camadas separam (explosão), guias surgem e no desktop linhas desenham (DrawSVG) e rótulos entram. De 80% a 100%: pausa para leitura | Ao rolar a página | 1 tela de rolagem (`+=100%`) |
| Passo 01 | Itens caem dentro da caixa e a seta aparece | Seção visível, em loop | 0,9s + pausa de 1,8s |
| Passo 02 | Barra de quadrados enche | Seção visível, em loop | 1,8s + pausa de 0,9s |
| Passo 03 | Anel verde se expande e some (radar) | Seção visível, em loop | 1,6s |
| Passo 04 | Pontos acendem em sequência (esteira) | Seção visível, em loop | 3 passos de 0,3s, com pausa de 0,5s |
| O que descartar | Movimentos leves: aparelhos flutuam, rodinha do mouse rola, luz do carregador pisca | Seção visível, em loop | 0,5s a 1,4s, todos com tempos diferentes |
| Mapa | Anel pulsando no ponto selecionado | Sempre que há um ponto selecionado | 1,6s |
| Filtro e busca | Só se mexe o que mudou. Pinos que saem encolhem e somem; pinos novos crescem com um "ping" fino em volta, em cascata (25ms entre eles, até 175ms). Na lista, itens novos sobem 8px enquanto aparecem, os que saem só esmaecem e os vizinhos deslizam para o lugar (FLIP) | Ao mudar o filtro ou a busca | Entrada 240ms, saída 160ms, ping 520ms, reorganizar 240ms (`PONTOS` em `movimento.ts`) |
| Impacto | Números contam de 0 até o valor | Ao entrar na tela, uma vez | 1,2s |
| Seções | Títulos e textos sobem 16px enquanto aparecem | Ao entrar na tela, uma vez | 0,6s |
| Modais (avaliação e sugestão) | Abertura: fundo escurece e o cartão surge 8px abaixo e 3% menor, já transparente; os blocos do formulário chegam em cascata curta (30ms entre eles). Fechamento: mais curto, com metade do movimento. Toque: botões e chips afundam 3% no clique. Envio: "Enviando…" com spinner só se a resposta passar de 300ms, e então fica ao menos 500ms (nada pisca). Erro: mensagem entra suave, sem tremer. Sucesso: formulário esmaece, o cartão ajusta a altura, o aro do ícone se desenha e o visto "assina" em seguida | Ao abrir, clicar, enviar e fechar | Entrada 260ms, saída 160ms, toque 120ms, altura 280ms, ícone ~600ms; curvas e tempos nos tokens `--curva-*`/`--dur-*` (tokens.css) e em `movimento.ts` |

Os loops param quando a seção sai da tela, para economizar bateria e processamento.

## 8. Arquitetura e tecnologias

```
Navegador ──► Site estático (SvelteKit) ──► arquivos (HTML, CSS, JS, fontes, SVG)
   │
   ├──► API (FastAPI) ──► pontos.json (dados dos ecopontos)
   │         └──► ViaCEP / Nominatim (geocodificação, com cache)
   │
   ├──► OpenFreeMap (dados e estilo do mapa, sem chave)
   └──► Google Analytics (só com consentimento)
```

| Camada | Escolha | Por quê |
|---|---|---|
| Framework | **Svelte 5 + SvelteKit**, exportado como site estático (`adapter-static`) | Página única com muita animação e pouco estado: o Svelte entrega menos JavaScript e integra o GSAP sem camadas extras |
| Animação | **GSAP 3** (ScrollTrigger, DrawSVG) | Padrão dos sites premiados; agora 100% gratuito, inclusive os plugins |
| Rolagem suave | **Lenis** | Leve e feito para trabalhar junto com o ScrollTrigger |
| Mapa | **MapLibre GL JS + OpenFreeMap** | Mapa real, em vetores, que pode ser estilizado no visual do site (traço fino, fundo branco). Grátis, sem chave de API |
| API | **Python 3.12 + FastAPI** | Busca e ordenação dos pontos, filtro por tipo e geocodificação com cache, num só lugar |
| Distância | Fórmula de haversine (ou `geopy.distance`) | A distância em linha reta basta para ordenar pontos dentro da cidade. Não usar `geopandas`/`shapely`, pesados demais para o volume de dados |
| CEP → endereço | **ViaCEP** | Gratuito e específico para o Brasil |
| Endereço → coordenada | **Nominatim** (OpenStreetMap) | Gratuito, limitado à área de Belém e sempre com cache |
| Analytics | **Google Analytics 4** + banner de cookies | Exigência da proposta (objetivo 6) |
| Formulários | Modais no próprio site, gravando pela API (sugestão de ponto e avaliação) | Mesmo visual do site e sem levar a pessoa para fora; os dados ficam em arquivos JSON, sem banco |
| Versionamento | **Git + GitHub** | Exigência da proposta |

**Diferenças em relação à proposta enviada à UNINTER** (para registrar e justificar no relatório final)

| Proposta | Projeto | Justificativa |
|---|---|---|
| HTML5, CSS3 e JavaScript puros | SvelteKit (que gera HTML, CSS e JavaScript) | Componentes reaproveitáveis e animações complexas com menos código e menos JavaScript no navegador |
| Bootstrap 5 | CSS próprio, com tokens | O Bootstrap impõe um visual genérico que conflita com a identidade definida no protótipo |
| Leaflet + OpenStreetMap | MapLibre + OpenFreeMap (dados do OpenStreetMap) | Mesma base de dados, mas permite estilizar o mapa no visual do site |
| Sem servidor; dados em JSON | API FastAPI lendo um JSON | Geocodificação com cache e regras de uso do Nominatim respeitadas num só lugar; os dados continuam num arquivo JSON, sem banco de dados |
| Hospedagem no GitHub Pages | Deploy unificado na Vercel via `vercel.json` (**Vercel Services**: serviço estático `web` + API FastAPI `api`), sob `https://recircuito.info` e `https://recircuito.vercel.app` | O GitHub Pages só serve arquivos estáticos e não executa a API FastAPI; a Vercel unifica site e API na mesma origem, evita bloqueios de CORS entre domínios e elimina a hibernação de 30–50s do plano gratuito anterior |
| Busca por bairro | Busca por CEP **ou** bairro, mais localização do aparelho | Ampliação do mesmo requisito |
| Sugestão de ponto e avaliação pelo Google Forms | Modais no site + `POST /api/sugestoes` e `POST /api/avaliacoes` | Mantém a pessoa no site, com o visual do projeto; a sugestão chega no mesmo formato dos pontos (tipos de resíduo com os mesmos códigos) e dispensa redirecionamento externo |
| Checklist de remoção de dados | Orientação em texto no passo 02 | Fora do escopo nesta versão (seção 2) |

## 9. Dados dos pontos de coleta

Os dados ficam em `api/dados/pontos.json` (atualmente com **140 pontos mapeados em 32 bairros de Belém**: **119** confirmados em fontes oficiais em `2026-11-12` e **21** pendentes de confirmação presencial/telefônica com `verificado_em: null` e `"NÃO CONFIRMADO"` em `observacoes`; levantamento completo em `docs/pesquisa-pontos-de-coleta.md`). Cada ponto deve citar a fonte de onde a informação veio, para que possa ser conferida.

```json
{
  "id": "ecoponto-centro",
  "nome": "Ecoponto Centro",
  "tipo_local": "ecoponto",
  "endereco": {
    "logradouro": "Av. Exemplo",
    "numero": "1200",
    "bairro": "Campina",
    "cep": "66010-000"
  },
  "coordenadas": { "lat": -1.4558, "lon": -48.4902 },
  "tipos_aceitos": ["celulares_tablets", "pilhas_baterias", "computadores_perifericos", "cabos_carregadores"],
  "horarios": [
    { "dias": [1, 2, 3, 4, 5], "abre": "08:00", "fecha": "18:00" },
    { "dias": [6], "abre": "08:00", "fecha": "12:00" }
  ],
  "contato": { "telefone": null, "site": null },
  "fonte": "https://exemplo.gov.br/pagina-de-onde-veio-a-informacao",
  "verificado_em": "2026-11-01",
  "observacoes": null
}
```

- `tipo_local`: `ecoponto`, `varejo`, `operadora`, `fabricante`, `cooperativa` ou `orgao_publico`.
- `tipos_aceitos`: `celulares_tablets`, `pilhas_baterias`, `computadores_perifericos` ou `cabos_carregadores`.
- `dias`: 0 = domingo, 6 = sábado. "Aberto agora" usa o fuso `America/Belem`.
- Os endereços e coordenadas acima são só exemplo de formato.

## 10. API

Base: `/api`. Respostas em JSON, sem autenticação. Consultas via `GET` e envios de sugestões/avaliações via `POST`. Em desenvolvimento, o CORS libera apenas as origens configuradas em `RECIRCUITO_ORIGENS_PERMITIDAS`; em produção na Vercel, site e API respondem sob a mesma origem.

**`GET /api/pontos`**: lista os pontos de coleta.

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `lat`, `lon` | número, opcional | Posição de referência. Com ela, a lista vem ordenada por distância e com `distancia_km` |
| `tipos` | texto, opcional | Tipos separados por vírgula, ex.: `pilhas_baterias,cabos_carregadores` |
| `limite` | inteiro, opcional | Máximo de resultados (padrão: todos) |

Resposta: `{ "pontos": [ { ...ponto, "distancia_km": 1.2, "aberto_agora": true } ], "total": 12 }`

`aberto_agora` é `true` ou `false` pelo horário de funcionamento no fuso de Belém, ou `null` quando o ponto não tem horário cadastrado (`horarios` vazio): o horário é desconhecido, e isso não equivale a "fechado".

**`GET /api/pontos/{id}`**: um ponto. Retorna 404 se não existir.

**`GET /api/geocodificar?q=`**: transforma CEP ou bairro em coordenada.
- **CEP** (8 dígitos): ViaCEP → endereço → Nominatim.
- **Texto:** Nominatim, limitado à área de Belém.
- Resposta: `{ "lat": -1.45, "lon": -48.49, "rotulo": "Campina, Belém - PA", "fonte": "viacep+nominatim" }`
- Não encontrado: 404, com `{ "erro": "nao_encontrado", "mensagem": "..." }`.
- Cache em memória (e opcionalmente em arquivo) por 30 dias, com no máximo 1 chamada por segundo ao Nominatim e `User-Agent` identificando o projeto.

**`GET /api/tipos`**: lista os tipos de resíduo com nome de exibição.

**`POST /api/sugestoes`**: recebe a indicação de um ponto de coleta enviada pelo modal "Sugerir um ponto" (RF08).
- Corpo JSON: `{ "nome", "endereco", "tipos", "observacao?" }` (`tipos` usa os códigos de `TipoResiduo`; sem campos pessoais como e-mail ou telefone).
- Resposta (`201 Created`): registro salvo com `data` gerada pelo servidor, gravado em `api/dados/sugestoes.json` localmente (ou `/tmp/recircuito/sugestoes.json` como reserva efêmera em ambiente serverless somente leitura).

**`POST /api/avaliacoes`**: recebe uma avaliação do site enviada pelo modal "Avaliar o site" (RF11).
- Corpo JSON: `{ "nota" (1–5), "encontrou_ponto" ("sim" | "parcialmente" | "nao"), "comentario?", "data?" }`.
- Resposta (`201 Created`): registro salvo com `data` ISO garantida, gravado em `api/dados/avaliacoes.json` localmente (ou `/tmp/recircuito/avaliacoes.json` como reserva efêmera em ambiente serverless somente leitura).

**`GET /api/saude`**: verificação simples para a hospedagem (Vercel) e monitoramento da API.

Erros seguem sempre o formato `{ "erro": "<codigo>", "mensagem": "<texto para a pessoa>" }`.

## 11. Estrutura do repositório

A pasta `recircuito/` é o repositório. O protótipo (`.figcraft`), a proposta (PDF) e os arquivos de criação do logo (`logos/`) ficam na pasta acima dela, fora do Git.

```
recircuito/
├── vercel.json                        # deploy unificado na Vercel (Vercel Services: web + api)
├── docs/                              # pesquisa consolidada dos pontos de coleta e guia de implementação
├── web/                               # SvelteKit (TypeScript)
│   ├── src/
│   │   ├── app.html, app.d.ts
│   │   ├── routes/                    # +layout.svelte, +layout.ts (prerender = true), +page.svelte,
│   │   │                              # privacidade/+page.svelte
│   │   └── lib/
│   │       ├── componentes/           # Abertura, Cabecalho, MenuMobile, Hero, Sobre, ComoDescartar,
│   │       │                          # Passo, OQueDescartar, Item, PontosDeColeta, Busca, FiltroTipos,
│   │       │                          # Mapa, ListaPontos, Impacto, Rodape, BannerCookies, ModalBase,
│   │       │                          # ModalAvaliacao, ModalSugestao, ícones SVG
│   │       ├── ilustracoes/           # SVGs em traço: CelularExplodido, Passo*, Item*
│   │       ├── animacao/              # gsap.ts, lenis.ts, movimento.ts, movimentoReduzido.ts,
│   │       │                          # abertura.ts, contador.ts, espera.ts, pausarForaDaTela.ts, revelar.ts
│   │       ├── api/pontos.ts          # cliente da API (GET + POST)
│   │       ├── conteudo/textos.ts     # textos do site num só lugar
│   │       ├── analytics.ts           # consentimento de cookies e carregamento condicional do GA4
│   │       └── estilos/               # tokens.css, fontes.css, base.css
│   └── static/                        # favicon.svg, logos/, fontes/ (newsreader-variavel, plus-jakarta-sans-variavel)
├── api/                               # FastAPI (Python)
│   ├── main.py                        # ponto de entrada compatível com a Vercel
│   ├── aplicacao/
│   │   ├── principal.py, configuracao.py, modelos.py
│   │   ├── rotas/                     # pontos, geocodificacao, tipos, saude, avaliacoes, sugestoes
│   │   └── servicos/                  # geocodificador, cache, distancia, horarios, registro_json
│   ├── dados/pontos.json              # 140 pontos mapeados em 32 bairros de Belém
│   ├── testes/
│   └── pyproject.toml
├── SPEC.md
└── README.md
```

**Convenção de idioma (obrigatória).** Tudo é escrito em **português do Brasil**: nomes de variáveis, funções, classes, componentes e arquivos próprios, comentários, docstrings, testes, mensagens da API, README e mensagens de commit. Exemplos: `calcular_distancia_km()`, `class PontoDeColeta`, `esta_aberto_agora()`, `FiltroTipos.svelte`, `const pontosFiltrados`.

- **Exceções:** só os nomes impostos por ferramentas e frameworks (`+page.svelte`, `package.json`, `main.py`, `app = FastAPI()`, o prefixo `test_` do pytest, propriedades de bibliotecas como `gsap.to({ duration })`).
- **Comentários** explicam o *porquê* e dão dicas para quem está aprendendo: o que a função resolve, por que aquela abordagem e que cuidado tomar ao mudar. Nada de comentário que só repete o código.

## 12. Hospedagem e deploy

Site e API são publicados de forma unificada na **Vercel** usando **Vercel Services** (`vercel.json`):

| Parte | Onde | Observação |
|---|---|---|
| Site (`web`) | Vercel (build estático em `web/build/`) | SvelteKit com `adapter-static` e `prerender = true`, atendendo `/(.*)` — inclui `/` e a rota estática `/privacidade` (entregue via `trailingSlash: false` e rewrite `/privacidade` → `/privacidade.html` em `vercel.json`). Fontes locais em `web/static/fontes/` |
| API (`api`) | Vercel (serviço FastAPI em `api/aplicacao/principal.py`, também exposto em `api/main.py`) | Atende `/api/(.*)` sob a mesma origem do site, eliminando CORS entre domínios e evitando a hibernação de 30–50s do plano anterior |
| Persistência em serverless | Memória + `/tmp/recircuito/` (efêmero) | A pasta do código na Vercel é somente leitura: o cache de geocodificação atua prioritariamente em memória; envios de `POST /api/avaliacoes` e `POST /api/sugestoes` usam `/tmp/recircuito/` como reserva efêmera em produção e `api/dados/` localmente |
| Domínios | `https://recircuito.info` e `https://recircuito.vercel.app` | Domínio próprio configurado com HTTPS automático na Vercel |
| Variáveis de ambiente | Vercel Project Settings | No site: `VITE_URL_DA_API` vazia em produção (mesma origem) e `VITE_ID_GOOGLE_ANALYTICS` opcional. Na API: `RECIRCUITO_ORIGENS_PERMITIDAS`, `RECIRCUITO_ARQUIVO_PONTOS`, `RECIRCUITO_CONTATO` (e-mail real para o Nominatim) e `RECIRCUITO_ARQUIVO_CACHE` |

## 13. Ordem de desenvolvimento

1. **Base:** repositório, SvelteKit e FastAPI rodando, tokens, fontes e logo.
2. **Estrutura:** as 6 seções estáticas no desktop e no mobile, fiéis ao protótipo.
3. **Dados:** levantamento dos pontos de Belém no `pontos.json`, com fontes.
4. **API:** rotas, geocodificação com cache e testes.
5. **Mapa e busca:** MapLibre estilizado, busca, filtro, lista e "Como chegar".
6. **Animações:** GSAP, Lenis e reduced-motion.
7. **Modais, privacidade e Analytics:** modais de sugestão/avaliação ligados à API, rota estática `/privacidade`, banner de cookies LGPD e suporte condicional a GA4.
8. **Qualidade:** inspeção WCAG 2.1 AA em navegador real (contraste, teclado e áreas de toque ≥ 44px), `svelte-check`, `pytest` e testes em celulares reais.
9. **Publicação e divulgação:** deploy unificado na Vercel (`vercel.json`), documentação atualizada e divulgação contínua em Belém.

## 14. Pendências e riscos

**Concluído recentemente**
- ~~Confirmar e ampliar os 8 pontos iniciais fictícios/não confirmados~~: base atualizada para **140 pontos em 32 bairros de Belém** (`119` confirmados em fontes oficiais em `12/11/2026` e `21` marcados como pendentes).
- ~~Trocar os números fictícios do Impacto por dados reais~~: seção `#impacto` atualizada para exibir métricas reais de cobertura do mapeamento (`140` pontos mapeados, `32` bairros atendidos, `119` pontos confirmados e `4` tipos de resíduo).
- ~~Criar os dois Google Forms~~: substituídos por modais nativos no site gravando pela API (`POST /api/sugestoes` e `POST /api/avaliacoes`, RF08 e RF11).
- ~~Criar e corrigir a página de política de privacidade~~: rota estática `/privacidade` implementada, linkada no banner de cookies e no rodapé, com entrega estática corrigida para o deploy na Vercel.
- ~~Contatos reais no rodapé e nome do projeto~~: contatos reais e marca **ReCircuito** publicados em `https://recircuito.info` e `https://recircuito.vercel.app`.

**Pendências atuais**
- **Conferência presencial/telefônica dos 21 pontos pendentes e 14 grades de horário faltantes:** contatar ou visitar os 21 pontos marcados com `verificado_em: null` e aviso `"NÃO CONFIRMADO"` em `observacoes` (e os 14 pontos atualmente com `horarios: []`, exibidos como `"Horário não informado"`) para validar endereço, funcionamento, itens aceitos e preencher `verificado_em`.
- **Configuração opcional do ID real de produção em `VITE_ID_GOOGLE_ANALYTICS`:** o fluxo de consentimento LGPD (banner de cookies, injeção condicional do `gtag.js` e opção "Rever minha escolha" em `/privacidade`) já está implementado; caso a equipe deseje ativar a medição em produção, basta definir um ID GA4 real em `VITE_ID_GOOGLE_ANALYTICS` nas variáveis de ambiente da Vercel.
- **Divulgação contínua em Belém:** compartilhar o guia (`https://recircuito.info`) em escolas, cooperativas, associações de bairro e redes sociais locais, acompanhando novas sugestões e avaliações.

**Riscos**
- **Dados desatualizados:** pontos fecham ou mudam de horário. Mitigação: campo `verificado_em`, exibição explícita de `"Horário não informado"` quando `horarios` está vazio e o modal `"Sugerir um ponto"` (`POST /api/sugestoes`).
- **Armazenamento efêmero em serverless (`/tmp`):** na Vercel, `POST /api/avaliacoes` e `POST /api/sugestoes` gravam em `/tmp/recircuito/` quando a pasta do código é somente leitura, não persistindo entre deploys ou novas instâncias. Mitigação: adequado ao volume inicial do projeto, com possibilidade de migração futura para armazenamento persistente se necessário.
- **Limites do Nominatim:** mitigação com cache (30 dias em memória) e limite de 1 requisição por segundo na API.
- **Animações pesadas em celulares simples:** mitigação com loops pausados fora da tela e `prefers-reduced-motion`.
