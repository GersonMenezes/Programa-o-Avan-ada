import pygame
import random
from collections import deque
from abc import ABC, abstractmethod

# --- Configurações Globais ---
CONFIG = {
    "LARGURA_TELA": 800,
    "ALTURA_TELA": 600,
    "GRID_RESOLUCAO": 20,
    "CORES": {
        "BRANCO": (255, 255, 255),
        "PRETO": (0, 0, 0),
        "VERMELHO": (255, 0, 0),
        "AZUL": (0, 0, 255),
        "VERDE": (0, 255, 0),
        "CINZA": (200, 200, 200)
    }
}

# ==========================================
# 1. Interfaces e Produtos (O que é criado)
# ==========================================

class EntidadeGrid(ABC):
    """Classe base para qualquer coisa desenhável no grid"""
    def __init__(self, pos_grid):
        self.pos = pos_grid # Tupla (linha, coluna)

    @abstractmethod
    def desenhar(self, tela, rect):
        pass

# --- Produtos Concretos: Obstáculos ---
class ObstaculoParede(EntidadeGrid):
    def desenhar(self, tela, rect):
        pygame.draw.rect(tela, CONFIG["CORES"]["PRETO"], rect)

# --- Produtos Concretos: Pontos ---
class PontoInicio(EntidadeGrid):
    def desenhar(self, tela, rect):
        centro = (rect.centerx, rect.centery)
        pygame.draw.circle(tela, CONFIG["CORES"]["AZUL"], centro, 6)

class PontoFim(EntidadeGrid):
    def desenhar(self, tela, rect):
        centro = (rect.centerx, rect.centery)
        pygame.draw.circle(tela, CONFIG["CORES"]["VERMELHO"], centro, 6)

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

# ==========================================
# 5. Classe Principal do Jogo (Controller/View)
# ==========================================

class GameEngine:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((CONFIG["LARGURA_TELA"], CONFIG["ALTURA_TELA"]))
        pygame.display.set_caption("Grid com Factory Pattern")
        self.clock = pygame.time.Clock()
        self.grid = GridSystem(self.tela.get_size())
        
        self.modo = "OBSTACULOS" # OBSTACULOS, PONTOS, CAMINHOS
        self.rodando = True
        
        # Instancia o algoritmo via Fábrica
        self.pathfinder = AlgoritmoFactory.get_algoritmo("BFS_SIMPLES")

    def processar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.rodando = False
            
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE: self.rodando = False
                if evento.key == pygame.K_s: self.alternar_modo()
                if evento.key == pygame.K_c: 
                    self.grid.limpar()
                    self.modo = "OBSTACULOS"
                if evento.key == pygame.K_a:
                    self.grid.gerar_aleatorio()
                    self.recalcular_caminhos()
                    self.modo = "CAMINHOS"

            elif evento.type == pygame.MOUSEBUTTONDOWN:
                cel = self.grid.pixel_para_grid(evento.pos)
                if cel:
                    if self.modo == "OBSTACULOS":
                        self.grid.toggle_obstaculo(cel)
                    elif self.modo == "PONTOS":
                        self.grid.adicionar_ponto(cel)

    def alternar_modo(self):
        if self.modo == "OBSTACULOS":
            self.modo = "PONTOS"
        elif self.modo == "PONTOS":
            self.modo = "CAMINHOS"
            self.recalcular_caminhos()
        elif self.modo == "CAMINHOS":
            self.modo = "OBSTACULOS"
            self.grid.caminhos.clear()
    
    def recalcular_caminhos(self):
        self.grid.caminhos = []
        pares = min(len(self.grid.pontos_inicio), len(self.grid.pontos_fim))
        obstaculos_coords = set(self.grid.obstaculos.keys())
        
        for i in range(pares):
            inicio = self.grid.pontos_inicio[i].pos
            fim = self.grid.pontos_fim[i].pos
            
            # Usa o algoritmo da fábrica
            caminho = self.pathfinder.encontrar_caminho(
                inicio, fim, obstaculos_coords, self.grid.resolucao
            )
            
            if caminho:
                cor = tuple(random.randint(50, 255) for _ in range(3))
                self.grid.caminhos.append((caminho, cor))

    def desenhar(self):
        self.tela.fill(CONFIG["CORES"]["BRANCO"])
        
        # Desenha Grid Lines
        area = self.grid.rect_area
        pygame.draw.rect(self.tela, CONFIG["CORES"]["VERDE"], area, 1)
        for i in range(self.grid.resolucao + 1):
            x = area.left + i * self.grid.largura_celula
            y = area.top + i * self.grid.altura_celula
            pygame.draw.line(self.tela, CONFIG["CORES"]["CINZA"], (x, area.top), (x, area.bottom))
            pygame.draw.line(self.tela, CONFIG["CORES"]["CINZA"], (area.left, y), (area.right, y))

        # Desenha Objetos usando Polimorfismo (cada objeto sabe se desenhar)
        for obs in self.grid.obstaculos.values():
            obs.desenhar(self.tela, self.grid.get_rect_celula(obs.pos))
            
        for p_ini in self.grid.pontos_inicio:
            p_ini.desenhar(self.tela, self.grid.get_rect_celula(p_ini.pos))
            
        for p_fim in self.grid.pontos_fim:
            p_fim.desenhar(self.tela, self.grid.get_rect_celula(p_fim.pos))

        # Desenha Caminhos
        for caminho, cor in self.grid.caminhos:
            pontos_pixel = [self.grid.get_centro_celula(p) for p in caminho]
            if len(pontos_pixel) > 1:
                pygame.draw.lines(self.tela, cor, False, pontos_pixel, 4)

        # UI Texto
        fonte = pygame.font.Font(None, 26)
        texto = f"Modo: {self.modo} | S: Trocar Modo | C: Limpar | A: Aleatório"
        surf = fonte.render(texto, True, CONFIG["CORES"]["PRETO"])
        self.tela.blit(surf, (20, 10))

        pygame.display.flip()

    def run(self):
        while self.rodando:
            self.processar_eventos()
            self.desenhar()
            self.clock.tick(30)
        pygame.quit()

if __name__ == "__main__":
    jogo = GameEngine()
    jogo.run()