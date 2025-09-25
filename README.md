# Diagrama de Voronoi - Gear Up!

### Modos de Operação

1. **Modo EDICAO (Tecla 'E')**:
   - Adiciona pontos clicando na tela
   - Cada novo ponto regenera automaticamente todo o Diagrama de Voronoi
   - Os pontos são numerados na ordem de criação

2. **Modo SELECIONAR (Tecla 'S')**:
   - Permite clicar em polígonos para identificá-los
   - Os polígonos são numerados (P1, P2, P3, etc.) na ordem de criação do ponto central
   - Mostra qual polígono foi clicado no log e no console
   - Clique no ponto e arraste para atualizar a posição do ponto e dos poligonos

### Funcionalidades

- Sistema de log completo (CSV)
- Rastreamento de movimento do mouse
- Contagem de cliques
- Interface visual com instruções

### Como Usar

1. Execute o programa: `python main.py`
2. Use a tecla **E** para entrar no modo de edição
3. Clique na tela para adicionar pontos
4. Use a tecla **S** para entrar no modo de seleção
5. Clique nos polígonos para identificá-los
6. Feche a janela para salvar o log
7. Execute o programa: 'analise.py'
8. Feche o primeiro gráfico para ver o segundo e assim por diante.
9. O terceiro gráfico só sera criado se no "modo seleção" houver cliques nos poligonos

### Dependências

- pygame
- scipy (para algoritmo de Voronoi)
- numpy
- shapely
- panda
- matplotlib

### Instalação das Dependências

```bash
pip install pygame scipy numpy pandas matplotlib shapely
```

### Estrutura do Log

O arquivo `log_execucao.csv` contém:
- `timestamp`: Data e hora do evento
- `tipo_evento`: 'criacao', 'selecao', 'movimento', 'fim_execucao'
- `pos_x`, `pos_y`: Posição do mouse
- `info_extra`: Informações adicionais (ex: 'ponto_1', 'poligono_2', 'nenhum_poligono')
