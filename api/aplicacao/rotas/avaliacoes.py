"""Rota para registrar avaliações dos usuários sobre o site."""

import json
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, status

from aplicacao.configuracao import configuracoes
from aplicacao.modelos import AvaliacaoRegistrada, NovaAvaliacao

roteador = APIRouter(tags=["avaliações"])
_trava_arquivo = threading.Lock()


def salvar_avaliacao(
    avaliacao: NovaAvaliacao, caminho: Path | None = None
) -> AvaliacaoRegistrada:
    """Grava a avaliação no arquivo JSON com persistência atômica e segura."""
    destino = caminho if caminho is not None else configuracoes.arquivo_avaliacoes
    destino.parent.mkdir(parents=True, exist_ok=True)

    with _trava_arquivo:
        avaliacoes: list[dict] = []
        if destino.exists():
            try:
                with destino.open("r", encoding="utf-8") as f:
                    conteudo = f.read().strip()
                    if conteudo:
                        dados = json.loads(conteudo)
                        if isinstance(dados, list):
                            avaliacoes = dados
            except (json.JSONDecodeError, OSError):
                avaliacoes = []

        registro = AvaliacaoRegistrada(
            nota=avaliacao.nota,
            encontrou_ponto=avaliacao.encontrou_ponto,
            comentario=avaliacao.comentario,
            data=avaliacao.data or datetime.now(UTC).isoformat(),
        )
        avaliacoes.append(registro.model_dump())

        # Gravação atômica via arquivo temporário único no mesmo diretório
        caminho_temporario = destino.with_name(f"{destino.name}.{uuid.uuid4().hex}.tmp")
        try:
            with caminho_temporario.open("w", encoding="utf-8") as f:
                json.dump(avaliacoes, f, ensure_ascii=False, indent=2)
            caminho_temporario.replace(destino)
        finally:
            if caminho_temporario.exists():
                try:
                    caminho_temporario.unlink()
                except OSError:
                    pass

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
