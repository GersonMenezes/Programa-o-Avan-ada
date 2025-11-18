from entidades import ObstaculoParede, PontoInicio, PontoFim # Importa os produtos
from algoritmos import BFSAlgoritmo # Importa o algoritmo

# ==========================================
# 3. FÁBRICAS (Factory Method)
# ==========================================

class ObstaculoFactory:
    @staticmethod
    def criar(tipo, pos):
        if tipo == "PAREDE":
            return ObstaculoParede(pos)
        # Futuro: elif tipo == "AGUA": return ObstaculoAgua(pos)
        raise ValueError(f"Tipo de obstáculo desconhecido: {tipo}")

class PontoFactory:
    @staticmethod
    def criar(tipo, pos):
        if tipo == "INICIO":
            return PontoInicio(pos)
        elif tipo == "FIM":
            return PontoFim(pos)
        raise ValueError(f"Tipo de ponto desconhecido: {tipo}")

class AlgoritmoFactory:
    @staticmethod
    def get_algoritmo(tipo="BFS_SIMPLES"):
        if tipo == "BFS_SIMPLES":
            return BFSAlgoritmo()
        # Futuro: elif tipo == "DIAGONAL": return BFSDiagonal()
        # Futuro: elif tipo == "ASTAR": return AStarAlgoritmo()
        return BFSAlgoritmo()