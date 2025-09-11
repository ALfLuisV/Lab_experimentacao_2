import requests
import json
from datetime import datetime
import time # Importamos a biblioteca time

# Substitua pelo seu Token de Acesso Pessoal do GitHub
GITHUB_TOKEN = ""

# Endpoint da API GraphQL do GitHub
URL = "https://api.github.com/graphql"

# A query GraphQL (sem alteração)
QUERY = """
query TopJavaRepositories($cursor: String) {
  search(query: "language:Java sort:stars stars:2000..4999", type: REPOSITORY, first: 100, after: $cursor) {
    pageInfo {
      endCursor
      hasNextPage
    }
    edges {
      node {
        ... on Repository {
          nameWithOwner
          stargazerCount
          createdAt
          releases {
            totalCount
          }
        }
      }
    }
  }
}
"""

def run_query(query, variables):
    """
    Função para executar a query GraphQL, agora com retentativas e timeout.
    """
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    max_retries = 5
    base_wait_time = 5 # segundos

    for attempt in range(max_retries):
        try:
            # Adicionado um timeout de 30 segundos na requisição
            request = requests.post(URL, json={'query': query, 'variables': variables}, headers=headers, timeout=30)
            
            # Se o status for 502, tentamos novamente
            if request.status_code == 502:
                print(f"  -> Tentativa {attempt + 1}/{max_retries}: Recebido erro 502 (Bad Gateway). Tentando novamente em {base_wait_time * (attempt + 1)}s...")
                time.sleep(base_wait_time * (attempt + 1)) # Espera aumenta a cada tentativa
                continue

            request.raise_for_status() # Lança um erro para outros status HTTP ruins (4xx, 5xx)
            
            return request.json()

        except requests.exceptions.RequestException as e:
            print(f"  -> Tentativa {attempt + 1}/{max_retries}: Ocorreu um erro de requisição: {e}. Tentando novamente em {base_wait_time * (attempt + 1)}s...")
            time.sleep(base_wait_time * (attempt + 1))
    
    # Se todas as tentativas falharem
    raise Exception(f"Query falhou após {max_retries} tentativas.")


# O resto do script (calculate_age, get_top_1000_java_repos, etc.) permanece o mesmo
def calculate_age(created_at_str):
    created_at_date = datetime.strptime(created_at_str, "%Y-%m-%dT%H:%M:%SZ")
    today = datetime.now()
    age = today.year - created_at_date.year - ((today.month, today.day) < (created_at_date.month, created_at_date.day))
    return age

def get_top_1000_java_repos():
    all_repos = []
    cursor = None
    
    print("Iniciando a coleta de dados do GitHub...")
    
    for i in range(10):
        print(f"Buscando página {i + 1}/10...")
        variables = {"cursor": cursor}
        
        try:
            result = run_query(QUERY, variables)
        except Exception as e:
            print(f"Erro fatal ao buscar a página {i + 1}: {e}")
            print("O script será interrompido. Os dados coletados até agora estão na variável 'all_repos'.")
            break
        
        if "errors" in result:
            print("Erro na API:", result["errors"])
            break

        data = result["data"]["search"]
        
        for edge in data["edges"]:
            repo_node = edge["node"]
            age_in_years = calculate_age(repo_node["createdAt"])
            
            repo_data = {
                "name": repo_node["nameWithOwner"],
                "stars": repo_node["stargazerCount"],
                "releases": repo_node["releases"]["totalCount"],
                "age_years": age_in_years,
                "created_at": repo_node["createdAt"]
            }
            all_repos.append(repo_data)

        if data["pageInfo"]["hasNextPage"]:
            cursor = data["pageInfo"]["endCursor"]
        else:
            break
            
    print(f"\nColeta finalizada. Total de {len(all_repos)} repositórios encontrados.")
    return all_repos

# --- Execução Principal ---
if __name__ == "__main__":
    if GITHUB_TOKEN == "SEU_TOKEN_AQUI":
        print("ERRO: Por favor, defina seu GITHUB_TOKEN no script.")
    else:
        repositories = get_top_1000_java_repos()
        with open("repo.json", "w", encoding="utf-8") as f:
            json.dump(repositories, f, ensure_ascii=False, indent=2)
        print(f"\n--- Exemplo dos primeiros {len(repositories[:5])} resultados ---")
        for repo in repositories[:5]:
            print(json.dumps(repo, indent=2))