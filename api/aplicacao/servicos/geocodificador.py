"""Geocodificação: transforma CEP ou bairro em coordenada (SPEC §10).

TODO (etapa "API" da SPEC §13):
- CEP com 8 dígitos: ViaCEP -> endereço -> Nominatim.
- Texto: Nominatim, limitado à área de Belém (parâmetros viewbox e bounded=1).
- No máximo 1 requisição por segundo ao Nominatim e User-Agent identificando o
  projeto (regras de uso do Nominatim, RNF08).
- Sempre consultar o cache (servicos/cache.py) antes de chamar a rede.
"""
