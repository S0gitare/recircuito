"""Rotas de pontos de coleta: GET /api/pontos e GET /api/pontos/{id} (SPEC §10)."""

import json
from functools import lru_cache
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from aplicacao.configuracao import configuracoes
from aplicacao.modelos import PontoDeColeta, PontoNaResposta, RespostaPontos, TipoResiduo
from aplicacao.servicos.distancia import calcular_distancia_km
from aplicacao.servicos.horarios import esta_aberto_agora

roteador = APIRouter(tags=["pontos"])


@lru_cache(maxsize=1)
def carregar_pontos(caminho: Path = configuracoes.arquivo_pontos) -> tuple[PontoDeColeta, ...]:
    """Lê e valida o pontos.json uma única vez.

    O lru_cache guarda o resultado na memória: o arquivo só muda com um novo
    deploy (SPEC §2), então não há por que relê-lo a cada requisição.
    Dica: nos testes, chame carregar_pontos.cache_clear() para recarregar.
    """
    with caminho.open(encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    return tuple(PontoDeColeta.model_validate(item) for item in dados)


def _aberto_agora(ponto: PontoDeColeta) -> bool | None:
    """True/False pelo horário do ponto; None quando o horário não é conhecido.

    Sem faixas cadastradas, esta_aberto_agora() devolveria False, e o site
    mostraria "Fechado agora" para quem só não tem horário informado.
    """
    if not ponto.horarios:
        return None
    return esta_aberto_agora(ponto.horarios)


def _ler_tipos(texto: str | None) -> set[TipoResiduo]:
    """Converte "pilhas_baterias,cabos_carregadores" em um conjunto de tipos."""
    if not texto:
        return set()
    tipos: set[TipoResiduo] = set()
    for codigo in (parte.strip() for parte in texto.split(",")):
        if not codigo:
            continue
        try:
            tipos.add(TipoResiduo(codigo))
        except ValueError:
            validos = ", ".join(tipo.value for tipo in TipoResiduo)
            raise HTTPException(
                status_code=400,
                detail={
                    "erro": "tipo_invalido",
                    "mensagem": f"O tipo “{codigo}” não existe. Use: {validos}.",
                },
            ) from None
    return tipos


@roteador.get("/pontos", response_model=RespostaPontos, response_model_exclude_none=False)
def listar_pontos(
    lat: Annotated[float | None, Query(ge=-90, le=90)] = None,
    lon: Annotated[float | None, Query(ge=-180, le=180)] = None,
    tipos: Annotated[str | None, Query(description="Tipos separados por vírgula")] = None,
    limite: Annotated[int | None, Query(ge=1)] = None,
) -> RespostaPontos:
    """Lista os pontos, filtrados por tipo e ordenados.

    - Com lat e lon: ordem por distância, com `distancia_km` preenchida.
    - Sem posição: ordem alfabética (RF03).
    - Com tipos: só os pontos que aceitam pelo menos um dos tipos marcados (RF04).

    `total` é o número de pontos encontrados antes de aplicar o `limite`, para
    o site poder dizer "mostrando 5 de 12".
    """
    if (lat is None) != (lon is None):
        raise HTTPException(
            status_code=400,
            detail={
                "erro": "posicao_incompleta",
                "mensagem": "Informe a latitude e a longitude juntas.",
            },
        )

    tipos_pedidos = _ler_tipos(tipos)
    pontos = [
        ponto
        for ponto in carregar_pontos()
        if not tipos_pedidos or tipos_pedidos.intersection(ponto.tipos_aceitos)
    ]

    resposta: list[PontoNaResposta] = []
    for ponto in pontos:
        distancia = None
        if lat is not None and lon is not None:
            distancia = round(
                calcular_distancia_km(lat, lon, ponto.coordenadas.lat, ponto.coordenadas.lon), 2
            )
        resposta.append(
            PontoNaResposta(
                **ponto.model_dump(),
                distancia_km=distancia,
                aberto_agora=_aberto_agora(ponto),
            )
        )

    if lat is not None:
        resposta.sort(key=lambda p: p.distancia_km or 0.0)
    else:
        # casefold() compara sem diferenciar maiúsculas, inclusive em acentos.
        resposta.sort(key=lambda p: p.nome.casefold())

    total = len(resposta)
    if limite is not None:
        resposta = resposta[:limite]
    return RespostaPontos(pontos=resposta, total=total)


@roteador.get("/pontos/{id_ponto}", response_model=PontoNaResposta)
def obter_ponto(id_ponto: str) -> PontoNaResposta:
    for ponto in carregar_pontos():
        if ponto.id == id_ponto:
            return PontoNaResposta(**ponto.model_dump(), aberto_agora=_aberto_agora(ponto))
    raise HTTPException(
        status_code=404,
        detail={
            "erro": "nao_encontrado",
            "mensagem": "Não encontramos esse ponto de coleta.",
        },
    )
