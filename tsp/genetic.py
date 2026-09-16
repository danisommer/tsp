"""Algoritmo Genético para o TSP: torneio, cruzamento OX, mutação por inversão e elitismo."""

import math
from collections.abc import Iterator
from dataclasses import dataclass

import numpy as np

from tsp.events import Finished, GAState, StopReason
from tsp.instance import Instance
from tsp.operators import order_crossover, random_order, random_segment, reverse_segment
from tsp.tour import Tour, cycle_cost


@dataclass(frozen=True, slots=True)
class GAParams:
    """Parâmetros do Algoritmo Genético.

    - `population_size`: rotas na população, o mesmo valor para qualquer instância.
    - `elite_size`: melhores rotas copiadas intactas para a geração seguinte.
    - `tournament_size`: rotas sorteadas, com reposição, em cada torneio de seleção.
    - `crossover_rate`: chance de o filho vir do cruzamento OX; senão, é cópia do primeiro pai.
    - `mutation_rate`: chance de o filho ter um trecho invertido.
    - `stagnation_limit`: gerações seguidas sem melhorar a melhor rota até parar.
    - `max_evaluations`: orçamento de avaliações da função objetivo.
    - `emit_every`: intervalo, em gerações, entre dois `GAState` emitidos.

    Levanta `ValueError` se `population_size < 2`, se não valer `1 <= elite_size < population_size`
    ou `1 <= tournament_size <= population_size`, se alguma taxa estiver fora de [0, 1], se
    `stagnation_limit` ou `emit_every` não forem positivos ou se `max_evaluations` não cobrir a
    população inicial e uma geração.
    """

    population_size: int = 100
    elite_size: int = 2
    tournament_size: int = 3
    crossover_rate: float = 0.9
    mutation_rate: float = 0.2
    stagnation_limit: int = 200
    max_evaluations: int = 1_000_000
    emit_every: int = 1

    def __post_init__(self) -> None:
        _require_in_range("population_size", self.population_size, 2, math.inf)
        _require_in_range("elite_size", self.elite_size, 1, self.population_size - 1)
        _require_in_range("tournament_size", self.tournament_size, 1, self.population_size)
        _require_in_range("crossover_rate", self.crossover_rate, 0.0, 1.0)
        _require_in_range("mutation_rate", self.mutation_rate, 0.0, 1.0)
        _require_in_range("stagnation_limit", self.stagnation_limit, 1, math.inf)
        _require_in_range("emit_every", self.emit_every, 1, math.inf)
        _require_in_range(
            "max_evaluations",
            self.max_evaluations,
            self.population_size + self.children_per_generation,
            math.inf,
        )

    @property
    def children_per_generation(self) -> int:
        return self.population_size - self.elite_size


def genetic_algorithm(instance: Instance, params: GAParams, seed: int) -> Iterator[GAState | Finished]:
    """Executa o Algoritmo Genético sobre `instance`, emitindo eventos conforme `tsp.events`.

    Emite o estado inicial, um `GAState` a cada `params.emit_every` gerações, o último estado e,
    por fim, `Finished`. Cada rota da população inicial e cada filho contam uma avaliação.
    Para por estagnação ou quando a próxima geração não cabe no orçamento, que nunca é ultrapassado.
    A mesma `seed` reproduz a mesma busca, qualquer que seja `emit_every`.
    """
    rng = np.random.default_rng(seed)
    distances = instance.distances
    population = np.array([random_order(instance.n_cities, rng) for _ in range(params.population_size)])
    costs = np.array([cycle_cost(distances, order) for order in population])
    generation, evaluations = 0, params.population_size
    best_cost, stagnant = float(costs.min()), 0
    last_emitted = generation
    yield _state(instance, population, costs, generation, evaluations)

    while (reason := _stop_reason(stagnant, evaluations, params)) is None:
        population, costs = _next_generation(distances, population, costs, params, rng)
        generation += 1
        evaluations += params.children_per_generation
        stagnant, best_cost = _stagnation(stagnant, best_cost, float(costs.min()))
        if generation % params.emit_every == 0:
            yield _state(instance, population, costs, generation, evaluations)
            last_emitted = generation

    if last_emitted != generation:
        yield _state(instance, population, costs, generation, evaluations)
    yield Finished(
        best=Tour(instance, population[np.argmin(costs)]),
        iterations=generation,
        evaluations=evaluations,
        reason=reason,
    )


def _next_generation(
    distances: np.ndarray,
    population: np.ndarray,
    costs: np.ndarray,
    params: GAParams,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    elite = np.argsort(costs, kind="stable")[: params.elite_size]
    next_population = np.empty_like(population)
    next_costs = np.empty_like(costs)
    next_population[: params.elite_size] = population[elite]
    next_costs[: params.elite_size] = costs[elite]
    for slot in range(params.elite_size, params.population_size):
        parent_1 = population[_tournament(costs, params.tournament_size, rng)]
        parent_2 = population[_tournament(costs, params.tournament_size, rng)]
        child = _offspring(parent_1, parent_2, params, rng)
        next_population[slot] = child
        next_costs[slot] = cycle_cost(distances, child)
    return next_population, next_costs


def _tournament(costs: np.ndarray, size: int, rng: np.random.Generator) -> int:
    contestants = rng.integers(len(costs), size=size)
    return int(contestants[np.argmin(costs[contestants])])


def _offspring(
    parent_1: np.ndarray, parent_2: np.ndarray, params: GAParams, rng: np.random.Generator
) -> np.ndarray:
    n_cities = len(parent_1)
    child = (
        order_crossover(parent_1, parent_2, *random_segment(n_cities, rng))
        if rng.random() < params.crossover_rate
        else parent_1.copy()
    )
    if rng.random() < params.mutation_rate:
        reverse_segment(child, *random_segment(n_cities, rng))
    return child


def _stagnation(stagnant: int, best_cost: float, generation_best: float) -> tuple[int, float]:
    return (0, generation_best) if generation_best < best_cost else (stagnant + 1, best_cost)


def _stop_reason(stagnant: int, evaluations: int, params: GAParams) -> StopReason | None:
    match (
        stagnant >= params.stagnation_limit,
        evaluations + params.children_per_generation > params.max_evaluations,
    ):
        case (True, _):
            return StopReason.STAGNATION
        case (_, True):
            return StopReason.MAX_EVALUATIONS
        case _:
            return None


def _state(
    instance: Instance, population: np.ndarray, costs: np.ndarray, generation: int, evaluations: int
) -> GAState:
    leader = Tour(instance, population[np.argmin(costs)])
    return GAState(
        iteration=generation,
        current=leader,
        best=leader,
        evaluations=evaluations,
        mean_cost=float(costs.mean()),
        worst_cost=float(costs.max()),
    )


def _require_in_range(name: str, value: float, low: float, high: float) -> None:
    if not low <= value <= high:
        raise ValueError(f"{name} precisa estar entre {low} e {high}, recebeu {value}")
