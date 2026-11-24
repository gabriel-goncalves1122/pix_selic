"""
Gera data/metricas.json com números reais Bronze x Prata para a apresentação.
Uso (na raiz do workspace):  venv/bin/python Projetofinal/apresentacao/gerar_metricas.py
"""
import json
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).parent
PROJ = AQUI.parent
BRONZE = PROJ / "dados" / "bronze" / "pix_bruto" / "Pix_DadosAbertos"
PRATA = PROJ / "dados" / "prata" / "pix_limpo"

DATASETS = {
    "transacoes": (BRONZE / "EstatisticasTransacoesPix" / "EstatisticasTransacoesPix_202011.csv",
                   PRATA / "estatisticas_transacoes_pix.parquet"),
    "fraudes": (BRONZE / "EstatisticasFraudesPix" / "EstatisticasFraudesPix_202011.csv",
                PRATA / "estatisticas_fraudes_pix.parquet"),
}


def perfil(df: pd.DataFrame) -> dict:
    tipos = df.dtypes.astype(str)
    return {
        "linhas": int(len(df)),
        "colunas": int(df.shape[1]),
        "texto": int((tipos.isin(["object", "str", "string"])).sum()),
        "numericas": int(df.select_dtypes("number").shape[1]),
        "nulos": int(df.isna().sum().sum()),
        "dtypes": {c: t for c, t in tipos.items()},
        "amostra": json.loads(df.head(3).astype(str).to_json(orient="records", force_ascii=False)),
    }


def tamanho_mb(p: Path) -> float:
    if p.is_dir():
        return round(sum(f.stat().st_size for f in p.rglob("*") if f.is_file()) / 2**20, 1)
    return round(p.stat().st_size / 2**20, 2)


def main():
    out = {"datasets": {}, "staircase": {}}
    for nome, (b, p) in DATASETS.items():
        bronze = pd.read_csv(b)
        prata = pd.read_parquet(p)
        out["datasets"][nome] = {
            "bronze": perfil(bronze) | {"mb": tamanho_mb(b)},
            "prata": perfil(prata) | {"mb_parquet": tamanho_mb(p)},
        }
    pasta = BRONZE / "EstatisticasTransacoesPix"
    out["staircase"] = {
        "arquivos": len(list(pasta.glob("*.csv"))),
        "mb_total": tamanho_mb(pasta),
        "mb_usado": tamanho_mb(DATASETS["transacoes"][0]),
    }
    destino = AQUI / "data" / "metricas.json"
    destino.parent.mkdir(exist_ok=True)
    destino.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    # também como JS, para funcionar abrindo o index.html direto (file://)
    (AQUI / "data" / "metricas.js").write_text("window.METRICAS = " + json.dumps(out, ensure_ascii=False) + ";")
    for n, d in out["datasets"].items():
        print(n, {k: {x: d[k][x] for x in ("linhas", "colunas", "texto", "numericas", "nulos")} for k in ("bronze", "prata")})
    print("staircase", out["staircase"])


if __name__ == "__main__":
    main()
