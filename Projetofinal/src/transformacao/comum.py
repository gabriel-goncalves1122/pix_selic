"""Funcoes compartilhadas de limpeza, persistencia e proveniencia na Camada Prata."""
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent.parent
if str(RAIZ / "src") not in sys.path:
    sys.path.insert(0, str(RAIZ / "src"))

import config

log = logging.getLogger(__name__)


def converter_numero_br(serie: pd.Series) -> pd.Series:
    """Converte strings numericas no padrao PT-BR ('1.234,56') para float64."""
    if pd.api.types.is_numeric_dtype(serie):
        return pd.to_numeric(serie, errors="coerce")
    limpa = (
        serie.astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    return pd.to_numeric(limpa, errors="coerce")


def salvar_prata(
    df: pd.DataFrame,
    destino_parquet: Path,
    gerar_csv: bool = False,
) -> Path:
    """Grava DataFrame em Parquet (Snappy) na Prata e opcionalmente em CSV."""
    destino_parquet.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(destino_parquet, engine="pyarrow", index=False, compression="snappy")
    if gerar_csv:
        df.to_csv(destino_parquet.with_suffix(".csv"), index=False)

    tamanho_mb = destino_parquet.stat().st_size / (1024 * 1024)
    log.info(
        "prata salvo: %s (%s linhas, %.2f MB)",
        destino_parquet.name,
        len(df),
        tamanho_mb,
    )
    return destino_parquet


def registrar_proveniencia(
    origem: str,
    destino: Path,
    linhas_antes: int,
    linhas_depois: int,
    decisoes: list[str],
    extras: dict | None = None,
) -> Path:
    """Registra linhagem e decisoes de tratamento em dados/prata/proveniencia.jsonl."""
    config.PRATA.mkdir(parents=True, exist_ok=True)
    info = {
        "origem": origem,
        "arquivo_prata": destino.name,
        "linhas_antes": int(linhas_antes),
        "linhas_depois": int(linhas_depois),
        "decisoes": decisoes,
        "transformado_em": datetime.now().isoformat(timespec="seconds"),
    }
    if extras:
        info.update(extras)

    caminho = config.PRATA / "proveniencia.jsonl"
    with caminho.open("a", encoding="utf-8") as f:
        f.write(json.dumps(info, ensure_ascii=False) + "\n")
    return caminho
