"""Rota GET /api/geocodificar?q= (SPEC §10).

Recebe um CEP ou o nome de um bairro de Belém e devolve a coordenada para o site
centralizar o mapa (RF01). A lógica pesada (ViaCEP, Nominatim, cache) fica em
servicos/geocodificador.py; esta rota só traduz o resultado para HTTP.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from aplicacao.modelos import Localizacao
from aplicacao.servicos.geocodificador import (
    Geocodificador,
    ServicoExternoIndisponivel,
    geocodificador,
)

roteador = APIRouter(tags=["geocodificação"])


def obter_geocodificador() -> Geocodificador:
    """Entrega o geocodificador à rota.

    Dica: ligar a rota por Depends (em vez de importar a instância direto) permite
    que os testes troquem o geocodificador por um falso, sem acessar a internet.
    """
    return geocodificador


@roteador.get("/geocodificar", response_model=Localizacao)
async def geocodificar(
    q: Annotated[str, Query(min_length=2, max_length=100, description="CEP ou bairro de Belém")],
    servico: Annotated[Geocodificador, Depends(obter_geocodificador)],
) -> Localizacao:
    try:
        localizacao = await servico.geocodificar(q)
    except ServicoExternoIndisponivel:
        # 503 = "tente de novo mais tarde": o problema não é da pessoa nem da API.
        raise HTTPException(
            status_code=503,
            detail={
                "erro": "servico_indisponivel",
                "mensagem": (
                    "O serviço de endereços está fora do ar agora. Tente de novo em instantes."
                ),
            },
        ) from None

    if localizacao is None:
        raise HTTPException(
            status_code=404,
            detail={
                "erro": "nao_encontrado",
                "mensagem": "Não encontramos esse CEP ou bairro em Belém. Confira e tente de novo.",
            },
        )
    return localizacao
