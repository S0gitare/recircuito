"""Testes da rota POST /api/sugestoes ("Sugerir um ponto", RF08)."""

import json
from dataclasses import replace
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from aplicacao.configuracao import configuracoes
from aplicacao.principal import app

cliente = TestClient(app)

SUGESTAO_VALIDA = {
    "nome": "Loja do Seu Zé",
    "endereco": "Travessa Quintino Bocaiúva, 100, Reduto",
    "tipos": ["celulares_tablets", "pilhas_baterias"],
    "observacao": "Vi a caixa de coleta perto do caixa.",
}


@pytest.fixture(autouse=True)
def arquivo_sugestoes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Garante que os testes não toquem no arquivo de sugestões real."""
    arquivo = tmp_path / "sugestoes.json"
    nova_config = replace(configuracoes, arquivo_sugestoes=arquivo)
    monkeypatch.setattr("aplicacao.rotas.sugestoes.configuracoes", nova_config)
    return arquivo


def ler(arquivo: Path) -> list[dict]:
    return json.loads(arquivo.read_text(encoding="utf-8"))


def test_sugestao_valida_retorna_201_e_grava_no_disco(arquivo_sugestoes: Path):
    resposta = cliente.post("/api/sugestoes", json=SUGESTAO_VALIDA)

    assert resposta.status_code == 201
    dados = resposta.json()
    assert dados["nome"] == "Loja do Seu Zé"
    assert dados["tipos"] == ["celulares_tablets", "pilhas_baterias"]
    assert dados["data"]

    gravadas = ler(arquivo_sugestoes)
    assert len(gravadas) == 1
    assert gravadas[0] == dados


def test_campos_minimos_sem_observacao():
    corpo = {"nome": "Ecoponto", "endereco": "Marco", "tipos": ["cabos_carregadores"]}
    resposta = cliente.post("/api/sugestoes", json=corpo)

    assert resposta.status_code == 201
    assert resposta.json()["observacao"] is None


def test_textos_sao_limpos_e_observacao_vazia_vira_nula():
    corpo = {**SUGESTAO_VALIDA, "nome": "  Loja  ", "observacao": "   "}
    dados = cliente.post("/api/sugestoes", json=corpo).json()

    assert dados["nome"] == "Loja"
    assert dados["observacao"] is None


def test_tipos_repetidos_sao_unificados():
    corpo = {**SUGESTAO_VALIDA, "tipos": ["pilhas_baterias", "pilhas_baterias"]}
    assert cliente.post("/api/sugestoes", json=corpo).json()["tipos"] == ["pilhas_baterias"]


def test_sugestoes_se_acumulam(arquivo_sugestoes: Path):
    cliente.post("/api/sugestoes", json=SUGESTAO_VALIDA)
    cliente.post("/api/sugestoes", json={**SUGESTAO_VALIDA, "nome": "Outro local"})

    assert [s["nome"] for s in ler(arquivo_sugestoes)] == ["Loja do Seu Zé", "Outro local"]


def test_data_vem_sempre_do_servidor():
    # O cliente não escolhe a data: um campo extra é ignorado.
    corpo = {**SUGESTAO_VALIDA, "data": "1999-01-01T00:00:00"}
    assert not cliente.post("/api/sugestoes", json=corpo).json()["data"].startswith("1999")


@pytest.mark.parametrize(
    "mudanca",
    [
        {"nome": "   "},  # só espaços
        {"nome": "x" * 121},
        {"endereco": ""},
        {"tipos": []},
        {"tipos": ["geladeira"]},  # tipo que não existe
        {"observacao": "x" * 501},
    ],
)
def test_dados_invalidos_retornam_400_no_formato_padrao(mudanca: dict, arquivo_sugestoes: Path):
    resposta = cliente.post("/api/sugestoes", json={**SUGESTAO_VALIDA, **mudanca})

    assert resposta.status_code == 400
    assert resposta.json()["erro"] == "parametro_invalido"
    assert not arquivo_sugestoes.exists()


def test_sem_campos_obrigatorios_retorna_400():
    resposta = cliente.post("/api/sugestoes", json={})
    assert resposta.status_code == 400
