"""Modelos (Pydantic) dos dados da API, no formato da SPEC §9.

O Pydantic valida o pontos.json ao carregar: se alguém digitar um tipo de
resíduo errado ou esquecer as coordenadas, a API falha logo na partida, com a
linha do problema, em vez de responder dados quebrados para o site.
"""

import re
from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

# "HH:MM" de 00:00 a 23:59. Para "até meia-noite", use "fecha": "24:00".
PADRAO_HORA = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$|^24:00$")


class TipoResiduo(StrEnum):
    """Tipos de resíduo aceitos. O valor é o código usado no JSON e na URL."""

    CELULARES_TABLETS = "celulares_tablets"
    PILHAS_BATERIAS = "pilhas_baterias"
    COMPUTADORES_PERIFERICOS = "computadores_perifericos"
    CABOS_CARREGADORES = "cabos_carregadores"


# Nome de exibição de cada tipo, usado pela rota /api/tipos.
NOMES_DOS_TIPOS: dict[TipoResiduo, str] = {
    TipoResiduo.CELULARES_TABLETS: "Celulares e tablets",
    TipoResiduo.PILHAS_BATERIAS: "Pilhas e baterias",
    TipoResiduo.COMPUTADORES_PERIFERICOS: "Computadores e periféricos",
    TipoResiduo.CABOS_CARREGADORES: "Cabos e carregadores",
}


class TipoLocal(StrEnum):
    ECOPONTO = "ecoponto"
    VAREJO = "varejo"
    OPERADORA = "operadora"
    FABRICANTE = "fabricante"
    COOPERATIVA = "cooperativa"
    ORGAO_PUBLICO = "orgao_publico"


class Endereco(BaseModel):
    logradouro: str
    numero: str | None = None
    bairro: str
    cep: str | None = None


class Coordenadas(BaseModel):
    # Limites geográficos válidos; evitam, por exemplo, lat e lon trocadas
    # quando o valor passa de 90.
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)


class FaixaDeHorario(BaseModel):
    """Um intervalo de funcionamento que se repete nos dias indicados.

    `dias` segue a convenção do JavaScript (Date.getDay): 0 = domingo, 6 = sábado.
    Atenção: o Python usa outra (weekday(): 0 = segunda). A conversão fica em
    servicos/horarios.py, não aqui.
    """

    dias: list[int] = Field(min_length=1)
    abre: str
    fecha: str

    @field_validator("dias")
    @classmethod
    def validar_dias(cls, dias: list[int]) -> list[int]:
        if any(dia < 0 or dia > 6 for dia in dias):
            raise ValueError("os dias vão de 0 (domingo) a 6 (sábado)")
        return dias

    @field_validator("abre", "fecha")
    @classmethod
    def validar_hora(cls, hora: str) -> str:
        if not PADRAO_HORA.match(hora):
            raise ValueError(f"hora inválida: {hora!r} (use HH:MM)")
        return hora


class Contato(BaseModel):
    telefone: str | None = None
    site: str | None = None


class PontoDeColeta(BaseModel):
    """Um ponto de coleta como está no pontos.json."""

    # Recusa campos desconhecidos: pega erros de digitação no JSON
    # (ex.: "tipos_aceito" sem o "s").
    model_config = ConfigDict(extra="forbid")

    id: str
    nome: str
    tipo_local: TipoLocal
    endereco: Endereco
    coordenadas: Coordenadas
    tipos_aceitos: list[TipoResiduo] = Field(min_length=1)
    horarios: list[FaixaDeHorario] = Field(default_factory=list)
    contato: Contato = Field(default_factory=Contato)
    # De onde veio a informação, para que possa ser conferida (SPEC §9).
    fonte: str
    verificado_em: str | None = None
    observacoes: str | None = None


class PontoNaResposta(PontoDeColeta):
    """Ponto devolvido pela API, com os campos calculados na hora."""

    # Só existe quando a busca informa lat/lon.
    distancia_km: float | None = None
    # None = horário não informado (lista `horarios` vazia). Não é o mesmo que
    # False: "fechado" é uma afirmação, e para esses pontos não sabemos.
    aberto_agora: bool | None


class RespostaPontos(BaseModel):
    pontos: list[PontoNaResposta]
    total: int


class Tipo(BaseModel):
    codigo: TipoResiduo
    nome: str


class RespostaTipos(BaseModel):
    tipos: list[Tipo]


class Localizacao(BaseModel):
    """Resultado de GET /api/geocodificar: onde fica o CEP ou bairro buscado."""

    lat: float
    lon: float
    # Texto curto para mostrar à pessoa, ex.: "Campina, Belém - PA".
    rotulo: str
    # De onde veio a coordenada: "viacep+nominatim" ou "nominatim".
    fonte: str


class Erro(BaseModel):
    """Formato único de erro da API (SPEC §10)."""

    erro: str
    mensagem: str


class NovaAvaliacao(BaseModel):
    """Dados de uma nova avaliação do site enviada pelo usuário."""

    nota: int = Field(ge=1, le=5, description="Nota de 1 a 5 dada ao site")
    encontrou_ponto: Literal["sim", "parcialmente", "nao"] = Field(
        description="Se o usuário conseguiu encontrar o ponto de coleta desejado"
    )
    comentario: str | None = Field(
        default=None, max_length=1000, description="Comentário opcional do usuário"
    )
    data: str | None = Field(
        default=None, description="Data ISO informada pelo cliente ou gerada pelo servidor"
    )

    @field_validator("data")
    @classmethod
    def validar_data_iso(cls, valor: str | None) -> str | None:
        if valor is None:
            return None
        texto = valor.strip()
        if not texto:
            raise ValueError("data não pode ser vazia; use formato ISO")
        try:
            datetime.fromisoformat(texto)
        except ValueError as erro:
            raise ValueError(f"data em formato inválido: {valor!r} (use formato ISO)") from erro
        return texto

    @field_validator("comentario")
    @classmethod
    def validar_comentario(cls, valor: str | None) -> str | None:
        if valor is None:
            return None
        texto = valor.strip()
        return texto if texto else None


class AvaliacaoRegistrada(NovaAvaliacao):
    """Avaliação gravada em disco com data ISO garantida."""

    data: str


def _texto_limpo(valor: str | None) -> str | None:
    """Tira espaços das pontas; texto vazio vira None."""
    if valor is None:
        return None
    texto = valor.strip()
    return texto or None


class NovaSugestao(BaseModel):
    """Ponto de coleta indicado por alguém pelo site ("Sugerir um ponto", RF08).

    De propósito, não há campo de contato (e-mail, telefone): seria dado
    pessoal, e o site promete não coletar nenhum além do Analytics (RNF06).
    """

    nome: str = Field(
        min_length=2, max_length=120, description="Nome do local (ex.: loja, ecoponto)"
    )
    endereco: str = Field(
        min_length=3, max_length=200, description="Endereço ou bairro do local em Belém"
    )
    tipos: list[TipoResiduo] = Field(
        min_length=1, description="Tipos de resíduo que o local recebe"
    )
    observacao: str | None = Field(
        default=None,
        max_length=500,
        description="Como a pessoa sabe do ponto, horário, observações (opcional)",
    )

    @field_validator("nome", "endereco", mode="before")
    @classmethod
    def limpar_obrigatorio(cls, valor: object) -> object:
        # Limpa antes de validar o tamanho: "   " não pode passar como nome.
        return valor.strip() if isinstance(valor, str) else valor

    @field_validator("observacao")
    @classmethod
    def limpar_observacao(cls, valor: str | None) -> str | None:
        return _texto_limpo(valor)

    @field_validator("tipos")
    @classmethod
    def sem_tipos_repetidos(cls, valor: list[TipoResiduo]) -> list[TipoResiduo]:
        # Mantém a ordem da primeira ocorrência.
        return list(dict.fromkeys(valor))


class SugestaoRegistrada(NovaSugestao):
    """Sugestão gravada em disco, com a data em que chegou (sempre do servidor)."""

    data: str
