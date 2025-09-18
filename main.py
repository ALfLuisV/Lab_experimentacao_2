import os
import subprocess
import shutil
import pandas as pd
import stat
import time 
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import logging

# Configuração de logging para monitorar threads
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ck_multithread.log'),
        logging.StreamHandler()
    ]
)

CK_JAR_PATH = 'ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar'; 
INPUT_JSON_FILE = 'repositorios_faltantes.json'
OUTPUT_CSV_FILE = 'resultados_metricas_faltante.csv'
CLONE_DIR_BASE = 'clones'
CK_OUTPUT_DIR_BASE = 'ck_output'

# Locks para thread-safety
file_write_lock = Lock()
directory_creation_lock = Lock()
cleanup_lock = Lock()

# Contador thread-safe para progresso
class ThreadSafeCounter:
    def __init__(self):
        self._value = 0
        self._lock = Lock()
    
    def increment(self):
        with self._lock:
            self._value += 1
            return self._value
    
    @property
    def value(self):
        with self._lock:
            return self._value

progress_counter = ThreadSafeCounter()

def analisar_repositorio(repo_info):
    """
    Função thread-safe para analisar um repositório usando CK.
    
    Args:
        repo_info: Tupla contendo (index, repo_name, total_repos)
    
    Returns:
        dict: Métricas calculadas ou None em caso de erro
    """
    index, repo_name, total_repos = repo_info
    thread_name = threading.current_thread().name
    
    try:
        logging.info(f"[{thread_name}] Iniciando análise do repositório {index + 1}/{total_repos}: {repo_name}")
        
        clone_url = f'https://github.com/{repo_name}.git'
        repo_safe_name = repo_name.replace('/', '_')
        repo_clone_path = os.path.join(CLONE_DIR_BASE, repo_safe_name)
        ck_output_path = os.path.join(CK_OUTPUT_DIR_BASE, repo_safe_name)

        # Thread-safe directory creation
        with directory_creation_lock:
            os.makedirs(ck_output_path, exist_ok=True)
            os.makedirs(CLONE_DIR_BASE, exist_ok=True)

        # Clonagem do repositório
        logging.info(f"[{thread_name}] Clonando {repo_name}...")
        clone_result = subprocess.run(
            ['git', 'clone', '--depth', '1', clone_url, repo_clone_path],
            check=True, capture_output=True, text=True, timeout=300  # 5 minutos timeout
        )

        # Execução do CK
        logging.info(f"[{thread_name}] Executando CK em {repo_name}...")
        ck_result = subprocess.run(
            ['java', '-jar', CK_JAR_PATH, repo_clone_path, 'false', '0', 'false', ck_output_path],
            check=True, capture_output=True, text=True, timeout=600  # 10 minutos timeout
        )

        # Processamento dos resultados
        class_metrics_file = os.path.join(CK_OUTPUT_DIR_BASE, f"{repo_safe_name}class.csv")
        logging.info(f"[{thread_name}] Verificando arquivo de métricas: {class_metrics_file}")

        if not os.path.exists(class_metrics_file):
            logging.warning(f"[{thread_name}] Arquivo 'class.csv' não encontrado para {repo_name}. Pode não ser um projeto Java válido.")
            return None

        df_class = pd.read_csv(class_metrics_file)

        if df_class.empty:
            logging.warning(f"[{thread_name}] Arquivo 'class.csv' está vazio para {repo_name}. Pulando.")
            return None
            
        metrics = {
            'repo_name': repo_name,
            'cbo_mean': df_class['cbo'].mean(),
            'dit_mean': df_class['dit'].mean(),
            'lcom_mean': df_class['lcom'].mean(),
            'cbo_total': df_class['cbo'].sum(),
            'dit_total': df_class['dit'].sum(),
            'lcom_total': df_class['lcom'].sum(),
            'thread_name': thread_name
        }
        
        logging.info(f"[{thread_name}] Métricas calculadas para {repo_name}: "
                    f"CBO_mean={metrics['cbo_mean']:.2f}, DIT_mean={metrics['dit_mean']:.2f}, "
                    f"LCOM_mean={metrics['lcom_mean']:.2f}")
        
        # Atualizar contador de progresso
        current_progress = progress_counter.increment()
        logging.info(f"[{thread_name}] Progresso: {current_progress}/{total_repos} repositórios processados")
        
        return metrics

    except subprocess.TimeoutExpired as e:
        logging.error(f"[{thread_name}] Timeout ao processar {repo_name}: {str(e)}")
        return None
    except subprocess.CalledProcessError as e:
        logging.error(f"[{thread_name}] Erro de processo ao processar {repo_name}: {e.stderr}")
        return None
    except Exception as e:
        logging.error(f"[{thread_name}] Erro inesperado ao processar {repo_name}: {str(e)}")
        return None
    finally:
        # Cleanup thread-safe
        cleanup_repository_files(repo_name, repo_clone_path, thread_name)

def cleanup_repository_files(repo_name, repo_clone_path, thread_name):
    """
    Função thread-safe para limpeza de arquivos temporários.
    """
    with cleanup_lock:
        try:
            # Pequeno delay para evitar conflitos de I/O
            time.sleep(1)
            
            # Remove o repositório clonado
            if os.path.exists(repo_clone_path):
                shutil.rmtree(repo_clone_path, onexc=remove_readonly)
                logging.info(f"[{thread_name}] Repositório clonado removido: {repo_clone_path}")
            
            # Remove os arquivos CSV criados no diretório de saída do CK
            repo_safe_name = repo_name.replace('/', '_')
            csv_files = [
                os.path.join(CK_OUTPUT_DIR_BASE, f"{repo_safe_name}class.csv"),
                os.path.join(CK_OUTPUT_DIR_BASE, f"{repo_safe_name}method.csv")
            ]
            
            for csv_file in csv_files:
                if os.path.exists(csv_file):
                    os.remove(csv_file)
                    logging.debug(f"[{thread_name}] Arquivo CSV removido: {csv_file}")
            
            # Remove o diretório específico do repositório se estiver vazio
            ck_output_path = os.path.join(CK_OUTPUT_DIR_BASE, repo_safe_name)
            if os.path.exists(ck_output_path) and not os.listdir(ck_output_path):
                os.rmdir(ck_output_path)
                logging.debug(f"[{thread_name}] Diretório vazio removido: {ck_output_path}")
                
        except Exception as e:
            logging.error(f"[{thread_name}] Erro durante cleanup de {repo_name}: {str(e)}")

def write_metrics_to_file(metrics_result):
    """
    Função thread-safe para escrever métricas no arquivo CSV.
    """
    if metrics_result:
        with file_write_lock:
            try:
                with open(OUTPUT_CSV_FILE, 'a', newline='', encoding='utf-8') as f:
                    f.write(f"{metrics_result['repo_name']},{metrics_result['cbo_mean']:.6f},"
                           f"{metrics_result['dit_mean']:.6f},{metrics_result['lcom_mean']:.6f},"
                           f"{metrics_result['cbo_total']:.0f},{metrics_result['dit_total']:.0f},"
                           f"{metrics_result['lcom_total']:.0f}\n")
                logging.info(f"Métricas salvas para {metrics_result['repo_name']} por {metrics_result['thread_name']}")
            except Exception as e:
                logging.error(f"Erro ao escrever métricas para {metrics_result['repo_name']}: {str(e)}")

def remove_readonly(func, path, excinfo):
    """Função auxiliar para remover arquivos readonly no Windows."""
    os.chmod(path, stat.S_IWRITE)
    func(path)

def process_repositories_multithread(repos_df, max_workers=4):
    """
    Processa repositórios usando múltiplas threads.
    
    Args:
        repos_df: DataFrame com os repositórios
        max_workers: Número máximo de threads trabalhadoras
    """
    total_repos = min(len(repos_df), 1000)  # Limita a 1000 como no código original
    
    # Preparar dados para processamento
    repo_tasks = []
    for index, row in repos_df.iterrows():
        if index < 1000:  # Mantém o limite original
            repo_name = row['name']
            repo_tasks.append((index, repo_name, total_repos))
    
    logging.info(f"Iniciando análise multithread de {len(repo_tasks)} repositórios com {max_workers} workers...")
    
    # Inicializar arquivo de saída
    with open(OUTPUT_CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        f.write('repo_name,cbo_mean,dit_mean,lcom_mean,cbo_total,dit_total,lcom_total\n')
    
    # Executar processamento multithread
    with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="CK-Worker") as executor:
        # Submeter todas as tarefas
        future_to_repo = {executor.submit(analisar_repositorio, repo_info): repo_info 
                         for repo_info in repo_tasks}
        
        # Processar resultados conforme completam
        for future in as_completed(future_to_repo):
            repo_info = future_to_repo[future]
            try:
                metrics_result = future.result(timeout=900)  # 15 minutos timeout por tarefa
                write_metrics_to_file(metrics_result)
            except Exception as e:
                repo_name = repo_info[1]
                logging.error(f"Erro ao processar {repo_name}: {str(e)}")

if __name__ == '__main__':
    try:
        # Carregar dados dos repositórios
        repos_df = pd.read_json(INPUT_JSON_FILE, encoding='utf-8')
    except FileNotFoundError:
        print(f"ERRO: Arquivo de entrada json não encontrado!")
        exit()

    if 'name' not in repos_df.columns:
        print(f"ERRO: O arquivo json deve conter uma coluna chamada 'name'.")
        exit()

    # Criar diretórios necessários
    os.makedirs(CLONE_DIR_BASE, exist_ok=True)
    os.makedirs(CK_OUTPUT_DIR_BASE, exist_ok=True)
    
    # Determinar número de workers baseado no número de CPUs
    import multiprocessing
    max_workers = min(multiprocessing.cpu_count(), 6)  # Máximo de 6 threads para evitar sobrecarga
    
    logging.info(f"Sistema detectou {multiprocessing.cpu_count()} CPUs. Usando {max_workers} workers.")
    
    start_time = time.time()
    
    # Processar repositórios com multithread
    process_repositories_multithread(repos_df, max_workers)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    logging.info(f"Análise concluída! Resultados salvos em '{OUTPUT_CSV_FILE}'.")
    logging.info(f"Tempo total de execução: {execution_time:.2f} segundos ({execution_time/60:.2f} minutos)")
    logging.info(f"Repositórios processados: {progress_counter.value}")
    
    print(f"\nAnálise multithread concluída!")
    print(f"Resultados salvos em '{OUTPUT_CSV_FILE}'")
    print(f"Tempo de execução: {execution_time:.2f} segundos")
    print(f"Repositórios processados: {progress_counter.value}")