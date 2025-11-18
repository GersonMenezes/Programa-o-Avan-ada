from abc import ABC, abstractmethod
from collections import deque
from config import CONFIG # Precisa do GRID_RESOLUCAO

# ==========================================
# 2. Interfaces de Algoritmo (Strategy Pattern)
# ==========================================

class IPathfinder(ABC):
    @abstractmethod
    def encontrar_caminho(self, inicio, fim, obstaculos_set, resolucao):
        pass

class BFSAlgoritmo(IPathfinder):
    """Implementação do BFS atual (Apenas Horizontal/Vertical)"""
    def encontrar_caminho(self, inicio, fim, obstaculos_set, resolucao):
        filas = deque([(inicio, [inicio])])
        visitados = {inicio}
        direcoes = [(1,0), (-1,0), (0,1), (0,-1)] # Sem diagonal por enquanto
        
        while filas:
            atual, caminho = filas.popleft()
            if atual == fim:
                return caminho
            
            lin, col = atual
            for dl, dc in direcoes:
                nl, nc = lin + dl, col + dc
                vizinho = (nl, nc)
                
                if (0 <= nl < resolucao and 
                    0 <= nc < resolucao and 
                    vizinho not in visitados and 
                    vizinho not in obstaculos_set):
                    
                    visitados.add(vizinho)
                    filas.append((vizinho, caminho + [vizinho]))
        return None