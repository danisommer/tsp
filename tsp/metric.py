"""Métricas de distância entre cidades."""

from enum import Enum
from typing import assert_never

import numpy as np


class Metric(Enum):
    """Como a distância entre duas cidades é calculada.

    - `EUCLIDEAN`: distância euclidiana real.
    - `EUC_2D`: euclidiana arredondada para o inteiro mais próximo, como na TSPLIB.
    """

    EUCLIDEAN = "euclidean"
    EUC_2D = "euc_2d"


def distance_matrix(coords: np.ndarray, metric: Metric) -> np.ndarray:
    """Matriz (n, n) em float64 com a distância entre todo par de cidades de `coords` (n, 2)."""
    deltas = coords[:, np.newaxis, :] - coords[np.newaxis, :, :]
    euclidean = np.linalg.norm(deltas, axis=-1)
    match metric:
        case Metric.EUCLIDEAN:
            return euclidean
        case Metric.EUC_2D:
            return np.floor(euclidean + 0.5)
        case _:
            assert_never(metric)
