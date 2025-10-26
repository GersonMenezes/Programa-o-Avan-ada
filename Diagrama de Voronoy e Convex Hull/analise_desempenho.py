import numpy as np
import time
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi

def gerar_pontos(n_pontos, tipo_distribuicao='uniforme'):
    """Gera um conjunto de pontos com uma distribuição específica."""
    if tipo_distribuicao == 'uniforme':
        # Pontos espalhados uniformemente em um quadrado de 1000x1000
        return np.random.rand(n_pontos, 2) * 1000
    
    elif tipo_distribuicao == 'cluster':
        # Gera 3 clusters de pontos
        # Garante que o total de pontos seja n_pontos
        n_por_cluster = n_pontos // 3
        pontos_restantes = n_pontos % 3
        
        # Cluster 1 (canto superior esquerdo)
        c1 = np.random.randn(n_por_cluster, 2) * 50 + np.array([200, 200])
        # Cluster 2 (canto inferior direito)
        c2 = np.random.randn(n_por_cluster, 2) * 50 + np.array([800, 800])
        # Cluster 3 (canto superior direito)
        c3 = np.random.randn(n_por_cluster + pontos_restantes, 2) * 50 + np.array([800, 200])
        
        # Junta todos os pontos
        return np.vstack([c1, c2, c3])

def executar_teste_desempenho():
    """Mede o tempo de execução do algoritmo Voronoi para diferentes N e distribuições."""
    resultados = []
    
    # Define a faixa de número de pontos que queremos testar
    # Começa com 10, vai até 3000, de 100 em 100
    pontos_a_testar = range(10, 10000, 100)
    
    for n in pontos_a_testar:
        print(f"Testando com {n} pontos...")
        
        # --- Teste com distribuição Uniforme ---
        pontos_uniforme = gerar_pontos(n, 'uniforme')
        start_time_uniforme = time.perf_counter()
        # A criação do objeto Voronoi é a operação que queremos medir
        _ = Voronoi(pontos_uniforme)
        end_time_uniforme = time.perf_counter()
        tempo_uniforme = end_time_uniforme - start_time_uniforme
        resultados.append({'n_pontos': n, 'distribuicao': 'Uniforme', 'tempo_s': tempo_uniforme})

        # --- Teste com distribuição em Cluster ---
        pontos_cluster = gerar_pontos(n, 'cluster')
        start_time_cluster = time.perf_counter()
        _ = Voronoi(pontos_cluster)
        end_time_cluster = time.perf_counter()
        tempo_cluster = end_time_cluster - start_time_cluster
        resultados.append({'n_pontos': n, 'distribuicao': 'Cluster', 'tempo_s': tempo_cluster})

    # Cria um DataFrame e salva em CSV
    df = pd.DataFrame(resultados)
    df.to_csv('log_desempenho.csv', index=False)
    print("\nArquivo 'log_desempenho.csv' salvo com sucesso!")
    return df

def plotar_graficos(df):
    """Plota os gráficos de desempenho a partir do DataFrame."""
    
    # Separa os dados por distribuição para facilitar o plot
    df_uniforme = df[df['distribuicao'] == 'Uniforme']
    df_cluster = df[df['distribuicao'] == 'Cluster']
    
    plt.figure(figsize=(12, 7))
    
    # Plota a linha para cada distribuição
    plt.plot(df_uniforme['n_pontos'], df_uniforme['tempo_s'], marker='o', linestyle='-', label='Distribuição Uniforme')
    plt.plot(df_cluster['n_pontos'], df_cluster['tempo_s'], marker='x', linestyle='--', label='Distribuição em Cluster')
    
    # Configurações do gráfico
    plt.title('Custo Computacional do Diagrama de Voronoi', fontsize=16)
    plt.xlabel('Número de Pontos (N)', fontsize=12)
    plt.ylabel('Tempo de Execução (segundos)', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # Adiciona texto explicativo sobre a complexidade
    texto_complexidade = (
        "O comportamento se aproxima de uma complexidade O(N log N).\n"
        "Isso significa que o tempo de execução não cresce linearmente, \n"
        "mas de forma um pouco mais acentuada, o que é típico para\n"
        "algoritmos eficientes baseados em divisão e conquista."
    )
    plt.text(0.05, 0.95, texto_complexidade, transform=plt.gca().transAxes,
             fontsize=12, verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', fc='wheat', alpha=0.5))
             
    plt.tight_layout()
    plt.savefig('images/grafico_desempenho_voronoi.png')
    print("Gráfico 'grafico_desempenho_voronoi.png' salvo com sucesso!")
    plt.show()

# --- Execução Principal ---
if __name__ == "__main__":
    # 1. Executa os testes e coleta os dados
    dados_desempenho = executar_teste_desempenho()
    
    # 2. Plota o gráfico a partir dos dados coletados
    plotar_graficos(dados_desempenho)