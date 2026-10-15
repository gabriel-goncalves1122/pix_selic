# ==============================================================================
# Script 02: Análise Exploratória de Fraudes Pix MED (Camada Prata)
# ==============================================================================
# Este script utiliza a biblioteca `arrow` para ler diretamente os dados
# colunares do formato Parquet. Em seguida, calcula métricas de sucesso 
# do Mecanismo Especial de Devolução (MED) e avalia tendências de bloqueios.
# ==============================================================================

if (!requireNamespace("arrow", quietly = TRUE)) install.packages("arrow")
if (!requireNamespace("dplyr", quietly = TRUE)) install.packages("dplyr")

library(arrow)
library(dplyr)

caminho_parquet <- "../../data/pix_limpo/estatisticas_fraudes_pix.parquet"

cat("========================================================\n")
cat("INICIANDO ANÁLISE DE FRAUDES PIX MED (VIA PARQUET + ARROW)\n")
cat("========================================================\n")

cat(paste("Lendo arquivo Parquet:", caminho_parquet, "\n\n"))
df_fraudes <- arrow::read_parquet(caminho_parquet)

cat("1. VISÃO GERAL DE FRAUDES (MACRO)\n")
cat("----------------------------------\n")
total_pix_contestados <- sum(df_fraudes$qtd_pix_contestados, na.rm = TRUE)
total_fraudes_aceitas <- sum(df_fraudes$qtd_contestacoes_aceitas, na.rm = TRUE)

cat(sprintf("-> Pix Totais Contestados: %s\n", format(total_pix_contestados, big.mark = ".")))
cat(sprintf("-> Contestacoes Aceitas (Fraude Confirmada): %s\n", format(total_fraudes_aceitas, big.mark = ".")))
cat("\n")

cat("2. ANÁLISE DE SUCESSO DO M.E.D (Mecanismo Especial de Devolução)\n")
cat("----------------------------------\n")
# Analisando a quantidade de vezes que o dinheiro foi devolvido
analise_med <- df_fraudes %>%
  summarise(
    total_devolvido_integral = sum(qtd_devolvida_integral_med, na.rm = TRUE),
    total_devolvido_parcial = sum(qtd_devolvida_parcial_med, na.rm = TRUE),
    total_nao_devolvido = sum(qtd_nao_devolvida_saldo_insuficiente, na.rm = TRUE) + 
                          sum(qtd_nao_devolvida_conta_encerrada, na.rm = TRUE)
  )

print(analise_med)
cat("\n")

cat("3. TENDÊNCIAS MENTAIS (Média de Contas e Chaves Marcadas por Fraude)\n")
cat("----------------------------------\n")
tendencias <- df_fraudes %>%
  summarise(
    media_mensal_usuarios_marcados = mean(qtd_usuarios_marcacao_fraude, na.rm = TRUE),
    media_mensal_chaves_marcadas = mean(qtd_chaves_marcacao_fraude, na.rm = TRUE)
  )

cat(sprintf("-> Média Mensal de Usuários Infratores: %s\n", format(round(tendencias$media_mensal_usuarios_marcados), big.mark = ".")))
cat(sprintf("-> Média Mensal de Chaves Infratoras: %s\n", format(round(tendencias$media_mensal_chaves_marcadas), big.mark = ".")))

cat("========================================================\n")
