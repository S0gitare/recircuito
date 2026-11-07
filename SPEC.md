# ReCircuito — Especificação do projeto

Guia web para o descarte correto de lixo eletrônico em Belém (PA).
Projeto de Atividade Extensionista II (UNINTER, Ciência da Computação).

| | |
|---|---|
| **Status** | Site e API implementados (seções, desenhos animados, mapa, busca, cookies); falta dados reais, formulários, Analytics com ID real, testes de acessibilidade e publicação |
| **Protótipo** | `ReCircuito - Prototipo.figcraft` (FigCraft): frames "Home — Desktop", "Home — Mobile", "Menu aberto — Mobile" e "Banner de cookies" (desktop e mobile) |
| **Logo** | Canva, design "Logo ReCircuito"; arquivos em `logos/final/` |
| **Proposta enviada** | `Proposta de Tema - Alecsander Lima - Guia de Descarte Eletronico.pdf` |
| **Nome** | "ReCircuito" (provisório até a validação final) |

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
- O site passa nas validações de acessibilidade (WCAG 2.1 AA, WAVE e ASES).
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
| 6 | Impacto | `#impacto` | 4 números: kg coletados, escolas visitadas, pontos mapeados, pessoas alcançadas | Números contam de 0 até o valor ao entrar na tela. **Os valores do protótipo são fictícios** |
| — | Rodapé | — | Logo escuro, frase, navegação, contato, "Projeto de Extensão II · 2026" e link do formulário de avaliação | Estático |

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
| RF11 | O rodapé tem link para o formulário de avaliação do site (Google Forms). |
| RF12 | Busca sem resultado, erro de rede e permissão de localização negada mostram mensagens claras, nunca uma lista vazia sem explicação. |

## 5. Requisitos não funcionais

| ID | Requisito |
|---|---|
| RNF01 | **Acessibilidade:** WCAG 2.1 nível AA, validado com WAVE e ASES. Contraste mínimo de 4,5:1 em texto normal, navegação completa por teclado com foco visível, textos alternativos nas ilustrações e áreas de toque de pelo menos 44×44px. |
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
| Hospedagem no GitHub Pages | Site no GitHub Pages; API no Render (plano gratuito) | O GitHub Pages só serve arquivos estáticos e não roda a API |
| Busca por bairro | Busca por CEP **ou** bairro, mais localização do aparelho | Ampliação do mesmo requisito |
| Sugestão de ponto pelo Google Forms | Modal no site + `POST /api/sugestoes` | Mantém a pessoa no site, com o visual do projeto; a sugestão chega no mesmo formato dos pontos (tipos de resíduo com os mesmos códigos) |
| Checklist de remoção de dados | Orientação em texto no passo 02 | Fora do escopo nesta versão (seção 2) |

## 9. Dados dos pontos de coleta

Os dados ficam em `api/dados/pontos.json`. Cada ponto deve citar a fonte de onde a informação veio, para que possa ser conferida.

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

Base: `/api`. Respostas em JSON. Só leitura, sem autenticação. CORS liberado apenas para o domínio do site.

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

**`GET /api/saude`**: verificação simples para a hospedagem.

Erros seguem sempre o formato `{ "erro": "<codigo>", "mensagem": "<texto para a pessoa>" }`.

## 11. Estrutura do repositório

A pasta `recircuito/` é o repositório. O protótipo (`.figcraft`), a proposta (PDF) e os arquivos de criação do logo (`logos/`) ficam na pasta acima dela, fora do Git.

```
recircuito/
├── .github/workflows/deploy-web.yml   # build e publicação do site no GitHub Pages
├── docs/                              # diagramas UML e material do relatório
├── web/                               # SvelteKit (TypeScript)
│   ├── src/
│   │   ├── app.html, app.d.ts
│   │   ├── routes/                    # +layout.svelte, +layout.ts (prerender), +page.svelte
│   │   └── lib/
│   │       ├── componentes/           # Cabecalho, MenuMobile, Hero, Sobre, ComoDescartar, Passo,
│   │       │                          # OQueDescartar, Item, PontosDeColeta, Busca, FiltroTipos,
│   │       │                          # Mapa, ListaPontos, Impacto, Rodape, BannerCookies, ModalAvaliacao
│   │       ├── ilustracoes/           # SVGs em traço: CelularExplodido, Passo*, Item*
│   │       ├── animacao/              # gsap.ts, lenis.ts, movimentoReduzido.ts
│   │       ├── api/pontos.ts          # cliente da API
│   │       ├── conteudo/textos.ts     # textos do site num só lugar
│   │       └── estilos/               # tokens.css, fontes.css, base.css
│   └── static/                        # favicon.svg, logos/, fontes/
├── api/                               # FastAPI (Python)
│   ├── aplicacao/
│   │   ├── principal.py, configuracao.py, modelos.py
│   │   ├── rotas/                     # pontos, geocodificacao, tipos, saude
│   │   └── servicos/                  # geocodificador, cache, distancia, horarios
│   ├── dados/pontos.json
│   ├── testes/
│   └── pyproject.toml
├── SPEC.md
└── README.md
```

**Convenção de idioma (obrigatória).** Tudo é escrito em **português do Brasil**: nomes de variáveis, funções, classes, componentes e arquivos próprios, comentários, docstrings, testes, mensagens da API, README e mensagens de commit. Exemplos: `calcular_distancia_km()`, `class PontoDeColeta`, `esta_aberto_agora()`, `FiltroTipos.svelte`, `const pontosFiltrados`.

- **Exceções:** só os nomes impostos por ferramentas e frameworks (`+page.svelte`, `package.json`, `main.py`, `app = FastAPI()`, o prefixo `test_` do pytest, propriedades de bibliotecas como `gsap.to({ duration })`).
- **Comentários** explicam o *porquê* e dão dicas para quem está aprendendo: o que a função resolve, por que aquela abordagem e que cuidado tomar ao mudar. Nada de comentário que só repete o código.

## 12. Hospedagem

| Parte | Onde | Observação |
|---|---|---|
| Site | GitHub Pages | Build estático via GitHub Actions |
| API | Render (plano gratuito) | O servidor "dorme" sem uso; a primeira busca pode levar de 30 a 50s. O site deve mostrar "carregando" nesse caso |
| Domínio | Endereço gratuito do GitHub Pages | Domínio próprio é opcional |

## 13. Ordem de desenvolvimento

1. **Base:** repositório, SvelteKit e FastAPI rodando, tokens, fontes e logo.
2. **Estrutura:** as 6 seções estáticas no desktop e no mobile, fiéis ao protótipo.
3. **Dados:** levantamento dos pontos de Belém no `pontos.json`, com fontes.
4. **API:** rotas, geocodificação com cache e testes.
5. **Mapa e busca:** MapLibre estilizado, busca, filtro, lista e "Como chegar".
6. **Animações:** GSAP, Lenis e reduced-motion.
7. **Formulários e Analytics:** Google Forms, GA4 e banner de cookies.
8. **Qualidade:** WAVE, ASES, Lighthouse e testes em celulares reais.
9. **Publicação e divulgação:** deploy, README e divulgação nos grupos de Belém.

## 14. Pendências e riscos

**Pendências**
- Confirmar os 8 pontos de coleta cadastrados em `api/dados/pontos.json` (levantamento em `docs/pesquisa-pontos-de-coleta.md`): todos estão **NÃO CONFIRMADOS** (confiança média ou baixa, sem fonte oficial), com coordenadas aproximadas obtidas pelo Nominatim. Ligar para cada local, conferir endereço, horário e itens aceitos, ajustar as coordenadas no Google Maps e só então preencher `verificado_em`. Procurar também pontos nos localizadores da Abree e da Green Eletron.
- Trocar os números fictícios do Impacto por dados reais, ou tirar a seção até haver dados.
- Nome da instituição e contatos reais no rodapé.
- ~~Criar os dois Google Forms~~: substituídos por modais que gravam pela API (RF08 e RF11).
- Criar uma página curta de política de privacidade e linkar no banner de cookies e no rodapé (boa prática da LGPD).
- Confirmar o nome "ReCircuito".

**Riscos**
- **Dados desatualizados:** pontos fecham ou mudam de horário. Mitigação: campo `verificado_em` e o formulário de sugestão.
- **Hospedagem gratuita lenta na primeira busca:** a API "dorme". Mitigação: indicador de carregamento e lista inicial já embutida no site.
- **Limites do Nominatim:** mitigação com cache e limite de requisições na API.
- **Animações pesadas em celulares simples:** mitigação com loops pausados fora da tela e reduced-motion.
