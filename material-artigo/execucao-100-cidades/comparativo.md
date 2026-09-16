# Comparativo: Têmpera Simulada × Algoritmo Genético na mesma instância

**O que a imagem mostra:** no topo, o custo da melhor rota de cada algoritmo ao longo das avaliações (eixo x em escala log), com a rota do vizinho mais próximo tracejada como referência; no meio, as rotas finais completas; embaixo, a tabela comparativa.

**Referência:** vizinho mais próximo a partir da cidade 0, custo 10518.2.

|  | Têmpera Simulada | Algoritmo Genético |
| --- | --- | --- |
| custo da melhor rota inicial | 51420.1 | 44894.6 |
| custo final | 10465.9 | 8541.8 |
| melhora | 79.6% | 81.0% |
| iterações | 670000 movimentos | 1564 gerações |
| avaliações | 670101 | 153372 |
| melhor rota encontrada em | 653101 avaliações | 133772 avaliações |
| tempo | 6.27 s | 15.17 s |
| motivo da parada | temperatura mínima | estagnação |
| diferença para o vizinho mais próximo | -0.5% | -18.8% |

**Custo da melhor rota em marcos de avaliações:**

| avaliações | Têmpera Simulada | Algoritmo Genético |
| --- | --- | --- |
| 100 | — | 44894.6 |
| 1000 | 42423.7 | 37662.8 |
| 10000 | 40256.7 | 21499.5 |
| 100000 | 37888.8 | 8928.0 |

**Rotas finais (ordem de visita):**

- Têmpera Simulada: `82 53 17 7 23 72 55 8 67 13 74 93 48 63 97 29 87 81 25 42 37 34 62 61 44 16 99 18 4 35 73 76 64 77 45 96 54 80 57 65 49 2 14 19 38 78 47 56 85 59 60 32 30 0 43 10 94 36 95 68 71 50 1 52 58 79 26 92 9 89 75 90 11 83 22 15 3 27 6 98 88 5 84 86 51 31 39 20 28 70 46 66 91 33 40 21 24 41 69 12`
- Algoritmo Genético: `46 23 53 72 7 55 17 8 24 12 94 36 95 41 69 67 13 74 93 48 63 81 25 87 42 29 97 37 99 4 44 18 61 34 62 64 76 47 38 78 19 14 45 77 96 54 80 2 49 65 57 86 51 84 5 88 20 60 31 39 98 6 27 79 58 3 22 83 75 15 90 11 89 1 50 71 68 9 26 52 92 32 30 43 0 10 21 40 66 33 91 82 70 28 59 56 73 85 35 16`
