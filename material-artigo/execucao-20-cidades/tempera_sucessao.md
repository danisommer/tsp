# Têmpera Simulada: sucessão da melhor rota

**O que a imagem mostra:** a melhor rota encontrada até cada marco de melhoria. O marco de f% é o primeiro estado emitido em que a melhor rota já tinha percorrido f% do caminho entre o custo inicial e o final. A estrela marca a cidade em que a rota começa.

**Resolução:** estados emitidos a cada 500 movimentos. Marcos atingidos no mesmo estado aparecem como um quadro só.

| marco | movimento | avaliações | custo da melhor rota |
| --- | --- | --- | --- |
| 0% | 0 | 101 | 11486.9 |
| 50% | 500 | 601 | 7449.4 |
| 80% | 43000 | 43101 | 5017.9 |
| 95% | 83000 | 83101 | 3455.1 |
| 100% | 99000 | 99101 | 3415.8 |

**Ordem de visita em cada marco:**

- 0%: `1 10 18 16 7 11 12 17 15 2 3 4 5 8 0 9 14 13 6 19`
- 50%: `11 1 0 13 9 3 5 15 2 14 7 4 18 16 8 12 17 10 19 6`
- 80%: `13 8 17 18 4 14 19 2 5 6 16 7 12 9 1 11 15 3 0 10`
- 95%: `15 11 3 1 9 0 10 12 8 13 17 7 16 4 18 14 19 2 5 6`
- 100%: `14 19 18 4 16 7 17 13 8 12 10 0 9 1 11 15 3 6 5 2`
