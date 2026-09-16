"""Têmpera Simulada para o TSP: vizinhança 2-opt, temperatura calibrada e resfriamento geométrico."""

import math
from collections.abc import Iterator
from dataclasses import dataclass

import numpy as np

from tsp.events import Finished, SAState, StopReason
from tsp.instance import Instance
from tsp.operators import random_order, random_segment, reversal_delta, reverse_segment
from tsp.tour import Tour, cycle_cost


@dataclass(frozen=True, slots=True)
class SAParams:
    """Parâmetros da Têmpera Simulada.

    - `initial_acceptance`: chance de aceitar uma piora típica no início; define a temperatura inicial.
    - `final_acceptance`: chance de aceitar uma piora típica no fim; define a temperatura mínima.
    - `calibration_samples`: movimentos sorteados na rota inicial para medir a piora típica.
    - `cooling_rate`: fator `α` do resfriamento geométrico `T ← α·T`.
    - `plateau_factor`: a temperatura cai a cada `plateau_factor × n` movimentos.
    - `max_evaluations`: orçamento de avaliações da função objetivo.
    - `emit_every`: intervalo, em movimentos, entre dois `SAState` emitidos.

    Levanta `ValueError` se não valer `0 < final_acceptance < initial_acceptance < 1` ou
    `0 < cooling_rate < 1`, se algum inteiro não for positivo ou se `max_evaluations` não passar de
    `calibration_samples + 1` (a rota inicial e a calibração).
    """

    initial_acceptance: float = 0.8
    final_acceptance: float = 0.001
    calibration_samples: int = 100
    cooling_rate: float = 0.95
    plateau_factor: int = 100
    max_evaluations: int = 1_000_000
    emit_every: int = 500

    def __post_init__(self) -> None:
        if not 0 < self.final_acceptance < self.initial_acceptance < 1:
            raise ValueError(
                "é preciso 0 < final_acceptance < initial_acceptance < 1, recebeu "
                f"final_acceptance={self.final_acceptance} e initial_acceptance={self.initial_acceptance}"
            )
        if not 0 < self.cooling_rate < 1:
            raise ValueError(f"cooling_rate precisa estar entre 0 e 1, recebeu {self.cooling_rate}")
        _require_positive("calibration_samples", self.calibration_samples)
        _require_positive("plateau_factor", self.plateau_factor)
        _require_positive("emit_every", self.emit_every)
        if self.max_evaluations <= self.calibration_samples + 1:
            raise ValueError(
                "max_evaluations precisa ser maior que calibration_samples + 1, "
                f"recebeu {self.max_evaluations}"
            )


def simulated_annealing(instance: Instance, params: SAParams, seed: int) -> Iterator[SAState | Finished]:
    """Executa a Têmpera Simulada sobre `instance`, emitindo eventos conforme `tsp.events`.

    Emite o estado inicial, um `SAState` a cada `params.emit_every` movimentos, o último estado e,
    por fim, `Finished`. A rota inicial, cada amostra da calibração e cada movimento proposto contam
    uma avaliação. Para ao atingir a temperatura mínima ou o orçamento de avaliações.
    A mesma `seed` reproduz a mesma busca, qualquer que seja `emit_every`.
    """
    rng = np.random.default_rng(seed)
    distances = instance.distances
    n_cities = instance.n_cities
    order = random_order(n_cities, rng)
    cost = cycle_cost(distances, order)
    typical_worsening = _typical_worsening(distances, order, params.calibration_samples, rng)
    temperature = _temperature_accepting(typical_worsening, params.initial_acceptance)
    min_temperature = _temperature_accepting(typical_worsening, params.final_acceptance)
    best_order, best_cost = order.copy(), cost
    plateau = params.plateau_factor * n_cities
    iteration, evaluations = 0, 1 + params.calibration_samples
    worsening_proposed, worsening_accepted = 0, 0
    last_emitted = iteration
    yield _state(instance, order, best_order, iteration, evaluations, temperature, 0, 0)

    while (reason := _stop_reason(temperature, min_temperature, evaluations, params.max_evaluations)) is None:
        i, j = random_segment(n_cities, rng)
        delta = reversal_delta(distances, order, i, j)
        iteration += 1
        evaluations += 1
        is_worsening = delta > 0
        accepted = _accepts(delta, temperature, rng)
        worsening_proposed += is_worsening
        worsening_accepted += is_worsening and accepted
        if accepted:
            reverse_segment(order, i, j)
            cost += delta
            if cost < best_cost:
                best_order[:] = order
                best_cost = cost
        if iteration % plateau == 0:
            temperature *= params.cooling_rate
        if iteration % params.emit_every == 0:
            yield _state(
                instance,
                order,
                best_order,
                iteration,
                evaluations,
                temperature,
                worsening_proposed,
                worsening_accepted,
            )
            last_emitted = iteration

    if last_emitted != iteration:
        yield _state(
            instance,
            order,
            best_order,
            iteration,
            evaluations,
            temperature,
            worsening_proposed,
            worsening_accepted,
        )
    yield Finished(best=Tour(instance, best_order), iterations=iteration, evaluations=evaluations, reason=reason)


def _typical_worsening(
    distances: np.ndarray, order: np.ndarray, samples: int, rng: np.random.Generator
) -> float:
    n_cities = len(order)
    deltas = np.array(
        [reversal_delta(distances, order, *random_segment(n_cities, rng)) for _ in range(samples)]
    )
    worsening = deltas[deltas > 0]
    match worsening.size:
        case 0:
            return 0.0
        case _:
            return float(worsening.mean())


def _temperature_accepting(worsening: float, probability: float) -> float:
    return -worsening / math.log(probability)


def _stop_reason(
    temperature: float, min_temperature: float, evaluations: int, max_evaluations: int
) -> StopReason | None:
    match (temperature <= min_temperature, evaluations >= max_evaluations):
        case (True, _):
            return StopReason.MIN_TEMPERATURE
        case (_, True):
            return StopReason.MAX_EVALUATIONS
        case _:
            return None


def _accepts(delta: float, temperature: float, rng: np.random.Generator) -> bool:
    match delta:
        case improving if improving <= 0:
            return True
        case worsening:
            return rng.random() < math.exp(-worsening / temperature)


def _state(
    instance: Instance,
    order: np.ndarray,
    best_order: np.ndarray,
    iteration: int,
    evaluations: int,
    temperature: float,
    worsening_proposed: int,
    worsening_accepted: int,
) -> SAState:
    return SAState(
        iteration=iteration,
        current=Tour(instance, order),
        best=Tour(instance, best_order),
        evaluations=evaluations,
        temperature=temperature,
        worsening_proposed=worsening_proposed,
        worsening_accepted=worsening_accepted,
    )


def _require_positive(name: str, value: int) -> None:
    if value < 1:
        raise ValueError(f"{name} precisa ser positivo, recebeu {value}")
