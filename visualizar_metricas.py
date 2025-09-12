import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.patches import Rectangle
from pathlib import Path

# Configurações do Seaborn
sns.set_style("whitegrid")
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

def carregar_dados():
    """Carrega os dados do arquivo CSV"""
    try:
        df = pd.read_csv('resultados_metricas.csv')
        print(f"Dados carregados com sucesso: {len(df)} repositórios")
        return df
    except FileNotFoundError:
        print("ERRO: Arquivo 'resultados_metricas.csv' não encontrado!")
        return None

def criar_histogramas(df):
    """Cria histogramas para as métricas medianas e totais"""
    # Criar diretório se não existir
    Path('graficos').mkdir(exist_ok=True)
    
    # Histogramas para métricas medianas
    fig, axes = plt.subplots(1, 3, figsize=(20, 8))
    fig.suptitle('Distribuição das Métricas de Qualidade de Código - Valores Medianos', fontsize=18, fontweight='bold')
    
    metricas_median = ['cbo_median', 'dit_median', 'lcom_median']
    titulos_median = ['CBO (Coupling Between Objects)', 'DIT (Depth of Inheritance Tree)', 'LCOM (Lack of Cohesion of Methods)']
    
    for i, (metrica, titulo) in enumerate(zip(metricas_median, titulos_median)):
        # Ajustar número de bins baseado no tamanho do dataset
        bins = min(30, max(10, len(df) // 20))
        sns.histplot(data=df, x=metrica, bins=bins, kde=True, ax=axes[i])
        axes[i].set_title(f'{titulo} (Mediana)', fontweight='bold', fontsize=14)
        axes[i].set_xlabel(f'{titulo} (Mediana)', fontsize=12)
        axes[i].set_ylabel('Frequência', fontsize=12)
        axes[i].tick_params(labelsize=10)
    
    plt.tight_layout()
    plt.savefig('graficos/histogramas_metricas_medianas.png', dpi=600, bbox_inches='tight')
    plt.show()
    print("✓ Histogramas (medianas) salvos como 'graficos/histogramas_metricas_medianas.png'")
    
    # Histogramas para métricas totais (separado para melhor visualização)
    fig, axes = plt.subplots(1, 3, figsize=(20, 8))
    fig.suptitle('Distribuição das Métricas de Qualidade de Código - Valores Totais (Log Scale)', fontsize=18, fontweight='bold')
    
    metricas_total = ['cbo_total', 'dit_total', 'lcom_total']
    titulos_total = ['CBO Total', 'DIT Total', 'LCOM Total']
    
    for i, (metrica, titulo) in enumerate(zip(metricas_total, titulos_total)):
        # Usar log scale para valores totais
        data_log = np.log1p(df[metrica])  # log1p para evitar log(0)
        bins = min(30, max(10, len(df) // 20))
        sns.histplot(data=data_log, bins=bins, kde=True, ax=axes[i])
        axes[i].set_title(f'{titulo} (Log Scale)', fontweight='bold', fontsize=14)
        axes[i].set_xlabel(f'{titulo} (Log Scale)', fontsize=12)
        axes[i].set_ylabel('Frequência', fontsize=12)
        axes[i].tick_params(labelsize=10)
    
    plt.tight_layout()
    plt.savefig('graficos/histogramas_metricas_totais.png', dpi=600, bbox_inches='tight')
    plt.show()
    print("✓ Histogramas (totais) salvos como 'graficos/histogramas_metricas_totais.png'")

def criar_boxplots(df):
    """Cria boxplots para visualizar a distribuição das métricas"""
    # Boxplots para métricas medianas
    fig, axes = plt.subplots(1, 3, figsize=(20, 10))
    fig.suptitle('Boxplots das Métricas de Qualidade de Código - Valores Medianos', fontsize=18, fontweight='bold')
    
    metricas_median = ['cbo_median', 'dit_median', 'lcom_median']
    titulos_median = ['CBO (Mediana)', 'DIT (Mediana)', 'LCOM (Mediana)']
    
    for i, (metrica, titulo) in enumerate(zip(metricas_median, titulos_median)):
        sns.boxplot(data=df, y=metrica, ax=axes[i], palette='Set2')
        axes[i].set_title(titulo, fontweight='bold', fontsize=14)
        axes[i].set_ylabel('Valor', fontsize=12)
        axes[i].tick_params(labelsize=10)
        # Adicionar estatísticas no gráfico
        median_val = df[metrica].median()
        axes[i].text(0.02, 0.98, f'Mediana: {median_val:.2f}', transform=axes[i].transAxes, 
                    verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('graficos/boxplots_metricas_medianas.png', dpi=600, bbox_inches='tight')
    plt.show()
    print("✓ Boxplots (medianas) salvos como 'graficos/boxplots_metricas_medianas.png'")
    
    # Boxplots para métricas totais (separado para melhor visualização)
    fig, axes = plt.subplots(1, 3, figsize=(20, 10))
    fig.suptitle('Boxplots das Métricas de Qualidade de Código - Valores Totais (Log Scale)', fontsize=18, fontweight='bold')
    
    metricas_total = ['cbo_total', 'dit_total', 'lcom_total']
    titulos_total = ['CBO (Total)', 'DIT (Total)', 'LCOM (Total)']
    
    for i, (metrica, titulo) in enumerate(zip(metricas_total, titulos_total)):
        sns.boxplot(data=df, y=metrica, ax=axes[i], palette='Set1')
        axes[i].set_title(titulo, fontweight='bold', fontsize=14)
        axes[i].set_ylabel('Valor (Log Scale)', fontsize=12)
        axes[i].tick_params(labelsize=10)
        # Usar escala logarítmica para valores totais
        axes[i].set_yscale('log')
        # Adicionar estatísticas no gráfico
        median_val = df[metrica].median()
        axes[i].text(0.02, 0.98, f'Mediana: {median_val:.0f}', transform=axes[i].transAxes, 
                    verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('graficos/boxplots_metricas_totais.png', dpi=600, bbox_inches='tight')
    plt.show()
    print("✓ Boxplots (totais) salvos como 'graficos/boxplots_metricas_totais.png'")

def criar_scatter_plots(df):
    """Cria gráficos de dispersão para analisar correlações"""
    # Scatter plots para métricas medianas
    fig, axes = plt.subplots(1, 3, figsize=(24, 8))
    fig.suptitle('Análise de Correlações - Métricas Medianas', fontsize=18, fontweight='bold')
    
    correlacoes_median = [
        ('cbo_median', 'dit_median', 'CBO vs DIT (Mediana)'),
        ('cbo_median', 'lcom_median', 'CBO vs LCOM (Mediana)'),
        ('dit_median', 'lcom_median', 'DIT vs LCOM (Mediana)')
    ]
    
    for i, (x_col, y_col, titulo) in enumerate(correlacoes_median):
        sns.scatterplot(data=df, x=x_col, y=y_col, ax=axes[i], alpha=0.7, s=60)
        axes[i].set_title(titulo, fontweight='bold', fontsize=14)
        axes[i].set_xlabel(x_col.replace('_', ' ').title(), fontsize=12)
        axes[i].set_ylabel(y_col.replace('_', ' ').title(), fontsize=12)
        axes[i].tick_params(labelsize=10)
        
        # Adicionar linha de tendência
        if len(df) > 1:  # Verificar se há dados suficientes
            z = np.polyfit(df[x_col], df[y_col], 1)
            p = np.poly1d(z)
            axes[i].plot(df[x_col], p(df[x_col]), "r--", alpha=0.8, linewidth=2)
        
        # Calcular e mostrar correlação
        corr = df[x_col].corr(df[y_col])
        axes[i].text(0.05, 0.95, f'r = {corr:.3f}', transform=axes[i].transAxes,
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.9), fontsize=11)
    
    plt.tight_layout()
    plt.savefig('graficos/scatter_plots_medianas.png', dpi=600, bbox_inches='tight')
    plt.show()
    print("✓ Scatter plots (medianas) salvos como 'graficos/scatter_plots_medianas.png'")
    
    # Scatter plots para métricas totais (separado para melhor visualização)
    fig, axes = plt.subplots(1, 3, figsize=(24, 8))
    fig.suptitle('Análise de Correlações - Métricas Totais (Log Scale)', fontsize=18, fontweight='bold')
    
    correlacoes_total = [
        ('cbo_total', 'dit_total', 'CBO vs DIT (Total)'),
        ('cbo_total', 'lcom_total', 'CBO vs LCOM (Total)'),
        ('dit_total', 'lcom_total', 'DIT vs LCOM (Total)')
    ]
    
    for i, (x_col, y_col, titulo) in enumerate(correlacoes_total):
        sns.scatterplot(data=df, x=x_col, y=y_col, ax=axes[i], alpha=0.7, s=60)
        axes[i].set_title(titulo, fontweight='bold', fontsize=14)
        axes[i].set_xlabel(x_col.replace('_', ' ').title(), fontsize=12)
        axes[i].set_ylabel(y_col.replace('_', ' ').title(), fontsize=12)
        axes[i].tick_params(labelsize=10)
        
        # Usar escala logarítmica para valores totais
        axes[i].set_xscale('log')
        axes[i].set_yscale('log')
        
        # Calcular e mostrar correlação
        corr = df[x_col].corr(df[y_col])
        axes[i].text(0.05, 0.95, f'r = {corr:.3f}', transform=axes[i].transAxes,
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.9), fontsize=11)
    
    plt.tight_layout()
    plt.savefig('graficos/scatter_plots_totais.png', dpi=600, bbox_inches='tight')
    plt.show()
    print("✓ Scatter plots (totais) salvos como 'graficos/scatter_plots_totais.png'")

def criar_heatmap_correlacao(df):
    """Cria heatmap de correlação entre as métricas"""
    # Calcular matriz de correlação
    correlation_matrix = df[['cbo_median', 'dit_median', 'lcom_median', 
                            'cbo_total', 'dit_total', 'lcom_total']].corr()
    
    plt.figure(figsize=(12, 10))
    
    # Criar máscara para a diagonal superior (opcional)
    mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
    
    # Criar heatmap com melhor formatação
    sns.heatmap(correlation_matrix, 
                annot=True, 
                cmap='RdBu_r', 
                center=0,
                square=True, 
                fmt='.3f', 
                cbar_kws={'shrink': 0.8, 'label': 'Coeficiente de Correlação'},
                annot_kws={'size': 12, 'weight': 'bold'},
                linewidths=0.5)
    
    plt.title('Matriz de Correlação - Métricas de Qualidade de Código', 
              fontsize=16, fontweight='bold', pad=20)
    
    # Melhorar labels dos eixos
    labels = ['CBO\n(Mediana)', 'DIT\n(Mediana)', 'LCOM\n(Mediana)', 
              'CBO\n(Total)', 'DIT\n(Total)', 'LCOM\n(Total)']
    plt.xticks(range(len(labels)), labels, rotation=45, ha='right', fontsize=11)
    plt.yticks(range(len(labels)), labels, rotation=0, fontsize=11)
    
    plt.tight_layout()
    plt.savefig('graficos/heatmap_correlacao.png', dpi=600, bbox_inches='tight')
    plt.show()
    print("✓ Heatmap de correlação salvo como 'graficos/heatmap_correlacao.png'")

def criar_grafico_barras_repositorios(df):
    """Cria gráficos de barras comparando repositórios (adaptado para grandes datasets)"""
    n_repos = len(df)
    
    if n_repos <= 20:
        # Para poucos repositórios, mostrar todos
        df_sorted = df.sort_values('cbo_median', ascending=False)
        
        fig, axes = plt.subplots(3, 1, figsize=(15, 18))
        fig.suptitle(f'Comparação entre Repositórios - Métricas Medianas ({n_repos} repositórios)', fontsize=16, fontweight='bold')
        
        # CBO
        sns.barplot(data=df_sorted, x='cbo_median', y='repo_name', ax=axes[0], palette='viridis')
        axes[0].set_title('CBO (Coupling Between Objects) - Mediana', fontweight='bold')
        axes[0].set_xlabel('CBO (Mediana)')
        axes[0].set_ylabel('Repositório')
        
        # DIT
        sns.barplot(data=df_sorted, x='dit_median', y='repo_name', ax=axes[1], palette='plasma')
        axes[1].set_title('DIT (Depth of Inheritance Tree) - Mediana', fontweight='bold')
        axes[1].set_xlabel('DIT (Mediana)')
        axes[1].set_ylabel('Repositório')
        
        # LCOM
        sns.barplot(data=df_sorted, x='lcom_median', y='repo_name', ax=axes[2], palette='inferno')
        axes[2].set_title('LCOM (Lack of Cohesion of Methods) - Mediana', fontweight='bold')
        axes[2].set_xlabel('LCOM (Mediana)')
        axes[2].set_ylabel('Repositório')
        
        plt.tight_layout()
        plt.savefig('graficos/barras_repositorios.png', dpi=600, bbox_inches='tight')
        plt.show()
        print("✓ Gráfico de barras salvo como 'graficos/barras_repositorios.png'")
    else:
        # Para muitos repositórios, mostrar top 20 e bottom 20
        print(f"📊 Dataset com {n_repos} repositórios. Criando visualizações otimizadas...")
        
        # Top 20 repositórios por CBO mediana
        top_20 = df.nlargest(20, 'cbo_median')
        bottom_20 = df.nsmallest(20, 'cbo_median')
        
        # Criar gráfico para top 20
        fig, axes = plt.subplots(3, 1, figsize=(20, 18))
        fig.suptitle(f'Top 20 Repositórios - Maiores Valores de CBO (Total: {n_repos} repos)', fontsize=16, fontweight='bold')
        
        # CBO - Top 20
        sns.barplot(data=top_20, x='cbo_median', y='repo_name', ax=axes[0], palette='viridis')
        axes[0].set_title('CBO (Coupling Between Objects) - Mediana', fontweight='bold')
        axes[0].set_xlabel('CBO (Mediana)')
        axes[0].set_ylabel('Repositório')
        
        # DIT - Top 20
        sns.barplot(data=top_20, x='dit_median', y='repo_name', ax=axes[1], palette='plasma')
        axes[1].set_title('DIT (Depth of Inheritance Tree) - Mediana', fontweight='bold')
        axes[1].set_xlabel('DIT (Mediana)')
        axes[1].set_ylabel('Repositório')
        
        # LCOM - Top 20
        sns.barplot(data=top_20, x='lcom_median', y='repo_name', ax=axes[2], palette='inferno')
        axes[2].set_title('LCOM (Lack of Cohesion of Methods) - Mediana', fontweight='bold')
        axes[2].set_xlabel('LCOM (Mediana)')
        axes[2].set_ylabel('Repositório')
        
        plt.tight_layout()
        plt.savefig('graficos/barras_top20_repositorios.png', dpi=600, bbox_inches='tight')
        plt.show()
        print("✓ Gráfico top 20 repositórios salvo como 'graficos/barras_top20_repositorios.png'")
        
        # Criar gráfico para bottom 20
        fig, axes = plt.subplots(3, 1, figsize=(20, 18))
        fig.suptitle(f'Bottom 20 Repositórios - Menores Valores de CBO (Total: {n_repos} repos)', fontsize=16, fontweight='bold')
        
        # CBO - Bottom 20
        sns.barplot(data=bottom_20, x='cbo_median', y='repo_name', ax=axes[0], palette='viridis')
        axes[0].set_title('CBO (Coupling Between Objects) - Mediana', fontweight='bold')
        axes[0].set_xlabel('CBO (Mediana)')
        axes[0].set_ylabel('Repositório')
        
        # DIT - Bottom 20
        sns.barplot(data=bottom_20, x='dit_median', y='repo_name', ax=axes[1], palette='plasma')
        axes[1].set_title('DIT (Depth of Inheritance Tree) - Mediana', fontweight='bold')
        axes[1].set_xlabel('DIT (Mediana)')
        axes[1].set_ylabel('Repositório')
        
        # LCOM - Bottom 20
        sns.barplot(data=bottom_20, x='lcom_median', y='repo_name', ax=axes[2], palette='inferno')
        axes[2].set_title('LCOM (Lack of Cohesion of Methods) - Mediana', fontweight='bold')
        axes[2].set_xlabel('LCOM (Mediana)')
        axes[2].set_ylabel('Repositório')
        
        plt.tight_layout()
        plt.savefig('graficos/barras_bottom20_repositorios.png', dpi=600, bbox_inches='tight')
        plt.show()
        print("✓ Gráfico bottom 20 repositórios salvo como 'graficos/barras_bottom20_repositorios.png'")

def gerar_estatisticas_descritivas(df):
    """Gera e exibe estatísticas descritivas dos dados"""
    print("\n" + "="*60)
    print("ESTATÍSTICAS DESCRITIVAS DAS MÉTRICAS")
    print("="*60)
    
    # Estatísticas das métricas medianas
    print("\n📊 MÉTRICAS MEDIANAS:")
    print("-" * 30)
    metricas_median = ['cbo_median', 'dit_median', 'lcom_median']
    for metrica in metricas_median:
        print(f"\n{metrica.upper()}:")
        print(f"  Média: {df[metrica].mean():.2f}")
        print(f"  Mediana: {df[metrica].median():.2f}")
        print(f"  Desvio Padrão: {df[metrica].std():.2f}")
        print(f"  Mínimo: {df[metrica].min():.2f}")
        print(f"  Máximo: {df[metrica].max():.2f}")
    
    # Estatísticas das métricas totais
    print("\n📈 MÉTRICAS TOTAIS:")
    print("-" * 30)
    metricas_total = ['cbo_total', 'dit_total', 'lcom_total']
    for metrica in metricas_total:
        print(f"\n{metrica.upper()}:")
        print(f"  Média: {df[metrica].mean():.0f}")
        print(f"  Mediana: {df[metrica].median():.0f}")
        print(f"  Desvio Padrão: {df[metrica].std():.0f}")
        print(f"  Mínimo: {df[metrica].min():.0f}")
        print(f"  Máximo: {df[metrica].max():.0f}")

def main():
    """Função principal"""
    print("🎨 Iniciando análise visual das métricas de qualidade de código...")
    print("="*60)
    
    # Carregar dados
    df = carregar_dados()
    if df is None:
        return
    
    # Exibir informações básicas
    print(f"\n📋 Dados carregados:")
    print(f"   • {len(df)} repositórios analisados")
    print(f"   • {len(df.columns)} métricas por repositório")
    print(f"   • Colunas: {', '.join(df.columns)}")
    
    # Gerar estatísticas descritivas
    gerar_estatisticas_descritivas(df)
    
    print("\n🎯 Gerando visualizações...")
    print("-" * 30)
    
    # Criar todos os gráficos
    criar_histogramas(df)
    criar_boxplots(df)
    criar_scatter_plots(df)
    criar_heatmap_correlacao(df)
    criar_grafico_barras_repositorios(df)
    
    print("\n✅ Análise visual concluída!")
    print("📁 Arquivos gerados na pasta 'graficos':")
    print("   • graficos/histogramas_metricas_medianas.png")
    print("   • graficos/histogramas_metricas_totais.png")
    print("   • graficos/boxplots_metricas_medianas.png")
    print("   • graficos/boxplots_metricas_totais.png")
    print("   • graficos/scatter_plots_medianas.png")
    print("   • graficos/scatter_plots_totais.png")
    print("   • graficos/heatmap_correlacao.png")
    if len(df) <= 20:
        print("   • graficos/barras_repositorios.png")
    else:
        print("   • graficos/barras_top20_repositorios.png")
        print("   • graficos/barras_bottom20_repositorios.png")
    print("\n🔍 Use esses gráficos para análise exploratória dos dados!")
    print("📂 Todos os gráficos estão organizados na pasta 'graficos' para fácil acesso.")

if __name__ == '__main__':
    main()