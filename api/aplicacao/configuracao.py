"""Configurações lidas de variáveis de ambiente.

Ficam num só lugar para que a hospedagem (Render) mude o comportamento da API
sem alterar código. Os nomes têm o prefixo RECIRCUITO_ para não colidir com
variáveis de outros programas.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path

PASTA_API = Path(__file__).resolve().parent.parent

# Em desenvolvimento, o Vite usa a porta 5173 (dev) e a 4173 (preview).
ORIGENS_PADRAO = "http://localhost:5173,http://localhost:4173"


def _ler_lista(nome: str, padrao: str) -> list[str]:
    """Lê uma variável de ambiente no formato "a,b,c" e devolve ["a", "b", "c"]."""
    valor = os.getenv(nome, padrao)
    return [item.strip() for item in valor.split(",") if item.strip()]


@dataclass(frozen=True)
class Configuracoes:
    # CORS: só o domínio do site pode chamar a API pelo navegador (SPEC §10).
    # Cuidado: nunca use "*" em produção; qualquer site poderia consumir a API.
    origens_permitidas: list[str] = field(
        default_factory=lambda: _ler_lista("RECIRCUITO_ORIGENS_PERMITIDAS", ORIGENS_PADRAO)
    )
    arquivo_pontos: Path = field(
        default_factory=lambda: (
            PASTA_API / os.getenv("RECIRCUITO_ARQUIVO_PONTOS", "dados/pontos.json")
        )
    )
    arquivo_avaliacoes: Path = field(
        default_factory=lambda: (
            PASTA_API / os.getenv("RECIRCUITO_ARQUIVO_AVALIACOES", "dados/avaliacoes.json")
        )
    )
    arquivo_sugestoes: Path = field(
        default_factory=lambda: (
            PASTA_API / os.getenv("RECIRCUITO_ARQUIVO_SUGESTOES", "dados/sugestoes.json")
        )
    )
    # Identificação enviada ao Nominatim (a política de uso exige um contato real).
    # Em produção, defina RECIRCUITO_CONTATO com o e-mail do projeto.
    agente_http: str = field(
        default_factory=lambda: (
            "ReCircuito/0.1 (projeto de extensao UNINTER; contato: "
            + os.getenv("RECIRCUITO_CONTATO", "nao-informado")
            + ")"
        )
    )
    # Cache de geocodificação em disco. Pasta api/.cache/ já é ignorada pelo Git.
    arquivo_cache_geocodificacao: Path = field(
        default_factory=lambda: (
            PASTA_API
            / os.getenv("RECIRCUITO_ARQUIVO_CACHE", ".cache/geocodificacao.json")
        )
    )
    # Fuso usado no "aberto agora". Belém não tem horário de verão (UTC-3 o ano todo).
    fuso_horario: str = "America/Belem"


configuracoes = Configuracoes()
