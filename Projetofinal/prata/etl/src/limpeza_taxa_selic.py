import pandas as pd
import numpy as np
from pathlib import Path
import time
import os

def limpar_taxa_selic():
    print("=" * 60)
    print("PROCESSAMENTO PRATA: TAXA SELIC (SGS 432 / 11)")
    print("=" * 60)
    inicio = time.time()

    base_dir = Path(__file__).parent.parent.parent.parent
    pasta_bronze = base_dir / "bronze" / "data" / "macro_bruto" / "sgs"
    pasta_destino = base_dir / "prata" / "data" / "macro_limpo"
    pasta_destino.mkdir(parents=True, exist_ok=True)

    arq_meta = pasta_bronze / "Selic_Meta_Diaria.csv"
    arq_realizada = pasta_bronze / "Selic_Realizada_Diaria.csv"

    print(f"Lendo dados brutos do SGS...")
    df_meta = pd.read_csv(arq_meta, sep=';', quotechar='"')
    df_real = pd.read_csv(arq_realizada, sep=';', quotechar='"')

    # 1. Tratamento Meta (Série 432 - % a.a.)
    df_meta['data_dt'] = pd.to_datetime(df_meta['data'], format='%d/%m/%Y')
    df_meta['selic_meta_aa'] = (
        df_meta['valor']
        .astype(str)
        .str.replace('.', '', regex=False)
        .str.replace(',', '.', regex=False)
        .pipe(pd.to_numeric, errors='coerce')
    )
    df_meta = df_meta[['data_dt', 'selic_meta_aa']].dropna(subset=['data_dt'])

    # 2. Tratamento Realizada (Série 11 - % ao dia útil base 252)
    df_real['data_dt'] = pd.to_datetime(df_real['data'], format='%d/%m/%Y')
    df_real['selic_realizada_dia_pct'] = (
        df_real['valor']
        .astype(str)
        .str.replace('.', '', regex=False)
        .str.replace(',', '.', regex=False)
        .pipe(pd.to_numeric, errors='coerce')
    )
    # Anualização base 252 dias úteis
    df_real['selic_realizada_anualizada_pct'] = (
        ((1.0 + (df_real['selic_realizada_dia_pct'] / 100.0)) ** 252 - 1.0) * 100.0
    ).round(4)
    df_real = df_real[['data_dt', 'selic_realizada_dia_pct', 'selic_realizada_anualizada_pct']].dropna(subset=['data_dt'])

    # 3. Consolidação Diária (Merge)
    print("Consolidando série temporal diária...")
    df_diario = pd.merge(df_meta, df_real, on='data_dt', how='outer').sort_values('data_dt').reset_index(drop=True)
    df_diario['ano_mes'] = df_diario['data_dt'].dt.strftime('%Y%m').astype(int)
    df_diario['ano_mes_dt'] = pd.to_datetime(df_diario['ano_mes'].astype(str) + '01', format='%Y%m%d')

    # Reordenar colunas
    cols_diario = [
        'data_dt', 'ano_mes', 'ano_mes_dt',
        'selic_meta_aa', 'selic_realizada_dia_pct', 'selic_realizada_anualizada_pct'
    ]
    df_diario = df_diario[cols_diario]

    # 4. Agregação Mensal (para merge direto com Pix)
    print("Gerando visão agregada mensal...")
    df_mensal = df_diario.groupby(['ano_mes', 'ano_mes_dt']).agg(
        selic_meta_fim_mes=('selic_meta_aa', 'last'),
        selic_meta_media_mes=('selic_meta_aa', 'mean'),
        selic_realizada_media_mes=('selic_realizada_anualizada_pct', 'mean'),
        dias_uteis=('selic_realizada_dia_pct', 'count')
    ).reset_index()

    df_mensal['selic_meta_fim_mes'] = df_mensal['selic_meta_fim_mes'].round(2)
    df_mensal['selic_meta_media_mes'] = df_mensal['selic_meta_media_mes'].round(2)
    df_mensal['selic_realizada_media_mes'] = df_mensal['selic_realizada_media_mes'].round(2)

    # 5. Salvar em Parquet e CSV
    print("Salvando artefatos na Camada Prata...")
    arq_diario_parquet = pasta_destino / "taxa_selic_diaria.parquet"
    arq_diario_csv = pasta_destino / "taxa_selic_diaria.csv"
    arq_mensal_parquet = pasta_destino / "taxa_selic_mensal.parquet"
    arq_mensal_csv = pasta_destino / "taxa_selic_mensal.csv"

    df_diario.to_parquet(arq_diario_parquet, engine='pyarrow', index=False, compression='snappy')
    df_diario.to_csv(arq_diario_csv, index=False)

    df_mensal.to_parquet(arq_mensal_parquet, engine='pyarrow', index=False, compression='snappy')
    df_mensal.to_csv(arq_mensal_csv, index=False)

    print("\nResumo da Operação:")
    print(f" - Registros diários: {len(df_diario)} ({arq_diario_parquet.name})")
    print(f" - Meses agregados:   {len(df_mensal)} ({arq_mensal_parquet.name})")
    print(f"Tempo total: {time.time() - inicio:.2f}s")
    print("=" * 60)

if __name__ == "__main__":
    limpar_taxa_selic()
