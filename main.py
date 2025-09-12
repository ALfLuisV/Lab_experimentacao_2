import os
import subprocess
import shutil
import pandas as pd
import stat
import time 

CK_JAR_PATH = 'ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar'; 
INPUT_JSON_FILE = 'repo.json'
OUTPUT_CSV_FILE = 'resultados_metricas.csv'
CLONE_DIR_BASE = 'clones'
CK_OUTPUT_DIR_BASE = 'ck_output'


def analisar_repositorio(repo_name):
    clone_url = f'https://github.com/{repo_name}.git'
    repo_clone_path = os.path.join(CLONE_DIR_BASE, repo_name.replace('/', '_'))
    ck_output_path = os.path.join(CK_OUTPUT_DIR_BASE, repo_name.replace('/', '_'))

    os.makedirs(ck_output_path, exist_ok=True)

    try:

        print(f"  Clonando {repo_name}...")
        subprocess.run(
            ['git', 'clone', '--depth', '1', clone_url, repo_clone_path],
            check=True, capture_output=True, text=True
        )

        print(f"  Executando CK em {repo_name}...")
        subprocess.run(
            ['java', '-jar', CK_JAR_PATH, repo_clone_path, 'false', '0', 'false', ck_output_path],
            check=True, capture_output=True, text=True
        )

        # O CK gera os arquivos diretamente no diretório base com nome concatenado
        class_metrics_file = os.path.join(CK_OUTPUT_DIR_BASE, f"{repo_name.replace('/', '_')}class.csv")
        print(f"  Arquivo de métricas de classe: {class_metrics_file}")

        if not os.path.exists(class_metrics_file):
            print(f"  ERRO: 'class.csv' não encontrado para {repo_name}. Pode não ser um projeto Java válido.")
            return None

        df_class = pd.read_csv(class_metrics_file)

        if df_class.empty:
            print(f"  AVISO: 'class.csv' está vazio para {repo_name}. Pulando.")
            return None
            
        metrics = {
            'repo_name': repo_name,
            'cbo_median': df_class['cbo'].median(),
            'dit_median': df_class['dit'].median(),
            'lcom_median': df_class['lcom'].median(),
            'cbo_total': df_class['cbo'].sum(),
            'dit_total': df_class['dit'].sum(),
            'lcom_total': df_class['lcom'].sum()
        }
        
        print(f"  Métricas calculadas para {repo_name}: CBO_median={metrics['cbo_median']:.2f}, DIT_median={metrics['dit_median']:.2f}, LCOM_median={metrics['lcom_median']:.2f}")
        print(f"  Totais: CBO_total={metrics['cbo_total']:.0f}, DIT_total={metrics['dit_total']:.0f}, LCOM_total={metrics['lcom_total']:.0f}")
        return metrics

    except subprocess.CalledProcessError as e:
        print(f"  ERRO ao processar {repo_name}: {e.stderr}")
        return None
    except Exception as e:
        print(f"  ERRO inesperado ao processar {repo_name}: {str(e)}")
        return None
    finally:
        # Remove o repositório clonado
        if os.path.exists(repo_clone_path):
            shutil.rmtree(repo_clone_path, onexc=remove_readonly)
        
        # Remove os arquivos CSV criados no diretório de saída do CK
        csv_files = [
            os.path.join(CK_OUTPUT_DIR_BASE, f"{repo_name.replace('/', '_')}class.csv"),
            os.path.join(CK_OUTPUT_DIR_BASE, f"{repo_name.replace('/', '_')}method.csv")
        ]
        
        for csv_file in csv_files:
            if os.path.exists(csv_file):
                os.remove(csv_file)
                # print(f"  Arquivo removido: {csv_file}")
        
        # Remove o diretório específico do repositório se estiver vazio
        if os.path.exists(ck_output_path) and not os.listdir(ck_output_path):
            os.rmdir(ck_output_path)
            # print(f"  Diretório vazio removido: {ck_output_path}")



def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

if __name__ == '__main__':
    try:
        repos_df = pd.read_json(INPUT_JSON_FILE, encoding='utf-8')
    except FileNotFoundError:
        print(f"ERRO: Arquivo de entrada json não encontrado!")
        exit()

    if 'name' not in repos_df.columns:
        print(f"ERRO: O arquivo json deve conter uma coluna chamada 'name'.")
        exit()

    with open(OUTPUT_CSV_FILE, 'w', newline='') as f:
        f.write('repo_name,cbo_median,dit_median,lcom_median,cbo_total,dit_total,lcom_total\n')

    total_repos = len(repos_df)
    print(f"Iniciando análise de {total_repos} repositórios...")
    indexTtotal = 0
    for index, row in repos_df.iterrows():
        if indexTtotal  < 5:
            repo_name = row['name']
            print(f"\n--- Processando repositório {index + 1}/{total_repos}: {repo_name} ---")
            
            metrics_result = analisar_repositorio(repo_name)
            if metrics_result:
                with open(OUTPUT_CSV_FILE, 'a', newline='') as f:
                    f.write(f"{metrics_result['repo_name']},{metrics_result['cbo_median']},{metrics_result['dit_median']},{metrics_result['lcom_median']},{metrics_result['cbo_total']},{metrics_result['dit_total']},{metrics_result['lcom_total']}\n")
            indexTtotal = indexTtotal + 1

    print(f"\nAnálise concluída! Resultados salvos em '{OUTPUT_CSV_FILE}'.")