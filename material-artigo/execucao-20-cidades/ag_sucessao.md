# Algoritmo Genético: sucessão da melhor rota

**O que a imagem mostra:** a melhor rota encontrada até cada marco de melhoria. O marco de f% é o primeiro estado emitido em que a melhor rota já tinha percorrido f% do caminho entre o custo inicial e o final. A estrela marca a cidade em que a rota começa.

**Resolução:** estados emitidos a cada 1 gerações. Marcos atingidos no mesmo estado aparecem como um quadro só.

| marco | geração | avaliações | custo da melhor rota |
| --- | --- | --- | --- |
| 0% | 0 | 100 | 8485.5 |
| 50% | 5 | 590 | 4941.6 |
| 80% | 31 | 3138 | 4340.9 |
| 95% | 41 | 4118 | 3635.6 |
| 100% | 66 | 6568 | 3428.7 |

**Ordem de visita em cada marco:**

- 0%: `12 13 17 7 16 0 14 5 4 8 6 1 3 15 11 9 18 10 19 2`
- 50%: `5 6 18 4 16 0 9 11 15 3 1 10 12 8 13 17 7 14 19 2`
- 80%: `7 17 13 8 12 10 0 9 1 3 15 11 6 14 19 2 5 16 4 18`
- 95%: `9 1 3 11 6 15 5 2 19 14 18 4 16 7 17 13 8 12 10 0`
- 100%: `9 1 3 11 15 6 5 2 14 19 18 4 16 7 17 13 8 12 10 0`
