# agentes.py
import pygame
import random
from abc import ABC, abstractmethod
from config import CONFIG


class Observer(ABC):
    @abstractmethod
    def update(self, evento, dados): pass

class Agente:
    def __init__(self, pos_inicial, cor):
        self.pos = pos_inicial
        self.cor = cor
        self.observers = []
        self.vida = CONFIG["VIDA_INICIAL"]

    def attach(self, observer):
        self.observers.append(observer)

    def notify(self, evento, dados=None):
        for observer in self.observers:
            observer.update(evento, dados)

    def desenhar(self, tela, rect):
        centro = (rect.centerx, rect.centery)
        pygame.draw.circle(tela, self.cor, centro, int(rect.width * 0.4))

    def mover_para(self, nova_pos):
        self.pos = nova_pos
        self.notify("moveu", nova_pos)

    def receber_dano(self, quantidade):
        self.vida -= quantidade
        self.notify("morreu" if self.vida <= 0 else "dano")

# ==========================================
# AGENTE IA (COM ESTRATÉGIA DE EVASÃO E TEMPO)
# ==========================================

class AgenteIA(Agente):
    def __init__(self, pos_inicial, pos_final, caminho, cor):
        super().__init__(pos_inicial, cor)
        self.pos_final = pos_final
        self.caminho_planejado = caminho
        
        # Estado de Intenção
        self.intenção_atual = pos_inicial 
        
        # Controle de Tempo Individual
        self.tempo_proximo_movimento = 0
        self.delay_atual = 0
        self.sortear_tempo_movimento() # Define se começa rápido ou devagar

    def sortear_tempo_movimento(self):
        """Sorteia se o próximo passo demora 250ms ou 500ms."""
        self.delay_atual = random.choice([250, 500])
    
    def verificar_tempo(self, tempo_jogo):
        """Retorna True se chegou a hora de se mover."""
        if tempo_jogo >= self.tempo_proximo_movimento:
            return True
        return False

    def agendar_proximo_movimento(self, tempo_jogo):
        self.sortear_tempo_movimento()
        self.tempo_proximo_movimento = tempo_jogo + self.delay_atual

    def planejar_movimento(self, grid_singleton, lista_agentes_ativos):
        """
        Retorna (dx, dy) para o movimento ou (0,0) se esperar/bloqueado.
        Realiza evasão de 2 células se houver conflito de intenção OU Físico.
        """
        # Se já chegou ou não tem caminho
        if not self.caminho_planejado or self.pos == self.pos_final:
            return None

        proximo_passo = self.caminho_planejado[0]
        
        # ============================================================
        # 1. VERIFICAÇÃO FÍSICA (Ocupação Atual)
        # ============================================================
        
        # Verifica se JÁ TEM um agente lá (Colisão Física)
        ocupado_fisicamente = False
        for outro_agente in lista_agentes_ativos:
            if outro_agente != self and outro_agente.pos == proximo_passo:
                ocupado_fisicamente = True
                break
        
        if ocupado_fisicamente:
            print(f"Agente {self.pos} detectou OBSTÁCULO FÍSICO em {proximo_passo}! Iniciando Evasão...")
            # MUDANÇA AQUI: Em vez de esperar, executa a evasão longa (mesma lógica da intenção)
            self.executar_evasao_longa(grid_singleton)
            self.intenção_atual = self.pos
            return (0, 0)

        # ============================================================
        # 2. VERIFICAÇÃO DE INTENÇÃO (Coordenação Futura)
        # ============================================================
        
        # Se alguém RESERVOU essa célula (e não sou eu mesmo)
        if (proximo_passo in grid_singleton.lista_intencao and 
            grid_singleton.lista_intencao[proximo_passo] != self):
            
            print(f"Agente {self.pos} detectou CONFLITO DE INTENÇÃO em {proximo_passo}! Iniciando Evasão...")
            self.executar_evasao_longa(grid_singleton)
            self.intenção_atual = self.pos
            return (0, 0)

        # ============================================================
        # 3. MOVIMENTO VÁLIDO
        # ============================================================
        
        dx = proximo_passo[0] - self.pos[0]
        dy = proximo_passo[1] - self.pos[1]
        
        self.caminho_planejado.pop(0) # Consome o passo
        self.intenção_atual = proximo_passo # Atualiza intenção
        return (dx, dy)

    def executar_evasao_longa(self, grid_singleton):
        """
        Tenta encontrar um ponto a 2 células de distância em direção aleatória
        e traça uma rota passando por lá.
        """
        # Direções possíveis (cardeais)
        direcoes = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        random.shuffle(direcoes)
        
        ponto_evasao = None
        
        # Tenta achar um ponto livre a 2 passos
        for dx, dy in direcoes:
            # Ponto a 2 passos de distância
            tentativa = (self.pos[0] + dx*2, self.pos[1] + dy*2)
            
            # Se 2 passos for fora do mapa ou bloqueado, tenta 1 passo
            if not grid_singleton.is_livre(tentativa, ignorar_agentes=True):
                tentativa = (self.pos[0] + dx, self.pos[1] + dy)
            
            # Verifica se é válido
            if grid_singleton.is_livre(tentativa, ignorar_agentes=True):
                ponto_evasao = tentativa
                break
        
        if ponto_evasao:
            # 1. Rota até o ponto de evasão
            rota_evasao = grid_singleton.pathfinder_ia.encontrar_caminho(
                self.pos, ponto_evasao, grid_singleton.obstaculos.keys(), grid_singleton.resolucao
            )
            
            # 2. Rota do ponto de evasão até o final
            rota_final = grid_singleton.pathfinder_ia.encontrar_caminho(
                ponto_evasao, self.pos_final, grid_singleton.obstaculos.keys(), grid_singleton.resolucao
            )
            
            # Concatena as rotas
            if rota_evasao and rota_final:
                # [A, B, C] + [C, D, E] -> [B, C, D, E]
                novo_caminho = rota_evasao[1:] + rota_final[1:]
                self.caminho_planejado = novo_caminho
            else:
                self.caminho_planejado = [] # Fica parado se não achar caminho
        else:
            self.caminho_planejado = [] # Fica preso/parado