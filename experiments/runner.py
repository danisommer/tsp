"""Execução e agregação dos experimentos, sem parte gráfica."""

import math
import time
from collections import Counter
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, replace
from enum import Enum
from statistics import fmean, stdev

import numpy as np

from tsp import (
    Finished,
    GAParams,
    Instance,
    SAParams,
    SearchState,
    StopReason,
    cycle_cost,
    genetic_algorithm,
    nearest_neighbor,
    random_order,
    random_uniform,
    record,
    simulated_annealing,
)

SECONDS_PER_YEAR = 365.25 * 24 * 3600


class Algorithm(Enum):
    """Algoritmos comparados na rodada."""

    SIMULATED_ANNEALING = "tempera"
    GENETIC_ALGORITHM = "ag"


@dataclass(frozen=True, slots=True)
class RunRecord:
    """Resultado de uma execução de um algoritmo numa instância da rodada.

    `reference_cost` é o custo da rota do vizinho mais próximo na mesma instância.
    Levanta `ValueError` se `reference_cost` não for positivo.
    """

    n_cities: int
    instance_seed: int
    algorithm: Algorithm
    initial_cost: float
    final_cost: float
    reference_cost: float
    evaluations: int
    iterations: int
    elapsed_seconds: float
    stop_reason: StopReason

    def __post_init__(self) -> None:
        if not self.reference_cost > 0:
            raise ValueError(f"reference_cost precisa ser positivo, recebeu {self.reference_cost}")

    @property
    def gap_to_reference(self) -> float:
        """Diferença relativa do custo final para a referência: negativa quando o algoritmo é melhor."""
        return (self.final_cost - self.reference_cost) / self.reference_cost


@dataclass(frozen=True, slots=True)
class SummaryRow:
    """Agregado das execuções de um algoritmo num tamanho de instância.

    `wins` conta as instâncias em que o algoritmo terminou com custo estritamente menor que o outro.
    """

    n_cities: int
    algorithm: Algorithm
    runs: int
    mean_final_cost: float
    mean_gap: float
    std_gap: float
    best_gap: float
    worst_gap: float
    wins: int
    mean_evaluations: float
    mean_seconds: float
    evaluations_per_second: float
    stop_reasons: tuple[tuple[StopReason, int], ...]


@dataclass(frozen=True, slots=True)
class SearchSpaceRow:
    """Tamanho do espaço de busca de um tamanho de instância e a velocidade medida da função objetivo."""

    n_cities: int
    log10_tours: float
    evaluations_per_second: float

    @property
    def log10_enumeration_years(self) -> float:
        """log10 dos anos para avaliar todas as rotas distintas na velocidade medida."""
        return self.log10_tours - math.log10(self.evaluations_per_second) - math.log10(SECONDS_PER_YEAR)


def run_experiments(
    sizes: Sequence[int], repetitions: int, sa_params: SAParams, ga_params: GAParams
) -> Iterator[RunRecord]:
    """Para cada tamanho e cada seed de `0` a `repetitions - 1`, gera a instância e roda os dois algoritmos.

    A seed da instância é também a seed dos algoritmos, e os dois resolvem a mesma instância.
    Os algoritmos só emitem o estado inicial e o final, para que o tempo medido seja o da busca.
    Levanta `ValueError`, ao começar a iteração, se `repetitions < 1`.
    """
    if repetitions < 1:
        raise ValueError(f"repetitions precisa ser positivo, recebeu {repetitions}")
    headless_sa = replace(sa_params, emit_every=sa_params.max_evaluations)
    headless_ga = replace(ga_params, emit_every=ga_params.max_evaluations)
    for n_cities in sizes:
        for seed in range(repetitions):
            instance = random_uniform(n_cities, seed)
            reference_cost = nearest_neighbor(instance).cost
            runs = [
                (Algorithm.SIMULATED_ANNEALING, simulated_annealing(instance, headless_sa, seed)),
                (Algorithm.GENETIC_ALGORITHM, genetic_algorithm(instance, headless_ga, seed)),
            ]
            for algorithm, events in runs:
                yield _record(instance, seed, reference_cost, algorithm, events)


def summarize(records: Sequence[RunRecord]) -> list[SummaryRow]:
    """Um `SummaryRow` por tamanho e algoritmo, na ordem em que aparecem em `records`."""
    groups: dict[tuple[int, Algorithm], list[RunRecord]] = {}
    by_instance: dict[tuple[int, int], list[RunRecord]] = {}
    for run in records:
        groups.setdefault((run.n_cities, run.algorithm), []).append(run)
        by_instance.setdefault((run.n_cities, run.instance_seed), []).append(run)
    return [
        _summary_row(n_cities, algorithm, group, sum(_wins(run, by_instance) for run in group))
        for (n_cities, algorithm), group in groups.items()
    ]


def search_space(sizes: Sequence[int], samples: int = 2000, seed: int = 0) -> list[SearchSpaceRow]:
    """Para cada tamanho: log10 das (n−1)!/2 rotas distintas e avaliações completas por segundo medidas."""
    rng = np.random.default_rng(seed)
    return [
        SearchSpaceRow(
            n_cities=n_cities,
            log10_tours=_log10_distinct_tours(n_cities),
            evaluations_per_second=measure_evaluation_rate(random_uniform(n_cities, seed), samples, rng),
        )
        for n_cities in sizes
    ]


def measure_evaluation_rate(instance: Instance, samples: int, rng: np.random.Generator) -> float:
    """Avaliações completas da função objetivo (`cycle_cost`) por segundo, em rotas aleatórias.

    Levanta `ValueError` se `samples < 1`.
    """
    if samples < 1:
        raise ValueError(f"samples precisa ser positivo, recebeu {samples}")
    orders = [random_order(instance.n_cities, rng) for _ in range(samples)]
    start = time.perf_counter()
    for order in orders:
        cycle_cost(instance.distances, order)
    return samples / (time.perf_counter() - start)


def _record(
    instance: Instance,
    seed: int,
    reference_cost: float,
    algorithm: Algorithm,
    events: Iterator[SearchState | Finished],
) -> RunRecord:
    run = record(events)
    return RunRecord(
        n_cities=instance.n_cities,
        instance_seed=seed,
        algorithm=algorithm,
        initial_cost=run.states[0].best.cost,
        final_cost=run.finished.best.cost,
        reference_cost=reference_cost,
        evaluations=run.finished.evaluations,
        iterations=run.finished.iterations,
        elapsed_seconds=run.elapsed_seconds,
        stop_reason=run.finished.reason,
    )


def _summary_row(n_cities: int, algorithm: Algorithm, group: list[RunRecord], wins: int) -> SummaryRow:
    gaps = [run.gap_to_reference for run in group]
    total_seconds = sum(run.elapsed_seconds for run in group)
    reasons = Counter(run.stop_reason for run in group)
    return SummaryRow(
        n_cities=n_cities,
        algorithm=algorithm,
        runs=len(group),
        mean_final_cost=fmean(run.final_cost for run in group),
        mean_gap=fmean(gaps),
        std_gap=stdev(gaps) if len(gaps) > 1 else 0.0,
        best_gap=min(gaps),
        worst_gap=max(gaps),
        wins=wins,
        mean_evaluations=fmean(run.evaluations for run in group),
        mean_seconds=total_seconds / len(group),
        evaluations_per_second=sum(run.evaluations for run in group) / total_seconds,
        stop_reasons=tuple(sorted(reasons.items(), key=lambda item: item[0].value)),
    )


def _wins(run: RunRecord, by_instance: dict[tuple[int, int], list[RunRecord]]) -> bool:
    same_instance = by_instance[(run.n_cities, run.instance_seed)]
    rivals = [other for other in same_instance if other.algorithm is not run.algorithm]
    return bool(rivals) and all(run.final_cost < rival.final_cost for rival in rivals)


def _log10_distinct_tours(n_cities: int) -> float:
    return math.lgamma(n_cities) / math.log(10) - math.log10(2)
