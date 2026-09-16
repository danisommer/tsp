"""Registro de uma execução completa e as séries derivadas dela.

Nada aqui depende de parte gráfica: são dados prontos para qualquer consumidor.
"""

import time
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

import numpy as np

from tsp.events import COST_REL_TOL, Finished, SAState, SearchState


@dataclass(frozen=True, slots=True, eq=False)
class Run:
    """Uma execução completa de um algoritmo.

    - `states`: estados emitidos, em ordem de iteração, todos do mesmo algoritmo.
    - `finished`: evento final.
    - `elapsed_seconds`: tempo de relógio para consumir a execução inteira.

    Levanta `ValueError` se `states` estiver vazio, misturar algoritmos ou não tiver iterações
    crescentes, ou se `elapsed_seconds` for negativo.
    """

    states: tuple[SearchState, ...]
    finished: Finished
    elapsed_seconds: float

    def __post_init__(self) -> None:
        match self.states:
            case ():
                raise ValueError("uma execução precisa de pelo menos um estado")
            case states if len({type(state) for state in states}) > 1:
                raise ValueError("todos os estados precisam ser do mesmo algoritmo")
            case states if any(a.iteration >= b.iteration for a, b in zip(states, states[1:])):
                raise ValueError("as iterações dos estados precisam ser crescentes")
        if self.elapsed_seconds < 0:
            raise ValueError(f"elapsed_seconds não pode ser negativo, recebeu {self.elapsed_seconds}")


@dataclass(frozen=True, slots=True, eq=False)
class Milestone:
    """Primeiro estado em que a melhor rota atingiu `fraction` da melhora total da execução."""

    fraction: float
    state: SearchState


def record(events: Iterable[SearchState | Finished]) -> Run:
    """Consome `events` até o fim e devolve o `Run`, medindo o tempo de relógio do consumo.

    Levanta `ValueError` se o último evento não for o único `Finished`, ou se não houver estado
    antes dele.
    """
    start = time.perf_counter()
    collected = list(events)
    elapsed = time.perf_counter() - start
    match collected:
        case [*states, Finished() as finished] if not any(isinstance(event, Finished) for event in states):
            return Run(states=tuple(states), finished=finished, elapsed_seconds=elapsed)
        case _:
            raise ValueError("a execução precisa terminar com um único Finished")


def improvement_milestones(run: Run, fractions: Sequence[float]) -> tuple[Milestone, ...]:
    """Marcos de melhoria de `run`, em ordem de iteração.

    Para cada fração `f`, escolhe o primeiro estado cuja melhor rota custe no máximo
    `inicial − f × (inicial − final)`, em que `inicial` é a melhor rota do primeiro estado e `final`
    a de `run.finished`. Frações que caem no mesmo estado viram um marco só, com a maior delas.
    Levanta `ValueError` se alguma fração estiver fora de [0, 1] ou se nenhum estado atingir o alvo.
    """
    costs = np.array([state.best.cost for state in run.states])
    initial, final = costs[0], run.finished.best.cost
    reached: dict[int, float] = {}
    for fraction in sorted(fractions):
        target = initial - _validated_fraction(fraction) * (initial - final)
        reaching = np.flatnonzero(costs <= target + COST_REL_TOL * abs(target))
        match reaching.size:
            case 0:
                raise ValueError(f"nenhum estado atinge {fraction:.0%} da melhora")
            case _:
                reached[int(reaching[0])] = fraction
    return tuple(Milestone(fraction, run.states[index]) for index, fraction in sorted(reached.items()))


def worsening_acceptance(states: Sequence[SAState]) -> tuple[np.ndarray, np.ndarray]:
    """Fração das pioras aceitas em cada intervalo entre estados consecutivos da Têmpera Simulada.

    Devolve as avaliações ao fim de cada intervalo e a fração aceita nele, omitindo os intervalos
    sem nenhuma piora proposta.
    """
    evaluations = np.array([state.evaluations for state in states])
    proposed = np.diff([state.worsening_proposed for state in states])
    accepted = np.diff([state.worsening_accepted for state in states])
    with_worsening = proposed > 0
    return evaluations[1:][with_worsening], accepted[with_worsening] / proposed[with_worsening]


def _validated_fraction(fraction: float) -> float:
    if not 0 <= fraction <= 1:
        raise ValueError(f"fraction precisa estar entre 0 e 1, recebeu {fraction}")
    return fraction
