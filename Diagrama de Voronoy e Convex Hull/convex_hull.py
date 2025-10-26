import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time
import csv
import pygame

# --- Variáveis Globais ---
pontos_voronoi = []
poligonos_voronoi = []
tela = None  # Vamos inicializar depois

# --- Cores ---
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)

def inicializar_jogo():
    global tela
    pygame.init()
    tela = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Trabalho 1: Gear Up! | Modo: EDICAO")

def processar_eventos(log_writer, modo_atual, largura_tela, altura_tela):
    global pontos_voronoi
    
    for evento in pygame.event.get():
        # Janela fechada
        if evento.type == pygame.QUIT: 
            return False, modo_atual

        # Evento de clique do mouse
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if modo_atual == 'EDICAO':
                pontos_voronoi.append(evento.pos)
                log_writer.writerow([time.time(), 'criacao',
                                    evento.pos[0], evento.pos[1], f'poligono_{len(pontos_voronoi)}'])
                print(f"Ponto {len(pontos_voronoi)} adicionado: {evento.pos}")
                
            elif modo_atual == 'SELECIONAR':
                #pontos_voronoi = gerar_pontos()
                pass

        # --- TECLAS ---
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_e:  
                modo_atual = 'EDICAO'
                pygame.display.set_caption(
                    f"Trabalho 1: Gear Up! | Modo: {modo_atual} (Clique para adicionar, arraste ponto para mover)"
                )
            elif evento.key == pygame.K_s:  
                modo_atual = 'SELECIONAR'
                pygame.display.set_caption(
                    f"Trabalho 1: Gear Up! | Modo: {modo_atual} (Clique em um polígono)"
                )
            elif evento.key == pygame.K_F12:
                pygame.image.save(pygame.display.get_surface(), "images/screenshot.png")
                print("Screenshot salva como 'images/screenshot.png'")
            elif evento.key == pygame.K_ESCAPE:  # Adicionei ESC para sair
                return False, modo_atual

    return True, modo_atual

def desenhar_tudo(tela, modo_atual):  # Agora recebe ambos os parâmetros
    tela.fill(BRANCO)
    for ponto in pontos_voronoi:
        pygame.draw.circle(tela, PRETO, ponto, 5)
    pygame.display.flip()

def main():
    inicializar_jogo()
    relogio = pygame.time.Clock()
    modo_atual = 'EDICAO'
    
    rodando = True
    largura_tela, altura_tela = tela.get_size()
    tempo_inicio = time.time()
    
    with open('log_execucao.csv', 'w', newline='', encoding='utf-8') as arquivo_log:
        log_writer = csv.writer(arquivo_log)
        log_writer.writerow(['timestamp', 'tipo_evento', 'pos_x', 'pos_y', 'info_extra'])
        
        while rodando:
            rodando, modo_atual = processar_eventos(log_writer, modo_atual, largura_tela, altura_tela)
            desenhar_tudo(tela, modo_atual)  # CORRIGIDO: passe os parâmetros
            relogio.tick(60)
    
    print("Tempo total: ", time.time() - tempo_inicio)
    pygame.quit()

# Adicione esta linha para executar o jogo
if __name__ == "__main__":
    main()