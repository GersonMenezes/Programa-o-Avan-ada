# 📊 Diagrama de Voronoi - Análise Computacional

Este projeto implementa uma aplicação interativa para visualização do **Diagrama de Voronoi** e sua estrutura dual, a **Triangulação de Delaunay**. Além da visualização, o projeto inclui scripts para análise de dados de interação do usuário e análise de desempenho computacional do algoritmo de geração.

---

## 📋 Tabela de Trabalhos e GIT

| Trabalho | Data e Hora | Link para os Arquivos no GIT | Status |
|:--------:|:---------------:|:-----------------------------------------------------|:------:|
| 1 | 17/09/25, 18:00 | [Repositório](https://github.com/GersonMenezes/Programa-o-Avan-ada) | ✅ Concluído |
| 2 | 03/10/25, 18:00 | [Repositório](https://github.com/GersonMenezes/Programa-o-Avan-ada) | ✅ Concluído |
| 3 | 18/10/25, 15:30 | [Repositório]([https://github.com/GersonMenezes/Programa-o-Avan-ada](https://github.com/GersonMenezes/Programa-o-Avan-ada/tree/main/Convex%20Hull%20-%20Monotone%20Chain)) | ✅ Concluído |
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

## 🚀 Como Usar

### 1. Aplicação Interativa

Execute o programa principal para criar e interagir com os diagramas:

```bash
python main.py
```

#### Modos de Operação:

**Modo EDIÇÃO** (pressione `E`):
- Clique na tela para adicionar pontos
- Clique e arraste um ponto existente para movê-lo

**Modo SELEÇÃO** (pressione `S`):
- Clique em uma região (polígono) para selecioná-la (a seleção é registrada no log)

### 2. Análise da Interação do Usuário

Após fechar a aplicação principal, execute este script para analisar o log de sua interação:

```bash
python analise.py
```

Este script irá gerar e exibir gráficos baseados no arquivo `log_execucao.csv`.

### 3. Análise de Desempenho do Algoritmo

Execute este script para realizar uma análise de performance automatizada:

```bash
python analise_desempenho.py
```

> **Nota:** Este script não é interativo. Ele rodará por alguns segundos, executando testes com milhares de pontos. Ao final, salvará os resultados em `log_desempenho.csv` e gerará o gráfico `grafico_desempenho_voronoi.png`.

---

## 📦 Dependências

| Biblioteca | Descrição |
|------------|-----------|
| `pygame` | Interface gráfica e interação |
| `scipy` | Computação científica |
| `numpy` | Operações numéricas |
| `shapely` | Manipulação de geometrias |
| `pandas` | Análise de dados |
| `matplotlib` | Geração de gráficos |

### Instalação das Dependências

```bash
pip install pygame scipy numpy pandas matplotlib shapely
```

---

## 🎯 Objetivos do Projeto

Este projeto demonstra:
- **Implementação prática** de algoritmos computacionais geométricos
- **Análise de complexidade** algorítmica
- **Visualização interativa** de estruturas matemáticas
- **Coleta e análise** de dados de interação do usuário
- **Geração automática** de relatórios e gráficos

---

## 📊 Resultados Esperados

- **Gráfico de desempenho** mostrando complexidade O(N log N)
- **Análise de padrões** de interação do usuário
- **Visualização clara** do Diagrama de Voronoi e Triangulação de Delaunay
- **Logs estruturados** para análise posterior
