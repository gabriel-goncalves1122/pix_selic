import sys
from pathlib import Path

# Adiciona a pasta src/utils ao PATH do Python para importar utils_ingestao
sys.path.append(str(Path(__file__).parent.parent / "utils"))
from utils_ingestao import extrair_tabela, gerar_periodos_mensais, fazer_request, salvar, registrar

# ==============================================================================
# Ingestão — Contexto: IFDATA (Balanço dos Bancos)
# ==============================================================================

SERVICO = 'IFDATA'

def extrair():
    print("=" * 60)
    print("INGESTÃO MACRO — Contexto: IFDATA (Lucros dos Bancos)")
    print("=" * 60)

    base_raw_path = Path(__file__).parent.parent.parent.parent / "data" / "macro_bruto" / "ifdata"

    # 1. Tabela Dimensão: Cadastro das Instituições (Puxamos o período atual, pois exige parâmetro AnoMes)
    print(f"\n  → Extraindo: TipoIfDataCadastro (Dimensão Bancos)")
    pasta_cadastro = base_raw_path / "TipoIfDataCadastro"
    # O BCB exige que a função IfDataCadastro receba o AnoMes atual. Pegaremos o último disponível
    ciclo_recente = "202403" # Usando um hardcode seguro pois IFDATA demora a atualizar
    url_cad = f"https://olinda.bcb.gov.br/olinda/servico/{SERVICO}/versao/v1/odata/IfDataCadastro(AnoMes={ciclo_recente})?$format=text/csv"
    
    if not (pasta_cadastro / "TipoIfDataCadastro.csv").exists():
        res_cad = fazer_request(url_cad)
        if res_cad and res_cad.status_code == 200:
            qtd = res_cad.text.strip().count('\n')
            if qtd > 0:
                arq = salvar(res_cad.text, pasta_cadastro, "TipoIfDataCadastro", "")
                registrar(pasta_cadastro, arq, url_cad, qtd)
                print(f"     ✅ Cadastro salvo.")
    else:
        print("     ⏭ Pulado (já existe: TipoIfDataCadastro.csv)")

    # 2. Tabela Fato: Valores dos Relatórios Financeiros (Fatiamos por AnoMes)
    print(f"\n  → Extraindo: TipoIfValores (Filtrado Mensalmente - Relatório Resumo, Bancos)")
    pasta_valores = base_raw_path / "TipoIfValores"
    
    # Gerar de 2020 até hoje
    periodos_yyyymm = gerar_periodos_mensais(ano_inicio=2020, mes_inicio=1)
    
    for ciclo in periodos_yyyymm:
        # Pula se já existe
        arquivo_esperado = pasta_valores / f"TipoIfValores_{ciclo}.csv"
        if arquivo_esperado.exists():
            print(f"     [{ciclo}] ⏭ Pulado (já existe)")
            continue
            
        print(f"     [{ciclo}] ", end="", flush=True)
        # TipoInstituicao=1 (Bancos), Relatorio='Resumo'
        url_val = f"https://olinda.bcb.gov.br/olinda/servico/{SERVICO}/versao/v1/odata/IfDataValores(AnoMes={ciclo},TipoInstituicao=1,Relatorio='Resumo')?$format=text/csv"
        
        res_val = fazer_request(url_val)
        if res_val is None:
            print("FALHA.")
            continue
            
        if res_val.status_code == 200:
            texto = res_val.text
            qtd = texto.strip().count('\n')
            if qtd == 0 or not texto.strip():
                print("Vazio (0 registros).")
            else:
                arq = salvar(texto, pasta_valores, "TipoIfValores", ciclo)
                registrar(pasta_valores, arq, url_val, qtd)
                print(f"✅ {qtd} registros → TipoIfValores_{ciclo}.csv")
        else:
            print(f"❌ HTTP {res_val.status_code}.")

if __name__ == "__main__":
    extrair()
