"""Cálculo do "aberto agora" de um ponto de coleta (RF05).

O servidor da API (Render) roda em UTC, mas o horário que importa é o de Belém.
Por isso todo cálculo converte "agora" para o fuso America/Belem antes de
comparar. Um fuso (time zone) é a regra que diz quantas horas um lugar está
adiantado ou atrasado em relação ao UTC; Belém fica em UTC-3 o ano todo.

Cuidado ao mexer: nunca use datetime.now() sem fuso aqui. Ele devolveria a hora
do servidor, e um ponto que fecha às 18h apareceria fechado às 15h em Belém.
"""

from datetime import datetime, time
from zoneinfo import ZoneInfo

from aplicacao.configuracao import configuracoes
from aplicacao.modelos import FaixaDeHorario

FUSO_BELEM = ZoneInfo(configuracoes.fuso_horario)


def _converter_hora(texto: str) -> time:
    """Converte "HH:MM" em time. "24:00" vira o último instante do dia."""
    if texto == "24:00":
        return time.max
    horas, minutos = texto.split(":")
    return time(int(horas), int(minutos))


def dia_da_semana_spec(momento: datetime) -> int:
    """Dia da semana na convenção da SPEC (0 = domingo ... 6 = sábado).

    O Python usa weekday() com 0 = segunda ... 6 = domingo. Somar 1 e tirar o
    resto por 7 desloca a contagem: segunda (0) vira 1 e domingo (6) vira 0.
    """
    return (momento.weekday() + 1) % 7


def esta_aberto_agora(horarios: list[FaixaDeHorario], agora: datetime | None = None) -> bool:
    """Diz se o ponto está aberto no momento `agora` (padrão: o momento atual).

    `agora` existe para os testes poderem fixar um horário. Se vier sem fuso
    (datetime "ingênuo"), é tratado como já estando no horário de Belém.

    Faixas que viram a noite (ex.: abre 22:00 e fecha 02:00) não são suportadas:
    divida em duas faixas, uma até "24:00" e outra a partir de "00:00" no dia seguinte.
    """
    if agora is None:
        agora = datetime.now(FUSO_BELEM)
    elif agora.tzinfo is None:
        agora = agora.replace(tzinfo=FUSO_BELEM)
    else:
        agora = agora.astimezone(FUSO_BELEM)

    dia = dia_da_semana_spec(agora)
    hora_atual = agora.time()

    for faixa in horarios:
        if dia not in faixa.dias:
            continue
        # Intervalo semiaberto: aberto às 08:00 em ponto, já fechado às 18:00 em ponto.
        if _converter_hora(faixa.abre) <= hora_atual < _converter_hora(faixa.fecha):
            return True
    return False
