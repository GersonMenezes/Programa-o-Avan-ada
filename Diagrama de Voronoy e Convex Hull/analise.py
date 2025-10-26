import pandas as pd
import matplotlib.pyplot as plt

# Carregar os dados do log para um DataFrame do Pandas
df = pd.read_csv('log_execucao.csv')

# --- Cálculos Simples ---
total_cliques = len(df[df['tipo_evento'].isin(['criacao', 'selecao'])])
print(f"Total de cliques na execução: {total_cliques}")

# --- Geração de Gráficos ---

# 1. Gráfico do Percurso do Mouse
df_movimento = df[df['tipo_evento'] == 'movimento']
plt.figure(figsize=(8, 6))
plt.plot(df_movimento['pos_x'], df_movimento['pos_y'] * -1, alpha=0.6) # Invertemos o Y porque o Pygame e Matplotlib têm eixos Y opostos
plt.title('Percurso do Mouse na Tela')
plt.xlabel('Posição X')
plt.ylabel('Posição Y')
plt.gca().set_aspect('equal', adjustable='box')
plt.savefig('images/grafico_percurso_mouse.png') # Salva o gráfico como imagem
plt.show()


# 2. Gráfico de Contagem de Objetos Criados
df_criacao = df[df['tipo_evento'] == 'criacao']
contagem_criacao = df_criacao['info_extra'].value_counts()

plt.figure(figsize=(10, 5))
contagem_criacao.plot(kind='bar')
plt.title('Contagem de Objetos Criados')
plt.ylabel('Número de Criações')
plt.xticks(rotation=45)

# 🔽 CONFIGURAÇÃO PARA NÚMEROS INTEIROS NO EIXO Y 🔽
if len(contagem_criacao) > 0:
    max_valor = int(contagem_criacao.max())  # Pega o maior valor (convertido para inteiro)
    plt.yticks(range(0, max_valor + 2))  # Cria ticks de 0 até max_valor + 1

plt.tight_layout()
plt.savefig('images/grafico_objetos_criados.png')
plt.show()

# 3. Gráfico de Contagem de Cliques por Polígono
df_selecoes = df[df['tipo_evento'] == 'selecao']
# Filtra apenas seleções de polígonos (não 'nenhum_poligono')
df_poligonos = df_selecoes[df_selecoes['info_extra'].str.contains('poligono_', na=False)]

if len(df_poligonos) > 0:
    # Extrai o número do polígono do info_extra
    df_poligonos['poligono_id'] = df_poligonos['info_extra'].str.extract(r'poligono_(\d+)').astype(int)
    contagem_poligonos = df_poligonos['poligono_id'].value_counts().sort_index()
    
    plt.figure(figsize=(12, 6))
    contagem_poligonos.plot(kind='bar')
    plt.title('Contagem de Cliques por Polígono')
    plt.xlabel('ID do Polígono')
    plt.ylabel('Número de Cliques')
    plt.xticks(rotation=0)
    
    # Configuração para números inteiros no eixo Y
    if len(contagem_poligonos) > 0:
        max_valor = int(contagem_poligonos.max())
        plt.yticks(range(0, max_valor + 2))
    
    plt.tight_layout()
    plt.savefig('images/grafico_cliques_poligonos.png')
    plt.show()
    
    # Estatísticas dos polígonos
    print(f"\n=== ESTATÍSTICAS DOS POLÍGONOS ===")
    print(f"Total de polígonos clicados: {len(contagem_poligonos)}")
    print(f"Polígono mais clicado: P{contagem_poligonos.idxmax()} ({contagem_poligonos.max()} cliques)")
    print(f"Total de cliques em polígonos: {contagem_poligonos.sum()}")
    print(f"Cliques em 'nenhum_poligono': {len(df_selecoes[df_selecoes['info_extra'] == 'nenhum_poligono'])}")
else:
    print("\nNenhum polígono foi clicado nesta execução.")
