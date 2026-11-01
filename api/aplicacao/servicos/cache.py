"""Cache das geocodificações (texto buscado -> coordenada).

TODO (etapa "API" da SPEC §13):
- Cache em memória com validade de 30 dias e, opcionalmente, gravado em
  api/.cache/ (pasta já ignorada pelo Git).
- Guardar só o par "texto normalizado -> coordenada". Nada de IP, horário ou
  qualquer dado da pessoa (LGPD, RNF06).
"""
