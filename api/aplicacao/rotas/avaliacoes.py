"""Rota para registrar avaliações dos usuários sobre o site."""

from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, status

from aplicacao.configuracao import configuracoes
from aplicacao.modelos import AvaliacaoRegistrada, NovaAvaliacao
from aplicacao.servicos.registro_json import anexar_registro

roteador = APIRouter(tags=["avaliações"])


def salvar_avaliacao(
    avaliacao: NovaAvaliacao, caminho: Path | None = None
) -> AvaliacaoRegistrada:
    """Grava a avaliação no arquivo JSON e devolve o registro com a data garantida."""
    destino = caminho if caminho is not None else configuracoes.arquivo_avaliacoes
    registro = AvaliacaoRegistrada(
        nota=avaliacao.nota,
        encontrou_ponto=avaliacao.encontrou_ponto,
        comentario=avaliacao.comentario,
        data=avaliacao.data or datetime.now(UTC).isoformat(),
    )
    anexar_registro(destino, registro.model_dump())
    return registro


@roteador.post(
    "/avaliacoes",
    status_code=status.HTTP_201_CREATED,
    response_model=AvaliacaoRegistrada,
    summary="Registrar avaliação",
    description="Recebe uma avaliação do site e a armazena para o relatório do projeto.",
)
def registrar_avaliacao(avaliacao: NovaAvaliacao) -> AvaliacaoRegistrada:
    """Recebe a avaliação validada e a persiste no disco."""
    return salvar_avaliacao(avaliacao)
