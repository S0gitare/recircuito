"""Cache das geocodificações (texto buscado -> coordenada).

Por que existe: o Nominatim e o ViaCEP são serviços públicos e gratuitos. Pedir
a mesma coisa duas vezes a eles é desperdício e pode levar a um bloqueio
(RNF08). Com o cache, a segunda pessoa que buscar "Campina" é atendida sem
nenhuma chamada externa.

Privacidade (LGPD, RNF06): o cache guarda SÓ o par "consulta normalizada ->
localização". Nada de IP, horário da busca ou qualquer dado de quem pesquisou.

O cache vive na memória, com validade de 30 dias. Em execução local, também é
gravado em arquivo (pasta api/.cache/, ignorada pelo Git) para sobreviver a
reinicializações da API. No ambiente serverless da Vercel a pasta do código é
somente leitura (e eventual arquivo via RECIRCUITO_ARQUIVO_CACHE em /tmp é
efêmero entre instâncias e deploys — diferente de avaliações/sugestões em
registro_json.py, que usam /tmp/recircuito como reserva), então em produção o
cache opera prioritariamente em memória.
"""

import json
import re
import time
import unicodedata
from collections.abc import Callable
from pathlib import Path
from typing import Any

TRINTA_DIAS_EM_SEGUNDOS = 30 * 24 * 60 * 60

# Teto de entradas: sem ele, alguém poderia encher a memória da API buscando
# milhares de textos diferentes.
LIMITE_DE_ENTRADAS = 5000


def normalizar_consulta(texto: str) -> str:
    """Padroniza o texto para que variações da mesma busca caiam na mesma chave.

    "  Campina " e "campína" viram "campina". Decompor os caracteres (NFKD)
    separa a letra do acento; depois descartamos os acentos soltos.
    """
    decomposto = unicodedata.normalize("NFKD", texto)
    sem_acentos = "".join(c for c in decomposto if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", sem_acentos).strip().lower()


def _entrada_valida(entrada: Any) -> bool:
    """Confere o formato de uma entrada lida do arquivo, que pode ter sido editado à mão."""
    return (
        isinstance(entrada, dict)
        and isinstance(entrada.get("expira_em"), int | float)
        and isinstance(entrada.get("valor"), dict)
    )


class CacheDeGeocodificacao:
    def __init__(
        self,
        validade_em_segundos: int = TRINTA_DIAS_EM_SEGUNDOS,
        arquivo: Path | None = None,
        # O relógio é um parâmetro para os testes poderem "avançar o tempo"
        # sem esperar 30 dias de verdade.
        relogio: Callable[[], float] = time.time,
        limite_de_entradas: int = LIMITE_DE_ENTRADAS,
    ) -> None:
        self._validade = validade_em_segundos
        self._arquivo = arquivo
        self._relogio = relogio
        self._limite = limite_de_entradas
        # Dicionários do Python preservam a ordem de inserção; usamos isso para
        # descartar as entradas mais antigas quando o limite é atingido.
        self._entradas: dict[str, dict[str, Any]] = {}
        self._carregar_do_arquivo()

    def obter(self, chave: str) -> dict[str, Any] | None:
        """Devolve o valor guardado, ou None se não existir ou já tiver expirado."""
        entrada = self._entradas.get(chave)
        if entrada is None:
            return None
        if entrada["expira_em"] <= self._relogio():
            del self._entradas[chave]
            return None
        return entrada["valor"]

    def guardar(self, chave: str, valor: dict[str, Any]) -> None:
        # Remover antes de inserir move a chave para o fim da fila (a mais nova).
        self._entradas.pop(chave, None)
        self._entradas[chave] = {"valor": valor, "expira_em": self._relogio() + self._validade}
        while len(self._entradas) > self._limite:
            self._entradas.pop(next(iter(self._entradas)))
        self._salvar_no_arquivo()

    def __len__(self) -> int:
        return len(self._entradas)

    def _carregar_do_arquivo(self) -> None:
        if self._arquivo is None or not self._arquivo.exists():
            return
        try:
            conteudo = json.loads(self._arquivo.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            # Arquivo corrompido não pode derrubar a API: começamos com o cache vazio.
            # (JSONDecodeError e UnicodeDecodeError são subclasses de ValueError.)
            return
        if not isinstance(conteudo, dict):
            # JSON válido, mas não é o nosso formato (ex.: uma lista): também ignoramos.
            return
        agora = self._relogio()
        self._entradas = {
            chave: entrada
            for chave, entrada in conteudo.items()
            if _entrada_valida(entrada) and entrada["expira_em"] > agora
        }

    def _salvar_no_arquivo(self) -> None:
        if self._arquivo is None:
            return
        try:
            self._arquivo.parent.mkdir(parents=True, exist_ok=True)
            # Grava num arquivo temporário e troca no final: se a API cair no
            # meio da escrita, o arquivo antigo continua inteiro.
            temporario = self._arquivo.with_suffix(".tmp")
            temporario.write_text(json.dumps(self._entradas, ensure_ascii=False), encoding="utf-8")
            temporario.replace(self._arquivo)
        except OSError:
            # Pasta somente leitura (ex.: ambiente serverless na Vercel): seguimos só com a memória.
            pass
