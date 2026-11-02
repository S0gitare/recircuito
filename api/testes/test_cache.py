"""Testes do cache de geocodificação (servicos/cache.py).

O relógio é falso: os testes "avançam o tempo" sem esperar de verdade.
"""

import json

from aplicacao.servicos.cache import (
    TRINTA_DIAS_EM_SEGUNDOS,
    CacheDeGeocodificacao,
    normalizar_consulta,
)

VALOR = {"lat": -1.45, "lon": -48.49, "rotulo": "Campina, Belém - PA", "fonte": "nominatim"}


class RelogioFalso:
    """Relógio controlado pelo teste: `agora` só muda quando chamamos avancar()."""

    def __init__(self) -> None:
        self.agora = 1_000.0

    def __call__(self) -> float:
        return self.agora

    def avancar(self, segundos: float) -> None:
        self.agora += segundos


def test_normalizar_remove_acentos_caixa_e_espacos_sobrando():
    assert normalizar_consulta("  Campína ") == "campina"
    assert normalizar_consulta("SÃO   BRÁS") == "sao bras"
    assert normalizar_consulta("Nazaré") == normalizar_consulta("nazare")


def test_guarda_e_devolve_o_valor():
    cache = CacheDeGeocodificacao()
    assert cache.obter("texto:campina") is None
    cache.guardar("texto:campina", VALOR)
    assert cache.obter("texto:campina") == VALOR
    assert len(cache) == 1


def test_entrada_expira_depois_da_validade():
    relogio = RelogioFalso()
    cache = CacheDeGeocodificacao(relogio=relogio)
    cache.guardar("chave", VALOR)

    relogio.avancar(TRINTA_DIAS_EM_SEGUNDOS - 1)
    assert cache.obter("chave") == VALOR

    relogio.avancar(1)
    assert cache.obter("chave") is None
    # A entrada vencida também é removida da memória.
    assert len(cache) == 0


def test_persiste_em_arquivo_e_outra_instancia_le(tmp_path):
    arquivo = tmp_path / "pasta" / "cache.json"
    relogio = RelogioFalso()
    CacheDeGeocodificacao(arquivo=arquivo, relogio=relogio).guardar("chave", VALOR)

    assert arquivo.exists()
    reaberto = CacheDeGeocodificacao(arquivo=arquivo, relogio=relogio)
    assert reaberto.obter("chave") == VALOR


def test_entradas_vencidas_nao_sao_carregadas_do_arquivo(tmp_path):
    arquivo = tmp_path / "cache.json"
    relogio = RelogioFalso()
    CacheDeGeocodificacao(arquivo=arquivo, relogio=relogio).guardar("chave", VALOR)

    relogio.avancar(TRINTA_DIAS_EM_SEGUNDOS + 1)
    assert len(CacheDeGeocodificacao(arquivo=arquivo, relogio=relogio)) == 0


def test_arquivo_corrompido_comeca_vazio_sem_derrubar(tmp_path):
    arquivo = tmp_path / "cache.json"
    arquivo.write_text("{isto não é json", encoding="utf-8")
    cache = CacheDeGeocodificacao(arquivo=arquivo)
    assert len(cache) == 0
    # E continua funcionando: o próximo salvamento sobrescreve o arquivo ruim.
    cache.guardar("chave", VALOR)
    assert json.loads(arquivo.read_text(encoding="utf-8"))["chave"]["valor"] == VALOR


def test_arquivo_com_formato_inesperado_comeca_vazio(tmp_path):
    arquivo = tmp_path / "cache.json"
    # JSON válido, mas uma lista; e um objeto com entradas fora do formato.
    arquivo.write_text("[1, 2, 3]", encoding="utf-8")
    assert len(CacheDeGeocodificacao(arquivo=arquivo)) == 0

    arquivo.write_text(json.dumps({"a": "texto", "b": {"expira_em": "x", "valor": {}}}))
    assert len(CacheDeGeocodificacao(arquivo=arquivo)) == 0


def test_limite_de_entradas_descarta_a_mais_antiga():
    cache = CacheDeGeocodificacao(limite_de_entradas=2)
    cache.guardar("a", VALOR)
    cache.guardar("b", VALOR)
    cache.guardar("c", VALOR)
    assert len(cache) == 2
    assert cache.obter("a") is None
    assert cache.obter("b") == VALOR
    assert cache.obter("c") == VALOR


def test_regravar_uma_chave_a_torna_a_mais_nova():
    cache = CacheDeGeocodificacao(limite_de_entradas=2)
    cache.guardar("a", VALOR)
    cache.guardar("b", VALOR)
    cache.guardar("a", VALOR)  # "a" vira a mais nova; "b" passa a ser a mais antiga
    cache.guardar("c", VALOR)
    assert cache.obter("b") is None
    assert cache.obter("a") == VALOR
