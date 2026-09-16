"""Operadores sobre rotas: solução inicial, inversão de trecho e cruzamento OX.

Trabalham com arrays numpy crus, a área de trabalho mutável dos algoritmos, e não com `Tour`.
Não validam a entrada: esperam permutações de `0..n-1` e índices dentro dos limites documentados.
"""

import numpy as np


def random_order(n_cities: int, rng: np.random.Generator) -> np.ndarray:
    """Permutação aleatória e mutável de `0..n_cities-1`: a solução inicial dos dois algoritmos."""
    return rng.permutation(n_cities)


def random_segment(n_cities: int, rng: np.random.Generator) -> tuple[int, int]:
    """Par de posições `(i, j)` com `0 <= i < j < n_cities`, uniforme entre todos os pares, em O(1).

    Define o trecho invertido pelo 2-opt e pela mutação, e os pontos de corte do cruzamento OX.
    """
    first = int(rng.integers(n_cities))
    second = (first + int(rng.integers(1, n_cities))) % n_cities
    return min(first, second), max(first, second)


def reversal_delta(distances: np.ndarray, order: np.ndarray, i: int, j: int) -> float:
    """Variação do custo de `order` se `order[i..j]` for invertido, em O(1) e sem alterar `order`.

    Só duas arestas mudam: saem as que ligam o trecho ao resto da rota e entram as mesmas ligações
    com as pontas trocadas. Inverter a rota inteira (`i = 0`, `j = n-1`) não muda o custo.
    Espera `0 <= i < j < len(order)`.
    """
    n = len(order)
    if i == 0 and j == n - 1:
        return 0.0
    before, first = order[i - 1], order[i]
    last, after = order[j], order[(j + 1) % n]
    return float(
        distances[before, last] + distances[first, after] - distances[before, first] - distances[last, after]
    )


def reverse_segment(order: np.ndarray, i: int, j: int) -> None:
    """Inverte `order[i..j]` no lugar, em O(j - i).

    É o movimento 2-opt da Têmpera Simulada e a mutação por inversão do Algoritmo Genético.
    Levanta `ValueError` se `order` for somente leitura.
    """
    order[i : j + 1] = order[i : j + 1][::-1]


def order_crossover(parent_1: np.ndarray, parent_2: np.ndarray, i: int, j: int) -> np.ndarray:
    """Filho do cruzamento OX, como array novo, em O(n). Não altera os pais.

    Copia `parent_1[i..j]` nas mesmas posições. As posições restantes são preenchidas a partir de
    `j + 1`, de forma circular, com as cidades que faltam na ordem em que aparecem em `parent_2`
    lido também a partir de `j + 1`. Espera `0 <= i <= j < n`.
    """
    n = len(parent_1)
    child = np.empty(n, dtype=parent_1.dtype)
    child[i : j + 1] = parent_1[i : j + 1]
    inherited = np.zeros(n, dtype=bool)
    inherited[parent_1[i : j + 1]] = True
    donor = np.roll(parent_2, -(j + 1))
    missing = donor[~inherited[donor]]
    child[np.arange(j + 1, j + 1 + len(missing)) % n] = missing
    return child
