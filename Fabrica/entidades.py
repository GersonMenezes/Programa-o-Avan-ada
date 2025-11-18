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