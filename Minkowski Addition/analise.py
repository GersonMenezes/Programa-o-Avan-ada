import csv
import time
import random
import math
import os.path
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# --- Funções do Algoritmo (Copiadas do main.py para independência) ---

def cross(a, b, c):
    """Produto vetorial (determinante) dos vetores AB e AC"""
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

def convex_hull(points):
    """ Algoritmo Monotone Chain para encontrar o Hull convexo """
    if len(points) < 3:
        return points

    # Ordena pontos por x (e por y em caso de empate)
    points = sorted(points, key=lambda p: (p[0], p[1]))

    # Lower hull
    lower = []
    for p in points:
        while len(lower) >= 2:
            a, b = lower[-2], lower[-1]
            if cross(a, b, p) <= 0:  # <= 0 significa anti-horário ou colinear
                lower.pop()
            else:
                break
        lower.append(p)

    # Upper hull
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

# --- Parte 1: Análise de Desempenho ---

def gerar_obstaculo_aleatorio(n_vertices, max_coord=1000):
    """Gera um conjunto de n vértices aleatórios."""
    obstaculo = []
    for _ in range(n_vertices):
        x = random.randint(0, max_coord)
        y = random.randint(0, max_coord)
        obstaculo.append((x, y))
    return obstaculo

def plotar_grafico(resultados):
    """Usa matplotlib para plotar os resultados do desempenho."""
    if not resultados:
        print("Nenhum resultado de desempenho para plotar.")
        return

    n_vals = [r[0] for r in resultados]
    tempos = [r[1] for r in resultados]

    plt.figure(figsize=(10, 6))
    plt.plot(n_vals, tempos, 'o-', label="Tempo de Execução Real")
    
    # Opcional: Tenta plotar uma curva O(n log n) para comparação
    if tempos and n_vals and n_vals[-1] > 1: # Adicionado check > 1
        try:
            ultimo_n = n_vals[-1]
            ultimo_tempo = tempos[-1]
            fator_c = ultimo_tempo / (ultimo_n * math.log(ultimo_n))
            n_log_n = [fator_c * n * math.log(n) for n in n_vals if n > 1]
            n_log_n_labels = [n for n in n_vals if n > 1]
            plt.plot(n_log_n_labels, n_log_n, 'r--', label="Referência O(n log n)")
        except Exception as e:
            print(f"Não foi possível plotar a curva de referência: {e}")


    plt.title('Análise de Desempenho: Soma de Minkowski (Geração + Convex Hull)')
    plt.xlabel('n (Número de Vértices do Obstáculo)')
    plt.ylabel('Tempo de Execução (segundos)')
    plt.grid(True, which="both", ls="--", alpha=0.5)
    plt.legend()
    
    # Salva o gráfico em um arquivo
    nome_arquivo = 'grafico_desempenho_minkowski.png'
    plt.savefig(nome_arquivo)
    print(f"\nGráfico de desempenho salvo como '{nome_arquivo}'")
    plt.show() # Mostra o gráfico


def rodar_analise_desempenho():
    """Executa o experimento de análise de complexidade."""
    print("\n--- Iniciando Análise de Desempenho ---")
    
    # Robô fixo (m=4)
    robo_forma_fixo = [(0, 0), (10, 0), (10, 10), (0, 10)]
    m = len(robo_forma_fixo)
    
    # Valores de n (vértices do obstáculo) para testar
    n_valores = [10, 50, 100, 200, 500, 1000, 2000, 3000, 5000]
    resultados = []

    print(f"Testando com robô fixo (m = {m} vértices). Variando n...")

    for n in n_valores:
        # 1. Gerar obstáculo aleatório com n vértices
        obstaculo = gerar_obstaculo_aleatorio(n)
        
        # 2. Medir o tempo do algoritmo principal
        t_inicio = time.perf_counter()
        
        # 2a. Criar a "poeira" de pontos
        pontos_soma = []
        for p_robo in robo_forma_fixo:
            for p_obs in obstaculo:
                pontos_soma.append((p_robo[0] + p_obs[0], p_robo[1] + p_obs[1]))
        
        # 2b. Calcular o Convex Hull
        _ = convex_hull(pontos_soma) # O resultado não importa, só o tempo
        
        t_fim = time.perf_counter()
        
        t_total = t_fim - t_inicio
        resultados.append((n, t_total))
        
        n_total_poeira = len(pontos_soma) # Deve ser n * m
        print(f"  n={n:<5} | N (poeira)={n_total_poeira:<6} | Tempo: {t_total:.6f} segundos")

    print("--- Análise de Desempenho Concluída ---")
    
    # 3. Plotar os resultados
    plotar_grafico(resultados)


# --- Parte 2: Tabela de Distâncias (Leitura do Log) ---

def plotar_tabela(df, ultimo_timestamp):
    """Cria uma figura do matplotlib para 'desenhar' o DataFrame da tabela."""
    print(f"\nGerando imagem da tabela de distâncias...")
    
    df_formatado = df.apply(lambda col: col.map(lambda x: f"{x:.2f}" if pd.notna(x) else "NaN"))

    cell_text = df_formatado.values
    row_labels = df.index
    col_labels = df.columns
    
    # Cria uma nova figura. Ajusta o figsize conforme o tamanho da tabela.
    # Aumenta o denominador para tornar as células maiores
    fig_height = max(1.5, len(row_labels) / 1.8) 
    fig_width = max(3, len(col_labels) / 1.2)
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    
    # Esconde os eixos do gráfico
    ax.set_axis_off() 
    
    # Cria a tabela
    tabela = ax.table(cellText=cell_text, 
                      rowLabels=row_labels, 
                      colLabels=col_labels, 
                      loc='center', 
                      cellLoc='center')
    
    tabela.auto_set_font_size(False)
    tabela.set_fontsize(10)
    tabela.scale(1.2, 1.2) # Escala a tabela para preencher a figura
    
    # Adiciona um título à figura
    plt.title(f'Tabela de Distâncias Mínimas (Vértice-a-Vértice)\nSimulação: {ultimo_timestamp}', 
              pad=20) # 'pad' adiciona espaço
    
    fig.tight_layout() # Ajusta para evitar cortes
    
    # Salva a figura da tabela
    nome_arquivo = 'tabela_distancias.png'
    plt.savefig(nome_arquivo, bbox_inches='tight', dpi=200)
    print(f"Imagem da tabela salva como '{nome_arquivo}'")
    plt.show() # Mostra a tabela

# --- FIM DA NOVA FUNÇÃO ---


def ler_tabela_distancia_log():
    """Lê o arquivo CSV e monta a tabela de distâncias da última simulação."""
    print("--- Lendo Tabela de Distâncias da Última Simulação ---")
    
    nome_arquivo = 'log_execucao_minkowski.csv'
    
    if not os.path.exists(nome_arquivo):
        print(f"Arquivo de log '{nome_arquivo}' não encontrado.")
        print("Execute o 'main.py' e pressione 'S' para gerar o log primeiro.")
        return

    distancias_eventos = []
    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader) # Pula o cabeçalho
            
            for row in reader:
                if row[1] == 'distancia': # Filtra apenas eventos de 'distancia'
                    distancias_eventos.append(row)
    except Exception as e:
        print(f"Erro ao ler o arquivo de log: {e}")
        return

    if not distancias_eventos:
        print("Nenhum evento de 'distancia' encontrado no log.")
        print("Execute o 'main.py' e pressione 'S' para gerar os dados.")
        return

    # Filtra apenas os eventos da última simulação (último timestamp)
    ultimo_timestamp = distancias_eventos[-1][0]
    eventos_recentes = [e for e in distancias_eventos if e[0] == ultimo_timestamp]
    
    dist_data = {} # Dicionário para armazenar distâncias
    entidades = set() # Conjunto de todas as entidades (RB, O1, S1, etc.)

    # Processa os eventos recentes
    for _, _, par_str, dist_str, _ in eventos_recentes:
        try:
            ent1, ent2 = par_str.split('-')
            dist = float(dist_str)
            
            entidades.add(ent1)
            entidades.add(ent2)
            
            # Armazena nos dois sentidos para a matriz
            if ent1 not in dist_data: dist_data[ent1] = {}
            if ent2 not in dist_data: dist_data[ent2] = {}
            dist_data[ent1][ent2] = dist
            dist_data[ent2][ent1] = dist
        except ValueError:
            print(f"Ignorando linha mal formatada: {par_str}, {dist_str}")
            continue
            
    if not entidades:
        print("Nenhuma entidade de distância processada.")
        return

    # Ordena as entidades para uma tabela consistente
    entidades_ordenadas = sorted(list(entidades), key=lambda x: (x.strip('0123456789'), int(x[1:] or 0) if x[1:].isdigit() else -1))

    # Cria o DataFrame com Pandas, especificando o dtype
    df = pd.DataFrame(index=entidades_ordenadas, columns=entidades_ordenadas, dtype=float)

    # Preenche o DataFrame
    for ent1 in entidades_ordenadas:
        for ent2 in entidades_ordenadas:
            if ent1 == ent2:
                df.loc[ent1, ent2] = 0.0
            else:
                # Usa .get() para evitar erros se um par estiver faltando
                df.loc[ent1, ent2] = dist_data.get(ent1, {}).get(ent2, np.nan)
    
    print(f"\n(Baseado na simulação de timestamp: {ultimo_timestamp})\n")
    
    if df.empty:
        print("A tabela de distâncias está vazia (nenhum dado de distância encontrado para o último timestamp).")
    else:
        # Imprime a tabela formatada no console
        print(df.to_string(float_format=lambda x: f"{x:.2f}", na_rep="NaN"))
        
        # --- FUNÇÃO DE PLOTAGEM CHAMADA AQUI ---
        plotar_tabela(df, ultimo_timestamp)
    
    print("\n--- Fim da Leitura da Tabela ---")


# --- Execução Principal ---

if __name__ == "__main__":
    print("Iniciando Script de Análise (Trabalho 4)...")
    
    # 1. Mostra a tabela de distâncias (no console E em uma janela gráfica)
    ler_tabela_distancia_log()
    
    # 2. Roda a análise de desempenho e gera o gráfico (segunda janela)
    rodar_analise_desempenho()
    
    print("\n--- Script de Análise Finalizado ---")