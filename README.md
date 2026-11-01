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
| `GET /api/tipos` | Tipos de resíduo com nome de exibição |
| `GET /api/saude` | Verificação para a hospedagem |

Para mudar os domínios liberados no CORS, defina as variáveis listadas em `api/.env.example` no ambiente (a API não lê o arquivo `.env` sozinha; na hospedagem, cadastre-as no painel do Render).

### Testes e lint

```bash
cd api
pytest
ruff check .
```
