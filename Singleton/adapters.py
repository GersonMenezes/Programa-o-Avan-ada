from abc import ABC, abstractmethod

# 1. Target (Interface do Cliente)
class IGridAdapter(ABC):
    """Interface que o GridSystem espera para obter a vizinhança."""
    @abstractmethod
    def obter_vizinhos(self, lin, col, resolucao):
        """Retorna uma lista de coordenadas vizinhas (linha, coluna)."""
        pass

# 2. Adaptee (Serviço Incompatível / Lógica de Geometria)
class RetangularAdapter(IGridAdapter):
    """Implementa a lógica de vizinhança para grids quadrados (4 direções)."""
    def obter_vizinhos(self, lin, col, resolucao):
        direcoes = [(1,0), (-1,0), (0,1), (0,-1)] # Horizontal/Vertical
        vizinhos = []
        for dl, dc in direcoes:
            nl, nc = lin + dl, col + dc
            if 0 <= nl < resolucao and 0 <= nc < resolucao:
                vizinhos.append((nl, nc))
        return vizinhos

# 3. Adaptee (Outro Serviço Incompatível / Outra Geometria)
class HexagonalAdapter(IGridAdapter):
    """Implementa a lógica de vizinhança para grids hexagonais (6 direções)."""
    def obter_vizinhos(self, lin, col, resolucao):
        # A lógica da vizinhança hexagonal depende se a linha é par ou ímpar
        if lin % 2 == 0:
            # Colunas pares
            direcoes = [(-1, 0), (-1, -1), (0, -1), (1, 0), (1, -1), (0, 1)]
        else:
            # Colunas ímpares
            direcoes = [(-1, 0), (-1, 1), (0, 1), (1, 0), (1, 1), (0, -1)]
        
        vizinhos = []
        for dl, dc in direcoes:
            nl, nc = lin + dl, col + dc
            if 0 <= nl < resolucao and 0 <= nc < resolucao:
                vizinhos.append((nl, nc))
        return vizinhos