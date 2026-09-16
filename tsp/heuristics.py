"""Heurística construtiva usada como referência de qualidade nos experimentos."""

import numpy as np

from tsp.instance import Instance
from tsp.tour import Tour


def nearest_neighbor(instance: Instance, start: int = 0) -> Tour:
    """Rota do vizinho mais próximo: parte de `start` e sempre vai à cidade mais próxima ainda não visitada.

    Determinística e O(n²); empates vão para a cidade de menor índice.
    Levanta `ValueError` se `start` não for uma cidade da instância.
    """
    n_cities = instance.n_cities
    if not 0 <= start < n_cities:
        raise ValueError(f"start precisa estar entre 0 e {n_cities - 1}, recebeu {start}")
    order = np.empty(n_cities, dtype=np.intp)
    visited = np.zeros(n_cities, dtype=bool)
    current = start
    for position in range(n_cities):
        order[position] = current
        visited[current] = True
        current = int(np.argmin(np.where(visited, np.inf, instance.distances[current])))
    return Tour(instance, order)
