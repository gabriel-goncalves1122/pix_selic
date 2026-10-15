import requests
import json
import csv
import re

base_url = 'https://dadosabertos.bcb.gov.br/api/3/action/package_search'
# Buscar até 3000 pacotes para cobrir a maioria (excluindo os milhões de SGS que não têm url Olinda)
# Usando a palavra chave 'olinda' de forma abrangente
params = {'q': 'olinda', 'rows': 2000}
print("Consultando a API do CKAN em busca de serviços Olinda...")

try:
    res = requests.get(base_url, params=params).json()
except Exception as e:
    print(f"Erro ao consultar CKAN: {e}")
    res = {}

olinda_services = {}

if res.get('success'):
    pacotes = res['result']['results']
    print(f"Encontrados {len(pacotes)} pacotes no CKAN que apontam para o Olinda.")
    for pkg in pacotes:
        title = pkg.get('title')
        desc = pkg.get('notes', '')
        if desc:
            desc = desc.replace('\n', ' ').replace('\r', '')[:250] + '...'
        
        # Procurar url olinda
        for r in pkg.get('resources', []):
            url = r.get('url', '')
            if 'olinda.bcb.gov.br/olinda/servico/' in url:
                # Extrair o nome do serviço (o "contexto" da API OData)
                match = re.search(r'servico/([^/]+)/', url)
                if match:
                    servico = match.group(1)
                    # Adiciona se não existir. Alguns pacotes diferentes apontam para o mesmo serviço Olinda
                    if servico not in olinda_services:
                        olinda_services[servico] = {
                            'Servico_Olinda': servico,
                            'Titulo_Contexto': title,
                            'Descricao_Curta': desc,
                            'Documentacao_Swagger': f'https://olinda.bcb.gov.br/olinda/servico/{servico}/versao/v1/swagger-ui3',
                            'Base_OData_URL': f'https://olinda.bcb.gov.br/olinda/servico/{servico}/versao/v1/odata/'
                        }

# Salvando no CSV para o usuário analisar
filename = 'catalogo_olinda_metadados.csv'
with open(filename, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['Servico_Olinda', 'Titulo_Contexto', 'Descricao_Curta', 'Documentacao_Swagger', 'Base_OData_URL'])
    writer.writeheader()
    writer.writerows(olinda_services.values())

print(f"\\nSUCESSO: Foram extraídos os metadados de {len(olinda_services)} Serviços Multidimensionais únicos do Olinda.")
print(f"Arquivo salvo em: {filename}")
