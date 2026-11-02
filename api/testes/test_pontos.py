"""Testes das rotas da API com o TestClient do FastAPI.

O TestClient chama a aplicação direto na memória, sem subir servidor nem usar a
rede. Os testes usam 3 pontos FICTÍCIOS fixos (testes/dados/pontos_de_exemplo.json),
e não o dados/pontos.json de verdade. Assim, adicionar ou corrigir um ponto real
nunca quebra estes testes. A validade do pontos.json real é checada em
test_dados_reais.py.
"""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from aplicacao.modelos import PontoDeColeta
from aplicacao.principal import app

ARQUIVO_DE_EXEMPLO = Path(__file__).parent / "dados" / "pontos_de_exemplo.json"


@pytest.fixture(autouse=True)
def usar_pontos_de_exemplo(monkeypatch):
    """Troca, em todos os testes deste arquivo, a leitura do pontos.json pelos pontos de exemplo.

    O autouse=True aplica a fixture sozinha, sem cada teste precisar pedi-la.
    O monkeypatch desfaz a troca ao fim de cada teste.
    """
    dados = json.loads(ARQUIVO_DE_EXEMPLO.read_text(encoding="utf-8"))
    pontos = tuple(PontoDeColeta.model_validate(item) for item in dados)
    monkeypatch.setattr("aplicacao.rotas.pontos.carregar_pontos", lambda: pontos)


cliente = TestClient(app)

# Perto do "Ecoponto de Exemplo A" (lat -1.4550, lon -48.4900).
PERTO_DO_PONTO_A = {"lat": -1.456, "lon": -48.491}


def test_saude_responde_ok():
    resposta = cliente.get("/api/saude")
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_tipos_lista_os_quatro_tipos_com_nome():
    resposta = cliente.get("/api/tipos")
    assert resposta.status_code == 200
    tipos = {tipo["codigo"]: tipo["nome"] for tipo in resposta.json()["tipos"]}
    assert len(tipos) == 4
    assert tipos["pilhas_baterias"] == "Pilhas e baterias"


def test_sem_posicao_lista_em_ordem_alfabetica_e_sem_distancia():
    corpo = cliente.get("/api/pontos").json()
    nomes = [ponto["nome"] for ponto in corpo["pontos"]]
    assert nomes == sorted(nomes, key=str.casefold)
    assert corpo["total"] == 3
    assert all(ponto["distancia_km"] is None for ponto in corpo["pontos"])
    # Os 3 pontos de exemplo têm horário, então o status é sempre true ou false.
    assert all(isinstance(ponto["aberto_agora"], bool) for ponto in corpo["pontos"])


def test_com_posicao_ordena_por_distancia():
    corpo = cliente.get("/api/pontos", params=PERTO_DO_PONTO_A).json()
    distancias = [ponto["distancia_km"] for ponto in corpo["pontos"]]
    assert corpo["pontos"][0]["id"] == "exemplo-ecoponto-a"
    assert distancias == sorted(distancias)
    assert distancias[0] < 0.5


def test_filtro_por_tipo_mantem_quem_aceita_algum_dos_tipos():
    corpo = cliente.get("/api/pontos", params={"tipos": "pilhas_baterias"}).json()
    ids = {ponto["id"] for ponto in corpo["pontos"]}
    assert ids == {"exemplo-ecoponto-a", "exemplo-loja-b"}

    # Mais de um tipo funciona como "ou" (RF04).
    corpo = cliente.get(
        "/api/pontos", params={"tipos": "pilhas_baterias,computadores_perifericos"}
    ).json()
    assert corpo["total"] == 3


def test_limite_corta_a_lista_mas_total_conta_todos():
    corpo = cliente.get("/api/pontos", params={**PERTO_DO_PONTO_A, "limite": 1}).json()
    assert len(corpo["pontos"]) == 1
    assert corpo["total"] == 3


def test_tipo_invalido_responde_erro_em_portugues():
    resposta = cliente.get("/api/pontos", params={"tipos": "geladeiras"})
    assert resposta.status_code == 400
    assert resposta.json()["erro"] == "tipo_invalido"
    assert "geladeiras" in resposta.json()["mensagem"]


def test_so_latitude_sem_longitude_e_recusado():
    resposta = cliente.get("/api/pontos", params={"lat": -1.45})
    assert resposta.status_code == 400
    assert resposta.json()["erro"] == "posicao_incompleta"


def test_parametro_com_formato_errado_usa_o_formato_de_erro_da_api():
    resposta = cliente.get("/api/pontos", params={"lat": "abc", "lon": -48.49})
    assert resposta.status_code == 400
    assert resposta.json()["erro"] == "parametro_invalido"


def test_obter_ponto_existente():
    resposta = cliente.get("/api/pontos/exemplo-loja-b")
    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Loja de Exemplo B"
    assert resposta.json()["fonte"] == "EXEMPLO"


def test_ponto_inexistente_responde_404_no_formato_da_api():
    resposta = cliente.get("/api/pontos/nao-existe")
    assert resposta.status_code == 404
    assert resposta.json() == {
        "erro": "nao_encontrado",
        "mensagem": "Não encontramos esse ponto de coleta.",
    }


def test_rota_inexistente_tambem_segue_o_formato_de_erro():
    resposta = cliente.get("/api/rota-que-nao-existe")
    assert resposta.status_code == 404
    assert resposta.json()["erro"] == "nao_encontrado"


def test_cors_libera_o_site_em_desenvolvimento():
    resposta = cliente.get("/api/saude", headers={"Origin": "http://localhost:5173"})
    assert resposta.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_cors_nao_libera_outros_sites():
    resposta = cliente.get("/api/saude", headers={"Origin": "https://site-qualquer.com"})
    assert "access-control-allow-origin" not in resposta.headers


def _trocar_pontos(monkeypatch, alterar):
    """Refaz a lista de pontos de exemplo aplicando `alterar` a cada dado bruto."""
    dados = json.loads(ARQUIVO_DE_EXEMPLO.read_text(encoding="utf-8"))
    for item in dados:
        alterar(item)
    pontos = tuple(PontoDeColeta.model_validate(item) for item in dados)
    monkeypatch.setattr("aplicacao.rotas.pontos.carregar_pontos", lambda: pontos)


def test_sem_horarios_aberto_agora_e_nulo(monkeypatch):
    _trocar_pontos(monkeypatch, lambda item: item.update(horarios=[]))

    corpo = cliente.get("/api/pontos").json()
    assert all(ponto["aberto_agora"] is None for ponto in corpo["pontos"])

    ponto = cliente.get("/api/pontos/exemplo-ecoponto-a").json()
    assert ponto["aberto_agora"] is None


@pytest.mark.parametrize("esperado", [True, False])
def test_com_horarios_aberto_agora_continua_booleano(monkeypatch, esperado):
    # Fixamos o resultado do cálculo para o teste não depender da hora em que roda.
    monkeypatch.setattr("aplicacao.rotas.pontos.esta_aberto_agora", lambda horarios: esperado)

    corpo = cliente.get("/api/pontos").json()
    assert all(ponto["aberto_agora"] is esperado for ponto in corpo["pontos"])

    assert cliente.get("/api/pontos/exemplo-ecoponto-a").json()["aberto_agora"] is esperado


def test_mistura_de_pontos_com_e_sem_horario(monkeypatch):
    def esvaziar_so_o_ecoponto(item):
        if item["id"] == "exemplo-ecoponto-a":
            item["horarios"] = []

    _trocar_pontos(monkeypatch, esvaziar_so_o_ecoponto)
    monkeypatch.setattr("aplicacao.rotas.pontos.esta_aberto_agora", lambda horarios: True)

    status = {p["id"]: p["aberto_agora"] for p in cliente.get("/api/pontos").json()["pontos"]}
    assert status["exemplo-ecoponto-a"] is None
    assert status["exemplo-loja-b"] is True
