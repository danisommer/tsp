"""Desenho de instâncias e rotas do TSP sobre um `Axes` do matplotlib.

As funções só desenham no `ax` recebido: não criam figura nem abrem janela.
"""

import numpy as np
from matplotlib.axes import Axes

from tsp import Instance, Tour

CITY_COLOR = "#52514e"
LABEL_COLOR = "#52514e"
ROUTE_COLOR = "#2a78d6"
START_COLOR = "#0b0b0b"
ARROW_LENGTH_INCHES = 0.16


def draw_instance(ax: Axes, instance: Instance) -> None:
    """Desenha as cidades numeradas de `instance`, com o nome dela como título."""
    _draw_cities(ax, instance)
    _draw_city_labels(ax, instance)
    ax.set_aspect("equal")
    ax.set_title(instance.name)


def draw_route(ax: Axes, tour: Tour, color: str = ROUTE_COLOR) -> None:
    """Desenha as cidades, a rota fechada na cor `color` e a cidade inicial em destaque.

    Versão enxuta, para miniaturas: sem números das cidades, setas, legenda nem título.
    """
    _draw_cities(ax, tour.instance)
    path = _closed_path(tour)
    ax.plot(path[:, 0], path[:, 1], color=color, linewidth=1.5, zorder=1, label="rota")
    start_x, start_y = path[0]
    ax.plot(
        start_x,
        start_y,
        marker="*",
        markersize=14,
        linestyle="none",
        color=START_COLOR,
        zorder=4,
        label="início",
    )
    ax.set_aspect("equal")


def draw_tour(ax: Axes, tour: Tour, color: str = ROUTE_COLOR) -> None:
    """Desenha a rota completa: `draw_route` mais números das cidades, setas de sentido e legenda.

    O título mostra o nome da instância e o custo da rota.
    """
    draw_route(ax, tour, color)
    _draw_city_labels(ax, tour.instance)
    _draw_direction_arrows(ax, _closed_path(tour), color)
    ax.legend(loc="best")
    ax.set_title(f"{tour.instance.name} · custo {tour.cost:.2f}")


def _closed_path(tour: Tour) -> np.ndarray:
    return tour.instance.coords[np.append(tour.order, tour.order[0])]


def _draw_cities(ax: Axes, instance: Instance) -> None:
    xs, ys = instance.coords.T
    ax.scatter(xs, ys, s=36, color=CITY_COLOR, zorder=3)


def _draw_city_labels(ax: Axes, instance: Instance) -> None:
    for city, (x, y) in enumerate(instance.coords):
        ax.annotate(
            str(city),
            (x, y),
            xytext=(4, 4),
            textcoords="offset points",
            fontsize=8,
            color=LABEL_COLOR,
            zorder=5,
        )


def _draw_direction_arrows(ax: Axes, path: np.ndarray, color: str) -> None:
    starts, ends = path[:-1], path[1:]
    deltas = ends - starts
    lengths = np.linalg.norm(deltas, axis=1, keepdims=True)
    directions = np.divide(deltas, lengths, out=np.zeros_like(deltas), where=lengths > 0)
    midpoints = (starts + ends) / 2
    ax.quiver(
        midpoints[:, 0],
        midpoints[:, 1],
        directions[:, 0],
        directions[:, 1],
        angles="xy",
        scale_units="inches",
        scale=1 / ARROW_LENGTH_INCHES,
        pivot="mid",
        color=color,
        zorder=2,
    )
