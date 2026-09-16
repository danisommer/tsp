# Configuração da rodada

| item | valor |
| --- | --- |
| tamanhos de instância | 20, 50, 100 |
| instâncias por tamanho | 10 |
| seeds (instância e algoritmos) | 0 a 9 |
| instâncias | aleatórias uniformes no quadrado [0, 1000]², métrica euclidiana |
| referência | vizinho mais próximo a partir da cidade 0 |
| emissão de estados | só o inicial e o final, para medir o tempo da busca |

**Parâmetros da Têmpera Simulada:**

| parâmetro | valor |
| --- | --- |
| initial_acceptance | 0.8 |
| final_acceptance | 1e-12 |
| calibration_samples | 100 |
| cooling_rate | 0.95 |
| plateau_factor | 100 |
| max_evaluations | 1000000 |
| emit_every | 500 |

**Parâmetros do Algoritmo Genético:**

| parâmetro | valor |
| --- | --- |
| population_size | 100 |
| elite_size | 2 |
| tournament_size | 3 |
| crossover_rate | 0.9 |
| mutation_rate | 0.2 |
| stagnation_limit | 200 |
| max_evaluations | 1000000 |
| emit_every | 1 |
