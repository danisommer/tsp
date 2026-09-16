# Comparativo: Têmpera Simulada × Algoritmo Genético na mesma instância

**O que a imagem mostra:** no topo, o custo da melhor rota de cada algoritmo ao longo das avaliações (eixo x em escala log), com a rota do vizinho mais próximo tracejada como referência; no meio, as rotas finais completas; embaixo, a tabela comparativa.

**Referência:** vizinho mais próximo a partir da cidade 0, custo 6367.6.

|  | Têmpera Simulada | Algoritmo Genético |
| --- | --- | --- |
| custo da melhor rota inicial | 22748.5 | 21423.7 |
| custo final | 5774.8 | 5960.1 |
| melhora | 74.6% | 72.2% |
| iterações | 335000 movimentos | 626 gerações |
| avaliações | 335101 | 61448 |
| melhor rota encontrada em | 320601 avaliações | 41848 avaliações |
| tempo | 3.30 s | 6.13 s |
| motivo da parada | temperatura mínima | estagnação |
| diferença para o vizinho mais próximo | -9.3% | -6.4% |

**Custo da melhor rota em marcos de avaliações:**

| avaliações | Têmpera Simulada | Algoritmo Genético |
| --- | --- | --- |
| 100 | — | 21423.7 |
| 1000 | 21614.9 | 17251.8 |
| 10000 | 18383.8 | 8055.3 |
| 100000 | 16742.6 | 5960.1 (já tinha parado) |

**Rotas finais (ordem de visita):**

- Têmpera Simulada: `48 25 29 42 37 34 4 18 44 35 23 7 17 33 46 16 28 47 38 19 14 45 2 49 5 20 39 31 6 15 27 3 22 11 1 9 26 32 30 40 43 0 10 21 12 41 36 24 8 13`
- Algoritmo Genético: `3 27 6 39 31 32 28 38 47 35 16 46 23 7 17 33 21 40 30 43 0 10 36 41 12 24 8 13 48 25 29 42 37 34 4 18 44 19 14 45 2 49 5 20 15 11 22 1 9 26`
