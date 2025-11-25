# entidades.py
import pygame
from abc import ABC, abstractmethod
from config import CONFIG # Importa a configuração

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

class EntidadeDecorator(EntidadeGrid):
    """Decorator Base (Mantém a mesma interface do Componente)"""
    def __init__(self, wrappee: EntidadeGrid):
        self._wrappee = wrappee
        # Passa a posição para a base (EntidadeGrid)
        super().__init__(wrappee.pos) 
        
    @abstractmethod
    def desenhar(self, tela, rect):
        """Delega a operação ao objeto envolvido."""
        self._wrappee.desenhar(tela, rect) 

    #Comportamento (Para o Decorator)
    @abstractmethod
    def interagir(self):
        pass

class ComportamentoFogoDecorator(EntidadeDecorator):
    """Decorator Concreto: Adiciona o comportamento 'fogo'."""
    
    def interagir(self):
        # Chama a interação do objeto base antes/depois (opcional)
        # self._wrappee.interagir() 
        print(f"DEBUG: {self.pos} está em Chamas!")
        return "DANO" # Exemplo de comportamento extra
        
    def desenhar(self, tela, rect):
        """Adiciona o efeito de fogo ao desenho da Parede."""
        self._wrappee.desenhar(tela, rect) # Desenha a parede normal
        # Adiciona um círculo vermelho por cima para simular fogo
        pygame.draw.circle(tela, CONFIG["CORES"]["VERMELHO"], rect.center, 5)