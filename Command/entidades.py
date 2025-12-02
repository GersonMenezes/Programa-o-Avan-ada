# entidades.py
import pygame
from abc import ABC, abstractmethod
from config import CONFIG

class EntidadeGrid(ABC):
    def __init__(self, pos_grid):
        self.pos = pos_grid
    
    @abstractmethod
    def desenhar(self, tela, rect): pass

    # Por padrão, entidades não dão dano
    def get_dano(self):
        return 0

class ObstaculoParede(EntidadeGrid):
    def desenhar(self, tela, rect):
        pygame.draw.rect(tela, CONFIG["CORES"]["PRETO"], rect)

class PontoInicio(EntidadeGrid):
    def desenhar(self, tela, rect):
        pygame.draw.circle(tela, CONFIG["CORES"]["AZUL"], (rect.centerx, rect.centery), 6)

class PontoFim(EntidadeGrid):
    def desenhar(self, tela, rect):
        pygame.draw.circle(tela, CONFIG["CORES"]["VERMELHO"], (rect.centerx, rect.centery), 6)

# --- Decorators ---
class EntidadeDecorator(EntidadeGrid):
    def __init__(self, wrappee: EntidadeGrid):
        self._wrappee = wrappee
        super().__init__(wrappee.pos)
    
    @abstractmethod
    def desenhar(self, tela, rect):
        self._wrappee.desenhar(tela, rect)
    
    # Repassa a pergunta para o objeto embrulhado (ou sobrescreve)
    def get_dano(self):
        return self._wrappee.get_dano()

class ComportamentoFogoDecorator(EntidadeDecorator):
    def desenhar(self, tela, rect):
        self._wrappee.desenhar(tela, rect)
        pygame.draw.circle(tela, CONFIG["CORES"]["VERMELHO"], (rect.centerx, rect.centery), int(rect.width/2.5), 3)

    # Sobrescreve para dar dano
    def get_dano(self):
        return CONFIG["DANO_FOGO"]
