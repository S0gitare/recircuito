"""Geocodificação: transforma CEP ou bairro em coordenada (SPEC §10).

Fluxo:
- CEP (8 dígitos): ViaCEP devolve o endereço -> Nominatim acha a coordenada.
- Texto livre (bairro, rua): Nominatim direto, limitado à área de Belém.
- Antes de qualquer chamada de rede, consulta o cache (servicos/cache.py).

Regras de uso do Nominatim que este módulo cumpre (RNF08):
- no máximo 1 requisição por segundo;
- User-Agent que identifica o projeto (o padrão do httpx seria bloqueado);
- resultados guardados em cache.
"""

import asyncio
import re
import time
from collections.abc import Awaitable, Callable

import httpx

from aplicacao.configuracao import configuracoes
from aplicacao.modelos import Localizacao
from aplicacao.servicos.cache import CacheDeGeocodificacao, normalizar_consulta

URL_VIACEP = "https://viacep.com.br/ws/{cep}/json/"
URL_NOMINATIM = "https://nominatim.openstreetmap.org/search"

# Caixa que envolve Belém: esquerda, topo, direita, base (longitude/latitude).
# Com bounded=1 o Nominatim ignora resultados fora dela, evitando que "Nazaré"
# devolva uma cidade homônima em outro estado.
CAIXA_DE_BELEM = "-48.60,-1.20,-48.35,-1.55"

PADRAO_CEP = re.compile(r"^\d{5}-?\d{3}$")


class ServicoExternoIndisponivel(Exception):
    """ViaCEP ou Nominatim fora do ar, lentos demais ou com resposta inesperada."""


class Geocodificador:
    def __init__(
        self,
        cache: CacheDeGeocodificacao,
        fabrica_de_cliente: Callable[[], httpx.AsyncClient] | None = None,
        intervalo_entre_chamadas: float = 1.0,
        relogio: Callable[[], float] = time.monotonic,
        dormir: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        self._cache = cache
        self._fabrica_de_cliente = fabrica_de_cliente or self._criar_cliente_padrao
        self._intervalo = intervalo_entre_chamadas
        self._relogio = relogio
        self._dormir = dormir
        self._trava = asyncio.Lock()
        self._ultima_chamada: float | None = None

    @staticmethod
    def _criar_cliente_padrao() -> httpx.AsyncClient:
        return httpx.AsyncClient(
            timeout=8.0,
            headers={"User-Agent": configuracoes.agente_http, "Accept-Language": "pt-BR"},
        )

    async def geocodificar(self, consulta: str) -> Localizacao | None:
        """Devolve a Localizacao, ou None se não encontrar em Belém.

        Levanta ServicoExternoIndisponivel se a rede ou os serviços falharem.
        """
        texto = consulta.strip()
        # Só espaços (ou 1 caractere) passa pela validação da rota, que conta o
        # texto bruto. Sem esta guarda, o Nominatim receberia apenas "Belém" e
        # devolveria o centro da cidade como se fosse o resultado da busca.
        if len(texto) < 2:
            return None
        if PADRAO_CEP.match(texto):
            cep = texto.replace("-", "")
            chave = f"cep:{cep}"
        else:
            cep = None
            chave = f"texto:{normalizar_consulta(texto)}"

        guardado = self._cache.obter(chave)
        if guardado is not None:
            return Localizacao(**guardado)

        try:
            async with self._fabrica_de_cliente() as cliente:
                if cep is not None:
                    localizacao = await self._por_cep(cep, cliente)
                else:
                    localizacao = await self._por_texto(texto, cliente)
        except (httpx.HTTPError, ValueError, KeyError, TypeError, AttributeError) as erro:
            # ValueError cobre JSON inválido; KeyError, campo faltando; TypeError e
            # AttributeError, JSON válido mas de outro formato (ex.: lista no lugar
            # de objeto). Tudo isso significa "o serviço respondeu algo inesperado".
            raise ServicoExternoIndisponivel(str(erro)) from erro

        if localizacao is not None:
            self._cache.guardar(chave, localizacao.model_dump())
        return localizacao

    async def _por_cep(self, cep: str, cliente: httpx.AsyncClient) -> Localizacao | None:
        resposta = await cliente.get(URL_VIACEP.format(cep=cep))
        # O ViaCEP responde 400 para CEP malformado e 200 com {"erro": true}
        # para CEP que não existe. Os dois significam "não encontrado".
        if resposta.status_code in (400, 404):
            return None
        resposta.raise_for_status()
        dados = resposta.json()
        if dados.get("erro"):
            return None
        # O serviço é só para Belém (SPEC §2): CEP de outra cidade não serve.
        if normalizar_consulta(dados.get("localidade") or "") != "belem":
            return None

        logradouro = dados.get("logradouro") or ""
        bairro = dados.get("bairro") or ""
        achado = await self._buscar_no_nominatim(
            _juntar(logradouro, bairro, "Belém", "PA", "Brasil"), cliente
        )
        # CEPs de rua inteira costumam falhar no Nominatim; o bairro já serve
        # para centralizar o mapa.
        if achado is None and logradouro and bairro:
            achado = await self._buscar_no_nominatim(
                _juntar(bairro, "Belém", "PA", "Brasil"), cliente
            )
        if achado is None:
            return None

        rotulo = f"{bairro or logradouro}, Belém - PA"
        return Localizacao(lat=achado[0], lon=achado[1], rotulo=rotulo, fonte="viacep+nominatim")

    async def _por_texto(self, texto: str, cliente: httpx.AsyncClient) -> Localizacao | None:
        achado = await self._buscar_no_nominatim(_juntar(texto, "Belém", "Pará", "Brasil"), cliente)
        if achado is None:
            return None
        return Localizacao(
            lat=achado[0], lon=achado[1], rotulo=f"{texto.title()}, Belém - PA", fonte="nominatim"
        )

    async def _buscar_no_nominatim(
        self, consulta: str, cliente: httpx.AsyncClient
    ) -> tuple[float, float] | None:
        await self._esperar_a_vez()
        resposta = await cliente.get(
            URL_NOMINATIM,
            params={
                "q": consulta,
                "format": "jsonv2",
                "limit": 1,
                "countrycodes": "br",
                "viewbox": CAIXA_DE_BELEM,
                "bounded": 1,
            },
        )
        resposta.raise_for_status()
        resultados = resposta.json()
        if not resultados:
            return None
        return float(resultados[0]["lat"]), float(resultados[0]["lon"])

    async def _esperar_a_vez(self) -> None:
        """Garante pelo menos `intervalo` segundos entre duas chamadas ao Nominatim.

        A trava (Lock) faz as requisições simultâneas entrarem numa fila: sem ela,
        duas pessoas buscando ao mesmo tempo furariam o limite de 1 por segundo.
        """
        async with self._trava:
            if self._ultima_chamada is not None:
                falta = self._intervalo - (self._relogio() - self._ultima_chamada)
                if falta > 0:
                    await self._dormir(falta)
            self._ultima_chamada = self._relogio()


def _juntar(*partes: str) -> str:
    """Junta só as partes que não estão vazias: ("Rua X", "", "Belém") -> "Rua X, Belém"."""
    return ", ".join(parte for parte in partes if parte)


# Instância única usada pela rota. Fica aqui (e não na rota) para o cache e o
# controle de 1 requisição por segundo valerem para a API inteira.
geocodificador = Geocodificador(
    CacheDeGeocodificacao(arquivo=configuracoes.arquivo_cache_geocodificacao)
)
