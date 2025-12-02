# chains.py
import pygame
from abc import ABC, abstractmethod
from config import CONFIG
from grid_system import GridSystem

class Handler(ABC):
    """Interface do Handler para o Chain of Responsibility."""
    def __init__(self):
        self._next_handler = None

    def set_next(self, handler):
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, context):
        if self._next_handler:
            return self._next_handler.handle(context)
        return True

# Inicializa o Pygame
class PygameInitHandler(Handler):
    def handle(self, context):
        print("Chain: Inicializando Pygame...")
        pygame.init()
        return super().handle(context)
# Inicializa a Tela
class DisplayInitHandler(Handler):
    def handle(self, context):
        print("Chain: Configurando Tela...")
        context.tela = pygame.display.set_mode((CONFIG["LARGURA_TELA"], CONFIG["ALTURA_TELA"]))
        pygame.display.set_caption("Grid Patterns: ...")
        context.clock = pygame.time.Clock()
        # Envia o primeiro evento repetido (pressionar e manter pressionado) após 250ms, depois a cada 100ms.
        pygame.key.set_repeat(250, 100) 
        
        return super().handle(context)
# Inicializa o Singleton do Grid
class GridInitHandler(Handler):
    def handle(self, context):
        print("Chain: Inicializando Singleton do Grid...")
        context.grid = GridSystem.getInstance(context.tela.get_size(), geometria="RETANGULAR")
        return super().handle(context)