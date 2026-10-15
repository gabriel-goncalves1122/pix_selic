import pandas as pd
from data_profiling import ProfileReport
from pathlib import Path
import os

# ==============================================================================
# Script de Análise Exploratória (EDA) — Contexto MACRO
# ==============================================================================

def analisar_macro():
    print("============================================================")
    print("Iniciando Data Profiling (EDA) — MACROECONOMIA")
    print("============================================================")

    base_raw = Path(__file__).parent.parent.parent / "data" / "macro_bruto"
    base_analytics = Path(__file__).parent
    
    # Lista dos módulos a serem analisados
    # Formato: (Nome_Pasta, Analisar_Todo_Historico)
    modulos = [
        ("sgs", True),           # IPCA e Selic diária (poucas linhas, full scan seguro)
        ("focus", True),         # Expectativas anuais/mensais (full scan)
        ("selic_operacoes", False), # OperacoesEmUmMes_YYYYMM (Pesado, amostragem)
        ("ifdata", False)        # Balanço dos bancos trimestrais (Pesado, amostragem)
    ]

    for pasta, analisar_tudo in modulos:
        caminho_pasta = base_raw / pasta
        if not caminho_pasta.exists():
            print(f"⚠ Pasta não encontrada: {caminho_pasta}")
            continue
            
        print(f"\n▶ Analisando Módulo: {pasta}")
        
        # Para Macro, as pastas podem ter subpastas ou arquivos diretos.
        # Vamos varrer a pasta em busca de arquivos CSV
        csvs_encontrados = list(caminho_pasta.rglob("*.csv"))
        if not csvs_encontrados:
            print(f"⚠ Nenhum CSV encontrado no módulo: {pasta}")
            continue
            
        csvs_ordenados = sorted(csvs_encontrados)
        
        # Estratégia de Amostragem vs Full Scan
        df_final = None
        if analisar_tudo:
            print("  ↳ Estratégia: Full Scan (Lendo todos os CSVs do módulo)")
            dfs = []
            for arq in csvs_ordenados:
                dfs.append(pd.read_csv(arq))
            df_final = pd.concat(dfs, ignore_index=True)
        else:
            # Amostragem representativa
            arquivo_representativo = csvs_ordenados[-1] 
            print(f"  ↳ Estratégia: Amostragem (Lendo apenas {arquivo_representativo.name})")
            df_final = pd.read_csv(arquivo_representativo)
        
        # Gerar o Profile Report
        print(f"  ↳ Gerando Profiling HTML (Linhas: {len(df_final)}, Colunas: {len(df_final.columns)})...")
        profile = ProfileReport(df_final, title=f"EDA - {pasta.upper()}", minimal=False, explorative=True)
        
        # Salvar o relatório HTML
        arquivo_html = base_analytics / f"eda_{pasta}.html"
        profile.to_file(arquivo_html)
        
        # Salvar o relatório JSON (Para a IA ler)
        arquivo_json = base_analytics / f"eda_{pasta}.json"
        profile.to_file(arquivo_json)
        
        print(f"  ✅ Relatório salvo: {arquivo_html.name} e {arquivo_json.name}")

if __name__ == "__main__":
    analisar_macro()
