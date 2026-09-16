"""Rodada de experimentos: várias instâncias por tamanho, os dois algoritmos e o vizinho mais próximo.

Uso:
    python -m experiments --sizes 20 50 100 --repetitions 10 --out material-artigo/experimentos
"""

import argparse
from pathlib import Path

from experiments.runner import run_experiments, search_space, summarize
from tsp import MIN_CITIES, GAParams, SAParams
from viz.experiment_figures import experiment_figures
from viz.notes import experiment_notes
from viz.output import save_images, save_notes


def main(argv: list[str] | None = None) -> None:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        sa_params = SAParams(max_evaluations=args.max_evaluations, final_acceptance=args.sa_final_acceptance)
        ga_params = GAParams(max_evaluations=args.max_evaluations)
    except ValueError as error:
        parser.error(str(error))
    if args.repetitions < 1:
        parser.error(f"--repetitions precisa ser positivo, recebeu {args.repetitions}")
    if min(args.sizes) < MIN_CITIES:
        parser.error(f"--sizes precisa ter pelo menos {MIN_CITIES} cidades, recebeu {min(args.sizes)}")
    records = []
    for run in run_experiments(args.sizes, args.repetitions, sa_params, ga_params):
        print(
            f"{run.n_cities} cidades · seed {run.instance_seed} · {run.algorithm.value}: "
            f"custo {run.final_cost:.1f} ({run.gap_to_reference:+.1%} vs vizinho mais próximo) "
            f"em {run.elapsed_seconds:.1f} s",
            flush=True,
        )
        records.append(run)
    summary = summarize(records)
    space = search_space(args.sizes)
    out = Path(args.out)
    save_images(experiment_figures(records), out, args.dpi)
    save_notes(experiment_notes(records, summary, space, sa_params, ga_params), out)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m experiments",
        description="Roda a têmpera e o AG em várias instâncias por tamanho e salva figuras, notas e CSVs.",
    )
    parser.add_argument("--sizes", type=int, nargs="+", default=[20, 50, 100], help="tamanhos (padrão: 20 50 100)")
    parser.add_argument("--repetitions", type=int, default=10, help="instâncias por tamanho (padrão: 10)")
    parser.add_argument(
        "--max-evaluations",
        type=int,
        default=1_000_000,
        help="orçamento de avaliações, o mesmo para os dois algoritmos (padrão: 1000000)",
    )
    parser.add_argument(
        "--sa-final-acceptance",
        type=float,
        default=SAParams().final_acceptance,
        help="chance de a têmpera aceitar uma piora típica na parada; define a temperatura mínima (padrão: 0.001)",
    )
    parser.add_argument("--out", default="material-artigo/experimentos", help="pasta de saída")
    parser.add_argument("--dpi", type=int, default=300, help="resolução dos PNG (padrão: 300)")
    return parser


if __name__ == "__main__":
    main()
