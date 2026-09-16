"""Uma solução do problema: a ordem de visita das cidades e o seu custo."""

from dataclasses import dataclass, field

import numpy as np

from tsp.instance import Instance


@dataclass(frozen=True, slots=True, eq=False)
class Tour:
    """Um ciclo hamiltoniano sobre `instance`.

    `order` é uma permutação de `0..n-1` e o retorno da última cidade à primeira é implícito.
    `cost` é derivado na construção por `cycle_cost`. `order` é uma cópia somente leitura.
    Levanta `ValueError` se `order` não for uma permutação de inteiros das cidades da instância.
    """

    instance: Instance = field(repr=False)
    order: np.ndarray
    cost: float = field(init=False)

    def __post_init__(self) -> None:
        order = _validated_order(self.order, self.instance.n_cities)
        object.__setattr__(self, "order", order)
        object.__setattr__(self, "cost", cycle_cost(self.instance.distances, order))


def cycle_cost(distances: np.ndarray, order: np.ndarray) -> float:
    """Soma das distâncias entre cidades consecutivas de `order`, incluindo o retorno à origem.

    Não valida a entrada: espera que `order` já seja uma permutação válida.
    """
    return float(distances[order, np.roll(order, -1)].sum())


def _validated_order(raw, n_cities: int) -> np.ndarray:
    order = np.asarray(raw)
    match order.shape:
        case (length,) if length != n_cities:
            raise ValueError(f"order precisa ter {n_cities} cidades, recebeu {length}")
        case (_,) if not np.issubdtype(order.dtype, np.integer):
            raise ValueError(f"order precisa conter inteiros, recebeu {order.dtype}")
        case (_,) if not np.array_equal(np.sort(order), np.arange(n_cities)):
            raise ValueError("order precisa visitar cada cidade exatamente uma vez")
        case (_,):
            validated = order.astype(np.intp, copy=True)
            validated.setflags(write=False)
            return validated
        case shape:
            raise ValueError(f"order precisa ser unidimensional, recebeu formato {shape}")
