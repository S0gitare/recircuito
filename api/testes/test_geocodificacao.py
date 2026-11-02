"""Testes da geocodificação (servicos/geocodificador.py e rotas/geocodificacao.py).

Nenhum teste usa a internet: ViaCEP e Nominatim são trocados por respostas
falsas com httpx.MockTransport. As funções assíncronas rodam com asyncio.run,
então não precisamos de pytest-asyncio.
"""

import asyncio

import httpx
import pytest
from fastapi.testclient import TestClient

from aplicacao.modelos import Localizacao
from aplicacao.principal import app
from aplicacao.rotas.geocodificacao import obter_geocodificador
from aplicacao.servicos.cache import CacheDeGeocodificacao
from aplicacao.servicos.geocodificador import Geocodificador, ServicoExternoIndisponivel

VIACEP_NAZARE = {
    "cep": "66035-000",
    "logradouro": "Avenida Nazaré",
    "bairro": "Nazaré",
    "localidade": "Belém",
    "uf": "PA",
}
NOMINATIM_ACHOU = [{"lat": "-1.4521", "lon": "-48.4880"}]


class ServicosFalsos:
    """Simula ViaCEP e Nominatim e anota cada requisição recebida."""

    def __init__(self, viacep=None, nominatim=None, status_viacep=200) -> None:
        self.viacep = viacep if viacep is not None else VIACEP_NAZARE
        self.nominatim = nominatim if nominatim is not None else NOMINATIM_ACHOU
        self.status_viacep = status_viacep
        self.chamadas: list[httpx.Request] = []

    def __call__(self, requisicao: httpx.Request) -> httpx.Response:
        self.chamadas.append(requisicao)
        if requisicao.url.host == "viacep.com.br":
            return httpx.Response(self.status_viacep, json=self.viacep)
        if requisicao.url.host == "nominatim.openstreetmap.org":
            return httpx.Response(200, json=self.nominatim)
        raise AssertionError(f"chamada inesperada: {requisicao.url}")

    def do_viacep(self) -> list[httpx.Request]:
        return [c for c in self.chamadas if c.url.host == "viacep.com.br"]

    def do_nominatim(self) -> list[httpx.Request]:
        return [c for c in self.chamadas if c.url.host == "nominatim.openstreetmap.org"]


def criar_geocodificador(tratador, cache=None, **opcoes) -> Geocodificador:
    """Monta um Geocodificador cujo cliente HTTP só fala com o `tratador` falso."""
    return Geocodificador(
        cache=cache if cache is not None else CacheDeGeocodificacao(),
        fabrica_de_cliente=lambda: httpx.AsyncClient(transport=httpx.MockTransport(tratador)),
        # Sem espera real, a não ser que o teste injete relógio e "dormir" próprios.
        intervalo_entre_chamadas=opcoes.pop("intervalo_entre_chamadas", 0.0),
        **opcoes,
    )


def geocodificar(geocodificador: Geocodificador, consulta: str) -> Localizacao | None:
    return asyncio.run(geocodificador.geocodificar(consulta))


# --- CEP -------------------------------------------------------------------


def test_cep_de_belem_vira_coordenada_com_rotulo_e_fonte():
    servicos = ServicosFalsos()
    resultado = geocodificar(criar_geocodificador(servicos), "66035-000")

    assert resultado is not None
    assert resultado.lat == pytest.approx(-1.4521)
    assert resultado.lon == pytest.approx(-48.4880)
    assert resultado.rotulo == "Nazaré, Belém - PA"
    assert resultado.fonte == "viacep+nominatim"
    # O endereço do ViaCEP é o que vai para o Nominatim.
    assert "Avenida Nazaré" in servicos.do_nominatim()[0].url.params["q"]


def test_cep_com_e_sem_hifen_usam_a_mesma_chave_de_cache():
    servicos = ServicosFalsos()
    geocodificador = criar_geocodificador(servicos)

    primeiro = geocodificar(geocodificador, "66035-000")
    segundo = geocodificar(geocodificador, "66035000")

    assert primeiro == segundo
    assert len(servicos.do_viacep()) == 1  # a segunda busca saiu do cache
    assert len(servicos.do_nominatim()) == 1


def test_cep_de_outra_cidade_devolve_none():
    servicos = ServicosFalsos(viacep={**VIACEP_NAZARE, "localidade": "São Paulo", "uf": "SP"})
    assert geocodificar(criar_geocodificador(servicos), "01001-000") is None
    assert servicos.do_nominatim() == []  # nem chega a procurar no mapa


def test_cep_inexistente_viacep_com_erro_true_devolve_none():
    servicos = ServicosFalsos(viacep={"erro": True})
    assert geocodificar(criar_geocodificador(servicos), "99999-999") is None
    assert servicos.do_nominatim() == []


def test_cep_sem_endereco_no_nominatim_cai_para_o_bairro():
    respostas = iter([[], NOMINATIM_ACHOU])

    def tratador(requisicao: httpx.Request) -> httpx.Response:
        if requisicao.url.host == "viacep.com.br":
            return httpx.Response(200, json=VIACEP_NAZARE)
        return httpx.Response(200, json=next(respostas))

    resultado = geocodificar(criar_geocodificador(tratador), "66035-000")
    assert resultado is not None
    assert resultado.rotulo == "Nazaré, Belém - PA"


# --- Texto livre ------------------------------------------------------------


def test_bairro_e_buscado_so_em_belem_e_sem_viacep():
    servicos = ServicosFalsos()
    resultado = geocodificar(criar_geocodificador(servicos), "marco")

    assert resultado is not None
    assert resultado.rotulo == "Marco, Belém - PA"
    assert resultado.fonte == "nominatim"
    assert servicos.do_viacep() == []
    (chamada,) = servicos.do_nominatim()
    assert chamada.url.params["bounded"] == "1"
    assert "viewbox" in chamada.url.params
    assert "Belém" in chamada.url.params["q"]


def test_variacoes_de_acento_e_caixa_acertam_o_cache():
    servicos = ServicosFalsos()
    geocodificador = criar_geocodificador(servicos)

    geocodificar(geocodificador, "São Brás")
    geocodificar(geocodificador, "  SAO BRAS ")
    geocodificar(geocodificador, "são brás")

    assert len(servicos.do_nominatim()) == 1


def test_nao_encontrado_nao_vai_para_o_cache():
    servicos = ServicosFalsos(nominatim=[])
    geocodificador = criar_geocodificador(servicos)

    assert geocodificar(geocodificador, "lugar que nao existe") is None
    assert geocodificar(geocodificador, "lugar que nao existe") is None

    # Cada tentativa foi até o Nominatim: o "não achei" não ficou guardado.
    assert len(servicos.do_nominatim()) == 2


def test_texto_so_com_espacos_nao_chama_ninguem():
    servicos = ServicosFalsos()
    assert geocodificar(criar_geocodificador(servicos), "   ") is None
    assert servicos.chamadas == []


# --- Falhas dos serviços ----------------------------------------------------


def test_falha_de_rede_levanta_servico_indisponivel():
    def tratador(requisicao: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("sem rede", request=requisicao)

    with pytest.raises(ServicoExternoIndisponivel):
        geocodificar(criar_geocodificador(tratador), "marco")


def test_erro_http_do_nominatim_levanta_servico_indisponivel():
    def tratador(requisicao: httpx.Request) -> httpx.Response:
        return httpx.Response(429)  # excesso de requisições

    with pytest.raises(ServicoExternoIndisponivel):
        geocodificar(criar_geocodificador(tratador), "marco")


@pytest.mark.parametrize(
    "resposta",
    [
        httpx.Response(200, content=b"<html>nao e json</html>"),
        httpx.Response(200, json={"error": "falhou"}),  # objeto no lugar de lista
        httpx.Response(200, json=[{"sem": "coordenadas"}]),
        httpx.Response(200, json="texto solto"),
    ],
)
def test_resposta_malformada_do_nominatim_levanta_servico_indisponivel(resposta):
    with pytest.raises(ServicoExternoIndisponivel):
        geocodificar(criar_geocodificador(lambda _: resposta), "marco")


def test_resposta_malformada_do_viacep_levanta_servico_indisponivel():
    servicos = ServicosFalsos(viacep=["não", "é", "objeto"])
    with pytest.raises(ServicoExternoIndisponivel):
        geocodificar(criar_geocodificador(servicos), "66035-000")


# --- Limite de 1 requisição por segundo ------------------------------------


def test_duas_chamadas_ao_nominatim_respeitam_o_intervalo_de_um_segundo():
    # Relógio falso: só avança quando o "dormir" falso é chamado.
    agora = [100.0]
    esperas: list[float] = []

    async def dormir_falso(segundos: float) -> None:
        esperas.append(segundos)
        agora[0] += segundos

    geocodificador = criar_geocodificador(
        ServicosFalsos(),
        intervalo_entre_chamadas=1.0,
        relogio=lambda: agora[0],
        dormir=dormir_falso,
    )

    async def duas_buscas() -> None:
        await geocodificador.geocodificar("marco")
        await geocodificador.geocodificar("guamá")  # texto diferente: não vem do cache

    asyncio.run(duas_buscas())

    # A primeira não espera; a segunda, feita no mesmo instante, espera 1 segundo inteiro.
    assert esperas == [pytest.approx(1.0)]


def test_buscas_simultaneas_tambem_respeitam_o_intervalo():
    agora = [0.0]
    esperas: list[float] = []

    async def dormir_falso(segundos: float) -> None:
        esperas.append(segundos)
        agora[0] += segundos

    geocodificador = criar_geocodificador(
        ServicosFalsos(),
        intervalo_entre_chamadas=1.0,
        relogio=lambda: agora[0],
        dormir=dormir_falso,
    )

    async def tres_ao_mesmo_tempo() -> None:
        await asyncio.gather(*(geocodificador.geocodificar(t) for t in ("a1", "b2", "c3")))

    asyncio.run(tres_ao_mesmo_tempo())
    assert esperas == [pytest.approx(1.0), pytest.approx(1.0)]


# --- Rota HTTP --------------------------------------------------------------


class GeocodificadorFalso:
    """Substituto do Geocodificador nos testes da rota: devolve algo pronto ou levanta erro."""

    def __init__(self, resultado=None, erro: Exception | None = None) -> None:
        self.resultado = resultado
        self.erro = erro
        self.consultas: list[str] = []

    async def geocodificar(self, consulta: str):
        self.consultas.append(consulta)
        if self.erro is not None:
            raise self.erro
        return self.resultado


@pytest.fixture
def cliente():
    """TestClient que troca o geocodificador real por um falso e limpa depois."""

    def configurar(falso: GeocodificadorFalso) -> TestClient:
        app.dependency_overrides[obter_geocodificador] = lambda: falso
        return TestClient(app)

    yield configurar
    app.dependency_overrides.clear()


def test_rota_responde_200_com_o_modelo(cliente):
    localizacao = Localizacao(
        lat=-1.45, lon=-48.49, rotulo="Campina, Belém - PA", fonte="viacep+nominatim"
    )
    falso = GeocodificadorFalso(resultado=localizacao)

    resposta = cliente(falso).get("/api/geocodificar", params={"q": "Campina"})

    assert resposta.status_code == 200
    assert resposta.json() == {
        "lat": -1.45,
        "lon": -48.49,
        "rotulo": "Campina, Belém - PA",
        "fonte": "viacep+nominatim",
    }
    assert falso.consultas == ["Campina"]


def test_rota_responde_404_quando_nao_encontra(cliente):
    resposta = cliente(GeocodificadorFalso(resultado=None)).get(
        "/api/geocodificar", params={"q": "Atlantida"}
    )
    assert resposta.status_code == 404
    corpo = resposta.json()
    assert corpo["erro"] == "nao_encontrado"
    assert corpo["mensagem"]


def test_rota_responde_503_quando_o_servico_externo_falha(cliente):
    falso = GeocodificadorFalso(erro=ServicoExternoIndisponivel("fora do ar"))
    resposta = cliente(falso).get("/api/geocodificar", params={"q": "Campina"})
    assert resposta.status_code == 503
    corpo = resposta.json()
    assert corpo["erro"] == "servico_indisponivel"
    assert corpo["mensagem"]


def test_rota_recusa_q_de_um_caractere_com_400(cliente):
    falso = GeocodificadorFalso()
    resposta = cliente(falso).get("/api/geocodificar", params={"q": "a"})
    assert resposta.status_code == 400
    assert resposta.json()["erro"] == "parametro_invalido"
    assert falso.consultas == []  # nem chegou a consultar


def test_rota_recusa_q_ausente_com_400(cliente):
    resposta = cliente(GeocodificadorFalso()).get("/api/geocodificar")
    assert resposta.status_code == 400
    assert resposta.json()["erro"] == "parametro_invalido"
