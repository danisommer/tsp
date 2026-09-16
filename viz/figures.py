"""Figuras prontas de execuções registradas, como `matplotlib.figure.Figure`, sem abrir janela."""

from collections.abc import Callable, Sequence

from matplotlib.axes import Axes
from matplotlib.figure import Figure, SubFigure

from tsp import GAParams, GAState, Run, SAParams, SAState, Tour
from viz.charts import (
    comparison_rows,
    draw_best_cost_comparison,
    draw_cost_curve,
    draw_final_route,
    draw_milestone,
    draw_population_band,
    draw_table,
    draw_temperature,
    draw_worsening_acceptance,
    milestones_of,
    profile,
    summary_rows,
)

Chart = Callable[[Axes, Run], None]


def algorithm_panel(run: Run, params: SAParams | GAParams, title: str) -> Figure:
    """Painel completo de uma execução: sucessão da rota, gráficos do algoritmo e quadro-resumo."""
    charts = _charts_of(run)
    figure = Figure(figsize=(15, 5.5 + 3.6 * len(charts)), layout="constrained")
    top, bottom = figure.subfigures(2, 1, height_ratios=[1.6, 3.6 * len(charts)])
    _fill_milestones(top, run)
    left, right = bottom.subfigures(1, 2, width_ratios=[1.4, 1])
    for ax, draw in zip(left.subplots(len(charts), 1, squeeze=False)[:, 0], charts):
        draw(ax, run)
    draw_table(right.subplots(), summary_rows(run, params), "Resumo da execução")
    figure.suptitle(title, fontsize=15)
    return figure


def algorithm_figures(run: Run, params: SAParams | GAParams) -> dict[str, Figure]:
    """Figuras separadas de uma execução, por nome de arquivo sem extensão.

    Sempre `sucessao`, `custo` e `resumo`; mais `temperatura` e `aceitacao` na têmpera, ou
    `populacao` no AG.
    """
    return {
        "sucessao": milestones_figure(run),
        "custo": _chart_figure(draw_cost_curve, run),
        **_specific_figures(run),
        "resumo": summary_figure(run, params),
    }


def milestones_figure(run: Run) -> Figure:
    """Miniaturas da melhor rota em cada marco de melhoria, lado a lado."""
    figure = Figure(figsize=(2.8 * len(milestones_of(run)), 3.4), layout="constrained")
    _fill_milestones(figure, run)
    return figure


def summary_figure(run: Run, params: SAParams | GAParams) -> Figure:
    """Quadro-resumo de uma execução como figura própria."""
    rows = summary_rows(run, params)
    figure = Figure(figsize=(7, 0.34 * len(rows) + 0.8), layout="constrained")
    draw_table(figure.subplots(), rows, f"{profile(run).name}: resumo da execução")
    return figure


def comparison_figure(runs: Sequence[Run], title: str, reference: Tour | None = None) -> Figure:
    """Comparativo de execuções na mesma instância: curvas no mesmo eixo, rotas finais e tabela.

    Com `reference`, a curva ganha o custo dessa rota como linha de referência.
    Levanta `ValueError` se `runs` estiver vazio ou tiver execuções de instâncias diferentes.
    """
    _require_same_instance(runs)
    figure = Figure(figsize=(6.5 * len(runs), 15), layout="constrained")
    top, middle, bottom = figure.subfigures(3, 1, height_ratios=[1, 1.5, 0.7])
    draw_best_cost_comparison(top.subplots(), runs, reference)
    for ax, run in zip(middle.subplots(1, len(runs), squeeze=False)[0], runs):
        draw_final_route(ax, run)
    header, rows = comparison_rows(runs)
    draw_table(bottom.subplots(), rows, "Resumo comparativo", header)
    figure.suptitle(title, fontsize=15)
    return figure


def _fill_milestones(container: Figure | SubFigure, run: Run) -> None:
    milestones = milestones_of(run)
    for ax, milestone in zip(container.subplots(1, len(milestones), squeeze=False)[0], milestones):
        draw_milestone(ax, milestone, run)
    container.suptitle(f"{profile(run).name}: sucessão da melhor rota nos marcos de melhoria")


def _charts_of(run: Run) -> list[Chart]:
    match run.states[0]:
        case SAState():
            return [draw_cost_curve, draw_temperature, draw_worsening_acceptance]
        case GAState():
            return [draw_cost_curve, draw_population_band]
        case other:
            raise TypeError(f"estado de algoritmo desconhecido: {type(other).__name__}")


def _specific_figures(run: Run) -> dict[str, Figure]:
    match run.states[0]:
        case SAState():
            return {
                "temperatura": _chart_figure(draw_temperature, run),
                "aceitacao": _chart_figure(draw_worsening_acceptance, run),
            }
        case GAState():
            return {"populacao": _chart_figure(draw_population_band, run)}
        case other:
            raise TypeError(f"estado de algoritmo desconhecido: {type(other).__name__}")


def _chart_figure(draw: Chart, run: Run) -> Figure:
    figure = Figure(figsize=(7, 4.2), layout="constrained")
    draw(figure.subplots(), run)
    return figure


def _require_same_instance(runs: Sequence[Run]) -> None:
    match [run.finished.best.instance for run in runs]:
        case []:
            raise ValueError("o comparativo precisa de pelo menos uma execução")
        case [first, *others] if any(instance is not first for instance in others):
            raise ValueError("as execuções do comparativo precisam ser da mesma instância")
