# grid_system.py
import pygame
import random
from config import CONFIG
from fabricas import ObstaculoFactory, PontoFactory
from adapters import RetangularAdapter, IGridAdapter, HexagonalAdapter
from entidades import ComportamentoFogoDecorator
from math import sqrt, ceil

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
            
        self.largura_tela, self.altura_tela = tela_size
        self.resolucao = CONFIG["GRID_RESOLUCAO"]
        self.obstaculos = {}
        self.pontos_inicio = []
        self.pontos_fim = []
        self.caminhos = []
        self.geometria = geometria
        
        # Margens
        margem_sup = 50
        margem = 20
        self.rect_area = pygame.Rect(margem, margem_sup, 
                                     self.largura_tela - 2*margem, 
                                     self.altura_tela - margem_sup - margem)
        
        # --- CÁLCULO DE DIMENSÕES ---
        if self.geometria == "HEXAGONAL":
            # Hexágonos "Pointy-Topped" (Ponta pra cima) encaixam melhor com offset de linha
            # Altura Total = (n_linhas * 0.75 + 0.25) * Altura_Hex
            self.altura_celula = self.rect_area.height / (self.resolucao * 0.75 + 0.25)
            # Largura = Altura * (sqrt(3)/2)
            self.largura_celula = self.altura_celula * (sqrt(3) / 2)
        else:
            # Retangular: base simples
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
            # Usa a mesma lógica de "Next - Current" para precisão
            col = int(x_rel / (self.rect_area.width / self.resolucao))
            lin = int(y_rel / (self.rect_area.height / self.resolucao))
            return (lin, col)
        
        elif self.geometria == "HEXAGONAL":
            # Aproximação para Pointy-Topped
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
            # Calcula baseado na divisão exata da área total
            step_w = self.rect_area.width / self.resolucao
            step_h = self.rect_area.height / self.resolucao
            cx = self.rect_area.left + col * step_w + step_w / 2
            cy = self.rect_area.top + lin * step_h + step_h / 2
            return (int(cx), int(cy))
        
        elif self.geometria == "HEXAGONAL":
            offset_x = (self.largura_celula / 2) if lin % 2 != 0 else 0
            cx = self.rect_area.left + col * self.largura_celula + offset_x + self.largura_celula / 2
            # Pointy-topped: Distância vertical é 0.75 da altura
            cy = self.rect_area.top + lin * (self.altura_celula * 0.75) + self.altura_celula / 2
            return (int(cx), int(cy))

    def get_rect_celula(self, grid_pos):
        lin, col = grid_pos
        
        if self.geometria == "RETANGULAR":
            step_w = self.rect_area.width / self.resolucao
            step_h = self.rect_area.height / self.resolucao
            
            # Coordenada exata inicial
            x1 = self.rect_area.left + int(col * step_w)
            y1 = self.rect_area.top + int(lin * step_h)
            
            # Coordenada exata final (início do próximo)
            x2 = self.rect_area.left + int((col + 1) * step_w)
            y2 = self.rect_area.top + int((lin + 1) * step_h)
            
            # Largura/Altura é a diferença (garante 0 furos)
            return pygame.Rect(x1, y1, x2 - x1, y2 - y1)
            
        else:
            # Para Hexagonal, retorna o bounding box centrado
            cx, cy = self.get_centro_celula(grid_pos)
            rect = pygame.Rect(0, 0, self.largura_celula, self.altura_celula)
            rect.center = (cx, cy)
            return rect

    def is_dentro(self, pos):
        lin, col = pos
        return 0 <= lin < self.resolucao and 0 <= col < self.resolucao

    def get_pontos_hexagonais(self, lin, col):
        cx, cy = self.get_centro_celula((lin, col))
        
        # Tamanho do lado (Raio) = Altura / 2
        R = self.altura_celula / 2
        # Meia largura = (R * sqrt(3)) / 2
        w_half = self.largura_celula / 2
        
        # Vértices (sentido horário, começando do topo)
        pontos = [
            (cx, cy - R),              # Topo
            (cx + w_half, cy - R/2),   # Nordeste
            (cx + w_half, cy + R/2),   # Sudeste
            (cx, cy + R),              # Baixo
            (cx - w_half, cy + R/2),   # Sudoeste
            (cx - w_half, cy - R/2)    # Noroeste
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

    def gerar_aleatorio(self):
        self.limpar()
        n_obstaculos = int((self.resolucao**2) * 0.2)
        n_pares = self.resolucao
        
        # 1. Obstáculos normais (Paredes)
        while len(self.obstaculos) < n_obstaculos:
            pos = (random.randint(0, self.resolucao-1), random.randint(0, self.resolucao-1))
            # Protege a área de nascimento (0,1) e (1,1)
            if pos != (0,1) and pos != (1,1): 
                self.toggle_obstaculo(pos)

        # 2. Obstáculos de FOGO (Quantidade definida no Config)
        count_fogo = 0
        while count_fogo < CONFIG["NUM_FOGO"]:
            pos = (random.randint(0, self.resolucao-1), random.randint(0, self.resolucao-1))
            
            # Só coloca fogo onde não tem nada e longe do spawn
            if pos not in self.obstaculos and pos != (0,1) and pos != (1,1):
                # Cria Parede -> Decora com Fogo -> Salva
                parede = ObstaculoFactory.criar("PAREDE", pos)
                fogo = ComportamentoFogoDecorator(parede)
                self.obstaculos[pos] = fogo
                count_fogo += 1

        '''# 3. Pontos (Início/Fim)
        for _ in range(n_pares):
            l1, c1 = random.randint(0, self.resolucao-1), random.randint(0, self.resolucao-1)
            l2, c2 = random.randint(0, self.resolucao-1), random.randint(0, self.resolucao-1)
            if (l1,c1) not in self.obstaculos and (l2,c2) not in self.obstaculos:
                self.pontos_inicio.append(PontoFactory.criar("INICIO", (l1,c1)))
                self.pontos_fim.append(PontoFactory.criar("FIM", (l2,c2)))'''
