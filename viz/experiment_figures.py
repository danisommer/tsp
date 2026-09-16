"""Figuras agregadas da rodada de experimentos, como `matplotlib.figure.Figure`, sem abrir janela."""

from collections.abc import Callable, Sequence
from statistics import fmean
from typing import assert_never

from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import PercentFormatter

from experiments.runner import Algorithm, RunRecord
from viz.charts import CONTEXT_COLOR, GA_COLOR, SA_COLOR, style_axes

Measure = Callable[[RunRecord], float]


def experiment_figures(records: Sequence[RunRecord]) -> dict[str, Figure]:
    """Figuras da rodada por nome de arquivo: `custo_final`, `tempo` e `avaliacoes`."""
    return {
        "custo_final": _strip_figure(
            records,
            lambda run: run.gap_to_reference,
            "diferença para o vizinho mais próximo",
            "Custo final relativo ao vizinho mais próximo (abaixo de 0% é melhor)",
            _reference_axis,
        ),
        "tempo": _strip_figure(
            records,
            lambda run: run.elapsed_seconds,
            "tempo de relógio (s, escala log)",
            "Tempo de execução",
            _log_axis,
        ),
        "avaliacoes": _strip_figure(
            records,
            lambda run: run.evaluations,
            "avaliações da função objetivo (escala log)",
            "Avaliações usadas (mesmo orçamento para os dois)",
            _log_axis,
        ),
    }


def _strip_figure(
    records: Sequence[RunRecord],
    measure: Measure,
    ylabel: str,
    title: str,
    configure: Callable[[Axes], None],
) -> Figure:
    sizes = sorted({run.n_cities for run in records})
    figure = Figure(figsize=(8, 4.8), layout="constrained")
    ax = figure.subplots()
    for algorithm in Algorithm:
        name, color, offset = _style_of(algorithm)
        for position, n_cities in enumerate(sizes):
            values = [measure(run) for run in records if run.algorithm is algorithm and run.n_cities == n_cities]
            if not values:
                continue
            ax.scatter(
                [position + offset] * len(values),
                values,
                s=30,
                color=color,
                alpha=0.7,
                zorder=3,
                label=name if position == 0 else None,
            )
            ax.plot(
                [position + offset - 0.12, position + offset + 0.12],
                [fmean(values)] * 2,
                color=color,
                linewidth=3,
                zorder=4,
            )
    ax.set_xticks(range(len(sizes)), [f"{n_cities} cidades" for n_cities in sizes])
    ax.set_xlim(-0.6, len(sizes) - 0.4)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    configure(ax)
    ax.legend()
    style_axes(ax)
    return figure


def _style_of(algorithm: Algorithm) -> tuple[str, str, float]:
    match algorithm:
        case Algorithm.SIMULATED_ANNEALING:
            return "Têmpera Simulada", SA_COLOR, -0.18
        case Algorithm.GENETIC_ALGORITHM:
            return "Algoritmo Genético", GA_COLOR, 0.18
        case _:
            assert_never(algorithm)


def _reference_axis(ax: Axes) -> None:
    ax.axhline(0, color=CONTEXT_COLOR, linewidth=1.2, linestyle="--", label="vizinho mais próximo")
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))


def _log_axis(ax: Axes) -> None:
    ax.set_yscale("log")
