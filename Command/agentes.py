# agentes.py
import pygame
from abc import ABC, abstractmethod
from config import CONFIG

class Observer(ABC):
    @abstractmethod
    def update(self, evento, dados): pass

class Agente:
    def __init__(self, pos_inicial):
        self.pos = pos_inicial
        self.observers = []
        self.vida = CONFIG["VIDA_INICIAL"]

    def attach(self, observer):
        self.observers.append(observer)

    def notify(self, evento, dados=None):
        for observer in self.observers:
            observer.update(evento, dados)

    def desenhar(self, tela, rect):
        centro = (rect.centerx, rect.centery)
        pygame.draw.circle(tela, CONFIG["CORES"]["VERDE"], centro, int(rect.width * 0.4))

    def mover_para(self, nova_pos):
        self.pos = nova_pos
        self.notify("moveu", nova_pos)

    def receber_dano(self, quantidade):
        self.vida -= quantidade
        print(f"Agente sofreu dano! Vida restante: {self.vida}")
        if self.vida <= 0:
            self.vida = 0
            self.notify("morreu")