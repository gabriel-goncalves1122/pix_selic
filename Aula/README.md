# Projeto Aula - Engenharia de Dados

Este repositório contém o ambiente e os scripts construídos durante as aulas da disciplina de **Engenharia de Dados**.

## Estrutura do Projeto

- `venv/`: Ambiente virtual contendo todas as dependências do projeto (Kaggle, Pandas, Requests, etc).
- `scripts/`: Diretório contendo os scripts de extração de dados.
  - `ingestao.py`: Script responsável por se conectar na API do Kaggle e extrair dados referentes aos artistas mais tocados no Spotify.
  - `ingestao2.py`: Script focado na extração via API Rest JSON do **Banco Mundial**, mapeando os países, suas regiões e agregados econômicos.
- `dados/`: Camada de Data Lake gerada automaticamente pelos scripts.
  - `bronze/`: Área de *landing* onde os dados brutos e metadados (`proveniencia.json`) são salvos exatamente como vieram das fontes.
- `.env`: Arquivo de variáveis de ambiente para armazenamento seguro de chaves de API (ex: `KAGGLE_API_TOKEN`).

## Como rodar localmente

1. Ative o ambiente virtual:
   ```bash
   source venv/bin/activate
   ```
2. Instale os requisitos (caso necessário):
   ```bash
   pip install -r requeirements.txt
   ```
3. Execute os pipelines de ingestão de dados:
   ```bash
   python3 scripts/ingestao.py
   python3 scripts/ingestao2.py
   ```
