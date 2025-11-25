import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time
import csv
import pygame
import random
import math

# --- Variáveis Globais ---
pontos = []
robo_forma = [] # Forma normalizada do robô
robo_desenho = [] # Robo Original
obstaculos = []
nuvens_de_pontos = [] # Lista para armazenar as "poeiras" de pontos de cada obstáculo
envoltorias_soma = [] # Lista para armazenar as envoltórias convexas das somas de cada obstáculo
tela = None
estado_app = "ROBO"

# --- Cores ---
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERMELHO = (255, 0, 0)
AZUL = (0, 0, 255)
VERDE = (0, 255, 0)
LARANJA = (255, 165, 0)
CINZA_FUNDO = (220, 220, 220)
CINZA = (128, 128, 128)

def inicializar_jogo():
    global tela
    pygame.init()
    tela = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Trabalho 4: Soma de Minkowski | Definindo Robô")

def get_area_desenho():
    largura, altura = tela.get_size()
    margem_superior = 50
    margem = 20
    return pygame.Rect(margem, margem_superior, largura - 2 * margem, altura - margem_superior - margem)

def distancia_pontos(p1, p2):
    """Calcula a distância euclidiana entre dois pontos."""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def distancia_minima_poligonos(poli1, poli2):
    """
    Calcula a distância mínima entre os VÉRTICES de dois polígonos.
    (Implementação O(n*m) por força bruta)
    """
    if not poli1 or not poli2:
        return float('inf') # Retorna infinito se um polígono estiver vazio
        
    min_dist = float('inf')
    
    # Compara cada vértice de poli1 com cada vértice de poli2
    for p1 in poli1:
        for p2 in poli2:
            dist = distancia_pontos(p1, p2) # Re-usa a função existente
            if dist < min_dist:
                min_dist = dist
                
    return min_dist

# --- FIM DAS FUNÇÕES DE CÁLCULO ---

''' Algoritmo Monotone Chain para encontrar o Hull convexo de um conjunto de pontos '''
def convex_hull(points):
    if len(points) < 3:
        return points

    points = sorted(points, key=lambda p: (p[0], p[1]))

    lower = []
    for p in points:
        while len(lower) >= 2:
            a, b = lower[-2], lower[-1]
            if cross(a, b, p) <= 0:
                lower.pop()
            else:
                break
        lower.append(p)

    upper = []
    for p in reversed(points):
        while len(upper) >= 2:
            a, b = upper[-2], upper[-1]
            if cross(a, b, p) <= 0:
                upper.pop()
            else:
                break
        upper.append(p)

    return lower[:-1] + upper[:-1]

def cross(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

# --- Calculo da Soma de Minkowski ---
def calcular_soma_minkowski(log_writer):
    """Calcula a soma de Minkowski para CADA obstáculo individualmente e LOGA as distâncias."""
    global nuvens_de_pontos, envoltorias_soma, estado_app

    if not robo_forma or not obstaculos:
        print("É preciso ter um robô e pelo menos um obstáculo para calcular a soma.")
        return

    nuvens_de_pontos.clear()
    envoltorias_soma.clear()
    print("Calculando Soma de Minkowski para cada obstáculo...")
    
    timestamp = time.time() # Timestamp para o grupo de eventos

    # --- Parte 2: Soma das coordenadas do robô com as coordenadas de cada obstáculo ---
    for i, obs in enumerate(obstaculos):
        pontos_soma_local = []
        for p_robo in robo_forma:
            for p_obs in obs:
                p_novo = (p_robo[0] + p_obs[0], p_robo[1] + p_obs[1])
                pontos_soma_local.append(p_novo)
        
        if pontos_soma_local:
            nuvens_de_pontos.append(pontos_soma_local)
        
        if len(pontos_soma_local) > 0:
            hull_soma_local = convex_hull(pontos_soma_local)
            envoltorias_soma.append(hull_soma_local)
            print(f"  - Obstáculo {i+1}: {len(pontos_soma_local)} pontos, {len(hull_soma_local)} vértices na envoltória.")
        else:
            print(f"  - Obstáculo {i+1}: Sem pontos de soma gerados.")

    print(f"Cálculo finalizado. {len(envoltorias_soma)} envoltórias geradas.")
    
    # --- Parte 2: Cálculo e Log das Distâncias ---
    print("Calculando e registrando distâncias mínimas (vértice-a-vértice)...")
    
    if not robo_desenho or not obstaculos or not envoltorias_soma:
        print("Não foi possível calcular distâncias (faltam polígonos).")
        return

    try:
        # 2. Logar distâncias (RB -> O_i) e (RB -> S_i)
        for i in range(len(obstaculos)):
            if i >= len(envoltorias_soma): continue # Caso um hull não tenha sido gerado
            
            obs = obstaculos[i]
            soma = envoltorias_soma[i]
            
            dist_rb_obs = distancia_minima_poligonos(robo_desenho, obs)
            dist_rb_soma = distancia_minima_poligonos(robo_desenho, soma)
            
            # tipo_evento 'distancia' para ser lido pelo analise.py
            log_writer.writerow([timestamp, 'distancia', f'RB-O{i+1}', f'{dist_rb_obs:.2f}', 'min_dist_vertice_a_vertice'])
            log_writer.writerow([timestamp, 'distancia', f'RB-S{i+1}', f'{dist_rb_soma:.2f}', 'min_dist_vertice_a_vertice'])

        # 3. Logar distâncias (S_i -> S_j)
        for i in range(len(envoltorias_soma)):
            for j in range(i + 1, len(envoltorias_soma)):
                soma_i = envoltorias_soma[i]
                soma_j = envoltorias_soma[j]
                
                # --- LÓGICA DE CÁLCULO ATUALIZADA ---
                dist_s_s = distancia_minima_poligonos(soma_i, soma_j)
                log_writer.writerow([timestamp, 'distancia', f'S{i+1}-S{j+1}', f'{dist_s_s:.2f}', 'min_dist_vertice_a_vertice'])
        
        print("Distâncias mínimas registradas no log 'log_execucao_minkowski.csv'.")

    except Exception as e:
        print(f"Erro ao calcular/registrar distâncias: {e}")
    
    # --- Fim da Parte 2 ---
    
    estado_app = "SOMA"
    pygame.display.set_caption("Trabalho 4: Soma de Minkowski | Exibindo Resultados")

def limpar_tudo():
    """Limpa todos os dados e reseta o estado"""
    global estado_app
    pontos.clear()
    robo_forma.clear()
    robo_desenho.clear()
    obstaculos.clear()
    nuvens_de_pontos.clear()
    envoltorias_soma.clear()
    estado_app = "ROBO"
    pygame.display.set_caption("Trabalho 4: Soma de Minkowski | Definindo Robô")
    print("Tudo limpo. Defina o robô.")

def processar_eventos(log_writer, largura_tela, altura_tela): # log_writer já estava aqui
    global pontos, robo_forma, robo_desenho, obstaculos, estado_app

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            return False

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                return False

            elif evento.key == pygame.K_c:
                limpar_tudo()
                
            elif evento.key == pygame.K_s:
                if estado_app in ["OBSTACULOS", "SOMA"]:
                    calcular_soma_minkowski(log_writer) # <<< Passa o log_writer

            elif evento.key == pygame.K_RETURN:
                if len(pontos) < 3:
                    print("Precisa de pelo menos 3 pontos para formar um polígono.")
                    continue

                if estado_app == "ROBO":
                    robo_desenho = pontos.copy() 
                    
                    robo_forma.clear()
                    ref_point = robo_desenho[0]
                    for p in robo_desenho:
                        norm_x = p[0] - ref_point[0]
                        norm_y = p[1] - ref_point[1]
                        robo_forma.append((norm_x, norm_y))

                    pontos.clear()
                    estado_app = "OBSTACULOS"
                    pygame.display.set_caption("Trabalho 4: Soma de Minkowski | Definindo Obstáculos")
                    print(f"Robô (desenho) definido com {len(robo_desenho)} vértices.")
                    print(f"Robô (forma normalizada) definido: {robo_forma}")

                elif estado_app == "OBSTACULOS":
                    novo_obstaculo = pontos.copy()
                    obstaculos.append(novo_obstaculo)
                    pontos.clear()
                    print(f"Obstáculo {len(obstaculos)} definido com {len(novo_obstaculo)} vértices.")

        if evento.type == pygame.MOUSEBUTTONDOWN:
            if estado_app == "SOMA":
                print("Soma já calculada. Pressione 'C' para limpar e recomeçar.")
                continue

            pos = evento.pos
            area_desenho = get_area_desenho()

            if area_desenho.collidepoint(pos):
                pontos.append(pos)
                # Modificado o nome do evento para 'criacao_ponto' para diferenciar de 'distancia'
                log_writer.writerow([time.time(), 'criacao_ponto',
                                     pos[0], pos[1], f'{estado_app}_{len(pontos)}'])
                print(f"Ponto {len(pontos)} adicionado: {pos}")
            else:
                print("Clique fora da área de desenho!")

    return True

def desenhar_tudo(tela):
    tela.fill(BRANCO)
    fonte_instrucoes = pygame.font.Font(None, 30)
    
    area_desenho = get_area_desenho()
    pygame.draw.rect(tela, CINZA_FUNDO, area_desenho)

    # 1. Desenha o Robô
    if len(robo_desenho) >= 3:
        pygame.draw.polygon(tela, CINZA, robo_desenho)
        pygame.draw.lines(tela, PRETO, True, robo_desenho, 2)

    # 2. Desenha os Obstáculos
    for obs in obstaculos:
        if len(obs) >= 3:
            pygame.draw.polygon(tela, PRETO, obs)

    # --- Desenha o polígono atual (em construção) ---
    if len(pontos) > 0:
        for ponto in pontos:
            pygame.draw.circle(tela, PRETO, ponto, 5)
        if len(pontos) >= 2:
            cor_linha = CINZA if estado_app == "ROBO" else PRETO
            pygame.draw.lines(tela, cor_linha, False, pontos, 2)

    # --- Desenha o resultado da Soma de Minkowski (Múltiplos) ---
    if estado_app == "SOMA":
        # 1. Poeiras
        for nuvem in nuvens_de_pontos:
            for ponto in nuvem:
                if area_desenho.collidepoint(ponto):
                    pygame.draw.circle(tela, LARANJA, ponto, 2)
            
        # 2. Envoltórias
        for hull in envoltorias_soma:
            if len(hull) >= 2:
                pygame.draw.lines(tela, VERMELHO, True, hull, 3)

    # --- Desenha instruções dinâmicas ---
    if estado_app == "ROBO":
        instrucao_txt = '"Enter": Adicionar robô | "C": Limpar | "ESC": Sair'
    else: 
        instrucao_txt = '"Enter": Adicionar obstáculo | "S": Ver Envoltória | "C": Limpar | "ESC": Sair'
        
    instrucao = fonte_instrucoes.render(instrucao_txt, True, PRETO)
    
    fundo_rect = pygame.Rect(10, 5, instrucao.get_width() + 20, instrucao.get_height() + 10)
    fundo_surf = pygame.Surface(fundo_rect.size, pygame.SRCALPHA)
    fundo_surf.fill((255, 255, 255, 220))
    tela.blit(fundo_surf, fundo_rect.topleft)
    tela.blit(instrucao, (20, 10))
    
    pygame.display.flip()

def main():
    inicializar_jogo()
    relogio = pygame.time.Clock()
    
    rodando = True
    largura_tela, altura_tela = tela.get_size()
    tempo_inicio = time.time()

    nome_arquivo_log = 'log_execucao_minkowski.csv'
    
    with open(nome_arquivo_log, 'w', newline='', encoding='utf-8') as arquivo_log:
        log_writer = csv.writer(arquivo_log)
        log_writer.writerow(['timestamp', 'tipo_evento', 'dado_1', 'dado_2', 'info_extra'])
        
        while rodando:
            rodando = processar_eventos(log_writer, largura_tela, altura_tela)
            desenhar_tudo(tela)
            relogio.tick(60)

    print("\n--- Simulação Finalizada ---")
    print(f"Log de dados salvo em: {nome_arquivo_log}")
    print(f"Robô (desenho): {len(robo_desenho)} vértices")
    print(f"Robô (forma): {len(robo_forma)} vértices")
    print(f"Obstáculos: {len(obstaculos)}")
    print(f"Nuvens de Pontos Geradas: {len(nuvens_de_pontos)}")
    print(f"Envoltórias Geradas: {len(envoltorias_soma)}")
    print("\nTempo total: ", time.time() - tempo_inicio)
    pygame.quit()

if __name__ == "__main__":
    main()