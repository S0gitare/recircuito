"""Ponto de entrada da API. Rode com: uvicorn aplicacao.principal:app --reload"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# O HTTPException do Starlette é a classe-mãe do FastAPI: tratando ele, pegamos
# também os 404 de rotas inexistentes, que o roteador lança direto.
from starlette.exceptions import HTTPException

from aplicacao.configuracao import configuracoes
from aplicacao.rotas import avaliacoes, geocodificacao, pontos, saude, tipos

app = FastAPI(
    title="ReCircuito API",
    description="Pontos de coleta de lixo eletrônico em Belém (PA).",
    version="0.1.0",
    # Documentação interativa em /api/docs, para ficar sob o mesmo prefixo.
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url=None,
)

# Libera GET para consultas e POST para envio de avaliações.
app.add_middleware(
    CORSMiddleware,
    allow_origins=configuracoes.origens_permitidas,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

for modulo in (saude, tipos, pontos, geocodificacao, avaliacoes):
    app.include_router(modulo.roteador, prefix="/api")


# Os dois tratadores abaixo garantem o formato único de erro da SPEC:
# {"erro": "<codigo>", "mensagem": "<texto para a pessoa>"}.
# Sem eles, o FastAPI responde {"detail": ...}, em inglês.

MENSAGENS_PADRAO = {
    404: ("nao_encontrado", "Não encontramos o que você procurou."),
    405: ("metodo_nao_permitido", "Esta operação não é permitida."),
}


@app.exception_handler(HTTPException)
async def tratar_erro_http(_: Request, excecao: HTTPException) -> JSONResponse:
    if isinstance(excecao.detail, dict) and "erro" in excecao.detail:
        corpo = excecao.detail
    else:
        codigo, mensagem = MENSAGENS_PADRAO.get(
            excecao.status_code, ("erro", "Algo deu errado. Tente de novo em instantes.")
        )
        corpo = {"erro": codigo, "mensagem": mensagem}
    return JSONResponse(status_code=excecao.status_code, content=corpo)


@app.exception_handler(RequestValidationError)
async def tratar_erro_de_validacao(_: Request, excecao: RequestValidationError) -> JSONResponse:
    # Parâmetro com formato errado (ex.: lat=abc). Respondemos 400, e não o 422
    # padrão do FastAPI, para seguir o formato de erro do restante da API.
    campos = sorted({str(erro["loc"][-1]) for erro in excecao.errors()})
    return JSONResponse(
        status_code=400,
        content={
            "erro": "parametro_invalido",
            "mensagem": f"Verifique o valor de: {', '.join(campos)}.",
        },
    )
