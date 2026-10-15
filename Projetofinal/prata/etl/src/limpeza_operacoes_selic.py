import pandas as pd
import numpy as np
from pathlib import Path
import glob
import time
import os

def limpar_operacoes_selic():
    print("=" * 60)
    print("PROCESSAMENTO PRATA: OPERAÇÕES SELIC (OLINDA)")
    print("=" * 60)
    inicio = time.time()

    base_dir = Path(__file__).parent.parent.parent.parent
    pasta_bronze = base_dir / "bronze" / "data" / "macro_bruto" / "selic_operacoes" / "OperacoesEmUmMes"
    pasta_destino = base_dir / "prata" / "data" / "macro_limpo"
    pasta_destino.mkdir(parents=True, exist_ok=True)

    arquivos_csv = sorted(pasta_bronze.glob("OperacoesEmUmMes_*.csv"))
    print(f"Encontrados {len(arquivos_csv)} arquivos mensais na Bronze...")

    if not arquivos_csv:
        raise FileNotFoundError(f"Nenhum arquivo CSV encontrado em {pasta_bronze}")

    dfs = []
    for arq in arquivos_csv:
        df_mes = pd.read_csv(arq)
        dfs.append(df_mes)

    df = pd.concat(dfs, ignore_index=True)
    linhas_originais = len(df)
    print(f"Total de registros consolidados: {linhas_originais}")

    # Renomeação Semântica
    renames = {
        'Mes': 'mes_orig',
        'Codigo': 'codigo_operacao',
        'Categoria': 'categoria_operacao',
        'QuantidadeAcumulada': 'qtd_acumulada',
        'ValorAcumulado': 'valor_acumulado_milhoes',
        'QuantidadeMediaDiaria': 'qtd_media_diaria',
        'ValorMedioDiario': 'valor_medio_diario_milhoes'
    }
    df.rename(columns=renames, inplace=True)

    # Tratamento Temporal
    # Ex: '2020-01' -> ano_mes: 202001, ano_mes_dt: 2020-01-01
    df['ano_mes'] = df['mes_orig'].str.replace('-', '', regex=False).astype(int)
    df['ano_mes_dt'] = pd.to_datetime(df['ano_mes'].astype(str) + '01', format='%Y%m%d')

    # Tratamento de Strings e Tipagem
    df['codigo_operacao'] = pd.to_numeric(df['codigo_operacao'], errors='coerce').fillna(0).astype('int64')
    df['categoria_operacao'] = df['categoria_operacao'].astype(str).str.strip()

    # Quantidades -> BIGINT (int64)
    for col_qtd in ['qtd_acumulada', 'qtd_media_diaria']:
        if col_qtd in df.columns:
            if df[col_qtd].dtype == 'object':
                df[col_qtd] = df[col_qtd].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            df[col_qtd] = pd.to_numeric(df[col_qtd], errors='coerce').fillna(0).astype('int64')

    # Valores Monetários -> DOUBLE (float64)
    for col_val in ['valor_acumulado_milhoes', 'valor_medio_diario_milhoes']:
        if col_val in df.columns:
            if df[col_val].dtype == 'object':
                df[col_val] = df[col_val].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            df[col_val] = pd.to_numeric(df[col_val], errors='coerce').fillna(0.0).astype('float64')

    # Ordenação e Seleção de Colunas
    cols_ordenadas = [
        'ano_mes', 'ano_mes_dt', 'codigo_operacao', 'categoria_operacao',
        'qtd_acumulada', 'valor_acumulado_milhoes',
        'qtd_media_diaria', 'valor_medio_diario_milhoes'
    ]
    df = df[cols_ordenadas].sort_values(['ano_mes', 'codigo_operacao']).reset_index(drop=True)

    # Salvar em Parquet e CSV
    arq_parquet = pasta_destino / "operacoes_selic.parquet"
    arq_csv = pasta_destino / "operacoes_selic.csv"

    print("Salvando artefatos na Camada Prata...")
    df.to_parquet(arq_parquet, engine='pyarrow', index=False, compression='snappy')
    df.to_csv(arq_csv, index=False)

    tamanho_mb = os.path.getsize(arq_parquet) / (1024 * 1024)
    print("\nResumo da Operação:")
    print(f" - Arquivos mensais processados: {len(arquivos_csv)}")
    print(f" - Linhas totais: {len(df)}")
    print(f" - Meses únicos: {df['ano_mes'].nunique()} (de {df['ano_mes'].min()} a {df['ano_mes'].max()})")
    print(f" - Arquivo Parquet gerado: {arq_parquet.name} ({tamanho_mb:.4f} MB)")
    print(f"Tempo total: {time.time() - inicio:.2f}s")
    print("=" * 60)

if __name__ == "__main__":
    limpar_operacoes_selic()
