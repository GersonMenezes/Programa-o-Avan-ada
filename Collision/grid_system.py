# grid_system.py
import pygame
import random
from config import CONFIG
from fabricas import ObstaculoFactory, PontoFactory, AlgoritmoFactory
from adapters import RetangularAdapter, IGridAdapter, HexagonalAdapter
from entidades import ComportamentoFogoDecorator, EntidadeGrid, ObstaculoParede, PontoInicio, PontoFim 
from math import sqrt, ceil
from typing import Dict, Tuple, List 

try:
    from agentes import AgenteIA
except ImportError:
    class AgenteIA: pass

class GridSystem:
    _instance = None 

    @staticmethod
    def getInstance(tela_size=None, geometria="RETANGULAR"):
        if GridSystem._instance is None:
            if tela_size is None:
                raise Exception("Tela indefinida.")
            GridSystem._instance = GridSystem(tela_size, geometria)
        return GridSystem._instance

    def __init__(self, tela_size, geometria):
        if GridSystem._instance is not None:
            raise Exception("Singleton violado!")
        
        self.obstaculos: Dict[Tuple[int, int], EntidadeGrid] = {}
        self.pontos_inicio: List[PontoInicio] = []
        self.pontos_fim: List[PontoFim] = []
        self.caminhos: List[Tuple[List, Tuple]] = []
        
        self.lista_intencao: Dict[Tuple[int, int], AgenteIA] = {}
        self.pathfinder_ia = AlgoritmoFactory.get_algoritmo("BFS_SIMPLES")
            
        self.largura_tela, self.altura_tela = tela_size
        self.resolucao = CONFIG["GRID_RESOLUCAO"]
        self.geometria = geometria
        
        margem_sup = 50
        margem = 20
        self.rect_area = pygame.Rect(margem, margem_sup, 
                                     self.largura_tela - 2*margem, 
                                     self.altura_tela - margem_sup - margem)
        
        if self.geometria == "HEXAGONAL":
            self.altura_celula = self.rect_area.height / (self.resolucao * 0.75 + 0.25)
            self.largura_celula = self.altura_celula * (sqrt(3) / 2)
        else:
            self.largura_celula = self.rect_area.width / self.resolucao
            self.altura_celula = self.rect_area.height / self.resolucao

        self.geometria_adapter = self._configurar_geometria(geometria)

    def _configurar_geometria(self, geometria):
        if geometria == "RETANGULAR":
            return RetangularAdapter() 
        elif geometria == "HEXAGONAL":
            return HexagonalAdapter()
        else:
            raise ValueError("Geometria desconhecida.")

    def obter_vizinhos(self, lin, col):
        return self.geometria_adapter.obter_vizinhos(lin, col, self.resolucao)

    def pixel_para_grid(self, pos_pixel):
        if not self.rect_area.collidepoint(pos_pixel):
            return None
        
        x_rel = pos_pixel[0] - self.rect_area.left
        y_rel = pos_pixel[1] - self.rect_area.top

        if self.geometria == "RETANGULAR":
            col = int(x_rel / (self.rect_area.width / self.resolucao))
            lin = int(y_rel / (self.rect_area.height / self.resolucao))
            return (lin, col)
        elif self.geometria == "HEXAGONAL":
            altura_efetiva = self.altura_celula * 0.75
            lin = int(y_rel // altura_efetiva)
            offset_x = (self.largura_celula / 2) if lin % 2 != 0 else 0
            col = int((x_rel - offset_x) // self.largura_celula)
            if 0 <= lin < self.resolucao and 0 <= col < self.resolucao:
                return (lin, col)
            return None

    def get_centro_celula(self, grid_pos):
        lin, col = grid_pos
        if self.geometria == "RETANGULAR":
            step_w = self.rect_area.width / self.resolucao
            step_h = self.rect_area.height / self.resolucao
            cx = self.rect_area.left + col * step_w + step_w / 2
            cy = self.rect_area.top + lin * step_h + step_h / 2
            return (int(cx), int(cy))
        elif self.geometria == "HEXAGONAL":
            offset_x = (self.largura_celula / 2) if lin % 2 != 0 else 0
            cx = self.rect_area.left + col * self.largura_celula + offset_x + self.largura_celula / 2
            cy = self.rect_area.top + lin * (self.altura_celula * 0.75) + self.altura_celula / 2
            return (int(cx), int(cy))

    def get_rect_celula(self, grid_pos):
        lin, col = grid_pos
        if self.geometria == "RETANGULAR":
            step_w = self.rect_area.width / self.resolucao
            step_h = self.rect_area.height / self.resolucao
            x1 = self.rect_area.left + int(col * step_w)
            y1 = self.rect_area.top + int(lin * step_h)
            x2 = self.rect_area.left + int((col + 1) * step_w)
            y2 = self.rect_area.top + int((lin + 1) * step_h)
            return pygame.Rect(x1, y1, x2 - x1, y2 - y1)
        else:
            cx, cy = self.get_centro_celula(grid_pos)
            rect = pygame.Rect(0, 0, self.largura_celula, self.altura_celula)
            rect.center = (cx, cy)
            return rect

    def is_dentro(self, pos):
        lin, col = pos
        return 0 <= lin < self.resolucao and 0 <= col < self.resolucao

    def is_livre(self, pos, ignorar_agentes=False):
        """Verifica se a posição é válida, dentro da tela e sem obstáculo."""
        if not self.is_dentro(pos):
            return False
        if pos in self.obstaculos:
            return False
        return True

    def get_pontos_hexagonais(self, lin, col):
        cx, cy = self.get_centro_celula((lin, col))
        R = self.altura_celula / 2
        w_half = self.largura_celula / 2
        pontos = [
            (cx, cy - R), (cx + w_half, cy - R/2), (cx + w_half, cy + R/2),
            (cx, cy + R), (cx - w_half, cy + R/2), (cx - w_half, cy - R/2)
        ]
        return [(int(px), int(py)) for px, py in pontos]

    # --- Lógica de Jogo ---
    def toggle_obstaculo(self, pos):
        if pos in self.obstaculos:
            del self.obstaculos[pos]
        else:
            self.obstaculos[pos] = ObstaculoFactory.criar("PAREDE", pos)

    def adicionar_ponto(self, pos):
        if pos in self.obstaculos: return
        if len(self.pontos_inicio) == len(self.pontos_fim):
            self.pontos_inicio.append(PontoFactory.criar("INICIO", pos))
        else:
            self.pontos_fim.append(PontoFactory.criar("FIM", pos))

    def limpar(self):
        self.obstaculos.clear()
        self.pontos_inicio.clear()
        self.pontos_fim.clear()
        self.caminhos.clear()
        self.lista_intencao.clear()

    def gerar_aleatorio(self):
        self.limpar()
        n_obstaculos = int((self.resolucao**2) * 0.2)
        while len(self.obstaculos) < n_obstaculos:
            pos = (random.randint(0, self.resolucao-1), random.randint(0, self.resolucao-1))
            if pos != (0,1) and pos != (1,1): 
                self.toggle_obstaculo(pos)
        count_fogo = 0
        while count_fogo < CONFIG["NUM_FOGO"]:
            pos = (random.randint(0, self.resolucao-1), random.randint(0, self.resolucao-1))
            if pos not in self.obstaculos and pos != (0,1) and pos != (1,1):
                parede = ObstaculoFactory.criar("PAREDE", pos)
                fogo = ComportamentoFogoDecorator(parede)
                self.obstaculos[pos] = fogo
                count_fogo += 1