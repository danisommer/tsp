"""Gráficos e tabelas de execuções registradas (`tsp.Run`) sobre um `Axes` do matplotlib.

As funções só desenham no `ax` recebido: não criam figura nem abrem janela. As séries usam as
avaliações da função objetivo no eixo x, a unidade comum aos dois algoritmos.
"""

from collections.abc import Sequence
from dataclasses import dataclass, fields
from typing import assert_never

from matplotlib.axes import Axes
from matplotlib.ticker import PercentFormatter

from tsp import (
    GAParams,
    GAState,
    Milestone,
    Run,
    SAParams,
    SAState,
    StopReason,
    Tour,
    improvement_milestones,
    worsening_acceptance,
)
from viz.draw import draw_route, draw_tour

SA_COLOR = "#2a78d6"
GA_COLOR = "#eb6834"
CONTEXT_COLOR = "#8c8b85"
GRID_COLOR = "#e4e3de"
TEXT_COLOR = "#52514e"
MILESTONE_FRACTIONS = (0.0, 0.5, 0.8, 0.95, 1.0)
EVALUATIONS_LABEL = "avaliações da função objetivo"


@dataclass(frozen=True, slots=True)
class AlgorithmProfile:
    """Como um algoritmo aparece nas figuras: nome, cor de identidade e nome do passo."""

    name: str
    color: str
    step: str
    steps: str


def profile(run: Run) -> AlgorithmProfile:
    """Perfil do algoritmo que produziu `run`. Levanta `TypeError` para estados desconhecidos."""
    match run.states[0]:
        case SAState():
            return AlgorithmProfile("Têmpera Simulada", SA_COLOR, "movimento", "movimentos")
        case GAState():
            return AlgorithmProfile("Algoritmo Genético", GA_COLOR, "geração", "gerações")
        case other:
            raise TypeError(f"estado de algoritmo desconhecido: {type(other).__name__}")


def draw_cost_curve(ax: Axes, run: Run) -> None:
    """Custo × avaliações: melhor rota e rota atual (têmpera) ou média da população (AG)."""
    identity = profile(run)
    evaluations = [state.evaluations for state in run.states]
    best = [state.best.cost for state in run.states]
    context_label, context = _context_series(run)
    ax.plot(evaluations, context, color=CONTEXT_COLOR, linewidth=1.2, label=context_label)
    ax.plot(evaluations, best, color=identity.color, linewidth=2, label="melhor rota")
    _log_evaluations_axis(ax)
    ax.set_ylabel("custo da rota")
    ax.set_title(f"{identity.name}: custo ao longo da busca")
    ax.legend()
    style_axes(ax)


def draw_temperature(ax: Axes, run: Run) -> None:
    """Temperatura × avaliações, com a temperatura em escala log. Levanta `TypeError` se não for têmpera."""
    heated = [state for state in _states_of(run, SAState) if state.temperature > 0]
    evaluations = [state.evaluations for state in heated]
    temperatures = [state.temperature for state in heated]
    ax.plot(evaluations, temperatures, color=SA_COLOR, linewidth=2)
    ax.set_yscale("log")
    ax.set_xlabel(EVALUATIONS_LABEL)
    ax.set_ylabel("temperatura (escala log)")
    ax.set_title("Têmpera Simulada: resfriamento geométrico")
    style_axes(ax)


def draw_worsening_acceptance(ax: Axes, run: Run) -> None:
    """Fração das pioras aceitas por intervalo × avaliações. Levanta `TypeError` se não for têmpera."""
    evaluations, rates = worsening_acceptance(_states_of(run, SAState))
    ax.plot(evaluations, rates, color=SA_COLOR, linewidth=1.5)
    ax.set_ylim(0, 1)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_xlabel(EVALUATIONS_LABEL)
    ax.set_ylabel("pioras aceitas")
    ax.set_title("Têmpera Simulada: decisões do critério de Metropolis")
    style_axes(ax)


def draw_population_band(ax: Axes, run: Run) -> None:
    """Melhor, média e pior custo da população × avaliações. Levanta `TypeError` se não for AG."""
    states = _states_of(run, GAState)
    evaluations = [state.evaluations for state in states]
    best = [state.best.cost for state in states]
    mean = [state.mean_cost for state in states]
    worst = [state.worst_cost for state in states]
    ax.fill_between(
        evaluations,
        best,
        worst,
        color=GA_COLOR,
        alpha=0.2,
        linewidth=0,
        label="população (melhor a pior)",
    )
    ax.plot(evaluations, mean, color=CONTEXT_COLOR, linewidth=1.2, label="média")
    ax.plot(evaluations, best, color=GA_COLOR, linewidth=2, label="melhor")
    _log_evaluations_axis(ax)
    ax.set_ylabel("custo da rota")
    ax.set_title("Algoritmo Genético: convergência da população")
    ax.legend()
    style_axes(ax)


def draw_best_cost_comparison(ax: Axes, runs: Sequence[Run], reference: Tour | None = None) -> None:
    """Custo da melhor rota × avaliações de cada execução, no mesmo eixo, com o nome no fim da curva.

    Com `reference`, desenha o custo dessa rota como linha horizontal tracejada.
    """
    if reference is not None:
        ax.axhline(
            reference.cost,
            color=CONTEXT_COLOR,
            linewidth=1.2,
            linestyle="--",
            label=f"vizinho mais próximo ({reference.cost:.1f})",
        )
    for run in runs:
        identity = profile(run)
        evaluations = [state.evaluations for state in run.states]
        costs = [state.best.cost for state in run.states]
        ax.plot(evaluations, costs, color=identity.color, linewidth=2, label=identity.name)
        ax.annotate(
            identity.name,
            (evaluations[-1], costs[-1]),
            xytext=(6, 0),
            textcoords="offset points",
            va="center",
            fontsize=9,
            color=TEXT_COLOR,
        )
    _log_evaluations_axis(ax)
    ax.set_ylabel("custo da melhor rota")
    ax.set_title("Melhor rota ao longo da busca")
    ax.legend()
    style_axes(ax)


def draw_final_route(ax: Axes, run: Run) -> None:
    """Rota final de `run`, completa e na cor do algoritmo, com nome e custo no título."""
    identity = profile(run)
    draw_tour(ax, run.finished.best, identity.color)
    ax.set_title(f"{identity.name} · custo {run.finished.best.cost:.1f}")


def draw_milestone(ax: Axes, milestone: Milestone, run: Run) -> None:
    """Miniatura da melhor rota num marco de melhoria, com fração, passo e custo no título."""
    identity = profile(run)
    state = milestone.state
    draw_route(ax, state.best, identity.color)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(
        f"{milestone.fraction:.0%} da melhora\n{identity.step} {state.iteration} · custo {state.best.cost:.1f}",
        fontsize=9,
    )


def draw_table(
    ax: Axes, rows: Sequence[Sequence[str]], title: str, header: Sequence[str] | None = None
) -> None:
    """Tabela de texto com `rows` e, se houver, `header`, sem eixos."""
    ax.axis("off")
    table = ax.table(
        cellText=[list(row) for row in rows],
        colLabels=list(header) if header else None,
        cellLoc="left",
        loc="upper center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.3)
    for cell in table.get_celld().values():
        cell.set_edgecolor(GRID_COLOR)
    ax.set_title(title)


def milestones_of(run: Run) -> tuple[Milestone, ...]:
    """Marcos de melhoria usados nas figuras: 0%, 50%, 80%, 95% e 100% da melhora."""
    return improvement_milestones(run, MILESTONE_FRACTIONS)


def summary_rows(run: Run, params: SAParams | GAParams) -> list[tuple[str, str]]:
    """Linhas do quadro-resumo: identificação, resultado, dados do algoritmo e parâmetros usados."""
    instance = run.finished.best.instance
    return [
        ("algoritmo", profile(run).name),
        ("instância", f"{instance.name} ({instance.n_cities} cidades)"),
        *_result_rows(run),
        *_algorithm_rows(run.states[0], run.states[-1]),
        *((f"parâmetro {field.name}", str(getattr(params, field.name))) for field in fields(params)),
    ]


def comparison_rows(runs: Sequence[Run]) -> tuple[list[str], list[list[str]]]:
    """Cabeçalho e linhas da tabela comparativa, com uma coluna de resultados por execução."""
    results = [dict(_result_rows(run)) for run in runs]
    header = ["", *(profile(run).name for run in runs)]
    rows = [[label, *(result[label] for result in results)] for label in results[0]]
    return header, rows


def stop_reason_text(reason: StopReason) -> str:
    """Motivo da parada em português, para figuras e tabelas."""
    match reason:
        case StopReason.MIN_TEMPERATURE:
            return "temperatura mínima"
        case StopReason.MAX_EVALUATIONS:
            return "orçamento de avaliações"
        case StopReason.STAGNATION:
            return "estagnação"
        case _:
            assert_never(reason)


def _result_rows(run: Run) -> list[tuple[str, str]]:
    initial, final = run.states[0].best.cost, run.finished.best.cost
    (found,) = improvement_milestones(run, (1.0,))
    return [
        ("custo da melhor rota inicial", f"{initial:.1f}"),
        ("custo final", f"{final:.1f}"),
        ("melhora", _improvement_text(initial, final)),
        ("iterações", f"{run.finished.iterations} {profile(run).steps}"),
        ("avaliações", str(run.finished.evaluations)),
        ("melhor rota encontrada em", f"{found.state.evaluations} avaliações"),
        ("tempo", f"{run.elapsed_seconds:.2f} s"),
        ("motivo da parada", stop_reason_text(run.finished.reason)),
    ]


def _context_series(run: Run) -> tuple[str, list[float]]:
    match run.states[0]:
        case SAState():
            return "rota atual", [state.current.cost for state in run.states]
        case GAState():
            return "média da população", [state.mean_cost for state in run.states]
        case other:
            raise TypeError(f"estado de algoritmo desconhecido: {type(other).__name__}")


def _algorithm_rows(first: SAState | GAState, last: SAState | GAState) -> list[tuple[str, str]]:
    match first, last:
        case SAState(), SAState():
            return [
                ("temperatura inicial", f"{first.temperature:.4g}"),
                ("temperatura final", f"{last.temperature:.4g}"),
                ("pioras aceitas", _share_text(last.worsening_accepted, last.worsening_proposed)),
            ]
        case GAState(), GAState():
            return [("média / pior custo final", f"{last.mean_cost:.1f} / {last.worst_cost:.1f}")]
        case _:
            raise TypeError(f"estados de algoritmo desconhecidos: {type(first).__name__}, {type(last).__name__}")


def _states_of(run: Run, kind: type) -> tuple:
    match run.states[0]:
        case state if isinstance(state, kind):
            return run.states
        case other:
            raise TypeError(f"este gráfico precisa de uma execução com {kind.__name__}, recebeu {type(other).__name__}")


def _improvement_text(initial: float, final: float) -> str:
    return f"{(initial - final) / initial:.1%}" if initial > 0 else "—"


def _share_text(part: int, total: int) -> str:
    return f"{part} de {total} ({part / total:.1%})" if total > 0 else "nenhuma proposta"


def _log_evaluations_axis(ax: Axes) -> None:
    ax.set_xscale("log")
    ax.set_xlabel(f"{EVALUATIONS_LABEL} (escala log)")


def style_axes(ax: Axes) -> None:
    """Estilo comum dos gráficos: grade discreta atrás dos dados e sem bordas superior e direita."""
    ax.grid(True, color=GRID_COLOR, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
