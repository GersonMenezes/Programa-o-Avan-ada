# game_engine.py
import pygame
import random
from config import CONFIG
from grid_system import GridSystem
from fabricas import AlgoritmoFactory
from entidades import EntidadeDecorator

class GameEngine:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((CONFIG["LARGURA_TELA"], CONFIG["ALTURA_TELA"]))
        pygame.display.set_caption("Grid com Factory Pattern")
        self.clock = pygame.time.Clock()
        
        # Mudar aqui entre "RETANGULAR" ou "HEXAGONAL"
        self.grid = GridSystem.getInstance(self.tela.get_size(), geometria="RETANGULAR")
        
        self.modo = "OBSTACULOS"
        self.rodando = True
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
            caminho = self.pathfinder.encontrar_caminho(
                inicio, fim, obstaculos_coords, self.grid.resolucao
            )
            if caminho:
                cor = tuple(random.randint(50, 255) for _ in range(3))
                self.grid.caminhos.append((caminho, cor))

    def desenhar(self):
        self.tela.fill(CONFIG["CORES"]["BRANCO"])
        area = self.grid.rect_area
        
        # === 1. DESENHO DO GRID (Fundo) ===
        if self.grid.geometria == "RETANGULAR":
            # Desenha linhas longas para evitar furos de arredondamento
            # Verticais
            for i in range(self.grid.resolucao + 1):
                # Calcula posição exata baseada na proporção
                x = area.left + int(i * (area.width / self.grid.resolucao))
                pygame.draw.line(self.tela, CONFIG["CORES"]["CINZA"], (x, area.top), (x, area.bottom), 1)
            # Horizontais
            for i in range(self.grid.resolucao + 1):
                y = area.top + int(i * (area.height / self.grid.resolucao))
                pygame.draw.line(self.tela, CONFIG["CORES"]["CINZA"], (area.left, y), (area.right, y), 1)
                
        elif self.grid.geometria == "HEXAGONAL":
            for lin in range(self.grid.resolucao):
                for col in range(self.grid.resolucao):
                    pontos = self.grid.get_pontos_hexagonais(lin, col)
                    pygame.draw.polygon(self.tela, CONFIG["CORES"]["CINZA"], pontos, 1)

        # === 2. DESENHO DOS OBSTÁCULOS ===
        for obs in self.grid.obstaculos.values():
            lin, col = obs.pos
            
            if self.grid.geometria == "HEXAGONAL":
                # Desenha o hexágono preto
                pontos = self.grid.get_pontos_hexagonais(lin, col)
                pygame.draw.polygon(self.tela, CONFIG["CORES"]["PRETO"], pontos)
                
                # Se for Decorator (ex: Fogo), desenha o efeito extra
                if isinstance(obs, EntidadeDecorator):
                    obs.desenhar(self.tela, self.grid.get_rect_celula(obs.pos))
            else:
                # No modo retangular, usa o rect corrigido (sem furos)
                obs.desenhar(self.tela, self.grid.get_rect_celula(obs.pos))

        # === 3. PONTOS E CAMINHOS ===
        for p in self.grid.pontos_inicio:
            p.desenhar(self.tela, self.grid.get_rect_celula(p.pos))
        for p in self.grid.pontos_fim:
            p.desenhar(self.tela, self.grid.get_rect_celula(p.pos))

        for caminho, cor in self.grid.caminhos:
            pontos_pixel = [self.grid.get_centro_celula(p) for p in caminho]
            if len(pontos_pixel) > 1:
                pygame.draw.lines(self.tela, cor, False, pontos_pixel, 4)

        # UI
        txt_geo = "Hexagonal" if self.grid.geometria == "HEXAGONAL" else "Retangular"
        fonte = pygame.font.Font(None, 26)
        texto = f"Modo: {self.modo} ({txt_geo}) | S: Trocar Modo | C: Limpar | A: Aleatório"
        surf = fonte.render(texto, True, CONFIG["CORES"]["PRETO"])
        self.tela.blit(surf, (20, 10))

        pygame.display.flip()

    def run(self):
        while self.rodando:
            self.processar_eventos()
            self.desenhar()
            self.clock.tick(30)
        pygame.quit()