"""Testes do "aberto agora" (servicos/horarios.py).

1º de novembro de 2026 é um domingo; os demais dias são calculados a partir dele.
"""

from datetime import UTC, datetime

from aplicacao.modelos import FaixaDeHorario
from aplicacao.servicos.horarios import dia_da_semana_spec, esta_aberto_agora

COMERCIAL = [
    FaixaDeHorario(dias=[1, 2, 3, 4, 5], abre="08:00", fecha="18:00"),
    FaixaDeHorario(dias=[6], abre="08:00", fecha="12:00"),
]

DOMINGO = datetime(2026, 11, 1)
SEGUNDA = datetime(2026, 11, 2)
SABADO = datetime(2026, 11, 7)


def test_dia_da_semana_segue_a_convencao_da_spec():
    assert dia_da_semana_spec(DOMINGO) == 0
    assert dia_da_semana_spec(SEGUNDA) == 1
    assert dia_da_semana_spec(SABADO) == 6


def test_aberto_no_meio_do_expediente():
    assert esta_aberto_agora(COMERCIAL, SEGUNDA.replace(hour=10))


def test_fechado_no_domingo():
    assert not esta_aberto_agora(COMERCIAL, DOMINGO.replace(hour=10))


def test_sabado_so_ate_meio_dia():
    assert esta_aberto_agora(COMERCIAL, SABADO.replace(hour=11, minute=59))
    assert not esta_aberto_agora(COMERCIAL, SABADO.replace(hour=12))


def test_abre_na_hora_exata_e_fecha_na_hora_exata():
    assert esta_aberto_agora(COMERCIAL, SEGUNDA.replace(hour=8))
    assert not esta_aberto_agora(COMERCIAL, SEGUNDA.replace(hour=18))


def test_horario_em_utc_e_convertido_para_belem():
    # 20:00 UTC de segunda = 17:00 em Belém (UTC-3): ainda aberto.
    assert esta_aberto_agora(COMERCIAL, datetime(2026, 11, 2, 20, 0, tzinfo=UTC))
    # 22:00 UTC = 19:00 em Belém: já fechado, embora 22h UTC pareça "noite".
    assert not esta_aberto_agora(COMERCIAL, datetime(2026, 11, 2, 22, 0, tzinfo=UTC))


def test_virada_do_dia_em_utc_muda_o_dia_da_semana():
    # 02:00 UTC de terça = 23:00 de segunda em Belém.
    noturno = [FaixaDeHorario(dias=[1], abre="22:00", fecha="24:00")]
    assert esta_aberto_agora(noturno, datetime(2026, 11, 3, 2, 0, tzinfo=UTC))


def test_sem_horarios_e_sempre_fechado():
    assert not esta_aberto_agora([], SEGUNDA.replace(hour=10))
