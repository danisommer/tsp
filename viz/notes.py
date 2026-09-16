"""Textos que acompanham as imagens: o que cada uma mostra e os números por trás dela.

Cada `Note` vira um `.md` ao lado da imagem e, quando há dados tabulares, também um `.csv` completo.
"""

from collections.abc import Sequence
from dataclasses import dataclass, fields
from typing import assert_never

import numpy as np

from experiments.runner import Algorithm, RunRecord, SearchSpaceRow, SummaryRow
from tsp import GAParams, GAState, Run, SAParams, SAState, Tour, improvement_milestones, worsening_acceptance
from viz.charts import comparison_rows, milestones_of, profile, stop_reason_text, summary_rows

Table = tuple[list[str], list[list[str]]]


@dataclass(frozen=True, slots=True)
class Note:
    """Texto de uma imagem ou conjunto de dados: `markdown` legível e, se houver, `table` para CSV."""

    markdown: str
    table: Table | None = None


def algorithm_notes(run: Run, params: SAParams | GAParams) -> dict[str, Note]:
    """Notas das imagens de uma execução, com os nomes de `algorithm_figures` mais `painel`."""
    return {
        "painel": _panel_note(run),
        "sucessao": _milestones_note(run, params),
        "custo": _cost_note(run),
        **_specific_notes(run, params),
        "resumo": _summary_note(run, params),
    }


def comparison_note(runs: Sequence[Run], reference: Tour) -> Note:
    """Nota do comparativo: tabela, diferença para a referência, custo em marcos de avaliações e rotas finais."""
    header, rows = comparison_rows(runs)
    gap_row = [
        "diferença para o vizinho mais próximo",
        *(_signed_share(run.finished.best.cost - reference.cost, reference.cost) for run in runs),
    ]
    budget = max(run.finished.evaluations for run in runs)
    checkpoints = [10**power for power in range(2, 8) if 10**power <= budget]
    checkpoint_rows = [[str(checkpoint), *(_best_cost_at(run, checkpoint) for run in runs)] for checkpoint in checkpoints]
    routes = "\n".join(f"- {profile(run).name}: `{_route_text(run.finished.best)}`" for run in runs)
    return Note(
        _document(
            "Comparativo: Têmpera Simulada × Algoritmo Genético na mesma instância",
            "**O que a imagem mostra:** no topo, o custo da melhor rota de cada algoritmo ao longo das avaliações "
            "(eixo x em escala log), com a rota do vizinho mais próximo tracejada como referência; no meio, as "
            "rotas finais completas; embaixo, a tabela comparativa.",
            f"**Referência:** vizinho mais próximo a partir da cidade 0, custo {reference.cost:.1f}.",
            markdown_table(header, [*rows, gap_row]),
            "**Custo da melhor rota em marcos de avaliações:**",
            markdown_table(["avaliações", *header[1:]], checkpoint_rows),
            "**Rotas finais (ordem de visita):**\n\n" + routes,
        )
    )


def experiment_notes(
    records: Sequence[RunRecord],
    summary: Sequence[SummaryRow],
    space: Sequence[SearchSpaceRow],
    sa_params: SAParams,
    ga_params: GAParams,
) -> dict[str, Note]:
    """Notas da rodada de experimentos: as três figuras, os dados brutos, o resumo, o espaço de busca e a configuração."""
    return {
        "custo_final": _gap_note(summary),
        "tempo": _time_note(summary),
        "avaliacoes": _evaluations_note(summary),
        "resumo": Note(_document("Resumo da rodada", markdown_table(*_summary_markdown(summary))), _summary_csv(summary)),
        "execucoes": Note(_records_markdown(records), _records_csv(records)),
        "espaco_de_busca": _search_space_note(space, summary),
        "configuracao": _configuration_note(records, sa_params, ga_params),
    }


def markdown_table(header: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    """Tabela em markdown; `|` dentro das células é escapado."""
    return "\n".join([_table_row(header), _table_row(["---"] * len(header)), *(_table_row(row) for row in rows)])


def _panel_note(run: Run) -> Note:
    identity = profile(run)
    parts = [["sucessão da melhor rota", "`sucessao`"], ["custo ao longo da busca", "`custo`"]]
    specific = _specific_parts(run)
    return Note(
        _document(
            f"{identity.name}: painel completo",
            "**O que a imagem mostra:** reúne numa só figura as imagens separadas desta execução. Os números de "
            "cada parte estão nas notas de mesmo prefixo indicadas abaixo.",
            markdown_table(["parte", "nota com os números"], [*parts, *specific, ["quadro-resumo", "`resumo`"]]),
        )
    )


def _milestones_note(run: Run, params: SAParams | GAParams) -> Note:
    identity = profile(run)
    milestones = milestones_of(run)
    rows = [
        [f"{m.fraction:.0%}", str(m.state.iteration), str(m.state.evaluations), f"{m.state.best.cost:.1f}"]
        for m in milestones
    ]
    routes = "\n".join(f"- {m.fraction:.0%}: `{_route_text(m.state.best)}`" for m in milestones)
    return Note(
        _document(
            f"{identity.name}: sucessão da melhor rota",
            "**O que a imagem mostra:** a melhor rota encontrada até cada marco de melhoria. O marco de f% é o "
            "primeiro estado emitido em que a melhor rota já tinha percorrido f% do caminho entre o custo "
            "inicial e o final. A estrela marca a cidade em que a rota começa.",
            f"**Resolução:** estados emitidos a cada {params.emit_every} {identity.steps}. Marcos atingidos no "
            "mesmo estado aparecem como um quadro só.",
            markdown_table(["marco", identity.step, "avaliações", "custo da melhor rota"], rows),
            "**Ordem de visita em cada marco:**\n\n" + routes,
        )
    )


def _cost_note(run: Run) -> Note:
    identity = profile(run)
    context_label, context_column, context = _context_of(run)
    first, finished = run.states[0], run.finished
    initial, final = first.best.cost, finished.best.cost
    milestones = {m.fraction: m.state for m in improvement_milestones(run, (0.5, 0.8, 0.95, 1.0))}
    key_rows = [
        ["custo da melhor rota inicial", f"{initial:.1f}"],
        ["custo final", f"{final:.1f}"],
        ["melhora", _share(initial - final, initial)],
        [f"{context_label} no último estado", f"{context[-1]:.1f}"],
        ["avaliações usadas", str(finished.evaluations)],
        *(
            [f"avaliações até {fraction:.0%} da melhora", f"{state.evaluations} ({_share(state.evaluations, finished.evaluations)} do total)"]
            for fraction, state in milestones.items()
        ),
    ]
    table = (
        ["avaliacoes", "iteracao", "custo_melhor", context_column],
        [
            [str(state.evaluations), str(state.iteration), f"{state.best.cost:.4f}", f"{value:.4f}"]
            for state, value in zip(run.states, context)
        ],
    )
    return Note(
        _document(
            f"{identity.name}: custo ao longo da busca",
            "**O que a imagem mostra:** eixo x com as avaliações da função objetivo (escala log). A linha colorida "
            f"é o custo da melhor rota encontrada até o momento; a linha cinza é o custo da {context_label}.",
            markdown_table(["item", "valor"], key_rows),
            "**Série completa:** CSV de mesmo nome, uma linha por estado emitido.",
        ),
        table,
    )


def _temperature_note(run: Run, params: SAParams) -> Note:
    states = run.states
    first, last = states[0], states[-1]
    plateau = params.plateau_factor * first.best.instance.n_cities
    key_rows = [
        ["temperatura inicial (T0, calibrada)", f"{first.temperature:.4g}"],
        ["temperatura final", f"{last.temperature:.4g}"],
        ["razão final / inicial", f"{last.temperature / first.temperature:.4g}" if first.temperature > 0 else "—"],
        ["fator de resfriamento α", str(params.cooling_rate)],
        ["movimentos por patamar (fator × n)", str(plateau)],
        ["resfriamentos aplicados", str(last.iteration // plateau)],
        ["chance de aceitar uma piora típica no início", f"{params.initial_acceptance:.1%}"],
        ["chance de aceitar uma piora típica na parada", f"{params.final_acceptance:.1%}"],
    ]
    table = (
        ["avaliacoes", "iteracao", "temperatura"],
        [[str(state.evaluations), str(state.iteration), f"{state.temperature:.6g}"] for state in states],
    )
    return Note(
        _document(
            "Têmpera Simulada: resfriamento geométrico",
            "**O que a imagem mostra:** a temperatura ao longo das avaliações, com o eixo da temperatura em escala "
            "log. No resfriamento geométrico `T ← α·T`, a curva vira uma escada descendente em linha reta nessa "
            "escala.",
            markdown_table(["item", "valor"], key_rows),
            "**Série completa:** CSV de mesmo nome, uma linha por estado emitido.",
        ),
        table,
    )


def _acceptance_note(run: Run) -> Note:
    last = run.states[-1]
    evaluations, rates = worsening_acceptance(run.states)
    key_rows = [
        ["pioras propostas no total", str(last.worsening_proposed)],
        ["pioras aceitas no total", str(last.worsening_accepted)],
        ["fração aceita no total", _share(last.worsening_accepted, last.worsening_proposed)],
        ["intervalos com alguma piora proposta", str(rates.size)],
        *_rate_rows(rates),
    ]
    table = (
        ["avaliacoes_fim_intervalo", "fracao_pioras_aceitas"],
        [[str(evaluation), f"{rate:.6f}"] for evaluation, rate in zip(evaluations, rates)],
    )
    return Note(
        _document(
            "Têmpera Simulada: decisões do critério de Metropolis",
            "**O que a imagem mostra:** entre dois estados emitidos consecutivos, a fração dos movimentos que "
            "piorariam a rota e mesmo assim foram aceitos. Melhorias são sempre aceitas e não entram na conta.",
            markdown_table(["item", "valor"], key_rows),
            "**Série completa:** CSV de mesmo nome, uma linha por intervalo.",
        ),
        table,
    )


def _population_note(run: Run) -> Note:
    first, last = run.states[0], run.states[-1]
    spread_initial = first.worst_cost - first.best.cost
    spread_final = last.worst_cost - last.best.cost
    key_rows = [
        ["geração inicial: melhor / média / pior", _triple(first)],
        ["última geração: melhor / média / pior", _triple(last)],
        ["amplitude inicial (pior − melhor)", f"{spread_initial:.1f}"],
        ["amplitude final", f"{spread_final:.1f}"],
        ["redução da amplitude", _share(spread_initial - spread_final, spread_initial)],
        ["média acima da melhor, no fim", _share(last.mean_cost - last.best.cost, last.best.cost)],
    ]
    table = (
        ["avaliacoes", "geracao", "custo_melhor", "custo_medio", "custo_pior"],
        [
            [
                str(state.evaluations),
                str(state.iteration),
                f"{state.best.cost:.4f}",
                f"{state.mean_cost:.4f}",
                f"{state.worst_cost:.4f}",
            ]
            for state in run.states
        ],
    )
    return Note(
        _document(
            "Algoritmo Genético: convergência da população",
            "**O que a imagem mostra:** a faixa colorida vai do custo da melhor à pior rota da população em cada "
            "geração; a linha cinza é o custo médio e a linha laranja, o da melhor. Eixo x em escala log.",
            markdown_table(["item", "valor"], key_rows),
            "**Série completa:** CSV de mesmo nome, uma linha por geração emitida.",
        ),
        table,
    )


def _summary_note(run: Run, params: SAParams | GAParams) -> Note:
    return Note(
        _document(
            f"{profile(run).name}: resumo da execução",
            markdown_table(["item", "valor"], summary_rows(run, params)),
        )
    )


def _gap_note(summary: Sequence[SummaryRow]) -> Note:
    rows = [
        [
            str(row.n_cities),
            _algorithm_name(row.algorithm),
            f"{row.mean_gap:+.1%} ± {row.std_gap:.1%}",
            f"{row.best_gap:+.1%}",
            f"{row.worst_gap:+.1%}",
            f"{row.wins} de {row.runs}",
        ]
        for row in summary
    ]
    return Note(
        _document(
            "Custo final relativo ao vizinho mais próximo",
            "**O que a imagem mostra:** cada ponto é uma execução; o eixo y é a diferença percentual entre o custo "
            "final e o custo do vizinho mais próximo na mesma instância (abaixo de 0% = melhor que a referência). "
            "O traço horizontal é a média do algoritmo naquele tamanho. Normalizar pela referência permite comparar "
            "instâncias diferentes.",
            markdown_table(
                ["cidades", "algoritmo", "diferença média ± desvio", "melhor", "pior", "vitórias na mesma instância"],
                rows,
            ),
        )
    )


def _time_note(summary: Sequence[SummaryRow]) -> Note:
    rows = [
        [str(row.n_cities), _algorithm_name(row.algorithm), f"{row.mean_seconds:.2f} s", f"{row.evaluations_per_second:,.0f}"]
        for row in summary
    ]
    return Note(
        _document(
            "Tempo de execução",
            "**O que a imagem mostra:** cada ponto é o tempo de relógio de uma execução (eixo y em escala log), "
            "com o traço horizontal na média. As execuções rodaram em sequência, na mesma máquina, emitindo só o "
            "estado inicial e o final.",
            markdown_table(["cidades", "algoritmo", "tempo médio", "avaliações por segundo"], rows),
        )
    )


def _evaluations_note(summary: Sequence[SummaryRow]) -> Note:
    rows = [
        [
            str(row.n_cities),
            _algorithm_name(row.algorithm),
            f"{row.mean_evaluations:,.0f}",
            ", ".join(f"{stop_reason_text(reason)}: {count}" for reason, count in row.stop_reasons),
        ]
        for row in summary
    ]
    return Note(
        _document(
            "Avaliações da função objetivo",
            "**O que a imagem mostra:** cada ponto é o número de avaliações usadas por uma execução (eixo y em "
            "escala log), com o traço na média. Os dois algoritmos têm o mesmo orçamento; parar antes dele "
            "significa temperatura mínima (têmpera) ou estagnação (AG).",
            markdown_table(["cidades", "algoritmo", "avaliações médias", "motivos da parada"], rows),
        )
    )


def _search_space_note(space: Sequence[SearchSpaceRow], summary: Sequence[SummaryRow]) -> Note:
    sa_evaluations = {
        row.n_cities: row.mean_evaluations for row in summary if row.algorithm is Algorithm.SIMULATED_ANNEALING
    }
    rows = [
        [
            str(row.n_cities),
            f"≈ 10^{row.log10_tours:.1f}",
            f"{row.evaluations_per_second:,.0f}",
            f"≈ 10^{row.log10_enumeration_years:.1f} anos",
            _fraction_of_space(sa_evaluations.get(row.n_cities), row.log10_tours),
        ]
        for row in space
    ]
    csv_rows = [
        [str(row.n_cities), f"{row.log10_tours:.4f}", f"{row.evaluations_per_second:.1f}", f"{row.log10_enumeration_years:.4f}"]
        for row in space
    ]
    return Note(
        _document(
            "Espaço de busca e busca clássica",
            "**O que é:** quantas rotas distintas existem, (n−1)!/2 (girar a rota ou invertê-la não muda o ciclo), "
            "e quanto tempo levaria avaliar todas na velocidade medida da função objetivo nesta máquina. É o "
            "custo de uma busca cega exaustiva e o pior caso de uma busca informada. A velocidade mede só a "
            "avaliação da rota, sem o custo de gerar as permutações, então o tempo real seria ainda maior.",
            markdown_table(
                [
                    "cidades",
                    "rotas distintas",
                    "avaliações completas por segundo",
                    "tempo para enumerar tudo",
                    "fração avaliada pela têmpera",
                ],
                rows,
            ),
            "Para comparação, a idade do universo é ≈ 10^10,1 anos.",
        ),
        (["cidades", "log10_rotas_distintas", "avaliacoes_por_segundo", "log10_anos_para_enumerar"], csv_rows),
    )


def _configuration_note(records: Sequence[RunRecord], sa_params: SAParams, ga_params: GAParams) -> Note:
    sizes = sorted({run.n_cities for run in records})
    seeds = sorted({run.instance_seed for run in records})
    return Note(
        _document(
            "Configuração da rodada",
            markdown_table(
                ["item", "valor"],
                [
                    ["tamanhos de instância", ", ".join(map(str, sizes))],
                    ["instâncias por tamanho", str(len(seeds))],
                    ["seeds (instância e algoritmos)", f"{seeds[0]} a {seeds[-1]}"],
                    ["instâncias", "aleatórias uniformes no quadrado [0, 1000]², métrica euclidiana"],
                    ["referência", "vizinho mais próximo a partir da cidade 0"],
                    ["emissão de estados", "só o inicial e o final, para medir o tempo da busca"],
                ],
            ),
            "**Parâmetros da Têmpera Simulada:**",
            markdown_table(["parâmetro", "valor"], _params_rows(sa_params)),
            "**Parâmetros do Algoritmo Genético:**",
            markdown_table(["parâmetro", "valor"], _params_rows(ga_params)),
        )
    )


def _records_markdown(records: Sequence[RunRecord]) -> str:
    header, _ = _records_csv(records)
    return _document(
        "Execuções da rodada",
        f"{len(records)} execuções, uma linha por execução no CSV de mesmo nome. Colunas:",
        "\n".join(f"- `{column}`" for column in header),
    )


def _records_csv(records: Sequence[RunRecord]) -> Table:
    header = [
        "cidades",
        "seed",
        "algoritmo",
        "custo_inicial",
        "custo_final",
        "custo_vizinho_mais_proximo",
        "diferenca_para_referencia",
        "avaliacoes",
        "iteracoes",
        "tempo_s",
        "motivo_parada",
    ]
    rows = [
        [
            str(run.n_cities),
            str(run.instance_seed),
            run.algorithm.value,
            f"{run.initial_cost:.4f}",
            f"{run.final_cost:.4f}",
            f"{run.reference_cost:.4f}",
            f"{run.gap_to_reference:.6f}",
            str(run.evaluations),
            str(run.iterations),
            f"{run.elapsed_seconds:.4f}",
            run.stop_reason.value,
        ]
        for run in records
    ]
    return header, rows


def _summary_markdown(summary: Sequence[SummaryRow]) -> Table:
    header = [
        "cidades",
        "algoritmo",
        "execuções",
        "custo final médio",
        "diferença média para a referência",
        "vitórias",
        "avaliações médias",
        "tempo médio",
    ]
    rows = [
        [
            str(row.n_cities),
            _algorithm_name(row.algorithm),
            str(row.runs),
            f"{row.mean_final_cost:.1f}",
            f"{row.mean_gap:+.1%} ± {row.std_gap:.1%}",
            f"{row.wins} de {row.runs}",
            f"{row.mean_evaluations:,.0f}",
            f"{row.mean_seconds:.2f} s",
        ]
        for row in summary
    ]
    return header, rows


def _summary_csv(summary: Sequence[SummaryRow]) -> Table:
    header = [
        "cidades",
        "algoritmo",
        "execucoes",
        "custo_final_medio",
        "diferenca_media",
        "desvio_diferenca",
        "melhor_diferenca",
        "pior_diferenca",
        "vitorias",
        "avaliacoes_medias",
        "tempo_medio_s",
        "avaliacoes_por_s",
    ]
    rows = [
        [
            str(row.n_cities),
            row.algorithm.value,
            str(row.runs),
            f"{row.mean_final_cost:.4f}",
            f"{row.mean_gap:.6f}",
            f"{row.std_gap:.6f}",
            f"{row.best_gap:.6f}",
            f"{row.worst_gap:.6f}",
            str(row.wins),
            f"{row.mean_evaluations:.1f}",
            f"{row.mean_seconds:.4f}",
            f"{row.evaluations_per_second:.1f}",
        ]
        for row in summary
    ]
    return header, rows


def _specific_notes(run: Run, params: SAParams | GAParams) -> dict[str, Note]:
    match run.states[0]:
        case SAState():
            return {"temperatura": _temperature_note(run, params), "aceitacao": _acceptance_note(run)}
        case GAState():
            return {"populacao": _population_note(run)}
        case other:
            raise TypeError(f"estado de algoritmo desconhecido: {type(other).__name__}")


def _specific_parts(run: Run) -> list[list[str]]:
    match run.states[0]:
        case SAState():
            return [["resfriamento", "`temperatura`"], ["decisões do critério de Metropolis", "`aceitacao`"]]
        case GAState():
            return [["convergência da população", "`populacao`"]]
        case other:
            raise TypeError(f"estado de algoritmo desconhecido: {type(other).__name__}")


def _context_of(run: Run) -> tuple[str, str, list[float]]:
    match run.states[0]:
        case SAState():
            return "rota atual", "custo_atual", [state.current.cost for state in run.states]
        case GAState():
            return "média da população", "custo_medio", [state.mean_cost for state in run.states]
        case other:
            raise TypeError(f"estado de algoritmo desconhecido: {type(other).__name__}")


def _rate_rows(rates: np.ndarray) -> list[list[str]]:
    match rates.size:
        case 0:
            return [["fração aceita por intervalo", "nenhum intervalo com piora proposta"]]
        case size:
            tenth = max(1, size // 10)
            return [
                ["fração aceita no primeiro intervalo", f"{rates[0]:.1%}"],
                ["média nos primeiros 10% dos intervalos", f"{rates[:tenth].mean():.1%}"],
                ["média nos últimos 10% dos intervalos", f"{rates[-tenth:].mean():.1%}"],
                ["fração aceita no último intervalo", f"{rates[-1]:.1%}"],
            ]


def _best_cost_at(run: Run, evaluations: int) -> str:
    reached = [state for state in run.states if state.evaluations <= evaluations]
    match reached:
        case []:
            return "—"
        case [*_, last] if run.finished.evaluations < evaluations:
            return f"{last.best.cost:.1f} (já tinha parado)"
        case [*_, last]:
            return f"{last.best.cost:.1f}"


def _fraction_of_space(evaluations: float | None, log10_tours: float) -> str:
    match evaluations:
        case None:
            return "—"
        case value:
            return f"≈ 10^{np.log10(value) - log10_tours:.1f}"


def _params_rows(params: SAParams | GAParams) -> list[list[str]]:
    return [[field.name, str(getattr(params, field.name))] for field in fields(params)]


def _algorithm_name(algorithm: Algorithm) -> str:
    match algorithm:
        case Algorithm.SIMULATED_ANNEALING:
            return "Têmpera Simulada"
        case Algorithm.GENETIC_ALGORITHM:
            return "Algoritmo Genético"
        case _:
            assert_never(algorithm)


def _triple(state: GAState) -> str:
    return f"{state.best.cost:.1f} / {state.mean_cost:.1f} / {state.worst_cost:.1f}"


def _route_text(tour: Tour) -> str:
    return " ".join(str(city) for city in tour.order)


def _share(part: float, total: float) -> str:
    return f"{part / total:.1%}" if total > 0 else "—"


def _signed_share(part: float, total: float) -> str:
    return f"{part / total:+.1%}" if total > 0 else "—"


def _document(title: str, *blocks: str) -> str:
    return "\n\n".join([f"# {title}", *blocks]) + "\n"


def _table_row(cells: Sequence[str]) -> str:
    return "| " + " | ".join(str(cell).replace("|", "\\|") for cell in cells) + " |"
