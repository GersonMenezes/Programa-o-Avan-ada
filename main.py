import pygame
import time
import csv
import math
from datetime import datetime
from scipy.spatial import Voronoi
import numpy as np

# --- Cores ---
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERMELHO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)
CINZA = (128, 128, 128)
AMARELO = (255, 255, 0)
ROXO = (128, 0, 128)
LARANJA = (255, 165, 0)
CIANO = (0, 255, 255)
ROSA = (255, 192, 203)

# Cores para os polígonos do Voronoi
CORES_VORONOI = [VERMELHO, VERDE, AZUL, AMARELO, ROXO, LARANJA, CIANO, ROSA]

# Variáveis Globais
tela = pygame.display.set_mode((800, 600))
cliques_total = 0
pontos_voronoi = []  # Lista de pontos para o Diagrama de Voronoi
poligonos_voronoi = []  # Lista de polígonos gerados pelo Voronoi
ponto_arrastando = None  # Índice do ponto sendo arrastado
posicao_inicial_arrasto = None  # Posição inicial do arrasto

def inicializar_jogo():
    pygame.init()
    pygame.display.set_caption("Trabalho 1: Gear Up! | Modo: EDICAO") # Mostra o modo inicial

# ==============================================================================
# ### FUNÇÃO AUXILIAR
# ==============================================================================
def voronoi_finite_polygons_2d(vor, radius=None):
    """
    Reconstroi regiões Voronoi em 2D para polígonos finitos.
    Código adaptado da documentação oficial do scipy.
    """
    if vor.points.shape[1] != 2:
        raise ValueError("Apenas 2D é suportado.")

    new_regions = []
    new_vertices = vor.vertices.tolist()

    center = vor.points.mean(axis=0)
    if radius is None:
        radius = np.ptp(vor.points, axis=0).max() * 2

    # Mapeia cada ponto para suas regiões
    all_ridges = {}
    for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
        all_ridges.setdefault(p1, []).append((p2, v1, v2))
        all_ridges.setdefault(p2, []).append((p1, v1, v2))

    # Reconstrói cada região
    for p1, region_idx in enumerate(vor.point_region):
        vertices = vor.regions[region_idx]

        if all(v >= 0 for v in vertices):
            # Região já finita
            new_regions.append(vertices)
            continue

        # Caso infinito → fecha manualmente
        ridges = all_ridges[p1]
        new_region = [v for v in vertices if v >= 0]

        for p2, v1, v2 in ridges:
            if v2 < 0: v1, v2 = v2, v1
            if v1 >= 0 and v2 >= 0: continue

            t = vor.points[p2] - vor.points[p1]  # direção entre pontos
            t /= np.linalg.norm(t)
            n = np.array([-t[1], t[0]])  # normal
            midpoint = vor.points[[p1, p2]].mean(axis=0)
            direction = np.sign(np.dot(midpoint - center, n)) * n
            far_point = vor.vertices[v2] + direction * radius

            new_region.append(len(new_vertices))
            new_vertices.append(far_point.tolist())

        # Ordena os vértices no sentido anti-horário
        vs = np.asarray([new_vertices[v] for v in new_region])
        c = vs.mean(axis=0)
        ang = np.arctan2(vs[:, 1] - c[1], vs[:, 0] - c[0])
        new_region = [v for _, v in sorted(zip(ang, new_region))]
        new_regions.append(new_region)

    return new_regions, np.asarray(new_vertices)



# ==============================================================================
# ### FUNÇÃO DE GERAÇÃO
# ==============================================================================
def gerar_diagrama_voronoi(pontos, largura_tela, altura_tela):
    global poligonos_voronoi
    poligonos_voronoi = []

    if len(pontos) < 2:  # Voronoi precisa de no mínimo 2 pontos
        poligonos_voronoi = []
        return

    try:
        array_pontos = np.array(pontos)
        vor = Voronoi(array_pontos)

        regions, vertices = voronoi_finite_polygons_2d(vor)

        # Clipa os polígonos aos limites da tela
        box = np.array([[0, 0], [largura_tela, 0], 
                        [largura_tela, altura_tela], [0, altura_tela]])

        if len(pontos) < 4:
            poligonos_voronoi = []
            return
        for i, region in enumerate(regions):
            polygon = vertices[region]
            # Faz interseção com a tela
            from shapely.geometry import Polygon
            poly = Polygon(polygon)
            box_poly = Polygon(box)
            poly = poly.intersection(box_poly)

            if not poly.is_empty and poly.geom_type == "Polygon":
                cor = CORES_VORONOI[i % len(CORES_VORONOI)]
                poligonos_voronoi.append({
                    'id': i + 1,
                    'ponto_central': pontos[i],
                    'vertices': [(int(x), int(y)) for x, y in poly.exterior.coords],
                    'cor': cor
                })

    except Exception as e:
        print(f"Erro ao gerar Diagrama de Voronoi: {e}")
        poligonos_voronoi = []


def processar_eventos(log_writer, modo_atual, largura_tela, altura_tela):
    global cliques_total, pontos_voronoi, ponto_arrastando, posicao_inicial_arrasto
    
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            return False, modo_atual

        # Evento de clique do mouse
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if modo_atual == 'EDICAO':
                # Primeiro verifica se clicou próximo a um ponto existente
                ponto_proximo = encontrar_ponto_proximo(evento.pos)
                
                if ponto_proximo is not None:
                    ponto_arrastando = ponto_proximo
                    posicao_inicial_arrasto = evento.pos
                    print(f"Iniciando arrasto do ponto {ponto_proximo + 1}")
                else:
                    pontos_voronoi.append(evento.pos)
                    gerar_diagrama_voronoi(pontos_voronoi, largura_tela, altura_tela)
                    log_writer.writerow([obter_data_hora_brasileira(), 'criacao',
                                         evento.pos[0], evento.pos[1], f'poligono_{len(pontos_voronoi)}'])
                    cliques_total += 1
                    print(f"Ponto {len(pontos_voronoi)} adicionado: {evento.pos}")
                
            elif modo_atual == 'SELECIONAR':
                poligono_clicado = encontrar_poligono_clicado(evento.pos)
                if poligono_clicado:
                    log_writer.writerow([obter_data_hora_brasileira(), 'selecao',
                                         evento.pos[0], evento.pos[1],
                                         f'poligono_{poligono_clicado["id"]}'])
                    print(f"Polígono {poligono_clicado['id']} selecionado")
                else:
                    log_writer.writerow([obter_data_hora_brasileira(), 'selecao',
                                         evento.pos[0], evento.pos[1], 'nenhum_poligono'])
                    print("Nenhum polígono clicado")
                cliques_total += 1
        
        if evento.type == pygame.MOUSEMOTION:
            pos = evento.pos
            log_writer.writerow([obter_data_hora_brasileira(), 'movimento', pos[0], pos[1], ''])
            
            # Se está arrastando um ponto, atualiza sua posição
            if ponto_arrastando is not None and modo_atual == 'EDICAO':
                pontos_voronoi[ponto_arrastando] = pos
                gerar_diagrama_voronoi(pontos_voronoi, largura_tela, altura_tela)
        
        # Evento de soltar o mouse
        if evento.type == pygame.MOUSEBUTTONUP:
            if ponto_arrastando is not None:
                # Finaliza o arrasto
                log_writer.writerow([obter_data_hora_brasileira(), 'movimento_ponto', 
                                     pontos_voronoi[ponto_arrastando][0], pontos_voronoi[ponto_arrastando][1], 
                                     f'ponto_{ponto_arrastando + 1}_movido'])
                print(f"Ponto {ponto_arrastando + 1} movido para: {pontos_voronoi[ponto_arrastando]}")
                ponto_arrastando = None
                posicao_inicial_arrasto = None
            
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
                pygame.image.save(pygame.display.get_surface(), "screenshot.png")
                print("Screenshot salva como 'screenshot.png'")

    return True, modo_atual


def encontrar_poligono_clicado(ponto_clique):
    """Encontra qual polígono do Voronoi foi clicado."""
    for poligono in poligonos_voronoi:
        if ponto_em_poligono(ponto_clique, poligono):
            return poligono
    return None

def encontrar_ponto_proximo(posicao, tolerancia=15):
    """Encontra o ponto mais próximo de uma posição, dentro da tolerância."""
    for i, ponto in enumerate(pontos_voronoi):
        distancia = math.sqrt((posicao[0] - ponto[0])**2 + (posicao[1] - ponto[1])**2)
        if distancia <= tolerancia:
            return i
    return None

def desenhar_tudo(tela, modo_atual):
    tela.fill(BRANCO)
    
    # --- Cria os objetos de fonte ---
    fonte_ponto = pygame.font.Font(None, 20)
    fonte_poligono_id = pygame.font.Font(None, 24)
    fonte_instrucoes = pygame.font.Font(None, 30)
    
    # Desenha os polígonos do Diagrama de Voronoi
    for poligono in poligonos_voronoi:
        if len(poligono['vertices']) >= 3:
            # Desenha o polígono preenchido
            pygame.draw.polygon(tela, poligono['cor'], poligono['vertices'])
            # Desenha borda normal (sempre a mesma espessura)
            pygame.draw.polygon(tela, PRETO, poligono['vertices'], 2)
    
    # Desenha os pontos centrais (sites)
    for i, ponto in enumerate(pontos_voronoi):
        pygame.draw.circle(tela, PRETO, ponto, 5)
        texto = fonte_ponto.render(str(i + 1), True, PRETO)
        tela.blit(texto, (ponto[0] + 8, ponto[1] - 8))
    
    # Desenha instruções na tela
    if modo_atual == 'EDICAO':
        instrucao_txt = "Modo EDICAO: Clique para adicionar pontos (S para selecionar)"
    else:
        instrucao_txt = "Modo SELECIONAR: Clique em um polígono (E para editar)"
    
    instrucao = fonte_instrucoes.render(instrucao_txt, True, PRETO)
    
    # Fundo semi-transparente para as instruções
    fundo_rect = pygame.Rect(10, 5, instrucao.get_width() + 20, instrucao.get_height() + 10)
    fundo_surf = pygame.Surface(fundo_rect.size, pygame.SRCALPHA)
    fundo_surf.fill((255, 255, 255, 180)) # Branco com 180 de alpha (transparência)
    tela.blit(fundo_surf, fundo_rect.topleft)
    tela.blit(instrucao, (20, 10))
        
    pygame.display.flip()

def obter_data_hora_brasileira():
    timestamp = time.time()
    
    # Converter para formato brasileiro
    data_hora_brasil = datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y %H:%M:%S.%f')[:-3]
    return data_hora_brasil

def ponto_em_poligono_simples(ponto_clique, vertices):
    """Verifica se um ponto está dentro de um polígono usando o algoritmo Ray Casting."""
    x, y = ponto_clique
    n = len(vertices)
    dentro = False
    
    p1x, p1y = vertices[0]
    for i in range(n + 1):
        p2x, p2y = vertices[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        x_intersecao = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= x_intersecao:
                        dentro = not dentro
        p1x, p1y = p2x, p2y
        
    return dentro

def ponto_em_poligono(ponto_clique, poligono):
    """Verifica se um ponto está dentro de um polígono usando o algoritmo Ray Casting."""
    return ponto_em_poligono_simples(ponto_clique, poligono['vertices'])

def main():
    global pontos_voronoi, poligonos_voronoi, ponto_arrastando, posicao_inicial_arrasto
    
    inicializar_jogo()
    relogio = pygame.time.Clock()
    
    # Variáveis para controlar o estado
    modo_atual = 'EDICAO'
    largura_tela, altura_tela = tela.get_size()
    
    # Inicializa variáveis de arrasto
    ponto_arrastando = None
    posicao_inicial_arrasto = None
    
    rodando = True
    tempo_inicio = time.time()
    
    with open('log_execucao.csv', 'w', newline='', encoding='utf-8') as arquivo_log:
        log_writer = csv.writer(arquivo_log)
        log_writer.writerow(['timestamp', 'tipo_evento', 'pos_x', 'pos_y', 'info_extra'])
        
        while rodando:
            # Processa eventos e atualiza o estado
            rodando, modo_atual = processar_eventos(log_writer, modo_atual, largura_tela, altura_tela)
            
            # Desenha tudo na tela
            desenhar_tudo(tela, modo_atual)
            relogio.tick(60)
        
        tempo_fim = time.time()
        tempo_total = tempo_fim - tempo_inicio
        log_writer.writerow([tempo_fim, 'fim_execucao', '', '', f'{tempo_total:.2f}'])
        log_writer.writerow([tempo_fim, 'Total de Cliques', '', '', f'{cliques_total}'])
        
        print(f"Tempo total: {tempo_total:.2f}s")
        print(f"Total de cliques: {cliques_total}")
        print(f"Total de pontos criados: {len(pontos_voronoi)}")
        print(f"Total de polígonos gerados: {len(poligonos_voronoi)}")
        print("Log 'log_execucao.csv' salvo com sucesso!")

    pygame.quit()

if __name__ == "__main__":
    main()