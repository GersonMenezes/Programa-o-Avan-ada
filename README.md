# 📊 Diagrama de Voronoi - Análise Computacional

Este projeto implementa uma aplicação interativa para visualização do **Diagrama de Voronoi** e sua estrutura dual, a **Triangulação de Delaunay**. Além da visualização, o projeto inclui scripts para análise de dados de interação do usuário e análise de desempenho computacional do algoritmo de geração.

---

## 📋 Tabela de Trabalhos e GIT

| Trabalho | Data e Hora | Link para os Arquivos no GIT | Status |
|:--------:|:---------------:|:-----------------------------------------------------|:------:|
| 1 | 17/09/25, 18:00 | [Repositório](https://github.com/GersonMenezes/Programa-o-Avan-ada) | ✅ Concluído |
| 2 | 03/10/25, 18:00 | [Repositório](https://github.com/GersonMenezes/Programa-o-Avan-ada) | ✅ Concluído |
| 3 | 18/10/25, 15:30 | [Repositório](https://github.com/GersonMenezes/Programa-o-Avan-ada/tree/main/Convex%20Hull%20-%20Monotone%20Chain) | ✅ Concluído |
| 15 | - | - | ⏳ Pendente |

---

## ✨ Funcionalidades

### 🎮 Visualização Interativa
- **Criação de pontos** de Voronoi com cliques do mouse
- **Geração e atualização** em tempo real do Diagrama de Voronoi
- **Exibição da Triangulação de Delaunay** (o gráfico dual) sobreposta
- **Capacidade de arrastar pontos** para modificar o diagrama dinamicamente

### 📈 Análise de Desempenho
- Script dedicado (`analise_desempenho.py`) para medir o custo computacional
- **Testes automatizados** com número crescente de pontos e diferentes distribuições espaciais (uniforme vs. cluster)
- **Geração de gráfico** para visualizar a complexidade do algoritmo, demonstrando seu comportamento **O(N log N)**

### 📝 Logging e Análise de Uso
- **Sistema de log completo** em CSV (`log_execucao.csv`) que registra:
  - Criação de pontos
  - Seleção de polígonos
  - Movimento do mouse
- Script (`analise.py`) para gerar gráficos a partir do log de uso

---

## 📁 Estrutura dos Arquivos

```
Programação Avançada/
├── main.py                    # Aplicação principal interativa (Pygame)
├── analise.py                 # Script para analisar log_execucao.csv
├── analise_desempenho.py      # Script para testes de performance
├── .gitignore                 # Configuração Git
├── images/                    # Pasta com gráficos gerados
│   ├── grafico_cliques_poligonos.png
│   ├── grafico_desempenho_voronoi.png
│   ├── grafico_objetos_criados.png
│   └── grafico_percurso_mouse.png
└── README.md                  # Este arquivo
```

---

## Cada pasta tem um vídeo mostrando a implementação feita e como rodar