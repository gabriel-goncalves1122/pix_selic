import duckdb
import time
from pathlib import Path

def executar_auditoria():
    print("="*60)
    print("AUDITORIA FORENSE: COMPLETUDE DE DADOS (DUCKDB)")
    print("="*60)
    
    inicio = time.time()
    
    # 1. Definir caminhos
    base_dir = Path(__file__).parent.parent.parent.parent
    pasta_transacoes = base_dir / "bronze" / "data" / "pix_bruto" / "Pix_DadosAbertos" / "EstatisticasTransacoesPix"
    
    padrao_todos_arquivos = str(pasta_transacoes / "*.csv")
    arquivo_base = str(pasta_transacoes / "EstatisticasTransacoesPix_202011.csv")
    
    con = duckdb.connect(database=':memory:')
    
    print("1. Calculando total de registros em todos os 70 arquivos (UNION ALL)...")
    total_linhas_bruto = con.execute(f"SELECT COUNT(*) FROM read_csv_auto('{padrao_todos_arquivos}')").fetchone()[0]
    print(f"   -> {total_linhas_bruto:,} linhas totais no disco (2.5 GB).")
    

    print("\n3. Contando linhas do arquivo raiz (202011.csv)...")
    total_arquivo_base = con.execute(f"SELECT COUNT(*) FROM read_csv_auto('{arquivo_base}')").fetchone()[0]
    print(f"   -> {total_arquivo_base:,} linhas.")
    
    print("\n4. TESTE DE FOGO: Existem linhas nos outros arquivos que NÃO estão no arquivo raiz?")
    # EXCEPT traz tudo da query A que não existe na query B (comparação exata de todas as colunas)
    query_divergencia = f"""
        SELECT * FROM read_csv_auto('{padrao_todos_arquivos}')
        EXCEPT
        SELECT * FROM read_csv_auto('{arquivo_base}')
    """
    df_divergencia = con.execute(query_divergencia).df()
    qtd_divergencia = len(df_divergencia)
    
    print(f"   -> Resultado: {qtd_divergencia:,} linhas encontradas fora do arquivo raiz.")
    
    if qtd_divergencia > 0:
        print("\n[ALERTA DE PERDA DE DADOS DETECTADA!]")
        print("A API atualizou ou inseriu dados nesses baldes em meses posteriores.")
        print("Amostra das linhas que perderíamos se usássemos só o arquivo 202011.csv:")
        print(df_divergencia.head(5))
        
        # Agrupar por ano_mes para ver onde estão as diferenças
        resumo_meses = df_divergencia['AnoMes'].value_counts().sort_index()
        print("\nMeses afetados (AnoMes: quantidade de linhas divergentes):")
        print(resumo_meses)
        print("\nCONCLUSÃO DA AUDITORIA: Estratégia alterada. Devemos ler todos os CSVs e aplicar drop_duplicates() na Prata.")
    else:
        print("\n[SUCESSO] O arquivo 202011.csv contém matematicamente 100% dos dados idênticos.")
        print("CONCLUSÃO DA AUDITORIA: Podemos usar a estratégia ultrarrápida na Camada Prata de ler apenas o arquivo base.")

    fim = time.time()
    print(f"\nTempo total da análise: {fim - inicio:.2f} segundos.")
    print("="*60)

if __name__ == "__main__":
    executar_auditoria()
