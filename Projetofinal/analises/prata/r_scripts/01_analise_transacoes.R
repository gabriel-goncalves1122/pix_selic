# ==============================================================================
# Script 01: Análise Exploratória de Transações Pix (Camada Prata)
# ==============================================================================
# Este script utiliza a biblioteca `arrow` para ler diretamente os dados
# colunares do formato Parquet com ultra-performance e o `dplyr` para
# sumarização dos "baldes" estatísticos de transações.
# ==============================================================================

# Instalando pacotes caso não existam no ambiente
if (!requireNamespace("arrow", quietly = TRUE)) install.packages("arrow")
if (!requireNamespace("dplyr", quietly = TRUE)) install.packages("dplyr")

library(arrow)
library(dplyr)

# 1. Definir Caminho do Parquet
caminho_parquet <- "../../data/pix_limpo/estatisticas_transacoes_pix.parquet"

cat("========================================================\n")
cat("INICIANDO ANÁLISE DE TRANSAÇÕES PIX (VIA PARQUET + ARROW)\n")
cat("========================================================\n")

# 2. Leitura Preguiçosa Otimizada (Lazy Evaluation via Arrow)
# O read_parquet do Arrow não carrega tudo para a RAM imediatamente,
# ele mapeia os arquivos e traz apenas quando necessário.
cat(paste("Lendo arquivo Parquet:", caminho_parquet, "\n\n"))
df_transacoes <- arrow::read_parquet(caminho_parquet)

# 3. Análise Geral (Big Numbers)
total_transacoes <- sum(df_transacoes$quantidade, na.rm = TRUE)
total_valor_reais <- sum(df_transacoes$valor, na.rm = TRUE)

cat("1. VISÃO GERAL (MACRO)\n")
cat("----------------------------------\n")
cat(sprintf("-> Total de Baldes/Linhas: %s\n", format(nrow(df_transacoes), big.mark = ".")))
cat(sprintf("-> Total de Pix Realizados: %s de transações\n", format(total_transacoes, big.mark = ".")))
cat(sprintf("-> Volume Financeiro Total: R$ %s\n", format(total_valor_reais, big.mark = ".", scientific = FALSE)))
cat("\n")

# 4. Análise por Perfil (Pessoa Física x Pessoa Jurídica)
cat("2. QUEM ENVIA MAIS PIX? (PF vs PJ)\n")
cat("----------------------------------\n")
analise_perfil <- df_transacoes %>%
  group_by(emissor = pag_pfpj) %>%
  summarise(
    qtd_total_transacoes = sum(quantidade, na.rm = TRUE),
    volume_financeiro_BRL = sum(valor, na.rm = TRUE)
  ) %>%
  arrange(desc(qtd_total_transacoes))

print(analise_perfil)
cat("\n")

# 5. Análise Geográfica
cat("3. QUAIS REGIÕES MAIS RECEBEM PIX?\n")
cat("----------------------------------\n")
analise_regiao <- df_transacoes %>%
  group_by(regiao_recebedora = rec_regiao) %>%
  summarise(
    qtd_total_recebida = sum(quantidade, na.rm = TRUE)
  ) %>%
  arrange(desc(qtd_total_recebida))

print(analise_regiao)
cat("========================================================\n")
