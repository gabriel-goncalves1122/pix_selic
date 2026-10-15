import pandas as pd
from data_profiling import ProfileReport
from pathlib import Path
import os

# ==============================================================================
# Script de Análise Exploratória (EDA) — Contexto PIX
# ==============================================================================

def analisar_pix():
    print("============================================================")
    print("Iniciando Data Profiling (EDA) — PIX")
    print("============================================================")

    base_raw = Path(__file__).parent.parent.parent / "data" / "pix_bruto" / "Pix_DadosAbertos"
    base_analytics = Path(__file__).parent
    
    # Lista dos módulos a serem analisados
    # Formato: (Nome_Pasta, Prefixo_Arquivo, Analisar_Todo_Historico)
    modulos = [
        ("PixUsuariosCadastradosDICT", "PixUsuariosCadastradosDICT", True),
        ("EstatisticasTransacoesPix", "EstatisticasTransacoesPix", False),
        ("EstatisticasFraudesPix", "EstatisticasFraudesPix", False),
        ("TransacoesPixPorMunicipio", "TransacoesPixPorMunicipio", False)
    ]

    for pasta, prefixo, analisar_tudo in modulos:
        caminho_pasta = base_raw / pasta
        if not caminho_pasta.exists():
            print(f"⚠ Pasta não encontrada: {caminho_pasta}")
            continue
            
        # Coletar arquivos CSV do módulo
        arquivos = sorted([f for f in os.listdir(caminho_pasta) if f.endswith(".csv")])
        if not arquivos:
            print(f"⚠ Nenhum CSV encontrado em: {caminho_pasta}")
            continue
            
        print(f"\n▶ Analisando Módulo: {pasta}")
        
        # Estratégia de Amostragem vs Full Scan
        df_final = None
        if analisar_tudo:
            print("  ↳ Estratégia: Full Scan (Lendo todos os arquivos)")
            dfs = []
            for arq in arquivos:
                dfs.append(pd.read_csv(caminho_pasta / arq))
            df_final = pd.concat(dfs, ignore_index=True)
        else:
            # Amostragem representativa: Pegamos o mês mais recente disponível para inferir o esquema (Schema)
            arquivo_representativo = arquivos[-1] # O último da lista ordenada
            print(f"  ↳ Estratégia: Amostragem de Mês Representativo (Lendo apenas {arquivo_representativo})")
            df_final = pd.read_csv(caminho_pasta / arquivo_representativo)
        
        # Gerar o Profile Report
        print(f"  ↳ Gerando Profiling HTML (Linhas: {len(df_final)}, Colunas: {len(df_final.columns)})...")
        profile = ProfileReport(df_final, title=f"EDA - {pasta}", minimal=False, explorative=True)
        
        # Salvar o relatório HTML
        arquivo_html = base_analytics / f"eda_{pasta.lower()}.html"
        profile.to_file(arquivo_html)
        
        # Salvar o relatório JSON (Para a IA ler)
        arquivo_json = base_analytics / f"eda_{pasta.lower()}.json"
        profile.to_file(arquivo_json)
        
        print(f"  ✅ Relatório salvo: {arquivo_html.name} e {arquivo_json.name}")

if __name__ == "__main__":
    analisar_pix()
