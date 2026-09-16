"""Roda a Têmpera Simulada e o Algoritmo Genético na mesma instância e salva imagens, notas e CSVs.

Cada imagem `<nome>.png` vem com `<nome>.md` (o que mostra e os números) e, nas séries, `<nome>.csv`.

Uso:
    python -m viz.report --cities 50 --instance-seed 42 --seed 1 --out figuras
"""

import argparse
from collections.abc import Iterable
from pathlib import Path

from tsp import (
    Finished,
    GAParams,
    Instance,
    Run,
    SAParams,
    SearchState,
    genetic_algorithm,
    nearest_neighbor,
    random_uniform,
    record,
    simulated_annealing,
)
from viz.charts import profile
from viz.figures import algorithm_figures, algorithm_panel, comparison_figure
from viz.notes import algorithm_notes, comparison_note
from viz.output import save_images, save_notes


def main(argv: list[str] | None = None) -> None:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        instance = random_uniform(args.cities, args.instance_seed)
        sa_params = SAParams(max_evaluations=args.max_evaluations)
        ga_params = GAParams(max_evaluations=args.max_evaluations)
    except ValueError as error:
        parser.error(str(error))
    sa_run = _run("Têmpera Simulada", simulated_annealing(instance, sa_params, args.seed))
    ga_run = _run("Algoritmo Genético", genetic_algorithm(instance, ga_params, args.seed))
    reference = nearest_neighbor(instance)
    runs = [("tempera", sa_run, sa_params), ("ag", ga_run, ga_params)]
    comparison_title = _title("Têmpera Simulada × Algoritmo Genético", instance, args.seed)
    out = Path(args.out)
    for prefix, run, params in runs:
        title = _title(profile(run).name, instance, args.seed)
        figures = {"painel": algorithm_panel(run, params, title), **algorithm_figures(run, params)}
        save_images(_prefixed(prefix, figures), out, args.dpi)
        save_notes(_prefixed(prefix, algorithm_notes(run, params)), out)
    save_images({"comparativo": comparison_figure([sa_run, ga_run], comparison_title, reference)}, out, args.dpi)
    save_notes({"comparativo": comparison_note([sa_run, ga_run], reference)}, out)


def _run(name: str, events: Iterable[SearchState | Finished]) -> Run:
    print(f"executando {name}...", flush=True)
    run = record(events)
    print(f"  custo final {run.finished.best.cost:.1f} em {run.elapsed_seconds:.2f} s", flush=True)
    return run


def _prefixed[T](prefix: str, items: dict[str, T]) -> dict[str, T]:
    return {f"{prefix}_{name}": item for name, item in items.items()}


def _title(subject: str, instance: Instance, seed: int) -> str:
    return f"{subject} · {instance.name} · seed {seed}"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m viz.report",
        description="Roda a Têmpera Simulada e o Algoritmo Genético na mesma instância e salva as imagens.",
    )
    parser.add_argument("--cities", type=int, default=50, help="número de cidades (padrão: 50)")
    parser.add_argument("--instance-seed", type=int, default=42, help="seed da instância (padrão: 42)")
    parser.add_argument("--seed", type=int, default=1, help="seed dos algoritmos (padrão: 1)")
    parser.add_argument(
        "--max-evaluations",
        type=int,
        default=1_000_000,
        help="orçamento de avaliações, o mesmo para os dois algoritmos (padrão: 1000000)",
    )
    parser.add_argument("--out", default="figuras", help="pasta de saída (padrão: figuras)")
    parser.add_argument("--dpi", type=int, default=300, help="resolução dos PNG (padrão: 300)")
    return parser


if __name__ == "__main__":
    main()
