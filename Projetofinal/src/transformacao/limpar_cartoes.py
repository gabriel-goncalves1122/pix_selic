import logging
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent.parent
for pasta in (RAIZ / "src", Path(__file__).resolve().parent):
    if str(pasta) not in sys.path:
        sys.path.insert(0, str(pasta))

import config
from comum import converter_numero_br, registrar_proveniencia, salvar_prata

log = logging.getLogger(__name__)


def transformar_cartoes(df_bruto: pd.DataFrame) -> pd.DataFrame:
    """Funcao pura: limpa e filtra estatisticas trimestrais de cartoes (MPV_DadosAbertos)."""
    df = df_bruto.copy()
    df["trimestre"] = pd.to_numeric(df["trimestre"], errors="coerce").astype("int64")
    df = df[df["trimestre"] >= 20201].copy()

    out = pd.DataFrame({
        "trimestre": df["trimestre"],
        "ano": (df["trimestre"] // 10).astype("int64"),
        "trimestre_num": (df["trimestre"] % 10).astype("int64"),
        "ano_trimestre": (df["trimestre"] // 10).astype(str) + "-T" + (df["trimestre"] % 10).astype(str),
        "nome_bandeira": df["nomeBandeira"].astype(str).str.strip(),
        "nome_funcao": df["nomeFuncao"].astype(str).str.strip(),
        "modalidade": df["modalidade"].astype(str).str.strip(),
        "qtd_cartoes_ativos": converter_numero_br(df["qtdCartoesAtivos"]).fillna(0).astype("int64"),
        "qtd_transacoes_nacionais": converter_numero_br(df["qtdTransacoesNacionais"]).fillna(0).astype("int64"),
        "valor_transacoes_nacionais": converter_numero_br(df["valorTransacoesNacionais"]).fillna(0.0),
        "qtd_transacoes_internacionais": converter_numero_br(df["qtdTransacoesInternacionais"]).fillna(0).astype("int64"),
        "valor_transacoes_internacionais": converter_numero_br(df["valorTransacoesInternacionais"]).fillna(0.0),
    })

    out["qtd_transacoes_total"] = out["qtd_transacoes_nacionais"] + out["qtd_transacoes_internacionais"]
    out["valor_transacoes_total"] = (
        out["valor_transacoes_nacionais"] + out["valor_transacoes_internacionais"]
    ).round(2)

    # Remove combinacoes sem nenhuma movimentacao
    out = out[(out["qtd_transacoes_total"] > 0) | (out["valor_transacoes_total"] > 0)].copy()
    return out.sort_values(["trimestre", "nome_funcao", "nome_bandeira"]).reset_index(drop=True)


def main():
    arq_bruto = (
        config.BRONZE_MPV
        / "Quantidadeetransacoesdecartoes"
        / "Quantidadeetransacoesdecartoes_20201.csv"
    )
    if not arq_bruto.exists():
        raise FileNotFoundError(f"Arquivo Bronze nao encontrado: {arq_bruto}")

    df_bruto = pd.read_csv(arq_bruto)
    df_limpo = transformar_cartoes(df_bruto)

    destino = config.PRATA_MPV / "cartoes_trimestral.parquet"
    salvar_prata(df_limpo, destino, gerar_csv=False)
    registrar_proveniencia(
        origem=arq_bruto.name,
        destino=destino,
        linhas_antes=len(df_bruto),
        linhas_depois=len(df_limpo),
        decisoes=[
            "mantidos apenas trimestres >= 20201 e combinacoes com transacoes > 0",
            "descartadas colunas produto e qtdCartoesEmitidos (foco em ativos e transacoes)",
            "valores PT-BR convertidos para float64 e totais consolidados",
        ],
    )


if __name__ == "__main__":
    config.configurar_log()
    main()
