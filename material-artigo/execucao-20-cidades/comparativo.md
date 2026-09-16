# Comparativo: Têmpera Simulada × Algoritmo Genético na mesma instância

**O que a imagem mostra:** no topo, o custo da melhor rota de cada algoritmo ao longo das avaliações (eixo x em escala log), com a rota do vizinho mais próximo tracejada como referência; no meio, as rotas finais completas; embaixo, a tabela comparativa.

**Referência:** vizinho mais próximo a partir da cidade 0, custo 4033.1.

|  | Têmpera Simulada | Algoritmo Genético |
| --- | --- | --- |
| custo da melhor rota inicial | 11486.9 | 8485.5 |
| custo final | 3415.8 | 3428.7 |
| melhora | 70.3% | 59.6% |
| iterações | 134000 movimentos | 266 gerações |
| avaliações | 134101 | 26168 |
| melhor rota encontrada em | 99101 avaliações | 6568 avaliações |
| tempo | 1.28 s | 2.56 s |
| motivo da parada | temperatura mínima | estagnação |
| diferença para o vizinho mais próximo | -15.3% | -15.0% |

**Custo da melhor rota em marcos de avaliações:**

| avaliações | Têmpera Simulada | Algoritmo Genético |
| --- | --- | --- |
| 100 | — | 8485.5 |
| 1000 | 7449.4 | 4941.6 |
| 10000 | 6704.3 | 3428.7 |
| 100000 | 3415.8 | 3428.7 (já tinha parado) |

**Rotas finais (ordem de visita):**

- Têmpera Simulada: `14 19 18 4 16 7 17 13 8 12 10 0 9 1 11 15 3 6 5 2`
- Algoritmo Genético: `9 1 3 11 15 6 5 2 14 19 18 4 16 7 17 13 8 12 10 0`
