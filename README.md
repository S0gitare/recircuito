# ReCircuito

Guia web para o descarte correto de lixo eletrônico em Belém (PA): explica por que o lixo eletrônico não vai no lixo comum, ensina o descarte em 4 passos, mostra os tipos de resíduo aceitos e encontra o ponto de coleta mais próximo, com filtro por tipo de resíduo.

Projeto de Atividade Extensionista II (UNINTER, Ciência da Computação). Publicado em [https://recircuito.info](https://recircuito.info) (e [https://recircuito.vercel.app](https://recircuito.vercel.app)). A especificação completa está em [SPEC.md](SPEC.md).

## Base de dados e cobertura

Os pontos de coleta ficam em [`api/dados/pontos.json`](api/dados/pontos.json) (com levantamento detalhado em [`docs/pesquisa-pontos-de-coleta.md`](docs/pesquisa-pontos-de-coleta.md)):

- **140 pontos mapeados em 32 bairros de Belém** (`ecoponto`, `orgao_publico`, `cooperativa`, `fabricante`, `varejo` e `operadora`).
- **119** confirmados em fontes oficiais em **12/11/2026** (`verificado_em: "2026-11-12"`) e **21** marcados como pendentes de confirmação presencial/telefônica (`verificado_em: null` e aviso `"NÃO CONFIRMADO"` em `observacoes`).
- **126** pontos possuem grade de horários verificada e **14** permanecem com `horarios: []` (exibidos como `"Horário não informado"`).

A seção **`#impacto`** da página inicial exibe métricas reais de cobertura desse mapeamento: **`140`** pontos mapeados, **`32`** bairros atendidos, **`119`** pontos confirmados em fontes oficiais e **`4`** tipos de resíduo eletrônico contemplados (`celulares_tablets`, `pilhas_baterias`, `computadores_perifericos` e `cabos_carregadores`).

## Estrutura

| Pasta / arquivo | O que tem |
|---|---|
| `web/` | Site em SvelteKit 2 + Svelte 5 (TypeScript), exportado como site estático (`adapter-static`), com as rotas `/` e `/privacidade` |
| `api/` | API em FastAPI (Python 3.12+) que lê os 140 pontos de `dados/pontos.json` |
| `docs/` | Pesquisa consolidada dos pontos de coleta e guia de implementação |
| `vercel.json` | Configuração de deploy unificado na Vercel usando **Vercel Services** (`web` + `api`) |

## Hospedagem e deploy (Vercel)

Site e API são publicados de forma unificada na **Vercel** a partir de [`vercel.json`](vercel.json) (**Vercel Services**), sob os domínios **[https://recircuito.info](https://recircuito.info)** e **[https://recircuito.vercel.app](https://recircuito.vercel.app)**:

- **Serviço `web`:** serve o build estático gerado em `web/build/` (incluindo `/` e a rota estática `/privacidade`, entregue via `cleanUrls: true` e `trailingSlash: false` em `vercel.json`) para `/(.*)`.
- **Serviço `api`:** executa a aplicação FastAPI (`api/aplicacao/principal.py`, também exposta em `api/main.py`) para `/api/(.*)`.
- Como ambos respondem sob a mesma origem em produção, o site chama `/api/...` diretamente (sem necessidade de URL externa nem bloqueios de CORS entre domínios).

## Rodar o site (`web/`)

Requer Node.js 20 ou mais novo.

```bash
cd web
npm install
npm run dev
```

O site abre em http://localhost:5173. Para gerar a versão de produção em `web/build/`:

```bash
npm run build
```

As fontes variáveis (**Newsreader** e **Plus Jakarta Sans**) já estão incluídas no repositório em `web/static/fontes/` (`newsreader-variavel.woff2` e `plus-jakarta-sans-variavel.woff2`) e são servidas localmente via `web/src/lib/estilos/fontes.css`, sem requisições externas ao Google Fonts.

Variáveis opcionais do site (exemplos em `web/.env.example`):

- `VITE_URL_DA_API`: endereço da API em desenvolvimento (`http://localhost:8010`). Em produção fica vazia para usar a mesma origem (`/api/...` via rewrite da Vercel).
- `VITE_ID_GOOGLE_ANALYTICS`: ID do Google Analytics 4 (`G-XXXXXXXXXX`), opcional. Quando definido, o carregamento só ocorre após consentimento explícito no banner de cookies (LGPD).

## Rodar a API (`api/`)

Requer Python 3.12 ou mais novo.

**Com [uv](https://docs.astral.sh/uv/):**

```bash
cd api
uv sync
uv run uvicorn aplicacao.principal:app --reload
```

**Com venv:**

```bash
cd api
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn aplicacao.principal:app --reload
```

Por padrão a API sobe em http://localhost:8000 (passe `--port 8010` caso queira alinhar com `VITE_URL_DA_API=http://localhost:8010` de `web/.env.example`). A documentação interativa fica em `/api/docs`.

| Rota | O que faz |
|---|---|
| `GET /api/pontos?lat=&lon=&tipos=&limite=` | Lista os pontos, filtrados por tipo e ordenados por distância (com posição) ou por nome (sem posição) |
| `GET /api/pontos/{id}` | Um ponto; 404 se não existir |
| `GET /api/geocodificar?q=` | Transforma um CEP ou bairro de Belém em coordenada (ver abaixo) |
| `GET /api/tipos` | Tipos de resíduo com nome de exibição |
| `POST /api/sugestoes` | Recebe a sugestão de um ponto de coleta ("Sugerir um ponto") e grava em `dados/sugestoes.json` para revisão |
| `POST /api/avaliacoes` | Recebe a avaliação do site (`nota` e `encontrou_ponto`, além de `comentario` e `data` opcionais) enviada pelo modal "Avaliar o site" e grava em `dados/avaliacoes.json` (`201 Created`) |
| `GET /api/saude` | Verificação de saúde para a hospedagem (Vercel) e monitoramento |

### Respostas do site

Localmente, as avaliações e as sugestões de pontos ficam em `api/dados/avaliacoes.json` e `api/dados/sugestoes.json`. Esses arquivos **não vão para o Git** (estão no `.gitignore`): são respostas de pessoas, e o repositório é público. A API cria cada arquivo no primeiro envio. No ambiente serverless da Vercel, onde a pasta do código é somente leitura, os envios usam `/tmp/recircuito/` como reserva efêmera.

### Variáveis de ambiente

A API não lê o arquivo `.env` sozinha: defina as variáveis no ambiente (em produção, cadastre-as em **Settings → Environment Variables** no projeto da Vercel). As principais variáveis, com exemplos, estão em `api/.env.example` (a API também aceita `RECIRCUITO_ARQUIVO_AVALIACOES` e `RECIRCUITO_ARQUIVO_SUGESTOES` para sobrescrever os caminhos em `api/dados/`).

| Variável | Para que serve |
|---|---|
| `RECIRCUITO_ORIGENS_PERMITIDAS` | Domínios liberados no CORS, separados por vírgula (em produção com `vercel.json`, site e API compartilham a mesma origem) |
| `RECIRCUITO_ARQUIVO_PONTOS` | Caminho do arquivo de pontos (relativo a `api/`) |
| `RECIRCUITO_CONTATO` | E-mail de contato enviado ao Nominatim no `User-Agent`. A política de uso do Nominatim exige que o projeto se identifique, então **defina um e-mail real em produção** |
| `RECIRCUITO_ARQUIVO_CACHE` | Onde guardar o cache de geocodificação (padrão: `.cache/geocodificacao.json`, relativo a `api/`). Em ambiente serverless na Vercel, o diretório da aplicação é somente leitura e `/tmp` é efêmero entre instâncias e deploys, então o cache atua prioritariamente em memória |

### Geocodificação: `GET /api/geocodificar?q=`

Recebe um CEP (com ou sem hífen) ou o nome de um bairro e devolve a coordenada para o site centralizar o mapa:

- **CEP:** a API consulta o [ViaCEP](https://viacep.com.br) para descobrir o endereço e depois o [Nominatim](https://nominatim.org) (OpenStreetMap) para achar a coordenada. CEP de outra cidade é tratado como não encontrado.
- **Texto:** vai direto ao Nominatim, limitado à área de Belém.
- O resultado fica em cache por 30 dias, e a API faz no máximo 1 chamada por segundo ao Nominatim.
- `q` deve ter de 2 a 100 caracteres.

```bash
curl "http://localhost:8000/api/geocodificar?q=66035-000"
```

```json
{ "lat": -1.4521, "lon": -48.488, "rotulo": "Nazaré, Belém - PA", "fonte": "viacep+nominatim" }
```

Erros seguem o formato `{ "erro": "<codigo>", "mensagem": "<texto>" }`:

| Status | `erro` | Quando |
|---|---|---|
| 400 | `parametro_invalido` | `q` ausente ou fora do tamanho permitido |
| 404 | `nao_encontrado` | CEP ou bairro não encontrado em Belém |
| 503 | `servico_indisponivel` | ViaCEP ou Nominatim fora do ar ou com resposta inesperada |

### Testes e lint

```bash
cd api
.venv/bin/pytest -v
.venv/bin/ruff check .
```
