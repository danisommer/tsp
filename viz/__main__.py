"""Desenha uma instância aleatória e a rota que visita as cidades na ordem 0, 1, ..., n-1.

Uso:
    python -m viz --cities 30 --seed 42
    python -m viz --cities 30 --seed 42 --save rota.png
"""

import argparse

import matplotlib.pyplot as plt
import numpy as np

from tsp import Tour, random_uniform
from viz.draw import draw_tour


def main(argv: list[str] | None = None) -> None:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        instance = random_uniform(args.cities, args.seed)
    except ValueError as error:
        parser.error(str(error))
    tour = Tour(instance, np.arange(instance.n_cities))
    figure, ax = plt.subplots(figsize=(7, 7))
    draw_tour(ax, tour)
    match args.save:
        case None:
            plt.show()
        case path:
            figure.savefig(path, bbox_inches="tight")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m viz",
        description="Desenha uma instância aleatória e a rota 0, 1, ..., n-1 sobre ela.",
    )
    parser.add_argument("--cities", type=int, default=20, help="número de cidades (padrão: 20)")
    parser.add_argument("--seed", type=int, default=0, help="seed da instância (padrão: 0)")
    parser.add_argument("--save", metavar="ARQUIVO", help="salva a figura em ARQUIVO em vez de abrir a janela")
    return parser


if __name__ == "__main__":
    main()
