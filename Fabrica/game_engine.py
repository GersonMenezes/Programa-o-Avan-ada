import pygame
import random
# Importa todos os módulos necessários
from config import CONFIG
from grid_system import GridSystem
from fabricas import AlgoritmoFactory

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