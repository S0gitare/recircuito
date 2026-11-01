"""Distância entre dois pontos na superfície da Terra.

Usamos a fórmula de haversine: ela trata a Terra como uma esfera e calcula a
distância "em linha reta" pela superfície (o arco do grande círculo), não pelas
ruas. Para ordenar pontos dentro de uma cidade isso basta (SPEC §8); o erro por
a Terra não ser uma esfera perfeita fica abaixo de 0,5%.

Dica: não troque por geopandas/shapely, pesados demais para este volume de dados.
Se um dia precisar de distância pelas ruas, isso é trabalho de um serviço de
rotas, não desta função.
"""

from math import asin, cos, radians, sin, sqrt

# Raio médio da Terra em km (valor adotado pela União Geodésica Internacional).
RAIO_DA_TERRA_KM = 6371.0088


def calcular_distancia_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distância em km entre (lat1, lon1) e (lat2, lon2), em graus decimais."""
    # As funções trigonométricas do Python trabalham em radianos, não em graus.
    phi1, phi2 = radians(lat1), radians(lat2)
    delta_phi = radians(lat2 - lat1)
    delta_lambda = radians(lon2 - lon1)

    # "a" é o quadrado da metade da corda entre os dois pontos;
    # "c" é o ângulo central, em radianos, entre eles.
    a = sin(delta_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(delta_lambda / 2) ** 2
    # min() protege contra a > 1 por arredondamento de ponto flutuante,
    # o que faria asin() lançar ValueError em pontos quase antípodas.
    c = 2 * asin(min(1.0, sqrt(a)))
    return RAIO_DA_TERRA_KM * c
