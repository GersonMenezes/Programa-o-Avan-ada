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
hull = []
formas_geometricas = []  # Lista para armazenar as formas geométricas
tela = None 
modo_entrada_numero = False  # Modo para entrada de número
numero_lados = 0  # Número de lados para a forma geométrica
texto_entrada = ""  # Texto digitado pelo usuário

# --- Cores ---
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERMELHO = (255, 0, 0)
AZUL = (0, 0, 255)
VERDE = (0, 255, 0)
LARANJA = (255, 165, 0)
CINZA = (200, 200, 200)

def inicializar_jogo():
    global tela
    pygame.init()
    tela = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Trabalho 1: Gear Up! | Modo: EDICAO")
    
def get_area_desenho():
    """Retorna a área segura para desenho (excluindo a área das instruções)"""
    largura, altura = tela.get_size()
    margem_superior = 50  # Espaço reservado para as instruções
    margem = 20  # Margem geral
    return pygame.Rect(margem, margem_superior, largura - 2 * margem, altura - margem_superior - margem)

''' Algoritmo Monotone Chain para encontrar o Hull convexo de um conjunto de pontos '''
def convex_hull(points): 
    if len(points) < 3:
        return points  # Precisa de pelo menos 3 pontos para formar um hull
    
    # Ordena pontos por x (e por y em caso de empate)
    points = sorted(points, key=lambda p: (p[0], p[1]))
    
    # Lower hull
    lower = []
    for p in points:
        while len(lower) >= 2:
            # Pega os últimos 2 pontos de lower + ponto atual
            a, b = lower[-2], lower[-1]
            # Verifica se faz curva horária
            if cross(a, b, p) <= 0:  # <= 0 significa horário ou colinear
                lower.pop()  # Remove o ponto do meio (b)
            else:
                break
        lower.append(p)
    
    # Upper hull (mesma lógica, ordem reversa)
    upper = []
    for p in reversed(points):
        while len(upper) >= 2:
            a, b = upper[-2], upper[-1]
            if cross(a, b, p) <= 0:
                upper.pop()
            else:
                break
        upper.append(p)
    
    # Junta lower e upper, removendo duplicatas das pontas
    return lower[:-1] + upper[:-1]

def cross(a, b, c):
    """Produto vetorial (determinante) dos vetores AB e AC"""
    return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])

def gerar_pontos_aleatorios():
    """Gera de 5 a 50 pontos aleatórios dentro da área de desenho"""
    global pontos, hull
    pontos.clear()
    num_pontos = random.randint(5, 50)
    area_desenho = get_area_desenho()
    
    for _ in range(num_pontos):
        x = random.randint(area_desenho.left, area_desenho.right)
        y = random.randint(area_desenho.top, area_desenho.bottom)
        pontos.append((x, y))
    
    # Recalcula o hull
    if len(pontos) >= 3:
        hull = convex_hull(pontos)
    else:
        hull = pontos.copy()
    
    print(f"Gerados {num_pontos} pontos aleatórios")

def criar_forma_geometrica(num_lados):
    """Cria uma forma geométrica com o número especificado de lados dentro da área de desenho"""
    global formas_geometricas
    area_desenho = get_area_desenho()
    forma = []
    
    if num_lados == 1:
        # Círculo - ponto central + raio
        centro_x = random.randint(area_desenho.left + 30, area_desenho.right - 30)
        centro_y = random.randint(area_desenho.top + 30, area_desenho.bottom - 30)
        raio_max = min(area_desenho.width, area_desenho.height) // 6
        raio = random.randint(20, raio_max)
        forma = [('circulo', (centro_x, centro_y), raio)]
        
    elif num_lados == 2:
        # Linha - dois pontos
        ponto1 = (
            random.randint(area_desenho.left, area_desenho.right),
            random.randint(area_desenho.top, area_desenho.bottom)
        )
        ponto2 = (
            random.randint(area_desenho.left, area_desenho.right),
            random.randint(area_desenho.top, area_desenho.bottom)
        )
        forma = [('linha', ponto1, ponto2)]
        
    else:
        # Polígono com n lados
        pontos_poligono = []
        for _ in range(num_lados):
            x = random.randint(area_desenho.left + 10, area_desenho.right - 10)
            y = random.randint(area_desenho.top + 10, area_desenho.bottom - 10)
            pontos_poligono.append((x, y))
        forma = [('poligono', pontos_poligono)]
    
    formas_geometricas.append(forma)
    print(f"Forma geométrica criada com {num_lados} lados")

def processar_eventos(log_writer, modo_atual, largura_tela, altura_tela):
    global pontos, hull, modo_entrada_numero, numero_lados, texto_entrada
    
    for evento in pygame.event.get():
        # Janela fechada
        if evento.type == pygame.QUIT: 
            return False, modo_atual

        if modo_entrada_numero:
            # Modo de entrada de número para formas geométricas
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    # Processa o número digitado
                    if texto_entrada.isdigit():
                        numero_lados = int(texto_entrada)
                        if numero_lados > 0:
                            criar_forma_geometrica(numero_lados)
                        modo_entrada_numero = False
                        texto_entrada = ""
                    else:
                        print("Por favor, digite um número válido")
                        
                elif evento.key == pygame.K_BACKSPACE:
                    texto_entrada = texto_entrada[:-1]
                elif evento.key == pygame.K_ESCAPE:
                    modo_entrada_numero = False
                    texto_entrada = ""
                else:
                    # Adiciona apenas dígitos
                    if evento.unicode.isdigit():
                        texto_entrada += evento.unicode
        else:
            # Modo normal
            # Evento de clique do mouse
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if modo_atual == 'EDICAO':
                    pos = evento.pos
                    area_desenho = get_area_desenho()
                    
                    # Verifica se o clique está dentro da área de desenho
                    if area_desenho.collidepoint(pos):
                        pontos.append(pos)
                        log_writer.writerow([time.time(), 'criacao',
                                            pos[0], pos[1], f'poligono_{len(pontos)}'])
                        print(f"Ponto {len(pontos)} adicionado: {pos}")
                        # Recalcula o hull sempre que adicionar um novo ponto
                        if len(pontos) >= 3:
                            hull = convex_hull(pontos)
                        else:
                            hull = pontos.copy()
                    else:
                        print("Clique fora da área de desenho!")

            # --- TECLAS ---
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_e:  # Tecla E - modo edição
                    modo_atual = 'EDICAO'
                    pygame.display.set_caption(
                        f"Trabalho 3: Convex Hull! | Modo: {modo_atual} (Clique para adicionar pontos)"
                    )
                    print("Modo EDIÇÃO - Pode adicionar pontos")
                    
                elif evento.key == pygame.K_a:  # Tecla A - pontos aleatórios
                    gerar_pontos_aleatorios()
                    
                elif evento.key == pygame.K_g:  # Tecla G - formas geométricas
                    modo_entrada_numero = True
                    texto_entrada = ""
                    print("Digite o número de lados e pressione ENTER:")
                    
                elif evento.key == pygame.K_F12:
                    pygame.image.save(pygame.display.get_surface(), "images/screenshot.png")
                    print("Screenshot salva como 'images/screenshot.png'")
                    
                elif evento.key == pygame.K_ESCAPE:
                    return False, modo_atual
                    
                elif evento.key == pygame.K_c:  # Tecla C - limpar tudo
                    pontos.clear()
                    hull.clear()
                    formas_geometricas.clear()
                    print("Todos os pontos e formas foram removidos")

    return True, modo_atual

def desenhar_formas_geometricas(tela):
    """Desenha todas as formas geométricas na tela"""
    for forma in formas_geometricas:
        for elemento in forma:
            tipo = elemento[0]
            
            if tipo == 'circulo':
                centro, raio = elemento[1], elemento[2]
                pygame.draw.circle(tela, VERDE, centro, raio, 2)
                pygame.draw.circle(tela, VERDE, centro, 5)  # Ponto central
                
            elif tipo == 'linha':
                ponto1, ponto2 = elemento[1], elemento[2]
                pygame.draw.line(tela, LARANJA, ponto1, ponto2, 3)
                pygame.draw.circle(tela, LARANJA, ponto1, 5)
                pygame.draw.circle(tela, LARANJA, ponto2, 5)
                
            elif tipo == 'poligono':
                pontos_poligono = elemento[1]
                if len(pontos_poligono) >= 2:
                    # Desenha as linhas do polígono
                    for i in range(len(pontos_poligono)):
                        ponto_atual = pontos_poligono[i]
                        proximo_ponto = pontos_poligono[(i + 1) % len(pontos_poligono)]
                        pygame.draw.line(tela, LARANJA, ponto_atual, proximo_ponto, 2)
                    
                    # Desenha os pontos do polígono
                    for ponto in pontos_poligono:
                        pygame.draw.circle(tela, LARANJA, ponto, 5)

def desenhar_tudo(tela, modo_atual):
    tela.fill(BRANCO)
    fonte_instrucoes = pygame.font.Font(None, 30)
    fonte_entrada = pygame.font.Font(None, 36)
    
    # Desenha a área de desenho
    area_desenho = get_area_desenho()
    pygame.draw.rect(tela, CINZA, area_desenho, 1)  # Borda cinza para mostrar a área
    
    # Desenha formas geométricas primeiro (fundo)
    desenhar_formas_geometricas(tela)
    
    # Desenha os pontos do usuário
    for ponto in pontos:
        pygame.draw.circle(tela, PRETO, ponto, 5)
    
    # Desenha o hull
    if len(hull) >= 2:
        # Desenha as linhas do hull
        for i in range(len(hull)):
            ponto_atual = hull[i]
            proximo_ponto = hull[(i + 1) % len(hull)]
            pygame.draw.line(tela, VERMELHO, ponto_atual, proximo_ponto, 2)
        
        # Destaca os pontos do hull em azul
        for ponto in hull:
            pygame.draw.circle(tela, AZUL, ponto, 7)

    # Desenha instruções na tela (sempre no topo)
    instrucao_txt = '"E": Editar | "A": Aleatório | "G": Formas | "C": Limpar | "ESC": Sair'
    instrucao = fonte_instrucoes.render(instrucao_txt, True, PRETO)
    
    # Fundo semi-transparente para as instruções
    fundo_rect = pygame.Rect(10, 5, instrucao.get_width() + 20, instrucao.get_height() + 10)
    fundo_surf = pygame.Surface(fundo_rect.size, pygame.SRCALPHA)
    fundo_surf.fill((255, 255, 255, 220))  # Menos transparente
    tela.blit(fundo_surf, fundo_rect.topleft)
    tela.blit(instrucao, (20, 10))
    
    # Desenha entrada de número se estiver no modo de entrada
    if modo_entrada_numero:
        prompt_texto = "Type 1 to Circle, 2 to Line 3+ to Polygon and Enter to Confirm: " + texto_entrada
        prompt = fonte_entrada.render(prompt_texto, True, PRETO)
        
        # Fundo para o prompt (mais à esquerda)
        prompt_rect = pygame.Rect(
            20,  # Começa mais à esquerda
            tela.get_height() // 2 - 25,
            min(700, prompt.get_width() + 20),  # Limita a largura máxima
            50
        )
        prompt_surf = pygame.Surface(prompt_rect.size, pygame.SRCALPHA)
        prompt_surf.fill((200, 200, 255, 240))
        tela.blit(prompt_surf, prompt_rect.topleft)
        tela.blit(prompt, (20, tela.get_height() // 2 - 15))  # Ajusta posição do texto
    
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
            desenhar_tudo(tela, modo_atual)
            relogio.tick(60)

    print("\nPontos:", pontos)
    print("\nPontos Externos:", hull)
    print("\nTempo total: ", time.time() - tempo_inicio)
    pygame.quit()

# Adicione esta linha para executar o jogo
if __name__ == "__main__":
    main()