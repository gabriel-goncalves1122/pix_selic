import requests
import json

def fetch_dataset_titles():
    # URL base da API do CKAN do Portal de Dados Abertos do BCB
    base_url = "https://dadosabertos.bcb.gov.br/api/3/action/package_search"
    
    # Parâmetros da busca (filtrando pela licença odc-odbl, conforme o link fornecido)
    params = {
        'q': 'license_id:odc-odbl',
        'rows': 100, # Quantidade de resultados por página
        'start': 0   # Paginação
    }
    
    titles = []
    
    import time
    
    while True:
        print(f"Buscando resultados a partir do índice {params['start']}...")
        try:
            response = requests.get(base_url, params=params)
        except requests.RequestException as e:
            print(f"Erro de conexão: {e}")
            break
        
        if response.status_code != 200:
            print(f"Erro ao acessar a API: {response.status_code}")
            print("Aguardando 5 segundos antes de tentar novamente...")
            time.sleep(5)
            continue
            
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            print("A resposta não veio no formato JSON. Provavelmente limite de taxa (rate-limit).")
            print("Aguardando 10 segundos antes de tentar novamente...")
            time.sleep(10)
            continue
        
        if not data.get('success'):
            print("A requisição não foi bem-sucedida.")
            break
            
        results = data['result']['results']
        
        if not results:
            break
            
        for dataset in results:
            titles.append(dataset.get('title'))
            
        params['start'] += params['rows']
        time.sleep(0.5) # Pausa leve para não sobrecarregar a API
        
    return titles

if __name__ == "__main__":
    print("Iniciando a extração dos títulos dos datasets...")
    dataset_titles = fetch_dataset_titles()
    
    file_path = "datasets_bcb.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("--- Títulos Encontrados ---\n")
        for i, title in enumerate(dataset_titles, 1):
            f.write(f"{i}. {title}\n")
        f.write(f"\nTotal de datasets encontrados com essa licença: {len(dataset_titles)}\n")
            
    print(f"\nExtração finalizada! Os dados foram salvos no arquivo: {file_path}")
    print(f"Total de datasets encontrados: {len(dataset_titles)}")
