"""Geradores de instâncias sintéticas."""

import numpy as np

from tsp.instance import Instance
from tsp.metric import Metric


def random_uniform(
    n_cities: int,
    seed: int,
    *,
    side: float = 1000.0,
    metric: Metric = Metric.EUCLIDEAN,
) -> Instance:
    """Instância com `n_cities` cidades sorteadas uniformemente no quadrado [0, side]².

    A mesma `seed` sempre gera a mesma instância.
    Levanta `ValueError` se `side` não for positivo ou se a instância resultante for inválida.
    """
    if side <= 0:
        raise ValueError(f"side precisa ser positivo, recebeu {side}")
    rng = np.random.default_rng(seed)
    coords = rng.uniform(0.0, side, size=(n_cities, 2))
    return Instance(name=f"uniform-n{n_cities}-seed{seed}", coords=coords, metric=metric)
