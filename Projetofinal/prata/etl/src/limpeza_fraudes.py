import pandas as pd
import numpy as np
from pathlib import Path
import time
import os

def limpar_estatisticas_fraudes():
    print("="*60)
    print("PROCESSAMENTO PRATA: ESTATÍSTICAS FRAUDES PIX (MED)")
    print("="*60)
    
    inicio = time.time()
    
    # 1. Definir caminhos (Usando o Bypass do Staircase Duplication)
    base_dir = Path(__file__).parent.parent.parent.parent
    arquivo_bruto = base_dir / "bronze" / "data" / "pix_bruto" / "Pix_DadosAbertos" / "EstatisticasFraudesPix" / "EstatisticasFraudesPix_202011.csv"
    
    pasta_destino = base_dir / "prata" / "data" / "pix_limpo"
    pasta_destino.mkdir(parents=True, exist_ok=True)
    arquivo_parquet = pasta_destino / "estatisticas_fraudes_pix.parquet"
    
    print(f"Lendo histórico completo (Staircase Duplication Bypass)...")
    print(f"-> {arquivo_bruto.name}")
    
    # 2. Carregar arquivo
    df = pd.read_csv(arquivo_bruto)
    linhas_originais = len(df)
    
    # 3. Dicionário Semântico de Renomeação
    renames = {
        'AnoMes': 'ano_mes',
        'QtdePixcontestados': 'qtd_pix_contestados',
        'Qtdecontestacoesaceitas': 'qtd_contestacoes_aceitas',
        'Qtdecontestacoesrejeitadas': 'qtd_contestacoes_rejeitadas',
        'Qtdecontestacoesaceitasacada100mil': 'taxa_contestacoes_aceitas_por_100mil',
        'QtdeUsuarioscommarcacoesdefraude': 'qtd_usuarios_marcacao_fraude',
        'QtdeChavesPixcommarcacoesdefraude': 'qtd_chaves_marcacao_fraude',
        'ValorPixcontestadosaceitos': 'valor_pix_contestados_aceitos',
        'QuantidadedevolvidaintegralmentepormeiodoMED': 'qtd_devolvida_integral_med',
        'ValorPixdevolvidosintegralmente': 'valor_devolvido_integral_med',
        'QuantidadedevolvidaparcialmentepormeiodoMED': 'qtd_devolvida_parcial_med',
        'ValorPixdevolvidosparcialmente': 'valor_devolvido_parcial_med',
        'ValorPixresidualnaodevolvido': 'valor_residual_nao_devolvido',
        'Quantidadedenaodevolvidossaldoinsuficiente': 'qtd_nao_devolvida_saldo_insuficiente',
        'ValorPixnaodevolvidossaldoinsuficiente': 'valor_nao_devolvido_saldo_insuficiente',
        'Quantidadedenaodevolvidoscontaencerrada': 'qtd_nao_devolvida_conta_encerrada',
        'Valornaodevolvidoscontaencerrada': 'valor_nao_devolvido_conta_encerrada',
        'Quantidadedenaodevolvidosmotivosdiversos': 'qtd_nao_devolvida_motivos_diversos',
        'ValorPixnaodevolvidosmotivosdiversos': 'valor_nao_devolvido_motivos_diversos',
        'PercentualdeDevolucao': 'percentual_devolucao',
        'QtdePixbloqueadoscautelarmenteeliberados': 'qtd_bloqueio_cautelar_liberado',
        'ValorPixbloqueadoscautelarmenteeliberados': 'valor_bloqueio_cautelar_liberado',
        'QtdePixbloqueadoscautelarmenteedevolvidos': 'qtd_bloqueio_cautelar_devolvido',
        'ValorPixbloqueadoscautelarmenteedevolvidos': 'valor_bloqueio_cautelar_devolvido'
    }
    
    df.rename(columns=renames, inplace=True)
    
    # 4. Limpeza e Tipagem Segura
    for col in df.columns:
        if col == 'ano_mes':
            df[col] = df[col].astype('int64')
        else:
            # Converter formato de moeda PT-BR para internacional
            if df[col].dtype == 'object':
                df[col] = df[col].str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            
            # Se a coluna começa com 'qtd_', é BigInt
            if col.startswith('qtd_'):
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype('int64')
            else:
                # Caso contrário é Float/Double (Valores ou Taxas)
                df[col] = pd.to_numeric(df[col], errors='coerce').astype('float64')

    # 5. Criar coluna de DateTime para BI (Data Mart)
    # Ex: 202401 -> 2024-01-01
    df['ano_mes_dt'] = pd.to_datetime(df['ano_mes'].astype(str) + '01', format='%Y%m%d', errors='coerce')
    
    # 6. Salvar em Parquet e CSV
    print("Salvando dados limpos em Parquet e CSV na Camada Prata...")
    arquivo_csv = pasta_destino / "estatisticas_fraudes_pix.csv"
    df.to_parquet(arquivo_parquet, engine='pyarrow', index=False, compression='snappy')
    df.to_csv(arquivo_csv, index=False)
    
    tamanho_mb = os.path.getsize(arquivo_parquet) / (1024 * 1024)
    
    print("Resumo da Operação:")
    print(f" - Linhas processadas: {linhas_originais}")
    print(f" - Arquivo Parquet gerado: {arquivo_parquet.name} ({tamanho_mb:.4f} MB)")
    print(f"Tempo total: {time.time() - inicio:.2f} segundos.")
    print("="*60)

if __name__ == "__main__":
    limpar_estatisticas_fraudes()
