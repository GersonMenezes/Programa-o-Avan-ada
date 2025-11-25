import pygame
import random
from collections import deque

# --- Variáveis Globais ---
tela = None
GRID_RESOLUCAO = 20
modo_atual = "OBSTACULOS"
pontos_inicio = []
pontos_fim = []
obstaculos = set()
caminhos = []

# --- Cores ---
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERMELHO = (255, 0, 0)
AZUL = (0, 0, 255)
VERDE = (0, 255, 0)
CINZA = (200, 200, 200)

# --- Inicialização ---
def inicializar_jogo():
    global tela
    pygame.init()
    tela = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Grid Interativo - Obstáculos / Pontos / Caminhos")

# --- Área de desenho ---
def get_area_desenho():
    largura, altura = tela.get_size()
    margem_superior = 50
    margem = 20
    return pygame.Rect(margem, margem_superior, largura - 2 * margem, altura - margem_superior - margem)

# --- Grid ---
def desenhar_grid(tela):
    area = get_area_desenho()
    largura_celula = area.width / GRID_RESOLUCAO
    altura_celula = area.height / GRID_RESOLUCAO
    for i in range(GRID_RESOLUCAO + 1):
        x = area.left + i * largura_celula
        y = area.top + i * altura_celula
        pygame.draw.line(tela, VERDE, (x, area.top), (x, area.bottom), 1)
        pygame.draw.line(tela, VERDE, (area.left, y), (area.right, y), 1)

# --- Converter clique para célula ---
def obter_celula(pos):
    area = get_area_desenho()
    if not area.collidepoint(pos): # Verifica se o clique está dentro da área de desenho
        return None
    largura_celula = area.width / GRID_RESOLUCAO
    altura_celula = area.height / GRID_RESOLUCAO
    col = int((pos[0] - area.left) // largura_celula) # O resto diz quantas células cabem na largura
    lin = int((pos[1] - area.top) // altura_celula)
    return (lin, col)

# --- Centro da célula para desenhar pontos ---
def centro_celula(lin, col):
    area = get_area_desenho()
    largura_celula = area.width / GRID_RESOLUCAO
    altura_celula = area.height / GRID_RESOLUCAO
    x = area.left + col * largura_celula + largura_celula / 2
    y = area.top + lin * altura_celula + altura_celula / 2
    return (int(x), int(y))


# --- Processar eventos ---
def processar_eventos():
    global modo_atual
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            return False
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                return False
            if evento.key == pygame.K_s:
                alternar_modo()
            if evento.key == pygame.K_c:
                limpar_tudo()
            if evento.key == pygame.K_a:
                gerar_aleatorio()
        if evento.type == pygame.MOUSEBUTTONDOWN:
            cel = obter_celula(evento.pos)
            if cel:
                if modo_atual == "OBSTACULOS":
                    if cel in obstaculos:
                        obstaculos.remove(cel)
                    else:
                        obstaculos.add(cel)
                elif modo_atual == "PONTOS":
                    adicionar_ponto(cel)
    return True

# --- Alternar modos ---
def alternar_modo():
    global modo_atual, caminhos
    if modo_atual == "OBSTACULOS":
        modo_atual = "PONTOS"
    elif modo_atual == "PONTOS":
        modo_atual = "CAMINHOS"
        gerar_caminhos()
    elif modo_atual == "CAMINHOS":
        modo_atual = "OBSTACULOS"
        caminhos.clear()
    print(f"Modo atual: {modo_atual}")

# --- Adicionar ponto ---
def adicionar_ponto(cel):
    if cel in obstaculos:
        return
    if len(pontos_inicio) == len(pontos_fim):
        pontos_inicio.append(cel)
    else:
        pontos_fim.append(cel)

# --- Gerar caminhos entre dois pares de pontos ---
def gerar_caminhos():
    global caminhos
    caminhos = []
    pares_validos = min(len(pontos_inicio), len(pontos_fim))
    for i in range(pares_validos):
        cor = tuple(random.randint(50,255) for _ in range(3))
        caminho = menor_caminho(pontos_inicio[i], pontos_fim[i], obstaculos)
        if caminho:
            caminhos.append((caminho, cor))

# --- BFS menor caminho ---
def menor_caminho(inicio, fim, obstaculos):
    filas = deque([(inicio, [inicio])])
    visitados = {inicio}
    direcoes = [(1,0), (-1,0), (0,1), (0,-1)]
    while filas:
        (lin, col), caminho = filas.popleft()
        if (lin, col) == fim:
            return caminho
        for dl, dc in direcoes:
            nl, nc = lin + dl, col + dc
            if 0 <= nl < GRID_RESOLUCAO and 0 <= nc < GRID_RESOLUCAO and (nl, nc) not in visitados and (nl, nc) not in obstaculos:
                visitados.add((nl, nc))
                filas.append(((nl, nc), caminho + [(nl, nc)]))
    return None

# --- Limpar tudo e voltar ao modo obstáculos ---
def limpar_tudo():
    global pontos_inicio, pontos_fim, obstaculos, caminhos, modo_atual
    pontos_inicio.clear()
    pontos_fim.clear()
    obstaculos.clear()
    caminhos.clear()
    modo_atual = "OBSTACULOS"
    print("Tudo limpo. Voltando para modo Obstáculos.")

# --- Gerar cenário aleatório ---
def gerar_aleatorio():
	
    limpar_tudo()
    DENSIDADE_OBSTACULOS = 0.20 # 20% do grid
    
    # Manter n_pares = O(R) para mirar na complexidade O(R^3)
    # (Se fizesse n_pares = O(R^2), a complexidade seria O(R^4)!)
    n_obstaculos = int((GRID_RESOLUCAO ** 2) * DENSIDADE_OBSTACULOS)
    n_pares = GRID_RESOLUCAO # Um número O(R)

    # Adicionar obstáculos aleatórios
    while len(obstaculos) < n_obstaculos:
        cel = (random.randint(0, GRID_RESOLUCAO-1), random.randint(0, GRID_RESOLUCAO-1))
        obstaculos.add(cel)

    # Adicionar pares de pontos aleatórios sem sobrepor obstáculos
    while len(pontos_inicio) < n_pares:
        lin = random.randint(0, GRID_RESOLUCAO-1)
        col = random.randint(0, GRID_RESOLUCAO-1)
        if (lin, col) in obstaculos or (lin, col) in pontos_inicio or (lin, col) in pontos_fim:
            continue
        pontos_inicio.append((lin, col))

        while True:
            lin_f = random.randint(0, GRID_RESOLUCAO-1)
            col_f = random.randint(0, GRID_RESOLUCAO-1)
            if (lin_f, col_f) in obstaculos or (lin_f, col_f) in pontos_inicio or (lin_f, col_f) in pontos_fim:
                continue
            pontos_fim.append((lin_f, col_f))
            break

    # Gerar automaticamente os caminhos
    gerar_caminhos()
    print(f"Cenário aleatório gerado: {n_obstaculos} obstáculos, {n_pares} pares de pontos.")

# --- Desenhar tudo ---
def desenhar_tudo():
    tela.fill(BRANCO)
    area = get_area_desenho()
    desenhar_grid(tela)
    largura_celula = area.width / GRID_RESOLUCAO
    altura_celula = area.height / GRID_RESOLUCAO

    # Obstáculos
    for lin, col in obstaculos:
        rect = pygame.Rect(area.left + col*largura_celula,
                           area.top + lin*altura_celula,
                           largura_celula, altura_celula)
        pygame.draw.rect(tela, PRETO, rect)

    # Caminhos
    for caminho, cor in caminhos:
        pontos_pixel = [centro_celula(l, c) for l, c in caminho]
        pygame.draw.lines(tela, cor, False, pontos_pixel, 4)

    # Pontos
    for cel in pontos_inicio:
        pygame.draw.circle(tela, AZUL, centro_celula(*cel), 6)
    for cel in pontos_fim:
        pygame.draw.circle(tela, VERMELHO, centro_celula(*cel), 6)

    # Instruções
    fonte = pygame.font.Font(None, 26)
    if modo_atual == "OBSTACULOS":
        instrucao_txt = 'Modo: Obstáculos | S → Pontos | C → Limpar | A → Aleatório | ESC: Sair'
    elif modo_atual == "PONTOS":
        instrucao_txt = 'Modo: Pontos | S → Caminhos | C → Limpar | A → Aleatório | ESC: Sair'
    else:
        instrucao_txt = 'Modo: Caminhos | S → Obstáculos | C → Limpar  | A → Aleatório | ESC: Sair'

    instrucao = fonte.render(instrucao_txt, True, PRETO)
    tela.blit(instrucao, (20, 10))
    pygame.display.flip()

# --- Loop principal ---
def main():
    inicializar_jogo()
    relogio = pygame.time.Clock()
    rodando = True

    while rodando:
        rodando = processar_eventos()
        desenhar_tudo()
        relogio.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
