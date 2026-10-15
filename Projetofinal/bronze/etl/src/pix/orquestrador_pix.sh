#!/bin/bash

# ==============================================================================
# Script de Orquestração — Execução Sequencial da Ingestão Pix
# ==============================================================================
# Entra na pasta atual do script (src/pix) não importa de onde o bash for chamado
cd "$(dirname "$0")"

echo "============================================================"
echo "Iniciando Ingestão Sequencial do PIX (Camada Bronze)"
echo "============================================================"
echo ""

echo "▶ 1. Baixando Cadastros..."
python3 ingestao_cadastros.py
echo ""

echo "▶ 2. Baixando Transações..."
python3 ingestao_transacoes.py
echo ""

echo "▶ 3. Baixando Fraudes..."
python3 ingestao_fraudes.py
echo ""

echo "▶ 4. Baixando SPI..."
python3 ingestao_spi.py
echo ""

echo "============================================================"
echo "Ingestão Concluída com Sucesso!"
echo "============================================================"
