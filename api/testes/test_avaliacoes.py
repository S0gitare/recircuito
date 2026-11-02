"""Testes da rota POST /api/avaliacoes."""

import json
from dataclasses import replace
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from aplicacao.configuracao import configuracoes
from aplicacao.principal import app

cliente = TestClient(app)


@pytest.fixture(autouse=True)
def isolar_arquivo_avaliacoes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Garante que os testes não toquem no arquivo de avaliações real."""
    arquivo_temporario = tmp_path / "avaliacoes.json"
    nova_config = replace(configuracoes, arquivo_avaliacoes=arquivo_temporario)
    monkeypatch.setattr("aplicacao.rotas.avaliacoes.configuracoes", nova_config)
    return arquivo_temporario


def test_envio_com_dados_validos_retorna_201_e_grava_no_disco(tmp_path: Path):
    corpo = {
        "nota": 5,
        "encontrou_ponto": "sim",
        "comentario": "Excelente iniciativa para descarte em Belém!",
    }
    resposta = cliente.post("/api/avaliacoes", json=corpo)

    assert resposta.status_code == 201
    dados = resposta.json()
    assert dados["nota"] == 5
    assert dados["encontrou_ponto"] == "sim"
    assert dados["comentario"] == "Excelente iniciativa para descarte em Belém!"
    assert "data" in dados and dados["data"] is not None

    # Verifica persistência no arquivo JSON
    arquivo = tmp_path / "avaliacoes.json"
    assert arquivo.exists()
    conteudo = json.loads(arquivo.read_text(encoding="utf-8"))
    assert len(conteudo) == 1
    assert conteudo[0]["nota"] == 5
    assert conteudo[0]["encontrou_ponto"] == "sim"
    assert conteudo[0]["comentario"] == "Excelente iniciativa para descarte em Belém!"
    assert conteudo[0]["data"] == dados["data"]


def test_envio_campos_minimos_sem_comentario():
    corpo = {
        "nota": 4,
        "encontrou_ponto": "parcialmente",
    }
    resposta = cliente.post("/api/avaliacoes", json=corpo)

    assert resposta.status_code == 201
    dados = resposta.json()
    assert dados["nota"] == 4
    assert dados["encontrou_ponto"] == "parcialmente"
    assert dados["comentario"] is None
    assert "data" in dados


def test_acumulo_de_multiplas_avaliacoes(tmp_path: Path):
    cliente.post("/api/avaliacoes", json={"nota": 1, "encontrou_ponto": "nao"})
    cliente.post("/api/avaliacoes", json={"nota": 5, "encontrou_ponto": "sim"})

    arquivo = tmp_path / "avaliacoes.json"
    conteudo = json.loads(arquivo.read_text(encoding="utf-8"))
    assert len(conteudo) == 2
    assert conteudo[0]["nota"] == 1
    assert conteudo[1]["nota"] == 5


def test_validacao_nota_abaixo_de_1():
    resposta = cliente.post("/api/avaliacoes", json={"nota": 0, "encontrou_ponto": "sim"})
    assert resposta.status_code == 400
    assert resposta.json()["erro"] == "parametro_invalido"


def test_validacao_nota_acima_de_5():
    resposta = cliente.post("/api/avaliacoes", json={"nota": 6, "encontrou_ponto": "sim"})
    assert resposta.status_code == 400
    assert resposta.json()["erro"] == "parametro_invalido"


def test_validacao_encontrou_ponto_opcao_invalida():
    resposta = cliente.post("/api/avaliacoes", json={"nota": 3, "encontrou_ponto": "talvez"})
    assert resposta.status_code == 400
    assert resposta.json()["erro"] == "parametro_invalido"


def test_validacao_comentario_excede_1000_caracteres():
    comentario_longo = "a" * 1001
    resposta = cliente.post(
        "/api/avaliacoes",
        json={"nota": 5, "encontrou_ponto": "sim", "comentario": comentario_longo},
    )
    assert resposta.status_code == 400
    assert resposta.json()["erro"] == "parametro_invalido"


def test_comentario_com_exatos_1000_caracteres_passa():
    comentario_limite = "a" * 1000
    resposta = cliente.post(
        "/api/avaliacoes",
        json={"nota": 5, "encontrou_ponto": "sim", "comentario": comentario_limite},
    )
    assert resposta.status_code == 201
    assert resposta.json()["comentario"] == comentario_limite


def test_data_customizada_preservada():
    data_iso = "2026-11-02T12:00:00Z"
    resposta = cliente.post(
        "/api/avaliacoes",
        json={"nota": 5, "encontrou_ponto": "sim", "data": data_iso},
    )
    assert resposta.status_code == 201
    assert resposta.json()["data"] == data_iso


def test_validacao_data_invalida_retorna_400():
    resposta = cliente.post(
        "/api/avaliacoes",
        json={"nota": 5, "encontrou_ponto": "sim", "data": "invalido"},
    )
    assert resposta.status_code == 400
    assert resposta.json()["erro"] == "parametro_invalido"
    assert "data" in resposta.json()["mensagem"]


def test_validacao_data_vazia_retorna_400():
    resposta = cliente.post(
        "/api/avaliacoes",
        json={"nota": 5, "encontrou_ponto": "sim", "data": "   "},
    )
    assert resposta.status_code == 400
    assert resposta.json()["erro"] == "parametro_invalido"
    assert "data" in resposta.json()["mensagem"]


def test_comentario_apenas_espacos_salvo_como_nulo():
    resposta = cliente.post(
        "/api/avaliacoes",
        json={"nota": 5, "encontrou_ponto": "sim", "comentario": "   "},
    )
    assert resposta.status_code == 201
    assert resposta.json()["comentario"] is None


def test_concorrencia_ao_salvar_avaliacoes(tmp_path: Path):
    from concurrent.futures import ThreadPoolExecutor

    def enviar(n: int):
        return cliente.post("/api/avaliacoes", json={"nota": 5, "encontrou_ponto": "sim"})

    with ThreadPoolExecutor(max_workers=10) as executor:
        respostas = list(executor.map(enviar, range(20)))

    for r in respostas:
        assert r.status_code == 201

    arquivo = tmp_path / "avaliacoes.json"
    conteudo = json.loads(arquivo.read_text(encoding="utf-8"))
    assert len(conteudo) == 20


def test_recuperacao_arquivo_avaliacoes_corrompido(tmp_path: Path):
    arquivo = tmp_path / "avaliacoes.json"
    arquivo.write_text("{ \"corrompido\": true }", encoding="utf-8")

    resposta = cliente.post("/api/avaliacoes", json={"nota": 4, "encontrou_ponto": "sim"})
    assert resposta.status_code == 201

    conteudo = json.loads(arquivo.read_text(encoding="utf-8"))
    assert isinstance(conteudo, list)
    assert len(conteudo) == 1
    assert conteudo[0]["nota"] == 4

