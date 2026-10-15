#!/bin/bash

# Entra na pasta atual do script (src/macro) não importa de onde o bash for chamado
cd "$(dirname "$0")"

echo "============================================================"
echo "Iniciando Ingestão Sequencial Macro (Camada Bronze)"
echo "============================================================"
echo ""

echo "▶ 1. Ingestão do SGS (Selic Histórica e IPCA)..."
python3 ingestao_sgs_realizado.py
echo ""

echo "▶ 2. Ingestão do Olinda (Expectativas Focus)..."
python3 ingestao_olinda_expectativas.py
echo ""

echo "▶ 3. Ingestão do Olinda (Selic Operações - Volumes)..."
python3 ingestao_olinda_selic_operacoes.py
echo ""

echo "▶ 4. Ingestão do Olinda (IFDATA - Balanço Bancário)..."
python3 ingestao_olinda_ifdata.py
echo ""

echo "============================================================"
echo "Ingestão Macroeconômica Concluída!"
echo "============================================================"
