import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import json
from matplotlib.patches import Rectangle
from pathlib import Path

# Configurações do Seaborn
sns.set_style("whitegrid")
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

def carregar_dados():
    """Carrega e combina os dados do CSV e JSON"""
    try:
        # Carregar dados de métricas de qualidade
        df_metricas = pd.read_csv('resultados_metricas.csv')
        print(f"Métricas de qualidade carregadas: {len(df_metricas)} repositórios")
        
        # Carregar dados do repositório (JSON)
        with open('repo.json', 'r', encoding='utf-8') as f:
            repos_data = json.load(f)
        
        # Converter para DataFrame
        df_repos = pd.DataFrame(repos_data)
        print(f"Dados de repositórios carregados: {len(df_repos)} repositórios")
        
        # Combinar os dados usando o nome do repositório
        df_combined = pd.merge(df_metricas, df_repos, left_on='repo_name', right_on='name', how='inner')
        print(f"Dados combinados com sucesso: {len(df_combined)} repositórios")
        
        return df_combined
    except FileNotFoundError as e:
        print(f"ERRO: Arquivo não encontrado - {e}")
        return None
    except Exception as e:
        print(f"ERRO ao carregar dados: {e}")
        return None

def criar_histogramas_completos(df):
    """Cria histogramas para todas as métricas"""
    Path('graficos').mkdir(exist_ok=True)
    
    # Histogramas para métricas de qualidade (médias)
    fig, axes = plt.subplots(2, 3, figsize=(24, 16))
    fig.suptitle('Distribuição de Todas as Métricas', fontsize=20, fontweight='bold')
    
    # Métricas de qualidade
    metricas_qualidade = ['cbo_mean', 'dit_mean', 'lcom_mean']
    titulos_qualidade = ['CBO (Média)', 'DIT (Média)', 'LCOM (Média)']
    
    for i, (metrica, titulo) in enumerate(zip(metricas_qualidade, titulos_qualidade)):
        bins = min(30, max(10, len(df) // 20))
        sns.histplot(data=df, x=metrica, bins=bins, kde=True, ax=axes[0, i])
        axes[0, i].set_title(f'{titulo}', fontweight='bold', fontsize=14)
        axes[0, i].set_xlabel(f'{titulo}', fontsize=12)
        axes[0, i].set_ylabel('Frequência', fontsize=12)
    
    # Métricas do repositório
    metricas_repo = ['stars', 'releases', 'age_years']
    titulos_repo = ['Stars', 'Releases', 'Idade (Anos)']
    
    for i, (metrica, titulo) in enumerate(zip(metricas_repo, titulos_repo)):
        bins = min(30, max(10, len(df) // 20))
        if metrica == 'stars':
            # Usar escala log para stars devido à grande variação
            data_log = np.log1p(df[metrica])
            sns.histplot(data=data_log, bins=bins, kde=True, ax=axes[1, i])
            axes[1, i].set_xlabel(f'{titulo} (Log Scale)', fontsize=12)
        else:
            sns.histplot(data=df, x=metrica, bins=bins, kde=True, ax=axes[1, i])
            axes[1, i].set_xlabel(f'{titulo}', fontsize=12)
        
        axes[1, i].set_title(f'{titulo}', fontweight='bold', fontsize=14)
        axes[1, i].set_ylabel('Frequência', fontsize=12)
    
    plt.tight_layout()
    plt.savefig('graficos/histogramas_todas_metricas.png', dpi=600, bbox_inches='tight')
    plt.close()
    print("✓ Histogramas completos salvos como 'graficos/histogramas_todas_metricas.png'")

def criar_boxplots_completos(df):
    """Cria boxplots para todas as métricas"""
    fig, axes = plt.subplots(2, 3, figsize=(24, 16))
    fig.suptitle('Boxplots de Todas as Métricas', fontsize=20, fontweight='bold')
    
    # Métricas de qualidade
    metricas_qualidade = ['cbo_mean', 'dit_mean', 'lcom_mean']
    titulos_qualidade = ['CBO (Média)', 'DIT (Média)', 'LCOM (Média)']
    
    for i, (metrica, titulo) in enumerate(zip(metricas_qualidade, titulos_qualidade)):
        sns.boxplot(data=df, y=metrica, ax=axes[0, i], palette='Set2')
        axes[0, i].set_title(titulo, fontweight='bold', fontsize=14)
        axes[0, i].set_ylabel('Valor', fontsize=12)
        mean_val = df[metrica].mean()
        axes[0, i].text(0.02, 0.98, f'Média: {mean_val:.2f}', transform=axes[0, i].transAxes, 
                       verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Métricas do repositório
    metricas_repo = ['stars', 'releases', 'age_years']
    titulos_repo = ['Stars', 'Releases', 'Idade (Anos)']
    
    for i, (metrica, titulo) in enumerate(zip(metricas_repo, titulos_repo)):
        sns.boxplot(data=df, y=metrica, ax=axes[1, i], palette='Set1')
        axes[1, i].set_title(titulo, fontweight='bold', fontsize=14)
        
        if metrica == 'stars':
            axes[1, i].set_yscale('log')
            axes[1, i].set_ylabel('Valor (Log Scale)', fontsize=12)
        else:
            axes[1, i].set_ylabel('Valor', fontsize=12)
        
        mean_val = df[metrica].mean()
        axes[1, i].text(0.02, 0.98, f'Média: {mean_val:.0f}', transform=axes[1, i].transAxes, 
                       verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('graficos/boxplots_todas_metricas.png', dpi=600, bbox_inches='tight')
    plt.close()
    print("✓ Boxplots completos salvos como 'graficos/boxplots_todas_metricas.png'")

def criar_matriz_correlacao_completa(df):
    """Cria matriz de correlação entre todas as métricas"""
    # Selecionar todas as métricas numéricas
    metricas = ['cbo_mean', 'dit_mean', 'lcom_mean', 'cbo_total', 'dit_total', 'lcom_total', 
                'stars', 'releases', 'age_years']
    
    correlation_matrix = df[metricas].corr()
    
    plt.figure(figsize=(14, 12))
    
    # Criar heatmap
    sns.heatmap(correlation_matrix, 
                annot=True, 
                cmap='RdBu_r', 
                center=0,
                square=True, 
                fmt='.3f', 
                cbar_kws={'shrink': 0.8, 'label': 'Coeficiente de Correlação'},
                annot_kws={'size': 10, 'weight': 'bold'},
                linewidths=0.5)
    
    plt.title('Matriz de Correlação Completa - Todas as Métricas', 
              fontsize=18, fontweight='bold', pad=20)
    
    # Melhorar labels dos eixos
    labels = ['CBO\n(Média)', 'DIT\n(Média)', 'LCOM\n(Média)',
              'CBO\n(Total)', 'DIT\n(Total)', 'LCOM\n(Total)',
              'Stars', 'Releases', 'Idade\n(Anos)']
    plt.xticks(range(len(labels)), labels, rotation=45, ha='right', fontsize=11)
    plt.yticks(range(len(labels)), labels, rotation=0, fontsize=11)
    
    plt.tight_layout()
    plt.savefig('graficos/matriz_correlacao_completa.png', dpi=600, bbox_inches='tight')
    plt.close()
    print("✓ Matriz de correlação completa salva como 'graficos/matriz_correlacao_completa.png'")

def criar_scatter_plots_correlacoes(df):
    """Cria scatter plots para correlações interessantes"""
    # Correlações entre métricas de qualidade e características do repositório
    fig, axes = plt.subplots(2, 3, figsize=(24, 16))
    fig.suptitle('Correlações entre Métricas de Qualidade e Características do Repositório', 
                 fontsize=18, fontweight='bold')
    
    correlacoes = [
        ('stars', 'cbo_mean', 'Stars vs CBO (Média)'),
        ('stars', 'dit_mean', 'Stars vs DIT (Média)'),
        ('stars', 'lcom_mean', 'Stars vs LCOM (Média)'),
        ('age_years', 'cbo_mean', 'Idade vs CBO (Média)'),
        ('releases', 'cbo_mean', 'Releases vs CBO (Média)'),
        ('age_years', 'releases', 'Idade vs Releases')
    ]
    
    for i, (x_col, y_col, titulo) in enumerate(correlacoes):
        row = i // 3
        col = i % 3
        
        sns.scatterplot(data=df, x=x_col, y=y_col, ax=axes[row, col], alpha=0.7, s=60)
        axes[row, col].set_title(titulo, fontweight='bold', fontsize=14)
        axes[row, col].set_xlabel(x_col.replace('_', ' ').title(), fontsize=12)
        axes[row, col].set_ylabel(y_col.replace('_', ' ').title(), fontsize=12)
        
        # Usar escala log para stars se necessário
        if x_col == 'stars':
            axes[row, col].set_xscale('log')
        
        # Adicionar linha de tendência
        if len(df) > 1:
            z = np.polyfit(df[x_col], df[y_col], 1)
            p = np.poly1d(z)
            axes[row, col].plot(df[x_col], p(df[x_col]), "r--", alpha=0.8, linewidth=2)
        
        # Calcular e mostrar correlação
        corr = df[x_col].corr(df[y_col])
        axes[row, col].text(0.05, 0.95, f'r = {corr:.3f}', transform=axes[row, col].transAxes,
                           bbox=dict(boxstyle='round', facecolor='white', alpha=0.9), fontsize=11)
    
    plt.tight_layout()
    plt.savefig('graficos/scatter_correlacoes_qualidade_repo.png', dpi=600, bbox_inches='tight')
    plt.close()
    print("✓ Scatter plots de correlações salvos como 'graficos/scatter_correlacoes_qualidade_repo.png'")

def criar_grafico_popularidade_qualidade(df):
    """Cria gráfico relacionando popularidade (stars) com qualidade de código"""
    # Criar categorias de popularidade
    df['categoria_stars'] = pd.cut(df['stars'], 
                                   bins=[0, 1000, 10000, 50000, float('inf')],
                                   labels=['Baixa (<1K)', 'Média (1K-10K)', 'Alta (10K-50K)', 'Muito Alta (>50K)'])
    
    fig, axes = plt.subplots(1, 3, figsize=(24, 8))
    fig.suptitle('Qualidade de Código por Categoria de Popularidade (Stars)', 
                 fontsize=18, fontweight='bold')
    
    metricas = ['cbo_mean', 'dit_mean', 'lcom_mean']
    titulos = ['CBO (Média)', 'DIT (Média)', 'LCOM (Média)']
    
    for i, (metrica, titulo) in enumerate(zip(metricas, titulos)):
        sns.boxplot(data=df, x='categoria_stars', y=metrica, ax=axes[i], palette='viridis')
        axes[i].set_title(titulo, fontweight='bold', fontsize=14)
        axes[i].set_xlabel('Categoria de Popularidade', fontsize=12)
        axes[i].set_ylabel('Valor da Métrica', fontsize=12)
        axes[i].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('graficos/qualidade_por_popularidade.png', dpi=600, bbox_inches='tight')
    plt.close()
    print("✓ Gráfico de qualidade por popularidade salvo como 'graficos/qualidade_por_popularidade.png'")

def criar_grafico_idade_metricas(df):
    """Cria gráfico relacionando idade do repositório com métricas"""
    # Criar categorias de idade
    df['categoria_idade'] = pd.cut(df['age_years'], 
                                   bins=[0, 2, 5, 10, float('inf')],
                                   labels=['Novo (0-2 anos)', 'Jovem (2-5 anos)', 'Maduro (5-10 anos)', 'Antigo (>10 anos)'])
    
    fig, axes = plt.subplots(2, 2, figsize=(20, 16))
    fig.suptitle('Métricas por Categoria de Idade do Repositório', 
                 fontsize=18, fontweight='bold')
    
    # Métricas de qualidade por idade
    sns.boxplot(data=df, x='categoria_idade', y='cbo_mean', ax=axes[0, 0], palette='plasma')
    axes[0, 0].set_title('CBO (Média) por Idade', fontweight='bold', fontsize=14)
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    sns.boxplot(data=df, x='categoria_idade', y='dit_mean', ax=axes[0, 1], palette='plasma')
    axes[0, 1].set_title('DIT (Média) por Idade', fontweight='bold', fontsize=14)
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    # Stars e releases por idade
    sns.boxplot(data=df, x='categoria_idade', y='stars', ax=axes[1, 0], palette='viridis')
    axes[1, 0].set_title('Stars por Idade', fontweight='bold', fontsize=14)
    axes[1, 0].set_yscale('log')
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    sns.boxplot(data=df, x='categoria_idade', y='releases', ax=axes[1, 1], palette='viridis')
    axes[1, 1].set_title('Releases por Idade', fontweight='bold', fontsize=14)
    axes[1, 1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('graficos/metricas_por_idade.png', dpi=600, bbox_inches='tight')
    plt.close()
    print("✓ Gráfico de métricas por idade salvo como 'graficos/metricas_por_idade.png'")

def criar_ranking_repositorios(df):
    """Cria ranking dos repositórios considerando múltiplas métricas"""
    # Calcular score composto (normalizado)
    df_norm = df.copy()
    
    # Normalizar métricas (0-1)
    metricas_para_normalizar = ['stars', 'releases', 'age_years', 'cbo_mean', 'dit_mean', 'lcom_mean']
    
    for metrica in metricas_para_normalizar:
        min_val = df_norm[metrica].min()
        max_val = df_norm[metrica].max()
        if max_val > min_val:
            df_norm[f'{metrica}_norm'] = (df_norm[metrica] - min_val) / (max_val - min_val)
        else:
            df_norm[f'{metrica}_norm'] = 0
    
    # Score de popularidade (stars + releases)
    df_norm['score_popularidade'] = (df_norm['stars_norm'] + df_norm['releases_norm']) / 2
    
    # Score de qualidade (inverso das métricas de qualidade - menores valores são melhores)
    df_norm['score_qualidade'] = (3 - (df_norm['cbo_mean_norm'] + df_norm['dit_mean_norm'] + df_norm['lcom_mean_norm'])) / 3
    
    # Top 20 por popularidade
    top_popularidade = df_norm.nlargest(20, 'score_popularidade')
    
    fig, axes = plt.subplots(1, 2, figsize=(24, 12))
    fig.suptitle('Ranking de Repositórios', fontsize=18, fontweight='bold')
    
    # Gráfico de popularidade
    sns.barplot(data=top_popularidade, y='repo_name', x='score_popularidade', ax=axes[0], palette='viridis')
    axes[0].set_title('Top 20 - Score de Popularidade', fontweight='bold', fontsize=14)
    axes[0].set_xlabel('Score de Popularidade (0-1)', fontsize=12)
    axes[0].set_ylabel('Repositório', fontsize=12)
    
    # Top 20 por qualidade
    top_qualidade = df_norm.nlargest(20, 'score_qualidade')
    sns.barplot(data=top_qualidade, y='repo_name', x='score_qualidade', ax=axes[1], palette='plasma')
    axes[1].set_title('Top 20 - Score de Qualidade', fontweight='bold', fontsize=14)
    axes[1].set_xlabel('Score de Qualidade (0-1)', fontsize=12)
    axes[1].set_ylabel('Repositório', fontsize=12)
    
    plt.tight_layout()
    plt.savefig('graficos/ranking_repositorios.png', dpi=600, bbox_inches='tight')
    plt.close()
    print("✓ Ranking de repositórios salvo como 'graficos/ranking_repositorios.png'")

def gerar_estatisticas_completas(df):
    """Gera estatísticas descritivas completas"""
    print("\n" + "="*80)
    print("ESTATÍSTICAS DESCRITIVAS COMPLETAS")
    print("="*80)
    
    # Estatísticas das métricas de qualidade
    print("\n📊 MÉTRICAS DE QUALIDADE DE CÓDIGO:")
    print("-" * 40)
    metricas_qualidade = ['cbo_total', 'dit_total', 'lcom_total']
    for metrica in metricas_qualidade:
        print(f"\n{metrica.upper()}:")
        print(f"  Média: {df[metrica].mean():.3f}")
        print(f"  Mediana: {df[metrica].median():.3f}")
        print(f"  Desvio Padrão: {df[metrica].std():.3f}")
        print(f"  Mínimo: {df[metrica].min():.3f}")
        print(f"  Máximo: {df[metrica].max():.3f}")
    
    # Estatísticas das métricas do repositório
    print("\n🌟 MÉTRICAS DO REPOSITÓRIO:")
    print("-" * 40)
    metricas_repo = ['stars', 'releases', 'age_years']
    for metrica in metricas_repo:
        print(f"\n{metrica.upper()}:")
        print(f"  Média: {df[metrica].mean():.0f}")
        print(f"  Mediana: {df[metrica].median():.0f}")
        print(f"  Desvio Padrão: {df[metrica].std():.0f}")
        print(f"  Mínimo: {df[metrica].min():.0f}")
        print(f"  Máximo: {df[metrica].max():.0f}")
    
    # Correlações mais interessantes
    print("\n🔗 CORRELAÇÕES MAIS SIGNIFICATIVAS:")
    print("-" * 40)
    correlacoes_interesse = [
        ('stars', 'cbo_mean'),
        ('stars', 'releases'),
        ('age_years', 'releases'),
        ('age_years', 'cbo_mean'),
        ('releases', 'cbo_mean')
    ]
    
    for metrica1, metrica2 in correlacoes_interesse:
        corr = df[metrica1].corr(df[metrica2])
        print(f"  {metrica1} vs {metrica2}: {corr:.3f}")

def main():
    """Função principal"""
    print("🎨 Iniciando análise visual completa das métricas...")
    print("="*80)
    
    # Carregar dados combinados
    df = carregar_dados()
    if df is None:
        return
    
    # Exibir informações básicas
    print(f"\n📋 Dados combinados carregados:")
    print(f"   • {len(df)} repositórios analisados")
    print(f"   • {len(df.columns)} colunas por repositório")
    print(f"   • Métricas disponíveis: {', '.join(df.columns)}")
    
    # Gerar estatísticas descritivas
    gerar_estatisticas_completas(df)
    
    print("\n🎯 Gerando visualizações completas...")
    print("-" * 50)
    
    # Criar todos os gráficos
    criar_histogramas_completos(df)
    criar_boxplots_completos(df)
    criar_matriz_correlacao_completa(df)
    criar_scatter_plots_correlacoes(df)
    criar_grafico_popularidade_qualidade(df)
    criar_grafico_idade_metricas(df)
    criar_ranking_repositorios(df)
    
    print("\n✅ Análise visual completa concluída!")
    print("📁 Novos arquivos gerados na pasta 'graficos':")
    print("   • graficos/histogramas_todas_metricas.png")
    print("   • graficos/boxplots_todas_metricas.png")
    print("   • graficos/matriz_correlacao_completa.png")
    print("   • graficos/scatter_correlacoes_qualidade_repo.png")
    print("   • graficos/qualidade_por_popularidade.png")
    print("   • graficos/metricas_por_idade.png")
    print("   • graficos/ranking_repositorios.png")
    print("\n🔍 Use esses gráficos para análise completa dos dados!")
    print("📊 Agora você tem correlações entre qualidade de código e características dos repositórios!")

if __name__ == '__main__':
    main()