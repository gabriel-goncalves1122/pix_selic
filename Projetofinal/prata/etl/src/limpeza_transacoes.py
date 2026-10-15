import pandas as pd
import os
import sys
from pathlib import Path

# Adiciona o diretório 'src' ao sys.path para conseguirmos importar a pasta 'utils'
sys.path.append(os.path.dirname(__file__))
from utils.formatadores import limpar_nomes_colunas, tratar_valor_financeiro

def processar_transacoes():
    print("="*60)
    print("PROCESSAMENTO PRATA: ESTATÍSTICAS TRANSAÇÕES PIX")
    print("="*60)
    
    # 1. Definir Caminhos (Cirúrgico: apontamos só para o 202011.csv que tem todo o histórico)
    base_dir = Path(__file__).parent.parent.parent.parent
    caminho_bronze = base_dir / "bronze" / "data" / "pix_bruto" / "Pix_DadosAbertos" / "EstatisticasTransacoesPix" / "EstatisticasTransacoesPix_202011.csv"
    pasta_prata = base_dir / "prata" / "data" / "pix_limpo"
    caminho_prata = pasta_prata / "estatisticas_transacoes_pix.parquet"
    
    print(f"Lendo histórico completo (Staircase Duplication Bypass)...")
    print(f"-> {caminho_bronze.name}")
    
    if not caminho_bronze.exists():
        print("ERRO: Arquivo base 202011 não encontrado na Bronze!")
        return

    # 2. Leitura
    df = pd.read_csv(caminho_bronze)
    linhas_originais = len(df)
    
    # 3. Limpeza de Nomes de Colunas (Snake Case)
    df = limpar_nomes_colunas(df)
    
    # 4. Tipagem de Dados
    # 'valor' vem como string com vírgula. Vamos converter para float.
    if 'valor' in df.columns:
        df['valor'] = tratar_valor_financeiro(df['valor'])
    
    # Transformar ano_mes de YYYYMM (inteiro) para formato de Data (pd.to_datetime) no primeiro dia do mês
    if 'ano_mes' in df.columns:
        # Ex: 202011 -> 2020-11-01
        df['ano_mes_dt'] = pd.to_datetime(df['ano_mes'].astype(str), format='%Y%m')
    
    # 5. Salvar na Prata (Formato Parquet e CSV)
    print(f"Salvando dados limpos em Parquet e CSV na Camada Prata...")
    caminho_prata_csv = caminho_prata.with_suffix('.csv')
    df.to_parquet(caminho_prata, engine='pyarrow', index=False)
    df.to_csv(caminho_prata_csv, index=False)
    
    tamanho_mb = caminho_prata.stat().st_size / (1024 * 1024)
    print(f"\nResumo da Operação:")
    print(f" - Linhas processadas: {linhas_originais}")
    print(f" - Colunas limpas: {list(df.columns)}")
    print(f" - Arquivo Parquet gerado: {caminho_prata.name} ({tamanho_mb:.2f} MB)")
    print("="*60)

if __name__ == "__main__":
    processar_transacoes()
