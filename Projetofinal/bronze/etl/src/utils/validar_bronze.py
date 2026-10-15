import json
import csv
import os
from pathlib import Path

# ==============================================================================
# Validador Automatizado da Camada Bronze — Schema Registry
# ==============================================================================
# Lê o schema.json (contrato) e varre todos os CSVs da Bronze verificando:
#   1. Contagem de colunas
#   2. Nomes das colunas
#   3. Arquivo vazio (só header, 0 dados)
#   4. Existência do proveniencia.json
#   5. Consistência intra-tabela (todos os CSVs da mesma tabela com mesmo header)
# ==============================================================================

def carregar_schema():
    """Carrega o contrato de colunas do schema.json."""
    schema_path = Path(__file__).parent.parent.parent.parent / "schema.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)

def ler_header(caminho_csv, delimitador=","):
    """Lê apenas a primeira linha (header) de um CSV."""
    with open(caminho_csv, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=delimitador)
        return next(reader)

def contar_linhas(caminho_csv):
    """Conta linhas de dados (excluindo o header)."""
    with open(caminho_csv, "r", encoding="utf-8") as f:
        return sum(1 for _ in f) - 1

def validar():
    print("=" * 60)
    print("VALIDAÇÃO DA CAMADA BRONZE — Schema Registry")
    print("=" * 60)

    schema = carregar_schema()
    base_raw = Path(__file__).parent.parent.parent.parent / "data"

    total_tabelas = 0
    total_ok = 0
    total_erros = 0
    total_avisos = 0
    total_arquivos = 0

    # Mapear contextos para pastas reais
    mapa_pastas = {
        "pix": base_raw / "pix" / "Pix_DadosAbertos",
        "macro": base_raw / "macro"
    }

    for contexto in ["pix", "macro"]:
        if contexto not in schema:
            continue

        print(f"\n{'─' * 60}")
        print(f"  CONTEXTO: {contexto.upper()}")
        print(f"{'─' * 60}")

        pasta_contexto = mapa_pastas[contexto]

        for tabela, contrato in schema[contexto].items():
            total_tabelas += 1
            colunas_esperadas = contrato["colunas"]
            qtd_esperada = contrato["qtd_colunas"]
            delim = contrato.get("delimitador", ",")

            # Localizar a pasta da tabela
            # Para macro, as tabelas podem estar em subpastas (focus/, selic_operacoes/, sgs/)
            pasta_tabela = None
            for root, dirs, files in os.walk(pasta_contexto):
                if os.path.basename(root) == tabela:
                    pasta_tabela = Path(root)
                    break
                # Para o SGS que não tem subpasta com o nome "sgs" dentro dele
                if tabela == "sgs" and os.path.basename(root) == "sgs":
                    pasta_tabela = Path(root)
                    break

            if pasta_tabela is None:
                print(f"\n  ⚠️  {tabela}: Pasta não encontrada")
                total_avisos += 1
                continue

            # Coletar CSVs
            csvs = sorted([f for f in os.listdir(pasta_tabela) if f.endswith(".csv")])
            if not csvs:
                print(f"\n  ⚠️  {tabela}: Nenhum CSV encontrado")
                total_avisos += 1
                continue

            total_arquivos += len(csvs)
            erros_tabela = []
            avisos_tabela = []

            # Verificação 4: Proveniência
            prov = pasta_tabela / "proveniencia.json"
            if not prov.exists():
                avisos_tabela.append("proveniencia.json ausente")

            # Verificar cada CSV
            headers_vistos = set()
            for arq in csvs:
                caminho = pasta_tabela / arq
                try:
                    header = ler_header(str(caminho), delim)
                except Exception as e:
                    erros_tabela.append(f"{arq}: Falha ao ler header ({e})")
                    continue

                headers_vistos.add(tuple(header))

                # Verificação 1: Contagem de colunas
                if len(header) != qtd_esperada:
                    erros_tabela.append(
                        f"{arq}: Esperado {qtd_esperada} colunas, encontrado {len(header)}"
                    )

                # Verificação 2: Nomes das colunas
                # Limpar aspas que o SGS coloca nos headers
                header_limpo = [h.strip().strip('"') for h in header]
                colunas_limpo = [c.strip().strip('"') for c in colunas_esperadas]
                if header_limpo != colunas_limpo:
                    colunas_faltando = set(colunas_limpo) - set(header_limpo)
                    colunas_extras = set(header_limpo) - set(colunas_limpo)
                    if colunas_faltando:
                        erros_tabela.append(f"{arq}: Colunas faltando: {colunas_faltando}")
                    if colunas_extras:
                        erros_tabela.append(f"{arq}: Colunas extras (novas?): {colunas_extras}")

                # Verificação 3: Arquivo vazio
                linhas = contar_linhas(str(caminho))
                if linhas == 0:
                    avisos_tabela.append(f"{arq}: Arquivo vazio (0 linhas de dados)")

            # Verificação 5: Consistência intra-tabela
            if len(headers_vistos) > 1:
                erros_tabela.append(
                    f"INCONSISTÊNCIA: {len(headers_vistos)} schemas diferentes entre os {len(csvs)} CSVs"
                )

            # Imprimir resultado
            if erros_tabela:
                total_erros += len(erros_tabela)
                print(f"\n  ❌ {tabela}: {len(csvs)} arquivo(s) | {qtd_esperada} colunas")
                for e in erros_tabela:
                    print(f"     ERRO: {e}")
            else:
                total_ok += 1
                extra = ""
                if delim != ",":
                    extra = f' | Delimitador "{delim}"'
                    total_avisos += 1
                print(f"\n  ✅ {tabela}: {len(csvs)} arquivo(s) | {qtd_esperada} colunas | Consistente{extra}")

            for a in avisos_tabela:
                print(f"     ⚠️  {a}")
                total_avisos += 1

    # Resumo final
    print(f"\n{'=' * 60}")
    print(f"RESULTADO FINAL")
    print(f"{'=' * 60}")
    print(f"  Tabelas verificadas: {total_tabelas}")
    print(f"  Arquivos varridos:   {total_arquivos}")
    print(f"  ✅ OK:               {total_ok}")
    print(f"  ❌ Erros:            {total_erros}")
    print(f"  ⚠️  Avisos:           {total_avisos}")
    print(f"{'=' * 60}")

    if total_erros == 0:
        print("  🎉 Bronze APROVADA — Todos os schemas estão em conformidade!")
    else:
        print("  🚨 Bronze REPROVADA — Corrija os erros acima antes de avançar para a Prata.")

    return total_erros


if __name__ == "__main__":
    erros = validar()
    exit(erros)
