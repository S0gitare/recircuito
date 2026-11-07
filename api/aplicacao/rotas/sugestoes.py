"""Rota POST /api/sugestoes: alguém indica um ponto de coleta que não está no mapa (RF08).

A sugestão NÃO entra no mapa sozinha. Ela fica guardada em dados/sugestoes.json
para a equipe conferir (o local existe? recebe mesmo esses resíduos?) e, se
confirmada, ser cadastrada à mão em dados/pontos.json.
"""

from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, status

from aplicacao.configuracao import configuracoes
from aplicacao.modelos import NovaSugestao, SugestaoRegistrada
from aplicacao.servicos.registro_json import anexar_registro

roteador = APIRouter(tags=["sugestões"])


def salvar_sugestao(sugestao: NovaSugestao, caminho: Path | None = None) -> SugestaoRegistrada:
    """Grava a sugestão no arquivo JSON e devolve o registro com a data do servidor."""
    destino = caminho if caminho is not None else configuracoes.arquivo_sugestoes
    registro = SugestaoRegistrada(
        **sugestao.model_dump(),
        data=datetime.now(UTC).isoformat(),
    )
    anexar_registro(destino, registro.model_dump(mode="json"))
    return registro


@roteador.post(
    "/sugestoes",
    status_code=status.HTTP_201_CREATED,
    response_model=SugestaoRegistrada,
    summary="Sugerir um ponto de coleta",
    description=(
        "Recebe a indicação de um ponto de coleta que ainda não está no mapa. "
        "A sugestão é revisada pela equipe antes de ser publicada."
    ),
)
def registrar_sugestao(sugestao: NovaSugestao) -> SugestaoRegistrada:
    return salvar_sugestao(sugestao)
