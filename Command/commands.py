# commands.py
from abc import ABC, abstractmethod
import time

# Interface Command
class Command(ABC):
    def __init__(self):
        self.timestamp = time.time() # Requisito: guardar o tempo

    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def undo(self):
        pass

# Concrete Command
class MoverAgenteCommand(Command):
    def __init__(self, agente, direcao_x, direcao_y):
        super().__init__()
        self.agente = agente
        self.dx = direcao_x
        self.dy = direcao_y
        self.pos_anterior = None # Estado para o Undo

    def execute(self):
        self.pos_anterior = self.agente.pos
        # Calcula nova posição
        nova_pos = (self.agente.pos[0] + self.dx, self.agente.pos[1] + self.dy)
        self.agente.mover_para(nova_pos)

    def undo(self):
        if self.pos_anterior:
            self.agente.mover_para(self.pos_anterior)

# Invoker (Gerenciador)
class CommandManager:
    def __init__(self):
        self.historico = []
    
    def executar(self, comando: Command):
        comando.execute()
        self.historico.append(comando)
        print(f"Comando executado às {comando.timestamp}")

    def desfazer(self):
        if self.historico:
            comando = self.historico.pop()
            comando.undo()
            print("Comando desfeito (Undo).")