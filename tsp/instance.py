"""A instância do problema: as cidades e as distâncias entre elas."""

from dataclasses import dataclass, field

import numpy as np

from tsp.metric import Metric, distance_matrix

MIN_CITIES = 3


@dataclass(frozen=True, slots=True, eq=False)
class Instance:
    """Uma instância do TSP simétrico.

    Recebe `name`, `coords` (qualquer sequência no formato (n, 2)) e `metric`.
    `distances` é derivada na construção. `coords` e `distances` são cópias somente leitura.
    Levanta `ValueError` se `coords` não tiver formato (n, 2), tiver menos de `MIN_CITIES`
    cidades ou contiver valor não finito.
    """

    name: str
    coords: np.ndarray
    metric: Metric
    distances: np.ndarray = field(init=False, repr=False)

    def __post_init__(self) -> None:
        coords = _validated_coords(self.coords)
        distances = distance_matrix(coords, self.metric)
        distances.setflags(write=False)
        object.__setattr__(self, "coords", coords)
        object.__setattr__(self, "distances", distances)

    @property
    def n_cities(self) -> int:
        return len(self.coords)


def _validated_coords(raw) -> np.ndarray:
    coords = np.array(raw, dtype=np.float64)
    match coords.shape:
        case (n, 2) if n < MIN_CITIES:
            raise ValueError(f"a instância precisa de pelo menos {MIN_CITIES} cidades, recebeu {n}")
        case (_, 2) if not np.isfinite(coords).all():
            raise ValueError("todas as coordenadas precisam ser números finitos")
        case (_, 2):
            coords.setflags(write=False)
            return coords
        case shape:
            raise ValueError(f"coords precisa ter formato (n, 2), recebeu {shape}")
