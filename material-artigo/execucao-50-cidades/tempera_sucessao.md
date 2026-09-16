# Têmpera Simulada: sucessão da melhor rota

**O que a imagem mostra:** a melhor rota encontrada até cada marco de melhoria. O marco de f% é o primeiro estado emitido em que a melhor rota já tinha percorrido f% do caminho entre o custo inicial e o final. A estrela marca a cidade em que a rota começa.

**Resolução:** estados emitidos a cada 500 movimentos. Marcos atingidos no mesmo estado aparecem como um quadro só.

| marco | movimento | avaliações | custo da melhor rota |
| --- | --- | --- | --- |
| 0% | 0 | 101 | 22748.5 |
| 50% | 145500 | 145601 | 13826.5 |
| 80% | 251000 | 251101 | 9051.1 |
| 95% | 312500 | 312601 | 6488.9 |
| 100% | 320500 | 320601 | 5774.8 |

**Ordem de visita em cada marco:**

- 0%: `15 25 37 23 30 6 27 49 3 28 9 33 16 24 0 20 22 7 48 35 17 19 47 29 31 21 44 1 11 39 14 4 42 40 43 26 45 34 2 12 10 36 5 8 32 41 46 18 13 38`
- 50%: `21 8 40 20 1 11 28 5 2 49 6 39 31 15 9 36 41 12 10 7 13 17 33 32 27 38 14 16 37 43 26 22 3 46 34 18 42 4 44 19 47 35 29 25 48 24 45 23 30 0`
- 80%: `16 44 4 38 47 19 45 49 2 14 20 34 42 37 18 5 15 11 22 1 9 3 26 27 6 31 39 28 0 43 32 30 10 40 36 12 41 21 8 24 33 17 46 7 23 13 48 25 29 35`
- 95%: `44 18 47 38 19 14 45 49 2 5 20 31 39 6 27 3 15 11 22 1 26 9 30 32 28 40 33 21 10 43 0 41 36 12 24 8 7 17 13 48 25 29 42 37 23 46 16 35 34 4`
- 100%: `48 25 29 42 37 34 4 18 44 35 23 7 17 33 46 16 28 47 38 19 14 45 2 49 5 20 39 31 6 15 27 3 22 11 1 9 26 32 30 40 43 0 10 21 12 41 36 24 8 13`
