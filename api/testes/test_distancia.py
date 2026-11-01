"""Testes da fórmula de haversine (servicos/distancia.py)."""

import pytest

from aplicacao.servicos.distancia import calcular_distancia_km


def test_mesmo_ponto_tem_distancia_zero():
    assert calcular_distancia_km(-1.455, -48.49, -1.455, -48.49) == 0


def test_um_grau_de_latitude_tem_cerca_de_111_km():
    # Ao longo de um meridiano, 1 grau vale 2πR/360 ≈ 111,19 km.
    assert calcular_distancia_km(0, 0, 1, 0) == pytest.approx(111.19, abs=0.01)


def test_distancia_e_simetrica():
    ida = calcular_distancia_km(-1.455, -48.49, -1.43, -48.46)
    volta = calcular_distancia_km(-1.43, -48.46, -1.455, -48.49)
    assert ida == pytest.approx(volta)


def test_belem_ate_sao_paulo_fica_perto_do_valor_conhecido():
    # Distância em linha reta Belém -> São Paulo: cerca de 2.460 km.
    distancia = calcular_distancia_km(-1.4558, -48.4902, -23.5505, -46.6333)
    assert distancia == pytest.approx(2460, rel=0.01)


def test_pontos_antipodas_nao_quebram_por_arredondamento():
    # Meia volta da Terra: π·R ≈ 20.015 km. Sem o min() em asin, poderia dar ValueError.
    assert calcular_distancia_km(0, 0, 0, 180) == pytest.approx(20015.1, abs=0.5)
