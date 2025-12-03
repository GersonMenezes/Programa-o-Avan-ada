# game_engine.py
import pygame
import random
from config import CONFIG
# Imports dos Padrões
from chains import PygameInitHandler, DisplayInitHandler, GridInitHandler
from commands import CommandManager, MoverAgenteCommand
from agentes import Agente, Observer
from fabricas import AlgoritmoFactory
from entidades import EntidadeDecorator

class GameEngine(Observer): # GameEngine observa o Agente
    def __init__(self):
        # --- PADRÃO CHAIN OF RESPONSIBILITY (Inicialização) ---
        self.tela = None
        self.grid = None
        self.clock = None
        
        # Cria a cadeia
        init_chain = PygameInitHandler()
        display_handler = DisplayInitHandler()
        grid_handler = GridInitHandler()
        
        init_chain.set_next(display_handler).set_next(grid_handler)
        
        # Executa a cadeia passando 'self' como contexto
        init_chain.handle(self)
        
        # --- Configuração do Jogo ---
        self.modo = "OBSTACULOS"
        self.rodando = True
        self.pathfinder = AlgoritmoFactory.get_algoritmo("BFS_SIMPLES")
        
        # --- PADRÃO COMMAND (Gerenciador) ---
        self.command_manager = CommandManager()
        
        # Criar Agente (Posição inicial 1,1)
        self.agente = Agente((1, 1))
        self.agente.attach(self)

        # --- CONTROLE DE REPETIÇÃO DE TECLA ---
        self.tempo_ultimo_movimento = 0 # Tempo em ms do último comando executado
        self.atraso_movimento_ms = 200  # Atraso desejado (0.2 segundos

    # --- IMPLEMENTAÇÃO DO OBSERVER ---
    def update(self, evento, dados):
        if evento == "morreu":
            print(">>> GAME OVER: Agente morreu! Reiniciando fase...")
            self.agente.vida = CONFIG["VIDA_INICIAL"]
            self.agente.mover_para((1, 1)) # Volta pro spawn seguro
            self.command_manager.historico.clear()
                    

    def processar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.rodando = False
            
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE: self.rodando = False
                
                tempo_atual = pygame.time.get_ticks() 

                # --- LÓGICA DE MOVIMENTO E COLISÃO ---
                dx, dy = 0, 0
                if evento.key == pygame.K_UP:    dx, dy = -1, 0
                if evento.key == pygame.K_DOWN:  dx, dy = 1, 0
                if evento.key == pygame.K_LEFT:  dx, dy = 0, -1
                if evento.key == pygame.K_RIGHT: dx, dy = 0, 1
                
                # Se houve tentativa de movimento e o atraso de tempo foi atingido
                if (dx != 0 or dy != 0) and (tempo_atual - self.tempo_ultimo_movimento > self.atraso_movimento_ms): 
                    
                    nova_pos = (self.agente.pos[0] + dx, self.agente.pos[1] + dy)
                    
                    # 1. Verifica Limites da Tela
                    if not self.grid.is_dentro(nova_pos):
                        print("Movimento bloqueado: Fim do mapa.")
                        continue 
                    
                    # 2. Verifica Obstáculos
                    if nova_pos in self.grid.obstaculos:
                        obs = self.grid.obstaculos[nova_pos]
                        dano = obs.get_dano()
                        
                        if dano > 0:
                            print(f"Bloqueado! Tentou entrar no fogo. Dano: -{dano}")
                            self.agente.receber_dano(dano)
                        else:
                            print("Bloqueado! Parede.")
                        
                        continue 

                    # Uma nova instância para cada movimento para salvar no histórico
                    cmd = MoverAgenteCommand(self.agente, dx, dy)
                    self.command_manager.executar(cmd)
                    
                    # 4. ATUALIZA O TEMPO: Registra o momento deste movimento
                    self.tempo_ultimo_movimento = tempo_atual

                # --- UNDO (Z) ---
                if evento.key == pygame.K_z:
                    self.command_manager.desfazer()

                # Teclas de Sistema
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
        if self.modo == "OBSTACULOS": self.modo = "PONTOS"
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
            caminho = self.pathfinder.encontrar_caminho(inicio, fim, obstaculos_coords, self.grid.resolucao)
            if caminho:
                cor = tuple(random.randint(50, 255) for _ in range(3))
                self.grid.caminhos.append((caminho, cor))

    def desenhar(self):
        self.tela.fill(CONFIG["CORES"]["BRANCO"])
        
        # 1. Desenha Grid (Lógica Hexagonal/Retangular interna do GridSystem)
        if self.grid.geometria == "HEXAGONAL":
            for lin in range(self.grid.resolucao):
                for col in range(self.grid.resolucao):
                    pontos = self.grid.get_pontos_hexagonais(lin, col)
                    pygame.draw.polygon(self.tela, CONFIG["CORES"]["CINZA"], pontos, 1)
        else:
            # Retangular
            area = self.grid.rect_area
            for i in range(self.grid.resolucao + 1):
                x = area.left + int(i * (area.width / self.grid.resolucao))
                pygame.draw.line(self.tela, CONFIG["CORES"]["CINZA"], (x, area.top), (x, area.bottom), 1)
            for i in range(self.grid.resolucao + 1):
                y = area.top + int(i * (area.height / self.grid.resolucao))
                pygame.draw.line(self.tela, CONFIG["CORES"]["CINZA"], (area.left, y), (area.right, y), 1)

        # 2. Obstáculos
        for obs in self.grid.obstaculos.values():
            lin, col = obs.pos
            if self.grid.geometria == "HEXAGONAL":
                pontos = self.grid.get_pontos_hexagonais(lin, col)
                pygame.draw.polygon(self.tela, CONFIG["CORES"]["PRETO"], pontos)
            if isinstance(obs, EntidadeDecorator) or self.grid.geometria == "RETANGULAR":
                obs.desenhar(self.tela, self.grid.get_rect_celula(obs.pos))

        # 3. Pontos e Caminhos
        for p in self.grid.pontos_inicio: p.desenhar(self.tela, self.grid.get_rect_celula(p.pos))
        for p in self.grid.pontos_fim: p.desenhar(self.tela, self.grid.get_rect_celula(p.pos))
        for caminho, cor in self.grid.caminhos:
            pontos_pixel = [self.grid.get_centro_celula(p) for p in caminho]
            if len(pontos_pixel) > 1: pygame.draw.lines(self.tela, cor, False, pontos_pixel, 4)

        # 4. Desenhar AGENTE
        self.agente.desenhar(self.tela, self.grid.get_rect_celula(self.agente.pos))

        # UI
        txt_geo = "Hexagonal" if self.grid.geometria == "HEXAGONAL" else "Retangular"
        fonte = pygame.font.Font(None, 24)
        texto = f"Modo: {self.modo} ({txt_geo}) | Setas: Mover Agente | Z: Undo | Vida: {self.agente.vida}"
        surf = fonte.render(texto, True, CONFIG["CORES"]["PRETO"])
        self.tela.blit(surf, (20, 10))
        pygame.display.flip()

    def run(self):
        while self.rodando:
            self.processar_eventos()
            self.desenhar()
            self.clock.tick(30)
        pygame.quit()
