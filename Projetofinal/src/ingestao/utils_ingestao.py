import json
import logging
import time
from datetime import datetime, date
from pathlib import Path

import requests

log = logging.getLogger(__name__)

# ==============================================================================
# Script Utilitário — Camada Bronze (Raw)
# Fonte: API OData do Banco Central do Brasil (Olinda)
#
# REGRAS CRÍTICAS DA API:
#   1. naoPaginavel = true → NÃO usar $top / $skip (causa HTTP 500)
#   2. Rate-limiting por DNS → mínimo 1s entre requests
#   3. Timeout de 180s → respostas podem ter 500K+ registros e demorar muito
# ==============================================================================

def gerar_periodos_mensais(ano_inicio=2020, mes_inicio=11):
    """Gera lista de períodos YYYYMM desde Nov/2020 até o mês atual."""
    periodos = []
    ano_atual = date.today().year
    mes_atual = date.today().month

    for ano in range(ano_inicio, ano_atual + 1):
        inicio = mes_inicio if ano == ano_inicio else 1
        fim = mes_atual if ano == ano_atual else 12
        for mes in range(inicio, fim + 1):
            periodos.append(f"{ano}{mes:02d}")
    return periodos


def salvar(texto_csv, pasta_destino, tabela, sufixo_periodo=""):
    """Salva o CSV bruto da resposta da API em disco."""
    pasta_destino.mkdir(parents=True, exist_ok=True)

    if sufixo_periodo:
        nome_arquivo = f"{tabela}_{sufixo_periodo}.csv"
    else:
        nome_arquivo = f"{tabela}.csv"

    destino = pasta_destino / nome_arquivo

    with open(destino, 'w', encoding='utf-8') as f:
        f.write(texto_csv)

    return destino


def registrar(pasta_destino, destino_arquivo, url, total_registros):
    """Registra metadados de proveniência da extração."""
    info = {
        "fonte": url,
        "arquivo_bronze": destino_arquivo.name,
        "registros_extraidos": total_registros,
        "extraido_em": datetime.now().isoformat(),
    }

    arquivo_proveniencia = pasta_destino / "proveniencia.json"
    lista_info = []
    if arquivo_proveniencia.exists():
        try:
            with open(arquivo_proveniencia, 'r', encoding='utf-8') as f:
                conteudo = json.load(f)
                lista_info = conteudo if isinstance(conteudo, list) else [conteudo]
        except Exception:
            pass

    lista_info.append(info)

    with open(arquivo_proveniencia, 'w', encoding='utf-8') as f:
        json.dump(lista_info, f, indent=2, ensure_ascii=False)


# Criação de Sessão Global para reaproveitar as conexões TCP (Keep-Alive)
session = requests.Session()
# Camuflagem de Navegador para evitar bloqueios WAF (F5 BIG-IP do BCB)
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "text/csv,application/json,*/*",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
})

def fazer_request(url, max_tentativas=5):
    """Faz GET com retry e backoff longo, inclusive para Erros 5xx."""
    backoffs = [15, 30, 60, 120]
    for tentativa in range(max_tentativas):
        try:
            # Timeout de 180s conforme documentado no cabecalho (respostas podem ter 500K+ registros)
            res = session.get(url, timeout=180)
            # Força exceção caso o servidor retorne Erro (ex: 504 Gateway Timeout)
            if res.status_code in [500, 502, 503, 504]:
                res.raise_for_status()
            
            # Pacing: Espera educada após sucesso para não disparar gatilhos Anti-DDoS
            if res.status_code == 200:
                time.sleep(1.5)
                
            return res
        except Exception as e:
            espera = backoffs[tentativa] if tentativa < len(backoffs) else 120
            log.warning("Erro de conexao/API (tentativa %s/%s): %s", tentativa + 1, max_tentativas, e)
            if tentativa < max_tentativas - 1:
                log.info("Aguardando %ss antes de tentar novamente...", espera)
                time.sleep(espera)
    return None


import urllib.parse

def extrair_tabela(servico, tabela, pasta_destino, param_name=None, ciclos=None, odata_filter=None):
    """Extrai uma tabela da API do Olinda (sem $top/$skip, conforme naoPaginavel=true)."""
    if ciclos is None:
        ciclos = [None]

    for ciclo in ciclos:
        sufixo = ciclo.replace("-", "") if ciclo else ""
        
        # Lógica de Checkpoint: Verifica se já foi baixado
        nome_arquivo_esperado = f"{tabela}_{sufixo}.csv" if sufixo else f"{tabela}.csv"
        caminho_arquivo_esperado = pasta_destino / nome_arquivo_esperado
        
        if caminho_arquivo_esperado.exists() and sufixo: # Pula apenas se tiver sufixo (ex: mes), atualiza se for estoque geral
            log.info("[%s] Pulado (ja existe: %s)", ciclo or "geral", nome_arquivo_esperado)
            continue

        # Montar URL (SEM $top e $skip!)
        if param_name and ciclo:
            url = (
                f"https://olinda.bcb.gov.br/olinda/servico/{servico}/versao/v1/odata/"
                f"{tabela}({param_name}='{ciclo}')?$format=text/csv"
            )
        else:
            url = (
                f"https://olinda.bcb.gov.br/olinda/servico/{servico}/versao/v1/odata/"
                f"{tabela}?$format=text/csv"
            )

        if odata_filter:
            filtro_formatado = odata_filter.replace("{ciclo}", ciclo) if ciclo else odata_filter
            url += f"&$filter={urllib.parse.quote(filtro_formatado)}"

        res = fazer_request(url)

        if res is None:
            log.error("FALHA apos 5 tentativas (%s). URL: %s", tabela, url)
            continue

        if res.status_code == 200:
            texto_csv = res.text

            # Se for vazio ou só tiver cabeçalho, \n count será 0
            qtd_linhas = texto_csv.strip().count('\n')

            if not texto_csv.strip() or qtd_linhas == 0:
                log.warning("%s [%s]: Vazio (0 registros).", tabela, ciclo or "geral")
                continue

            sufixo = ciclo.replace("-", "") if ciclo else ""
            destino_arquivo = salvar(texto_csv, pasta_destino, tabela, sufixo)
            registrar(pasta_destino, destino_arquivo, url, qtd_linhas)
            log.info("%s [%s]: %s registros -> %s", tabela, ciclo or "geral", qtd_linhas, destino_arquivo.name)
        else:
            log.error("%s [%s]: HTTP %s. URL: %s", tabela, ciclo or "geral", res.status_code, url)

        # Rate-limiting: esperar 1s entre requests
        time.sleep(1)
