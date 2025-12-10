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
    """Implementação do BFS que usa o Adapter da GridSystem para obter vizinhos."""
    def encontrar_caminho(self, inicio, fim, obstaculos_set, resolucao):

        from grid_system import GridSystem # Para obter a vizinhança
        # Obtém a instância única do GridSystem
        grid_singleton = GridSystem.getInstance() 

        filas = deque([(inicio, [inicio])])
        visitados = {inicio}
        
        while filas:
            atual, caminho = filas.popleft()
            if atual == fim:
                return caminho
            
            lin, col = atual
            
            # CHAMA O ADAPTER através do Singleton
            vizinhos = grid_singleton.obter_vizinhos(lin, col) 
            
            for vizinho in vizinhos:
                if vizinho not in visitados and vizinho not in obstaculos_set:
                    visitados.add(vizinho)
                    filas.append((vizinho, caminho + [vizinho]))
        return None