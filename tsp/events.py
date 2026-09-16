"""Eventos que os algoritmos de busca emitem durante e ao fim da execução.

Durante a execução, cada algoritmo emite o seu tipo de estado (`SAState`, `GAState`),
que compartilham os campos de `SearchState`. O último evento é sempre `Finished`.
Comparações entre custos toleram ruído de ponto flutuante (`COST_REL_TOL`).
"""

import math
from dataclasses import dataclass
from enum import Enum

from tsp.tour import Tour

COST_REL_TOL = 1e-9


class StopReason(Enum):
    """Por que um algoritmo parou."""

    MAX_EVALUATIONS = "max_evaluations"
    MIN_TEMPERATURE = "min_temperature"
    STAGNATION = "stagnation"


@dataclass(frozen=True, slots=True, eq=False)
class SearchState:
    """Campos comuns a todo estado emitido durante a busca.

    - `iteration`: passos já executados (movimentos na têmpera, gerações no AG).
    - `current`: rota atual (na têmpera, a solução corrente; no AG, a melhor da geração).
    - `best`: melhor rota encontrada até agora.
    - `evaluations`: avaliações da função objetivo até agora.

    Levanta `ValueError` se algum contador for negativo, se as rotas forem de instâncias
    diferentes ou se `best` for pior que `current`.
    """

    iteration: int
    current: Tour
    best: Tour
    evaluations: int

    def __post_init__(self) -> None:
        _require_non_negative("iteration", self.iteration)
        _require_non_negative("evaluations", self.evaluations)
        _require_same_instance(self.current, self.best)
        _require_not_worse("best", self.best.cost, "current", self.current.cost)


@dataclass(frozen=True, slots=True, eq=False)
class SAState(SearchState):
    """Estado da Têmpera Simulada: campos comuns mais temperatura e contadores de pioras.

    - `temperature`: temperatura atual.
    - `worsening_proposed`: movimentos propostos até agora que piorariam a rota.
    - `worsening_accepted`: desses, quantos o critério de Metropolis aceitou.

    Levanta `ValueError` se `temperature` for negativa ou não finita, ou se não valer
    `0 <= worsening_accepted <= worsening_proposed <= iteration`.
    """

    temperature: float
    worsening_proposed: int
    worsening_accepted: int

    def __post_init__(self) -> None:
        SearchState.__post_init__(self)
        if not math.isfinite(self.temperature) or self.temperature < 0:
            raise ValueError(f"temperature precisa ser finita e não negativa, recebeu {self.temperature}")
        if not 0 <= self.worsening_accepted <= self.worsening_proposed <= self.iteration:
            raise ValueError(
                "é preciso 0 <= worsening_accepted <= worsening_proposed <= iteration, recebeu "
                f"{self.worsening_accepted}, {self.worsening_proposed} e {self.iteration}"
            )


@dataclass(frozen=True, slots=True, eq=False)
class GAState(SearchState):
    """Estado do Algoritmo Genético: campos comuns mais o custo médio e o pior custo da população.

    Levanta `ValueError` se `mean_cost` ou `worst_cost` não forem finitos, ou se não valer
    custo de `current` (a melhor rota da geração) <= `mean_cost` <= `worst_cost`.
    """

    mean_cost: float
    worst_cost: float

    def __post_init__(self) -> None:
        SearchState.__post_init__(self)
        _require_finite("mean_cost", self.mean_cost)
        _require_finite("worst_cost", self.worst_cost)
        _require_not_worse("current", self.current.cost, "mean_cost", self.mean_cost)
        _require_not_worse("mean_cost", self.mean_cost, "worst_cost", self.worst_cost)


@dataclass(frozen=True, slots=True, eq=False)
class Finished:
    """Último evento de uma execução: melhor rota, totais e motivo da parada.

    Levanta `ValueError` se algum total for negativo.
    """

    best: Tour
    iterations: int
    evaluations: int
    reason: StopReason

    def __post_init__(self) -> None:
        _require_non_negative("iterations", self.iterations)
        _require_non_negative("evaluations", self.evaluations)


def _require_non_negative(name: str, value: int) -> None:
    if value < 0:
        raise ValueError(f"{name} não pode ser negativo, recebeu {value}")


def _require_finite(name: str, value: float) -> None:
    if not math.isfinite(value):
        raise ValueError(f"{name} precisa ser finito, recebeu {value}")


def _require_same_instance(current: Tour, best: Tour) -> None:
    if current.instance is not best.instance:
        raise ValueError("current e best precisam ser rotas da mesma instância")


def _require_not_worse(name: str, cost: float, reference_name: str, reference_cost: float) -> None:
    if cost > reference_cost and not math.isclose(cost, reference_cost, rel_tol=COST_REL_TOL):
        raise ValueError(f"{name} ({cost}) não pode ser pior que {reference_name} ({reference_cost})")
