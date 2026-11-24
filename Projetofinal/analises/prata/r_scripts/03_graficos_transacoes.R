# ==============================================================================
# Script 03: Geração de Gráficos de Transações Pix (ggplot2)
# ==============================================================================
# Este script lê o Parquet de transações e gera gráficos de alta 
# qualidade para inclusão no TCC/Relatório final.
# ==============================================================================

if (!requireNamespace("arrow", quietly = TRUE)) install.packages("arrow")
if (!requireNamespace("dplyr", quietly = TRUE)) install.packages("dplyr")
if (!requireNamespace("ggplot2", quietly = TRUE)) install.packages("ggplot2")
if (!requireNamespace("scales", quietly = TRUE)) install.packages("scales")
if (!requireNamespace("lubridate", quietly = TRUE)) install.packages("lubridate")

library(arrow)
library(dplyr)
library(ggplot2)
library(scales)
library(lubridate)

# Criar pasta de destino caso não exista
pasta_charts <- "../charts"
if (!dir.exists(pasta_charts)) {
  dir.create(pasta_charts, recursive = TRUE)
}

caminho_parquet <- "../../data/pix_limpo/estatisticas_transacoes_pix.parquet"
cat("Lendo dados...\n")
df <- arrow::read_parquet(caminho_parquet)

cat("Processando Gráfico 1: Adoção Temporal...\n")
# 1. Curva de Adoção (Volume por Mês)
df_temporal <- df %>%
  group_by(ano_mes_dt) %>%
  summarise(total_transacoes = sum(quantidade, na.rm = TRUE))

g1 <- ggplot(df_temporal, aes(x = ano_mes_dt, y = total_transacoes)) +
  geom_line(color = "#00B4D8", linewidth = 1.5) +
  geom_point(color = "#0077B6", size = 2) +
  scale_y_continuous(labels = label_number(scale_cut = cut_short_scale())) +
  labs(
    title = "Evolução Temporal do Volume de Transações Pix",
    subtitle = "Crescimento exponencial desde Nov/2020",
    x = "Mês/Ano",
    y = "Quantidade de Transações",
    caption = "Fonte: Banco Central do Brasil (API Olinda)"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(face = "bold", size = 16),
    plot.subtitle = element_text(color = "gray30", size = 12)
  )

ggsave(file.path(pasta_charts, "pix_evolucao_temporal.png"), plot = g1, width = 10, height = 6, dpi = 300)

cat("Processando Gráfico 2: Perfis PF vs PJ...\n")
# 2. Guerra de Perfis (PF vs PJ)
df_perfil <- df %>%
  filter(pag_pfpj %in% c("PF", "PJ")) %>%
  group_by(pag_pfpj) %>%
  summarise(
    Transacoes = sum(quantidade, na.rm = TRUE),
    Financeiro_BRL = sum(valor, na.rm = TRUE)
  )

g2 <- ggplot(df_perfil, aes(x = pag_pfpj, y = Financeiro_BRL, fill = pag_pfpj)) +
  geom_col(show.legend = FALSE) +
  scale_fill_manual(values = c("PF" = "#48CAE4", "PJ" = "#023E8A")) +
  scale_y_continuous(labels = label_number(scale_cut = cut_short_scale(), prefix = "R$ ")) +
  labs(
    title = "Volume Financeiro Movimentado: PF vs PJ",
    subtitle = "Empresas movimentam a maior fatia financeira do sistema",
    x = "Tipo de Emissor",
    y = "Volume Financeiro Acumulado",
    caption = "Fonte: Banco Central do Brasil (API Olinda)"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(face = "bold", size = 16)
  )

ggsave(file.path(pasta_charts, "pix_volume_pf_pj.png"), plot = g2, width = 8, height = 6, dpi = 300)

cat("Processando Gráfico 3: Distribuição Geográfica...\n")
# 3. Distribuição Geográfica
df_regiao <- df %>%
  filter(rec_regiao != "Nao informado") %>%
  group_by(rec_regiao) %>%
  summarise(total_recebido = sum(quantidade, na.rm = TRUE)) %>%
  mutate(prop = total_recebido / sum(total_recebido) * 100)

g3 <- ggplot(df_regiao, aes(x = reorder(rec_regiao, prop), y = prop, fill = rec_regiao)) +
  geom_col(show.legend = FALSE) +
  coord_flip() +
  geom_text(aes(label = sprintf("%.1f%%", prop)), hjust = -0.1) +
  scale_fill_brewer(palette = "Blues") +
  labs(
    title = "Distribuição Geográfica do Pix no Brasil",
    subtitle = "Proporção de transações recebidas por região",
    x = "Região",
    y = "Proporção (%) das Transações",
    caption = "Fonte: Banco Central do Brasil (API Olinda)"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(face = "bold", size = 16)
  )

ggsave(file.path(pasta_charts, "pix_geografia.png"), plot = g3, width = 10, height = 6, dpi = 300)

cat("Gráficos de Transações gerados com sucesso na pasta 'charts/'.\n")
