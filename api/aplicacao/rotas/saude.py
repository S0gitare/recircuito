"""Rota de saúde, usada pela hospedagem (Vercel) e monitoramento da API para saber se subiu."""

from fastapi import APIRouter

roteador = APIRouter(tags=["saúde"])


@roteador.get("/saude")
def verificar_saude() -> dict[str, str]:
    # Fica de propósito sem ler arquivo nem chamar serviço externo: precisa
    # responder rápido mesmo quando algo mais está fora do ar.
    return {"status": "ok"}
