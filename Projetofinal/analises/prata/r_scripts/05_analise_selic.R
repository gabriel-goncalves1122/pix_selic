# ==============================================================================
# Script 05: Análise Exploratória da Taxa e Operações Selic (Camada Prata)
# ==============================================================================
# Este script utiliza a biblioteca `arrow` para ler diretamente os dados
# colunares do formato Parquet com ultra-performance e o `dplyr` para
# sumarização dos ciclos de juros e volume de títulos públicos.
# ==============================================================================

if (!requireNamespace("arrow", quietly = TRUE)) install.packages("arrow")
if (!requireNamespace("dplyr", quietly = TRUE)) install.packages("dplyr")

library(arrow)
library(dplyr)

# 1. Definir Caminhos dos Parquets
caminho_taxa <- "../../data/macro_limpo/taxa_selic_mensal.parquet"
caminho_operacoes <- "../../data/macro_limpo/operacoes_selic.parquet"

cat("========================================================\n")
cat("INICIANDO ANÁLISE MACROECONÔMICA DA SELIC (PARQUET + ARROW)\n")
cat("========================================================\n\n")

# 2. Leitura dos Dados
cat(paste("Lendo Parquet Taxa Selic:", caminho_taxa, "\n"))
df_taxa <- arrow::read_parquet(caminho_taxa)

cat(paste("Lendo Parquet Operações Selic:", caminho_operacoes, "\n\n"))
df_operacoes <- arrow::read_parquet(caminho_operacoes)

# 3. Visão da Taxa de Juros (Ciclo Selic)
cat("1. CICLO HISTÓRICO DA TAXA SELIC (% a.a.)\n")
cat("--------------------------------------------------------\n")
min_selic <- min(df_taxa$selic_meta_fim_mes, na.rm = TRUE)
max_selic <- max(df_taxa$selic_meta_fim_mes, na.rm = TRUE)
media_selic <- mean(df_taxa$selic_meta_media_mes, na.rm = TRUE)
mes_min <- df_taxa$ano_mes[which.min(df_taxa$selic_meta_fim_mes)]
mes_max <- df_taxa$ano_mes[which.max(df_taxa$selic_meta_fim_mes)]

cat(sprintf("-> Menor Selic Meta: %.2f%% a.a. (no mês %s)\n", min_selic, mes_min))
cat(sprintf("-> Maior Selic Meta: %.2f%% a.a. (no mês %s)\n", max_selic, mes_max))
cat(sprintf("-> Taxa Selic Média Histórica: %.2f%% a.a.\n", media_selic))
cat(sprintf("-> Total de Meses Monitorados: %d\n\n", nrow(df_taxa)))

# 4. Visão das Operações de Liquidação de Títulos
cat("2. OPERAÇÕES DE TÍTULOS PÚBLICOS NO SELIC (TOP CATEGORIAS)\n")
cat("--------------------------------------------------------\n")
resumo_operacoes <- df_operacoes %>%
  group_by(categoria = categoria_operacao) %>%
  summarise(
    qtd_total_transacoes = sum(qtd_acumulada, na.rm = TRUE),
    volume_total_milhoes_BRL = sum(valor_acumulado_milhoes, na.rm = TRUE)
  ) %>%
  arrange(desc(volume_total_milhoes_BRL))

print(head(resumo_operacoes, 7))

cat("\n========================================================\n")
cat("ANÁLISE DA SELIC CONCLUÍDA COM SUCESSO!\n")
cat("========================================================\n")
