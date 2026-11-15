# Guia de implementação do site

Complemento da `SPEC.md`: medidas do protótipo (FigCraft), geometria dos desenhos e contratos entre as peças, para várias sessões trabalharem em paralelo sem esbarrar. Se este guia e a SPEC divergirem, vale a SPEC.

## 0. Regras gerais (valem para todas as sessões)

- **Tudo em português do Brasil**: identificadores, comentários, README, testes, mensagens. Comentários explicam o *porquê* e dão dicas para quem está aprendendo (ver SPEC §11). Exceções só para nomes impostos (`+page.svelte`, `package.json`, `gsap.to({ duration })`…).
- **Não rode `git add/commit/push`.** As mudanças ficam no working tree, para revisão depois.
- **Cada sessão mexe só nos seus arquivos** (listados na sua tarefa). Não edite arquivo de outra sessão. Se faltar algo de outra peça, escreva contra o contrato da seção 1 e siga.
- Svelte 5 com runes (`$state`, `$derived`, `$props`, `$effect`) e TypeScript. CSS com escopo no componente; cores sempre pelos tokens de `src/lib/estilos/tokens.css` (só **acrescente** linhas ao final dele, nunca reescreva).
- Textos visíveis vêm de `src/lib/conteudo/textos.ts` (não escreva texto de interface solto nos componentes). Variáveis de ambiente por `src/lib/configuracao.ts`.
- Breakpoint: **mobile < 768px**, desktop ≥ 768px. Referências do protótipo: 1440px e 390px. Margem lateral: `var(--margem-lateral)`.
- Ícones: nada de caractere de seta (→) nem emoji. Use SVG inline. Seta (Phosphor arrow-right): `viewBox="0 0 256 256"`, `fill="currentColor"`, path `M221.66,133.66l-72,72a8,8,0,0,1-11.32-11.32L196.69,136H40a8,8,0,0,1,0-16H196.69L138.34,61.66a8,8,0,0,1,11.32-11.32l72,72A8,8,0,0,1,221.66,133.66Z`.
- Acessibilidade (RNF01): foco visível, alvos de toque ≥ 44px, `aria-label` nos botões de ícone, desenhos com `role="img"` + texto alternativo (ou `aria-hidden="true"` se decorativos), contraste AA.
- Verificação: `cd web && npm run check` (svelte-check) e `npm run build`. O servidor de desenvolvimento do site e a API sobem pelo `preview_start` com os nomes `site` (porta 5173) e `api` (porta 8010), definidos em `../.claude/launch.json` (na pasta acima de `recircuito/`). O site lê a API em `http://localhost:8010` (`web/.env`).

## 1. Contratos entre as peças

**`$lib/animacao/` (dona: sessão de ilustrações e animações).** Os arquivos `lenis.ts`, `revelar.ts` e `contador.ts` hoje são stubs com a assinatura final:
- `iniciarLenis(): () => void` liga a rolagem suave (GSAP ticker + ScrollTrigger) com `virtualScroll: ({ event }) => !event.defaultPrevented` (isolando o scroll de contêineres com `data-lenis-prevent`, como o mapa) e devolve a função que desliga. Com movimento reduzido, não liga nada.
- `rolarPara(alvo: string): void` rola até uma âncora (`'#sobre'`); com Lenis, `lenis.scrollTo`; senão `scrollIntoView`.
- `revelar` é uma *action* Svelte: `<h2 use:revelar>` ou `use:revelar={{ atraso: 0.1 }}`. Sobe 16px enquanto aparece, uma vez, ao entrar na tela (0,6s).
- `contarAte` é uma *action*: `<span use:contarAte={{ valor: 140 }}></span>`. Escreve o número formatado em pt-BR e conta de 0 até o valor (1,2s, uma vez, ao entrar na tela).
- `prefereMovimentoReduzido(): boolean` já está pronto em `movimentoReduzido.ts`.

**`$lib/ilustracoes/` (dona: sessão de ilustrações).** Componentes **sem props obrigatórias** que já se animam sozinhos (`onMount`, só quando visíveis, parando fora da tela, respeitando movimento reduzido): `CelularExplodido`, `PassoSepare`, `PassoApague`, `PassoPonto`, `PassoEntregue`, `ItemCelulares`, `ItemPilhas`, `ItemComputadores`, `ItemCabos`. Todos aceitam a prop opcional `titulo?: string` (texto alternativo; há um padrão).
- `CelularExplodido` desenha o bloco inteiro do topo: pilha de camadas + linhas-guia + chamadas + rótulos (HTML), com os textos de `textos.hero.camadas`. Os rótulos e chamadas somem no mobile.
- Os desenhos dos passos têm 300×300 (viewBox `0 0 300 300`) e os dos itens 386×260 (viewBox `0 0 386 260`); o tamanho final na tela é decidido por CSS de quem os usa (`width: 100%; height: auto`).

**`$lib/configuracao.ts`** (pronto): `urlDaApi`, `urlFormularioSugestao`, `urlFormularioAvaliacao`, `idGoogleAnalytics`.

**Ícones compartilhados:** a sessão das seções estáticas cria `IconeSeta.svelte` (e `IconeMenu`, `IconeFechar`); a sessão de pontos de coleta cria `IconeLupa.svelte` e `IconeMira.svelte`. Cada uma só usa os seus.

## 2. Medidas do protótipo por seção

Fontes: **Newsreader** (`var(--font-leitura)`) = lido; **Plus Jakarta Sans** (`var(--font-interface)`, "PJS") = usado. Newsreader Medium = `font-weight: 500`. Cores pelos tokens (`--ink`, `--ink-2`, `--muted`, `--line`, `--line-soft`, `--green`, `--green-strong`, `--bg-*`, `--footer`).

**Topo (hero), fundo `--bg-hero`, altura mínima `100svh`.**
- Desktop: cabeçalho com logo (`/logos/logo-simbolo-no-c-site.svg`, 26px de altura; em versão antiga do guia era o símbolo ao lado do nome) à esquerda e links à direita (PJS Medium 16px, `--ink`, espaçamento 48px), top ≈ 32px. Arte centralizada (1212×491, ver seção 3). Embaixo: título Newsreader Medium 100px/96px, `letter-spacing: -0.025em`, duas linhas ("Seu lixo eletrônico" / "tem destino.") à esquerda (margem 48); à direita (coluna de 392px, alinhada à base do título) o texto de apoio (Newsreader 20px/27px, `--ink-2`) e, 20px abaixo, o botão: 300×52, fundo `--green-strong`, texto branco PJS SemiBold 17px com seta de 20px à direita (gap 10).
- Mobile: cabeçalho com logo (28px de altura) e botão ☰ (44×44, traço de 2px `--ink`); arte ≈ 257×324 centralizada; título 50px/50px; texto 18px/26px; botão 52px de altura em largura total; paddings de 20px e espaços de 24px.

**O projeto (`#sobre`), fundo `--bg-alt`.** Desktop: duas colunas: frase (Newsreader Medium 46px/54px, `-0.015em`, máx. 780px) e, à direita, parágrafo de 392px (Newsreader 20px/28px, `--ink-2`); padding vertical ≈ 120px. Mobile: empilhado; frase 30px/36px, parágrafo 18px/27px; padding 56px 20px.

**Como descartar (`#como-descartar`), fundo `--bg`.** Cabeçalho: título Newsreader Medium 56px/62px (`-0.02em`) + parágrafo à direita (392px, 20px/28px, `--ink-2`). Abaixo (margem ≈ 64px), 4 colunas iguais; cada coluna tem borda esquerda 1px `--line-soft` (menos a primeira). Em cada uma: faixa `--green` de 72px de altura com largura `calc(100% - 66px)`, nome em Newsreader Medium 26px branco (padding-left 24); o número ("01"…) em PJS Medium 16px `--muted`, na área livre à direita da faixa; ilustração 300×300 centralizada (48px abaixo da faixa); descrição Newsreader 17px/25px `--muted` com padding lateral de 24px. Mobile: passos empilhados (gap 32px); faixa em largura total (padding 14px 16px, nome 24px, número PJS 14px cor `#DFF3E5` dentro da faixa, à direita); ilustração reduzida a ≈ 210×210 centralizada; descrição centralizada.

**O que descartar (`#o-que-descartar`), fundo `--bg-alt`.** Título centralizado Newsreader Medium 72px/76px (`-0.02em`); parágrafo centralizado (máx. 560px, 20px/28px, `--ink-2`, 24px abaixo); grade 2×2 (≈ 80px abaixo) com linhas finas **só internas** (1px `--line`: borda direita nas células da esquerda, borda inferior nas de cima). Célula: padding 48px 48px 56px, conteúdo centralizado; ilustração 386×260; nome Newsreader Medium 28px (12px abaixo); descrição Newsreader 18px `--muted`. Mobile: mesma grade 2×2; célula com padding 24px 6px; ilustração ≈ 162×109; nome 19px/23px; descrição 15px/20px; título 38px/42px.

**Pontos de coleta (`#pontos-de-coleta`), fundo `--bg`.** Desktop: duas colunas: esquerda 460px, mapa à direita (832×570, borda 1px `--line-soft`), gap ≈ 52px, padding vertical ≈ 100px. Coluna esquerda, de cima para baixo: título (Newsreader Medium 52px/56px, `-0.02em`); campo de busca (48px abaixo; altura 56px, borda 1px `--line`, fundo branco, cantos retos, ícone de lupa à esquerda, placeholder PJS 16px `--muted`; o botão da lupa envia a busca); "Usar minha localização" (12px abaixo; PJS SemiBold 14px `--green`, ícone de mira de 18px, sem sublinhado); filtro (16px abaixo): grade de **6 colunas**, gap 8px, linhas de 36px: "Todos" (2 colunas), "Cabos" (2), "Pilhas" (2) na 1ª linha; "Computadores" (3), "Celulares" (3) na 2ª; chip PJS Medium 14px centralizado, borda 1px `--line`, fundo branco; selecionado: fundo e borda `--ink`, texto branco (`aria-pressed`); lista (24px abaixo): contida em janela de rolagem vertical própria (`max-height: 380px`, `overflow-x: hidden`, `overflow-y: auto`, `overscroll-behavior: contain` e `data-lenis-prevent`, exibindo ~2,5 a 3 itens com corte no último como affordance, bordas superior e inferior em 1px solid `--line-soft`, padding-right 10px e scrollbar fina nos tokens `--line` e `--ink-2`; ao clicar em um pino no mapa, a lista rola suavemente por dentro até exibir o ponto); item com padding 20px 4px, borda inferior 1px `--line-soft` (exceto o último `li:last-child` para não duplicar traço com o contêiner), bolinha de 12px à esquerda (verde `--green` para o selecionado; `#A3AFA7` para os outros), nome PJS SemiBold 17px, endereço PJS 15px `--muted`, status ("Aberto agora" em `--green`, "Fechado agora" em `--muted`) e tipos aceitos em PJS 14px, link "Como chegar" PJS SemiBold 14px `--green` sublinhado, distância à direita (PJS SemiBold 15px, `--green` no 1º/selecionado, `--muted` nos demais); por fim "Conhece um ponto que não está aqui? **Sugerir um ponto**" (PJS 15px `--muted`, link SemiBold `--green` sublinhado, posicionado sempre fixo fora da caixa de rolagem). Mobile: coluna única na ordem título, busca, localização, filtro, **mapa (≈ 240px de altura)**, lista, sugerir; título 34px/38px.

**Impacto (`#impacto`), fundo `--bg-alt`.** Título Newsreader Medium 44px/50px (mobile 32px/36px); 4 colunas (≈ 64px abaixo) com borda esquerda 1px `--line` (menos a 1ª) e padding-left 32px; número Newsreader Medium 64px (`-0.02em`, mobile 44px); rótulo PJS 15px `--muted` (mobile 14px). Mobile: grade 2×2, gap 20px/24px, cada item com borda superior 1px `--line` e padding-top 14px, sem borda esquerda.

**Rodapé, fundo `--footer`.** Desktop (padding 64px 48px 32px): à esquerda logo escuro (`/logos/logo-simbolo-no-c-escuro-site.svg`, 26px) e frase (Newsreader 17px, `#A9C7B4`); à direita duas colunas (Navegação e Contato) com cabeçalho PJS SemiBold 15px branco e itens PJS 15px `#DFF3E5` com `line-height: 30px`; em Contato, o link "Avaliar o site" (SemiBold, sublinhado, `--green-dark-mode`); linha divisória 1px `rgba(255,255,255,.12)`; créditos PJS 13px `#7E9C89`. Mobile: tudo empilhado; as duas colunas lado a lado (gap 40px).

**Banner de cookies.** `role="region"` com `aria-label` de `textos.bannerCookies.rotuloDaRegiao`. Desktop: fixo no canto inferior esquerdo (24px das bordas), largura 520px, fundo branco, borda 1px `--line`, padding 24px, gap 12px; título Newsreader Medium 22px; texto PJS 15px/22px `--ink`; dois botões **de mesmo tamanho e mesma cor** (altura 44px, `--green-strong`, texto branco PJS SemiBold 15px), "Recusar" e "Aceitar". Mobile: barra fixa na base, largura total (padding 20px 20px 24px). Só aparece na primeira visita (escolha guardada em `localStorage`); não prende o foco; fica no início da ordem de tabulação (primeiro filho do `<body>`/layout).

**Menu mobile.** `<dialog>` em tela cheia (fundo `--bg-hero`): linha com logo e botão X (44×44); links em Newsreader Medium 34px, cada um com borda inferior 1px `--line` e padding 18px 0; botão "Ver pontos de coleta" na base (52px, `--green-strong`, com seta). Fecha no X, no Esc e ao escolher um link (que então rola até a âncora).

**Modal de avaliação (`ModalAvaliacao.svelte`).** `<dialog>` nativo acionado pelo link "Avaliar o site" do rodapé. Fundo escurecido (backdrop) com fade in suave (`opacity: 0 -> 1`, ~220ms, `cubic-bezier(0.16, 1, 0.3, 1)`). O cartão do diálogo surge com leve zoom (escala `0.96 -> 1.0`), subida sutil de 8px (`translateY(8px) -> translateY(0)`) e fade in (220ms). Ao fechar (no "X", em "Cancelar", fora do modal, tecla Esc ou no botão "Fechar" do sucesso), executa animação de saída: o cartão desce 6px (`translateY(0) -> translateY(6px)`), reduz escala (`1.0 -> 0.97`) e faz fade out em ~180ms (`ease-in`), enquanto o backdrop desvanece (`opacity: 1 -> 0`), aguardando o término antes de chamar `elementoDialog.close()`. No envio (`enviando = true`), o botão exibe spinner SVG (16×16, traço 2px, rotação contínua linear 0,8s) ao lado de "Enviando...", preservando largura mínima estável (`min-width: 180px`, mobile `170px`) para eliminar qualquer layout shift. Na confirmação de sucesso, ocorre crossfade: o formulário esmaece suavemente (160ms) e dá lugar ao bloco de confirmação que surge com fade in e leve subida (200ms) acompanhado de ícone SVG de confirmação/check verde discreto em traço 2px com micro-revelação suave. Com movimento reduzido (RNF02), as animações de deslocamento, rotação e escala são anuladas, aplicando transição instantânea ou fade direto.

## 3. Geometria dos desenhos (SVG)

Regras: traço `--ink` de 2px (`stroke-linecap/linejoin: round`), no máximo um detalhe `--green` por desenho, sem sombras nem gradientes. Raios como `rx`. Onde diz "fundo", use `var(--bg-alt)` nos itens (fundo da seção) e branco nos passos (fundo `--bg`).

### CelularExplodido (5 camadas)

Bloco de **1212×491**. A pilha é um `<svg viewBox="0 0 390 491">` posicionado em `left: 36.39%` (441/1212), largura `32.18%`. Cada camada é um `<g>` que se desloca no eixo Y; ordem no DOM de baixo para cima: **Carcaça, Placa, Bateria, Tela, Vidro** (Vidro por cima). Todas têm:
- espessura: `M0 150 L130 225 L390 75 L390 85 L130 235 L0 160 Z`, preenchimento `#CFE3D5`, traço 2px;
- forma: `M260 0 L390 75 L130 225 L0 150 Z`, preenchimento branco, traço 2px.

Detalhes por camada (coordenadas no espaço da camada):
- **Vidro:** ilha (verde) `M297.3 33.5 L332 53.5 L326.8 56.5 L292.1 36.5 Z`; rachadura `M286 75 L225.4 90 L216.7 125 L129.9 135 M225.4 90 L180.3 77.5` (sem preenchimento, traço 1.5).
- **Tela:** display `M260 10 L372.6 75 L130.2 215 L17.5 150 Z` (sem preenchimento, traço 1).
- **Bateria:** célula (verde, traço 1.5) `M229.7 42.5 L316.3 92.5 L160.4 182.5 L73.9 132.5 Z`.
- **Placa:** chip (verde, traço 1.5) `M147.4 155 L190.7 180 L147.4 205 L104.1 180 Z`; trilhas `M190.7 180 L250 146 L280 150 M104.1 180 L70 160 M169 192.5 L190 205` (traço 1.5); conector `M34.8 145 L60.8 160 L43.5 170 L17.3 155 Z` (sem preenchimento, traço 1.5).
- **Carcaça:** câmera `M78.1 125 L112.8 145 L60.8 175 L26 155 Z` (sem preenchimento, traço 1.5); lente (verde) `M69.3 144 L79.7 150 L69.3 156 L58.9 150 Z`.

Posição Y de cada camada (índice i: Vidro 0, Tela 1, Bateria 2, Placa 3, Carcaça 4): **montado** `100 + 14·i`; **explodido** `64·i`. Linhas-guia tracejadas (cor `#9DBFA8`, 1px, `stroke-dasharray: 4 4`), visíveis só no explodido: `x=0` de y=150 até 406; `x=390` de y=75 até 331; `x=130` de y=225 até 481.

Chamadas e rótulos (somente desktop; coordenadas no bloco de 1212×491; use porcentagens para posicionar os rótulos em HTML):
- Direita: linha de x=837 a x=957, traço 1px `--ink`, bolinha de 7px em x≈957; rótulos com `left: 972px`, largura 240px, topo = y da linha − 11. Linhas em y: **Vidro 75, Bateria 203, Carcaça 331**. Bolinha de Bateria em `--green`; as outras `--ink`.
- Esquerda: linha de x=315 a x=435, bolinha de 7px em x≈314.5; rótulos alinhados à direita, caixa de x=0 a x=300. Linhas em y: **Tela 214, Placa 342**. Bolinha de Placa `--green`.
- Rótulo: duas linhas, nome (PJS SemiBold 15px `--ink`) e destino (PJS Regular 14px `--ink-2`), `line-height: 24px`.

Animação: ao carregar no topo da página (`window.scrollY <= 5`), ocorre uma **cascata de entrada do topo** (~1,35s no total, `power2.out`), na qual os elementos da seção Hero descem suavemente: cabeçalho em 0s (`y: -32 -> 0`), seguido pelas 5 camadas caindo uma a uma de cima (`y: -300 -> yMontado(i)`) em ordem construtiva da base ao topo (Carcaça `i=4`, Placa `i=3`, Bateria `i=2`, Tela `i=1` e Vidro `i=0`, com stagger de 0,12s e duração de 0,45s), até montar o celular (guias, chamadas e rótulos ocultos); em seguida, o título `h1` (0,70s, `y: -24 -> 0`) e o bloco de apoio com texto e botão (0,85s, `y: -20 -> 0`) aterrissam. Ao rolar a página para baixo, a seção Hero fica fixada na tela (`pin: true`, gatilho no `<header class="hero">`, `start: 'top top'`, `end: '+=100%'`, `scrub: 0.6`); de 0% a 80% do scroll, as camadas separam de `yMontado` para `yExplodido`, guias pontilhadas surgem e, no desktop, as linhas de chamada se desenham com DrawSVG, as bolinhas surgem e os rótulos entram; de 80% a 100% do scroll, há uma pausa para leitura com o celular totalmente explodido e estável antes de desfixar o Hero. Se o usuário rolar enquanto a cascata de entrada ainda estiver rodando, ela é imediatamente interrompida (`kill()`), posicionando todos os elementos no estado montado e visível e transferindo o controle ao ScrollTrigger. Com movimento reduzido (RNF02): sem pin/animações, exibindo o estado explodido estático final.

### PassoSepare (300×300)
Itens, em repouso: celular `<rect x=84 y=66 width=46 height=84 rx=9>` girado −12° (em torno do centro); bobina `<circle cx=148 cy=104 r=20>` + miolo `<circle cx=148 cy=104 r=9>` (traço 1.5); pilha `<rect x=180 y=86 width=28 height=62 rx=6>` girada 10°. Todos sem preenchimento. Caixa `<rect x=75 y=140 width=150 height=96>` com **preenchimento branco** (cobre a base dos itens) e abas `M75 140 L53 114 M225 140 L247 114`; seta `M150 172 V204 M138 192 L150 204 L162 192`. Ordem: itens, caixa, abas, seta.
Animação (loop): itens começam 60px acima e a seta com opacidade 0; caem para a posição de repouso em 0,9s (`power2.in`) e a seta aparece; pausa de 1,8s; reinicia (fade de 0,3s).

### PassoApague (300×300)
Celular `<rect x=95 y=45 width=110 height=210 rx=18>`; ilha `<rect x=135 y=58 width=30 height=4 rx=2>` (verde, sem traço); ícone restaurar `M172 118 A22 22 0 1 1 165.6 102.4 M165.6 102.4 L166 93 M165.6 102.4 L156 103` (traço 2, sem preenchimento); barra de 12 quadrados 10×10 em 2 linhas × 6 colunas, passo de 14px, origem (110,178), traço 1.5 sem preenchimento; sobre ela os mesmos 12 quadrados **preenchidos de verde**, dentro de um recorte retangular `x=110 y=178 height=24` cuja largura anima.
Animação (loop): largura do recorte de 0 a 80 em 1,8s (`none`); pausa 0,9s; zera (0,2s).

### PassoPonto (300×300)
Círculos centrados em (150,150): raio 110 (traço `#9DBFA8` 1px), 80 (traço 2), 40 (traço 1.5, sem preenchimento); centro `r=12` preenchido de verde; pontos `r=7` (preenchimento branco, traço 2 `--ink`) em (219,190) e (81,190); ponto `r=7` verde (preenchimento e traço verdes) em (150,70). Pulso: círculo `r=12` (traço verde 2, sem preenchimento) em (150,150).
Animação (loop): o pulso vai de `r=12` a `r=110` com opacidade 1→0 em 1,6s (`power2.out`), atraso 0,2s; reinicia instantâneo.

### PassoEntregue (300×300)
Lixeira (traço 2): `M90 70 H210 M100 70 L110 210 H190 L200 70 M135 70 V56 H165 V70 M135 100 V185 M150 100 V185 M165 100 V185`. Fileira de 9 pontos `r=6` com centros em x = 70 + 20·i (i = 0…8), y = 244; pontos acesos = verde, apagados = vazados (traço 1.5 `--ink`).
Animação (loop, "esteira"): acesos quando `(i − t) mod 3 == 0`, com t = 0, 1, 2 mudando a cada 0,3s; pausa de 0,5s entre voltas. Estado estático (movimento reduzido): t = 0.

### ItemCelulares (386×260)
Corpo `<rect x=143 y=30 width=100 height=200 rx=20>` (sem preenchimento); ilha `<rect x=178 y=44 width=30 height=6 rx=3>` verde; tablet `<rect x=96 y=80 width=120 height=150 rx=12>` com preenchimento `var(--bg-alt)`; câmera do tablet `<circle cx=155 cy=92 r=4>` (traço 1.5). Animação (loop, 1,4s, `sine.inOut`, yoyo): corpo + ilha sobem 12px; tablet + câmera descem 8px.

### ItemPilhas (386×260)
Pilha 1: polo `<rect x=159 y=40 width=16 height=10>` (`--ink` cheio), corpo `<rect x=147 y=48 width=40 height=170 rx=8>`, faixa verde `<rect x=148 y=90 width=38 height=18>`. Pilha 2: polo `<rect x=213 y=70 width=16 height=10>` cheio, corpo `<rect x=201 y=78 width=40 height=140 rx=8>`, "+" `M221 130 V146 M213 138 H229` (traço 2). Animação (loop, 1,4s, yoyo): pilha 1 (com polo e faixa) sobe 10px; pilha 2 (com polo e "+") desce 6px.

### ItemComputadores (386×260)
Tela `<rect x=78 y=40 width=230 height=150 rx=10>`; display `<rect x=90 y=52 width=206 height=126 rx=3>` (traço 1); base `M58 190 H328 L314 206 H72 Z` (traço 2, sem preenchimento); mouse `<rect x=300 y=168 width=26 height=40 rx=13>` com preenchimento `var(--bg-alt)`; rodinha `<rect x=311 y=176 width=4 height=8 rx=2>` verde. Animação (loop, 0,7s, yoyo): a rodinha desce 14px.

### ItemCabos (386×260)
Fio `M60 216 C120 106 180 266 230 176 S310 76 265 66` (traço 2, sem preenchimento); fonte `<rect x=230 y=34 width=70 height=82 rx=12>` com preenchimento `var(--bg-alt)`; pinos `M252 14 V34 M278 14 V34` (traço 2); LED `<circle cx=265 cy=75 r=6>` verde; ponta do fio `<circle cx=60 cy=216 r=7>` (preenchimento `var(--bg-alt)`, traço 2). Animação (loop, 0,5s, yoyo): LED com opacidade 1 → 0,15.

## 4. Mapa (MapLibre + OpenFreeMap)

- Estilo base: `https://tiles.openfreemap.org/styles/positron` (JSON). Busque o JSON em tempo de execução, **modifique as camadas em código** (função `estilizarMapa(estilo)`) e passe o objeto ao `new maplibregl.Map({ style })`. Importe o `maplibre-gl` dinamicamente dentro do `onMount` (não funciona no build/SSR) e o CSS `maplibre-gl/dist/maplibre-gl.css`.
- Ids das camadas do estilo: `background`, `park`, `water`, `landcover_ice_shelf`, `landcover_glacier`, `landuse_residential`, `landcover_wood`, `waterway`, `building`, `tunnel_motorway_casing/inner`, `aeroway-*`, `road_area_pier`, `road_pier`, `highway_path`, `highway_minor`, `highway_major_casing/inner/subtle`, `highway_motorway_casing/inner/subtle`, `railway*`, `highway_motorway_bridge_casing/inner`, `boundary_*`, rótulos (`waterway_line_label`, `water_name_*`, `highway-name-path/minor/major`, `highway-shield-*`, `road_shield_us`, `airport`, `label_other`, `label_village`, `label_town`, `label_state`, `label_city*`, `label_country_*`); fontes: `ne2_shaded` (raster) e `openmaptiles` (vetorial).
- Visual (SPEC §6): fundo `#FFFFFF`; esconder raster `ne2_shaded`, `building`, `landcover_*`, `landuse_residential`, `aeroway-*`, `boundary_*`, `railway*`, escudos de rodovia; `park` sem preenchimento com contorno `#9DBFA8`; `water` preenchida com `--bg-hero` (`#E8F1EA`) e `waterway` em linha `#9DBFA8` (1.5px); ruas: `highway_minor` `#EEF2EF` 1px, `highway_major_inner` `#DCE3DD` 2px, `highway_motorway_inner` `#C9D3CC` 2.5px; casings invisíveis; rótulos (`highway-name-*`, `label_other`, `label_village`, `label_town`, `label_city`) em `#5B6B61` com halo branco, tamanhos pequenos (10–12px); manter as fontes de texto do estilo.
- Marcadores: botões HTML (`<button>` com `aria-label` = nome do ponto): círculo de 22px, preenchimento branco, borda 2px `--ink`; o **selecionado**: círculo de 28px preenchido de `--green` + anel pulsando (traço `--green` 1.5px, cresce de 28px a 108px e some, 1,6s, em loop). Balão: caixa branca, borda 1px `--line`, cantos retos, sem sombra, com o nome (PJS SemiBold 14px) e "Aberto agora" ou "Fechado agora" (PJS 12px, com bolinha verde se aberto).
- Mapa inicial: centro (−1.4558, −48.4902), zoom ≈ 11.5, limites `[[-48.75, -1.65], [-48.25, -1.05]]`; sem busca, ajustar para mostrar todos os pontos. Mantenha o crédito "© OpenStreetMap" (controle de atribuição compacto, discreto). Sem WebGL: mostrar uma mensagem em vez do mapa (a lista continua funcionando).
