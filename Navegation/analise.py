import random
import time
import matplotlib.pyplot as plt
from collections import deque
import numpy as np

# ----------------------------
# Funções de geração e caminhos
# ----------------------------

# função menor_caminho
def menor_caminho(inicio, fim, obstaculos, GRID_RESOLUCAO):
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


def gerar_aleatorio(GRID_RESOLUCAO, densidade_obstaculos, dist="uniforme"):
    obstaculos = set()
    pontos_inicio = []
    pontos_fim = []
    caminhos = []

    n_obstaculos = int((GRID_RESOLUCAO ** 2) * densidade_obstaculos)
    n_pares = GRID_RESOLUCAO # Mantém n_pares = O(R)

    # Obstáculos aleatórios
    while len(obstaculos) < n_obstaculos:
        cel = (random.randint(0, GRID_RESOLUCAO-1), random.randint(0, GRID_RESOLUCAO-1))
        obstaculos.add(cel)

    if dist == "uniforme":
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

    elif dist == "cluster":
        RAIO_CLUSTER = max(2, GRID_RESOLUCAO // 10) 
        n_clusters = max(1, n_pares // 5)
        cluster_centers = [(random.randint(0, GRID_RESOLUCAO-1), random.randint(0, GRID_RESOLUCAO-1)) for _ in range(n_clusters)]
        
        while len(pontos_inicio) < n_pares:
            c = random.choice(cluster_centers)
            lin = min(max(c[0] + random.randint(-RAIO_CLUSTER, RAIO_CLUSTER), 0), GRID_RESOLUCAO-1)
            col = min(max(c[1] + random.randint(-RAIO_CLUSTER, RAIO_CLUSTER), 0), GRID_RESOLUCAO-1)
            
            if (lin, col) in obstaculos or (lin, col) in pontos_inicio or (lin, col) in pontos_fim:
                continue
            pontos_inicio.append((lin, col))

            while True:
                lin_f = min(max(c[0] + random.randint(-RAIO_CLUSTER, RAIO_CLUSTER), 0), GRID_RESOLUCAO-1)
                col_f = min(max(c[1] + random.randint(-RAIO_CLUSTER, RAIO_CLUSTER), 0), GRID_RESOLUCAO-1)
                
                if (lin_f, col_f) in obstaculos or (lin_f, col_f) in pontos_inicio or (lin_f, col_f) in pontos_fim:
                    continue
                pontos_fim.append((lin_f, col_f))
                break

    # Gerar caminhos
    for i in range(len(pontos_inicio)):
        # Verificação para garantir que o ponto de início não seja um obstáculo
        if pontos_inicio[i] in obstaculos or pontos_fim[i] in obstaculos:
            continue 
            
        caminho = menor_caminho(pontos_inicio[i], pontos_fim[i], obstaculos, GRID_RESOLUCAO)
        if caminho:
            caminhos.append(caminho)

    return caminhos


def analisar_desempenho_por_resolucao(resolucoes=[10,20,30,40,50]):
    tempos_uniforme = []
    tempos_cluster = []
    
    # Densidade fixa 20% do grid
    DENSIDADE_FIXA = 0.20 

    for res in resolucoes:
        print(f"Resolução: {res} (Uniforme)")
        start = time.time()
        # Passa a densidade fixa
        gerar_aleatorio(res, DENSIDADE_FIXA, dist="uniforme")
        end = time.time()
        tempos_uniforme.append(end-start)

        print(f"Resolução: {res} (Cluster)")
        start = time.time()
        # Passa a densidade fixa
        gerar_aleatorio(res, DENSIDADE_FIXA, dist="cluster")
        end = time.time()
        tempos_cluster.append(end-start)

    # Plot
    plt.figure(figsize=(10,6))
    plt.plot(resolucoes, tempos_uniforme, marker='o', label="Distribuição Uniforme")
    plt.plot(resolucoes, tempos_cluster, marker='s', label="Distribuição em Clusters")
    plt.xlabel("Resolução do Grid")
    plt.ylabel("Tempo de Execução (s)")
    plt.title("Análise de Desempenho - Tempo x Resolução (Densidade Fixa em 20%)")
    plt.legend()
    plt.grid(True)
    plt.show()

# função de análise por densidade
def analisar_desempenho_por_densidade(resolucao_fixa=60): # Use uma resolução média/alta
    
    # Cria uma lista de densidades para testar
    densidades = np.linspace(0.0, 0.7, 15) # 15 pontos de 0% a 70%
    tempos_uniforme = []
    
    print(f"Iniciando análise por densidade (Resolução fixa em {resolucao_fixa})")

    for dens in densidades:
        print(f"Testando Densidade: {dens*100:.1f}%")
        start = time.time()
        gerar_aleatorio(resolucao_fixa, dens, dist="uniforme")
        end = time.time()
        print(f"Tempo de execução: {end-start} segundos")
        tempos_uniforme.append(end-start)

    # Plot
    plt.figure(figsize=(10,6))
    plt.plot(densidades * 100, tempos_uniforme, marker='o', label="Distribuição Uniforme")
    plt.xlabel("Densidade de Obstáculos (%)")
    plt.ylabel("Tempo de Execução (s)")
    plt.title(f"Análise de Desempenho - Tempo x Densidade (Resolução Fixa em {resolucao_fixa}x{resolucao_fixa})")
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    
    # Gráfico 1: Tempo vs Resolução
    analisar_desempenho_por_resolucao(resolucoes=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    
    # Gráfico 2: Tempo vs Densidade
    analisar_desempenho_por_densidade(resolucao_fixa=90)