# game_engine.py
import pygame
import random
import time
from config import CONFIG
from chains import PygameInitHandler, DisplayInitHandler, GridInitHandler
from commands import CommandManager, MoverAgenteCommand
from agentes import Agente, AgenteIA, Observer
from fabricas import AlgoritmoFactory
from entidades import EntidadeDecorator

# Tipagem
from typing import List
try:
    from agentes import AgenteIA
except ImportError:
    class AgenteIA: pass

class GameEngine(Observer):
    def __init__(self):
        self.tela = None
        self.grid = None
        self.clock = None
        
        init_chain = PygameInitHandler()
        display_handler = DisplayInitHandler()
        grid_handler = GridInitHandler()
        
        init_chain.set_next(display_handler).set_next(grid_handler)
        init_chain.handle(self)
        
        self.modo = "OBSTACULOS"
        self.rodando = True
        self.pathfinder = AlgoritmoFactory.get_algoritmo("BFS_SIMPLES")
        
        self.command_manager = CommandManager()
        self.agentes_ativos: List[AgenteIA] = [] 

    def update(self, evento, dados):
        if evento == "morreu":
            agente_morto = dados
            print(f">>> AGENTE {agente_morto.pos} MORREU! Removendo...")
            if agente_morto in self.agentes_ativos:
                self.agentes_ativos.remove(agente_morto)
                if agente_morto.intenção_atual in self.grid.lista_intencao:
                    del self.grid.lista_intencao[agente_morto.intenção_atual]

    def controlar_agentes_ia(self):
        tempo_atual = pygame.time.get_ticks()
        
        # 1. Atualizar a Lista de Intenção Global
        # Limpar e recriar com base no que cada agente QUER fazer (ou onde está parado)
        self.grid.lista_intencao.clear()
        for agente in self.agentes_ativos:
            self.grid.lista_intencao[agente.intenção_atual] = agente

        # 2. Executar Lógica Individual
        for agente in list(self.agentes_ativos):
            if agente.pos == agente.pos_final:
                self.agentes_ativos.remove(agente)
                continue
            
            # Verifica se está na hora deste agente se mover
            if agente.verificar_tempo(tempo_atual):
                
                # Planeja (Retorna movimento ou 0,0 se esperar/desviar)
                # Passar a lista de agentes para ele checar colisão física
                delta = agente.planejar_movimento(self.grid, self.agentes_ativos)
                
                if delta:
                    dx, dy = delta
                    nova_pos = agente.pos[0] + dx, agente.pos[1] + dy
                    
                    if nova_pos != agente.pos:
                        # Aplica Dano se houver
                        if nova_pos in self.grid.obstaculos:
                             dano = self.grid.obstaculos[nova_pos].get_dano()
                             if dano > 0:
                                agente.receber_dano(dano)
                        
                        # Executa Movimento
                        cmd = MoverAgenteCommand(agente, dx, dy)
                        self.command_manager.executar(cmd)
                        
                        # Atualiza Intenção no Grid (Remove da velha, põe na nova)
                        if agente.pos in self.grid.lista_intencao:
                            del self.grid.lista_intencao[agente.pos]
                        self.grid.lista_intencao[agente.intenção_atual] = agente

                # Agenda o próximo movimento (sorteia 250 ou 500ms)
                agente.agendar_proximo_movimento(tempo_atual)

    def processar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.rodando = False
            
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE: self.rodando = False
                if evento.key == pygame.K_z: self.command_manager.desfazer()
                if evento.key == pygame.K_s: self.alternar_modo()
                if evento.key == pygame.K_c: 
                    self.grid.limpar()
                    self.agentes_ativos.clear()
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
            self.agentes_ativos.clear()
    
    def recalcular_caminhos(self):
        self.grid.caminhos.clear()
        self.agentes_ativos.clear()
        self.grid.lista_intencao.clear()
        
        cores = [CONFIG["CORES"]["AZUL"], CONFIG["CORES"]["VERDE"], CONFIG["CORES"]["VERMELHO"], CONFIG["CORES"]["LARANJA"]]
        pares = min(len(self.grid.pontos_inicio), len(self.grid.pontos_fim))
        
        tempo_atual = pygame.time.get_ticks()

        for i in range(pares):
            inicio = self.grid.pontos_inicio[i].pos
            fim = self.grid.pontos_fim[i].pos
            cor = cores[i % len(cores)]
            
            caminho_completo = self.pathfinder.encontrar_caminho(
                inicio, fim, self.grid.obstaculos.keys(), self.grid.resolucao
            )
            
            if caminho_completo and len(caminho_completo) > 1:
                agente_ia = AgenteIA(inicio, fim, caminho_completo[1:], cor)
                agente_ia.attach(self)
                # Inicia o timer do agente
                agente_ia.agendar_proximo_movimento(tempo_atual)
                self.agentes_ativos.append(agente_ia)
                
                # Adiciona caminho para visualização (opcional)
                self.grid.caminhos.append((caminho_completo, cor))
                
        if self.agentes_ativos:
            print(f"Controle IA ATIVADO: {len(self.agentes_ativos)} agentes.")

    def desenhar(self):
        self.tela.fill(CONFIG["CORES"]["BRANCO"])
        
        # Grid
        if self.grid.geometria == "HEXAGONAL":
            for lin in range(self.grid.resolucao):
                for col in range(self.grid.resolucao):
                    pontos = self.grid.get_pontos_hexagonais(lin, col)
                    pygame.draw.polygon(self.tela, CONFIG["CORES"]["CINZA"], pontos, 1)
        else:
            area = self.grid.rect_area
            for i in range(self.grid.resolucao + 1):
                x = area.left + int(i * (area.width / self.grid.resolucao))
                pygame.draw.line(self.tela, CONFIG["CORES"]["CINZA"], (x, area.top), (x, area.bottom), 1)
            for i in range(self.grid.resolucao + 1):
                y = area.top + int(i * (area.height / self.grid.resolucao))
                pygame.draw.line(self.tela, CONFIG["CORES"]["CINZA"], (area.left, y), (area.right, y), 1)

        # Obstáculos
        for obs in self.grid.obstaculos.values():
            lin, col = obs.pos
            if self.grid.geometria == "HEXAGONAL":
                pontos = self.grid.get_pontos_hexagonais(lin, col)
                pygame.draw.polygon(self.tela, CONFIG["CORES"]["PRETO"], pontos)
            if isinstance(obs, EntidadeDecorator) or self.grid.geometria == "RETANGULAR":
                obs.desenhar(self.tela, self.grid.get_rect_celula(obs.pos))

        # Pontos e Caminhos
        for p in self.grid.pontos_inicio: p.desenhar(self.tela, self.grid.get_rect_celula(p.pos))
        for p in self.grid.pontos_fim: p.desenhar(self.tela, self.grid.get_rect_celula(p.pos))
        for caminho, cor in self.grid.caminhos:
            pontos_pixel = [self.grid.get_centro_celula(p) for p in caminho]
            if len(pontos_pixel) > 1: pygame.draw.lines(self.tela, cor, False, pontos_pixel, 4)

        # Agentes
        for agente in self.agentes_ativos:
             agente.desenhar(self.tela, self.grid.get_rect_celula(agente.pos))

        # UI
        txt_geo = "Hexagonal" if self.grid.geometria == "HEXAGONAL" else "Retangular"
        fonte = pygame.font.Font(None, 24)
        texto = f"Modo: {self.modo} ({txt_geo}) | Agentes: {len(self.agentes_ativos)} | Z: Undo "
        surf = fonte.render(texto, True, CONFIG["CORES"]["PRETO"])
        self.tela.blit(surf, (20, 10))
        pygame.display.flip()

    def run(self):
        while self.rodando:
            self.processar_eventos()
            self.controlar_agentes_ia()
            self.desenhar()
            self.clock.tick(30)
        pygame.quit()