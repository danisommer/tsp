# Algoritmo Genético: sucessão da melhor rota

**O que a imagem mostra:** a melhor rota encontrada até cada marco de melhoria. O marco de f% é o primeiro estado emitido em que a melhor rota já tinha percorrido f% do caminho entre o custo inicial e o final. A estrela marca a cidade em que a rota começa.

**Resolução:** estados emitidos a cada 1 gerações. Marcos atingidos no mesmo estado aparecem como um quadro só.

| marco | geração | avaliações | custo da melhor rota |
| --- | --- | --- | --- |
| 0% | 0 | 100 | 21423.7 |
| 50% | 27 | 2746 | 13453.8 |
| 80% | 84 | 8332 | 9048.9 |
| 95% | 172 | 16956 | 6704.7 |
| 100% | 426 | 41848 | 5960.1 |

**Ordem de visita em cada marco:**

- 0%: `11 3 9 6 27 35 30 28 5 40 39 32 31 43 22 42 7 45 4 23 47 29 24 41 17 19 34 21 13 48 16 49 1 26 18 2 15 36 25 12 8 20 46 0 33 38 37 44 14 10`
- 50%: `12 30 8 42 7 41 36 10 33 48 0 20 27 15 26 22 1 11 9 3 6 39 5 38 44 49 2 45 19 34 29 37 32 43 21 16 24 40 31 47 14 18 4 25 46 28 35 23 17 13`
- 80%: `16 35 46 23 7 48 25 42 34 29 37 4 18 44 14 19 45 38 47 20 27 15 26 22 1 11 9 3 6 28 40 12 10 0 30 21 24 8 13 17 33 41 36 43 32 39 31 5 2 49`
- 95%: `20 15 11 22 1 9 26 27 3 6 39 31 32 43 21 33 17 13 8 24 12 41 36 10 0 40 30 28 38 47 35 16 46 23 7 48 25 29 42 34 37 4 18 44 14 45 19 49 2 5`
- 100%: `3 27 6 39 31 32 28 38 47 35 16 46 23 7 17 33 21 40 30 43 0 10 36 41 12 24 8 13 48 25 29 42 37 34 4 18 44 19 14 45 2 49 5 20 15 11 22 1 9 26`
