# ReCircuito

Guia web para o descarte correto de lixo eletrônico em Belém (PA): explica por que o lixo eletrônico não vai no lixo comum, ensina o descarte em 4 passos e encontra o ponto de coleta mais próximo, com filtro por tipo de resíduo.

Projeto de Atividade Extensionista II (UNINTER, Ciência da Computação). A especificação completa está em [SPEC.md](SPEC.md).

> **Atenção:** os pontos em `api/dados/pontos.json` são **fictícios** (`"fonte": "EXEMPLO"`), só para desenvolvimento. O levantamento dos pontos reais ainda está pendente.

## Estrutura

| Pasta | O que tem |
|---|---|
| `web/` | Site em SvelteKit 2 + Svelte 5 (TypeScript), exportado como site estático |
| `api/` | API em FastAPI (Python 3.12+) que lê os pontos de `dados/pontos.json` |
| `docs/` | Diagramas e material do relatório |

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

As fontes (Newsreader e Plus Jakarta Sans) ainda não estão no repositório. Baixe os arquivos `.woff2` e coloque em `web/static/fontes/` com os nomes listados em `web/src/lib/estilos/fontes.css`. Até lá, o site usa fontes reserva.

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

A API sobe em http://localhost:8000. A documentação interativa fica em http://localhost:8000/api/docs.

| Rota | O que faz |
|---|---|
| `GET /api/pontos?lat=&lon=&tipos=&limite=` | Lista os pontos, filtrados por tipo e ordenados por distância (com posição) ou por nome (sem posição) |
| `GET /api/pontos/{id}` | Um ponto; 404 se não existir |
| `GET /api/geocodificar?q=` | Transforma um CEP ou bairro de Belém em coordenada (ver abaixo) |
| `GET /api/tipos` | Tipos de resíduo com nome de exibição |
| `POST /api/sugestoes` | Recebe a sugestão de um ponto de coleta ("Sugerir um ponto") e grava em `dados/sugestoes.json` para revisão |
| `GET /api/saude` | Verificação para a hospedagem |

### Respostas do site

As avaliações e as sugestões de pontos ficam em `api/dados/avaliacoes.json` e `api/dados/sugestoes.json`. Esses arquivos **não vão para o Git** (estão no `.gitignore`): são respostas de pessoas, e o repositório é público. A API cria cada arquivo no primeiro envio.

### Variáveis de ambiente

A API não lê o arquivo `.env` sozinha: defina as variáveis no ambiente (na hospedagem, cadastre-as no painel do Render). A lista completa, com exemplos, está em `api/.env.example`.

| Variável | Para que serve |
|---|---|
| `RECIRCUITO_ORIGENS_PERMITIDAS` | Domínios liberados no CORS, separados por vírgula |
| `RECIRCUITO_ARQUIVO_PONTOS` | Caminho do arquivo de pontos (relativo a `api/`) |
| `RECIRCUITO_CONTATO` | E-mail de contato enviado ao Nominatim no `User-Agent`. A política de uso do Nominatim exige que o projeto se identifique, então **defina um e-mail real em produção** |
| `RECIRCUITO_ARQUIVO_CACHE` | Onde guardar o cache de geocodificação (padrão: `.cache/geocodificacao.json`, relativo a `api/`). No Render gratuito o disco é apagado a cada deploy, então o arquivo ajuda, mas não é garantia |

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
pytest
ruff check .
```
