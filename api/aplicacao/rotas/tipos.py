"""Rota GET /api/tipos: tipos de resíduo com o nome de exibição.

O site usa esta lista para montar o filtro, assim os nomes ficam num só lugar.
"""

from fastapi import APIRouter

from aplicacao.modelos import NOMES_DOS_TIPOS, RespostaTipos, Tipo

roteador = APIRouter(tags=["tipos"])


@roteador.get("/tipos", response_model=RespostaTipos)
def listar_tipos() -> RespostaTipos:
    return RespostaTipos(
        tipos=[Tipo(codigo=codigo, nome=nome) for codigo, nome in NOMES_DOS_TIPOS.items()]
    )
