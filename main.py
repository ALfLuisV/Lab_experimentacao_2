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

        class_metrics_file = os.path.join(ck_output_path, 'class.csv')
        
        if not os.path.exists(class_metrics_file):
            print(f"  AVISO: CK não gerou 'class.csv' para {repo_name}. Pulando.")
            return None

        df_class = pd.read_csv(class_metrics_file)

        if df_class.empty:
            print(f"  AVISO: 'class.csv' está vazio para {repo_name}. Pulando.")
            return None
            
        metrics = {
            'repo_name': repo_name,
            'cbo_mean': df_class['cbo'].mean(),
            'dit_mean': df_class['dit'].mean(),
            'lcom_mean': df_class['lcom'].mean()
        }
        
        print(f"  Métricas calculadas para {repo_name}: CBO={metrics['cbo_mean']:.2f}, DIT={metrics['dit_mean']:.2f}, LCOM={metrics['lcom_mean']:.2f}")
        return metrics

    except subprocess.CalledProcessError as e:
        print(f"  ERRO ao processar {repo_name}: {e.stderr}")
        return None
    except FileNotFoundError:
        print(f"  ERRO: 'class.csv' não encontrado para {repo_name}. Pode não ser um projeto Java válido.")
        return None
    finally:
        if os.path.exists(repo_clone_path):
            shutil.rmtree(repo_clone_path, onerror=remove_readonly)


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
        f.write('repo_name,cbo_mean,dit_mean,lcom_mean\n')

    total_repos = len(repos_df)
    print(f"Iniciando análise de {total_repos} repositórios...")
    indexTtotal = 0;
    for index, row in repos_df.iterrows():
        if indexTtotal  < 10:
            repo_name = row['name']
            print(f"\n--- Processando repositório {index + 1}/{total_repos}: {repo_name} ---")
            
            metrics_result = analisar_repositorio(repo_name)
            if metrics_result:
                with open(OUTPUT_CSV_FILE, 'a', newline='') as f:
                    f.write(f"{metrics_result['repo_name']},{metrics_result['cbo_mean']},{metrics_result['dit_mean']},{metrics_result['lcom_mean']}\n")
            indexTtotal = indexTtotal + 1

    print(f"\nAnálise concluída! Resultados salvos em '{OUTPUT_CSV_FILE}'.")