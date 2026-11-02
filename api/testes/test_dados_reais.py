"""Confere o dados/pontos.json de verdade (o que o site mostra para as pessoas).

Estes testes não checam se o ponto existe (só uma ligação ou visita confirma isso),
mas pegam os erros que um cadastro manual costuma ter: campo com nome errado,
coordenada fora de Belém, id repetido, ponto sem fonte.
"""

from aplicacao.rotas.pontos import carregar_pontos

# Mesma caixa usada pela geocodificação (servicos/geocodificador.py).
LON_MIN, LON_MAX = -48.60, -48.35
LAT_MIN, LAT_MAX = -1.55, -1.20

# Importado no topo do módulo, antes de qualquer troca feita por outros testes.
PONTOS = carregar_pontos()


def test_o_arquivo_tem_pelo_menos_um_ponto_e_passa_na_validacao():
    # Se o JSON tiver um campo errado, o carregar_pontos() já falha ao importar este módulo.
    assert len(PONTOS) >= 1


def test_ids_nao_se_repetem():
    ids = [ponto.id for ponto in PONTOS]
    assert len(ids) == len(set(ids)), "há ids repetidos no pontos.json"


def test_coordenadas_ficam_dentro_de_belem():
    for ponto in PONTOS:
        c = ponto.coordenadas
        assert LAT_MIN <= c.lat <= LAT_MAX and LON_MIN <= c.lon <= LON_MAX, (
            f"{ponto.id}: coordenada fora de Belém (lat e lon trocadas?)"
        )


def test_todo_ponto_cita_a_fonte():
    for ponto in PONTOS:
        assert ponto.fonte.strip(), f"{ponto.id}: sem fonte"


def test_ponto_sem_verificacao_avisa_nas_observacoes():
    """Quem não tem `verificado_em` precisa dizer, nas observações, que não foi confirmado."""
    for ponto in PONTOS:
        if ponto.verificado_em is None:
            assert ponto.observacoes and "NÃO CONFIRMADO" in ponto.observacoes, (
                f"{ponto.id}: sem data de verificação e sem o aviso NÃO CONFIRMADO"
            )
