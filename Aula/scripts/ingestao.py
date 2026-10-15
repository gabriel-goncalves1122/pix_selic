import os
import json
import shutil
from pathlib import Path
from datetime import date, datetime
from dotenv import load_dotenv
import kagglehub

# Carrega a chave/token do arquivo .env localizado na pasta raiz (Aula/)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

DATASET = "rishavsvault/most-streamed-artists-on-spotify"
# Ajustado para garantir que a pasta dados/ fique dentro de Aula/ independentemente de onde o script for rodado
BRONZE = Path(__file__).parent.parent / "dados/bronze/spotify"

def baixar():
    pasta = kagglehub.dataset_download(DATASET)
    print("baixado em:", pasta)
    return Path(pasta)

def localizar(pasta):
    arquivos = list(pasta.glob("*.csv"))
    if not arquivos:
        raise FileNotFoundError("nenhum CSV")
    print("encontrados:", [a.name for a in arquivos])
    return arquivos[0]

def copiar(origem):
    BRONZE.mkdir(parents=True, exist_ok=True)
    hoje = date.today().strftime("%Y%m%d")
    destino = BRONZE / f"artists_{hoje}.csv"
    shutil.copy(origem, destino)
    return destino

def registrar(origem, destino):
    info = {
        "fonte": DATASET,
        "arquivo_origem": origem.name,
        "arquivo_bronze": destino.name,
        "extraido_em": datetime.now().isoformat(),
    }
    (BRONZE / "proveniencia.json").write_text(json.dumps(info, indent=2))

def main():
    print("Iniciando processo de ingestão...")
    pasta = baixar()
    origem = localizar(pasta)
    destino = copiar(origem)
    registrar(origem, destino)
    print(f"Ingestão finalizada com sucesso! Arquivo salvo em: {destino}")

if __name__ == "__main__":
    main()