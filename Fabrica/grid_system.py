import pygame
import random
from config import CONFIG # Configurações
from fabricas import ObstaculoFactory, PontoFactory # Fábricas para criação

# ==========================================
# 4. Gerenciamento do Grid (Model)
# ==========================================

class GridSystem:
    def __init__(self, tela_size):
        self.largura_tela, self.altura_tela = tela_size
        self.resolucao = CONFIG["GRID_RESOLUCAO"]
        self.obstaculos = {} # Dict {pos: Objeto} para acesso rápido
        self.pontos_inicio = [] # Lista de Objetos
        self.pontos_fim = []    # Lista de Objetos
        self.caminhos = []      # Lista de tuplas (lista_coords, cor)
        
        # Definir área de desenho
        margem_sup = 50
        margem = 20
        self.rect_area = pygame.Rect(margem, margem_sup, 
                                     self.largura_tela - 2*margem, 
                                     self.altura_tela - margem_sup - margem)
        self.largura_celula = self.rect_area.width / self.resolucao
        self.altura_celula = self.rect_area.height / self.resolucao

    def pixel_para_grid(self, pos_pixel):
        """Converte clique do mouse (x,y) para (linha, coluna)"""
        if not self.rect_area.collidepoint(pos_pixel):
            return None
        col = int((pos_pixel[0] - self.rect_area.left) // self.largura_celula)
        lin = int((pos_pixel[1] - self.rect_area.top) // self.altura_celula)
        return (lin, col)

    def get_rect_celula(self, grid_pos):
        """Retorna o pygame.Rect para uma posição do grid"""
        lin, col = grid_pos
        x = self.rect_area.left + col * self.largura_celula
        y = self.rect_area.top + lin * self.altura_celula
        return pygame.Rect(x, y, self.largura_celula, self.altura_celula)
    
    def get_centro_celula(self, grid_pos):
        r = self.get_rect_celula(grid_pos)
        return (r.centerx, r.centery)

    def toggle_obstaculo(self, pos):
        if pos in self.obstaculos:
            del self.obstaculos[pos]
        else:
            # USA A FÁBRICA DE OBSTÁCULOS
            obs = ObstaculoFactory.criar("PAREDE", pos)
            self.obstaculos[pos] = obs

    def adicionar_ponto(self, pos):
        if pos in self.obstaculos: return
        
        # USA A FÁBRICA DE PONTOS
        if len(self.pontos_inicio) == len(self.pontos_fim):
            p = PontoFactory.criar("INICIO", pos)
            self.pontos_inicio.append(p)
        else:
            p = PontoFactory.criar("FIM", pos)
            self.pontos_fim.append(p)

    def limpar(self):
        self.obstaculos.clear()
        self.pontos_inicio.clear()
        self.pontos_fim.clear()
        self.caminhos.clear()

    def gerar_aleatorio(self):
        self.limpar()
        densidade = 0.2
        n_obstaculos = int((self.resolucao**2) * densidade)
        n_pares = self.resolucao
        
        # Gerar obstáculos
        while len(self.obstaculos) < n_obstaculos:
            pos = (random.randint(0, self.resolucao-1), random.randint(0, self.resolucao-1))
            if pos not in self.obstaculos:
                self.obstaculos[pos] = ObstaculoFactory.criar("PAREDE", pos)
        
        # Gerar pontos
        count = 0
        while count < n_pares:
            l1, c1 = random.randint(0, self.resolucao-1), random.randint(0, self.resolucao-1)
            if (l1,c1) in self.obstaculos: continue
            
            l2, c2 = random.randint(0, self.resolucao-1), random.randint(0, self.resolucao-1)
            if (l2,c2) in self.obstaculos or (l1,c1) == (l2,c2): continue

            self.pontos_inicio.append(PontoFactory.criar("INICIO", (l1,c1)))
            self.pontos_fim.append(PontoFactory.criar("FIM", (l2,c2)))
            count += 1