import time
import numpy as np
import matplotlib.pyplot as plt
import math

def convex_hull(points): 
    # Convertendo para tuplas
    points = [tuple(p) for p in points]
    
    # Ordena pontos por x (e por y em caso de empate)
    # O set() remove pontos duplicados que podem causar problemas
    points = sorted(list(set(points)), key=lambda p: (p[0], p[1]))
    
    if len(points) < 3:
        return points  # Precisa de pelo menos 3 pontos para formar um hull

    # --- Lower hull ---
    lower = []
    for p in points:
        while len(lower) >= 2:
            a, b = lower[-2], lower[-1]
            if cross(a, b, p) <= 0:  # <= 0 significa horário ou colinear
                lower.pop()
            else:
                break
        lower.append(p)
    
    # --- Upper hull ---
    upper = []
    for p in reversed(points):
        while len(upper) >= 2:
            a, b = upper[-2], upper[-1]
            if cross(a, b, p) <= 0:
                upper.pop()
            else:
                break
        upper.append(p)
    
    # Junta lower e upper para formar o polígono na ordem correta.
    return lower[:-1] + upper[:-1]


def cross(a, b, c):
    """Produto vetorial (determinante) dos vetores AB e AC"""
    return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])

# --- FUNÇÕES AUXILIARES PARA GERAÇÃO E ANÁLISE ---

def generate_points(n, distribution='uniform', scale=1000):
    """Gera N pontos em diferentes distribuições"""
    if distribution == 'uniform':
        return (np.random.rand(n, 2) * scale).tolist()
    elif distribution == 'circle':
        radius = scale
        angles = 2 * np.pi * np.random.rand(n)
        r_noise = radius * (1 - (np.random.rand(n) * 0.1)) 
        x = r_noise * np.cos(angles) + (scale/2)
        y = r_noise * np.sin(angles) + (scale/2)
        return np.column_stack((x, y)).tolist()
    elif distribution == 'line':
        x = np.linspace(0, scale, n)
        y = (scale / 4) + (x * 0.5) + (np.random.randn(n) * (scale*0.01))
        return np.column_stack((x, y)).tolist()
    elif distribution == 'cluster':
        std_dev = scale * 0.1
        center = scale / 2
        x = np.random.randn(n) * std_dev + center
        y = np.random.randn(n) * std_dev + center
        return np.column_stack((x, y)).tolist()


# --- EXPERIMENTOS E GRÁFICOS ---

# --- Gráfico 1 e 3: Custo Computacional e Crescimento ---
N_values = [100, 500, 1000, 5000, 10000, 25000, 50000, 75000]
times = []
hull_sizes = []
inside_counts = []
areas = []

print("Calculando Gráficos 1, 3, 4, 5 (Custo vs N)...")
for n in N_values:
    points = generate_points(n, 'uniform')
    start_time = time.perf_counter()
    hull = convex_hull(points)
    end_time = time.perf_counter()
    times.append(end_time - start_time)
    hull_sizes.append(len(hull))
    inside_counts.append(n - len(hull))

# Gráfico 2: Custo Computacional
plt.figure(figsize=(10, 6))
plt.plot(N_values, times, 'o-', label='Tempo Medido (Monotone Chain)')
if len(N_values) > 1:
    log_n_values = [n * np.log(n) for n in N_values]
    scale_factor = times[-1] / log_n_values[-1]
    n_log_n_scaled = [val * scale_factor for val in log_n_values]
    plt.plot(N_values, n_log_n_scaled, 'r--', label='Referência O(N log N)')
plt.title('Custo Computacional vs. Número de Pontos (N)')
plt.xlabel('Número de Pontos (N)')
plt.ylabel('Tempo de Execução (segundos)')
plt.legend()
plt.grid(True)


# --- Gráfico 3: Pontos Dentro vs. Fora ---
plt.figure(figsize=(10, 6))
p1 = plt.bar(N_values, hull_sizes, width=np.diff(N_values + [N_values[-1]*1.1])*0.8, label='Pontos no Hull (Vértices)')
p2 = plt.bar(N_values, inside_counts, bottom=hull_sizes, width=np.diff(N_values + [N_values[-1]*1.1])*0.8, label='Pontos Internos / Colineares')
plt.title('Proporção de Pontos no Hull vs. Internos')
plt.xlabel('Número Total de Pontos (N)')
plt.ylabel('Contagem de Pontos')
plt.xscale('log')
plt.yscale('log')
plt.legend()
plt.grid(True)

# --- Gráfico 4: Informação Extra 1 - Proporção de Pontos no Hull ---
plt.figure(figsize=(10, 6))
proportion_hull = [h / n for h, n in zip(hull_sizes, N_values)]
plt.plot(N_values, proportion_hull, 'g-o')
plt.title('Informação Extra: Proporção de Pontos no Hull (H/N)')
plt.xlabel('Número Total de Pontos (N)')
plt.ylabel('Proporção (Pontos no Hull / Total de Pontos)')
plt.xscale('log')
plt.grid(True)


# --- Gráfico 5: Custo por Distribuição ---
N_fixed = 50000
N_visual = 150
distributions = ['uniform', 'circle', 'line', 'cluster']
dist_times = []
print(f"Calculando Gráfico 2 (Custo por Distribuição) com N={N_fixed}...")
for dist in distributions:
    print(f"  Testando distribuição: {dist}")
    points = generate_points(N_fixed, dist)
    #np.random.shuffle(points)
    start_time = time.perf_counter()
    hull = convex_hull(points)
    end_time = time.perf_counter()
    dist_times.append(end_time - start_time)
    print(f"Tempo de execução: {end_time - start_time} segundos para Distribuição: {dist}")

    '''Visualização do Hull Convexo para cada distribuição'''
    points_visual = generate_points(N_visual, dist)
    hull_visual = convex_hull(points_visual)
    x_all, y_all = zip(*points_visual)
    if hull_visual: # Adiciona verificação para caso de poucos pontos
        hull_plot = hull_visual + [hull_visual[0]] # Fecha o polígono para o plot
        x_hull, y_hull = zip(*hull_plot)
        plt.figure(figsize=(7, 7))
        plt.plot(x_all, y_all, 'bo', label='Pontos', markersize=3)
        plt.plot(x_hull, y_hull, 'r-o', label='Hull Convexo', markersize=4)
        plt.title(f'Exemplo de Hull Convexo (N={N_visual}) - Distribuição: {dist}')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.legend()
        plt.grid(True)

plt.figure(figsize=(10, 6))
plt.bar(distributions, dist_times, color=['blue', 'green', 'red', 'purple'])
plt.title(f'Custo Computacional por Distribuição de Pontos (N={N_fixed})')
plt.xlabel('Tipo de Distribuição')
plt.ylabel('Tempo de Execução (segundos)')
plt.grid(axis='y')

# --- Exibe todos os gráficos ---
print("Análise concluída. Exibindo gráficos.")
plt.tight_layout()
plt.show()