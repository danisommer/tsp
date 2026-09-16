# Espaço de busca e busca clássica

**O que é:** quantas rotas distintas existem, (n−1)!/2 (girar a rota ou invertê-la não muda o ciclo), e quanto tempo levaria avaliar todas na velocidade medida da função objetivo nesta máquina. É o custo de uma busca cega exaustiva e o pior caso de uma busca informada. A velocidade mede só a avaliação da rota, sem o custo de gerar as permutações, então o tempo real seria ainda maior.

| cidades | rotas distintas | avaliações completas por segundo | tempo para enumerar tudo | fração avaliada pela têmpera |
| --- | --- | --- | --- | --- |
| 20 | ≈ 10^16.8 | 63,420 | ≈ 10^4.5 anos | ≈ 10^-11.7 |
| 50 | ≈ 10^62.5 | 60,113 | ≈ 10^50.2 anos | ≈ 10^-57.0 |
| 100 | ≈ 10^155.7 | 58,685 | ≈ 10^143.4 anos | ≈ 10^-149.8 |

Para comparação, a idade do universo é ≈ 10^10,1 anos.
