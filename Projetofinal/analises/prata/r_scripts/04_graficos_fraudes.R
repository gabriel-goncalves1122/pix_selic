# ==============================================================================
# Script 04: Geração de Gráficos de Fraudes Pix MED (ggplot2)
# ==============================================================================
# Este script lê o Parquet de fraudes e gera visualizações impactantes
# focadas na segurança do ecossistema e recuperação de valores.
# ==============================================================================

if (!requireNamespace("arrow", quietly = TRUE)) install.packages("arrow")
if (!requireNamespace("dplyr", quietly = TRUE)) install.packages("dplyr")
if (!requireNamespace("ggplot2", quietly = TRUE)) install.packages("ggplot2")
if (!requireNamespace("scales", quietly = TRUE)) install.packages("scales")
if (!requireNamespace("tidyr", quietly = TRUE)) install.packages("tidyr")

library(arrow)
library(dplyr)
library(ggplot2)
library(scales)
library(tidyr)

pasta_charts <- "../charts"
caminho_parquet <- "../../data/pix_limpo/estatisticas_fraudes_pix.parquet"

cat("Lendo dados...\n")
df <- arrow::read_parquet(caminho_parquet)

cat("Processando Gráfico 1: Evolução das Contas Laranjas...\n")
# 1. Evolução das Contas Laranjas
g1 <- ggplot(df, aes(x = ano_mes_dt)) +
  geom_line(aes(y = qtd_usuarios_marcacao_fraude, color = "Usuários (CPFs) Marcados"), linewidth = 1.2) +
  geom_line(aes(y = qtd_chaves_marcacao_fraude, color = "Chaves Pix Marcadas"), linewidth = 1.2, linetype = "dashed") +
  scale_color_manual(values = c("Usuários (CPFs) Marcados" = "#D62828", "Chaves Pix Marcadas" = "#F77F00")) +
  scale_y_continuous(labels = label_number(scale_cut = cut_short_scale())) +
  labs(
    title = "Crescimento de Contas Laranjas no Brasil",
    subtitle = "Evolução mensal de marcadores de fraude na infraestrutura Pix",
    x = "Mês/Ano",
    y = "Quantidade de Infratores / Chaves",
    color = "Indicador",
    caption = "Fonte: Banco Central do Brasil (API Olinda)"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(face = "bold", size = 16),
    legend.position = "bottom"
  )

ggsave(file.path(pasta_charts, "fraudes_contas_laranjas.png"), plot = g1, width = 10, height = 6, dpi = 300)

cat("Processando Gráfico 2: O Funil da Fraude (MED)...\n")
# 2. O Funil da Fraude (Como o dinheiro desaparece)
# Vamos somar os totais para criar um funil simples de volume
totais_med <- df %>%
  summarise(
    Contestados = sum(qtd_pix_contestados, na.rm = TRUE),
    Aceitos = sum(qtd_contestacoes_aceitas, na.rm = TRUE),
    Devolvidos = sum(qtd_devolvida_integral_med, na.rm = TRUE) + sum(qtd_devolvida_parcial_med, na.rm = TRUE)
  )

df_funil <- data.frame(
  Etapa = factor(c("1. Contestados", "2. Aceitos (Fraude)", "3. Devolvidos (Parcial/Integral)"), 
                 levels = c("1. Contestados", "2. Aceitos (Fraude)", "3. Devolvidos (Parcial/Integral)")),
  Volume = c(totais_med$Contestados, totais_med$Aceitos, totais_med$Devolvidos)
)

g2 <- ggplot(df_funil, aes(x = Etapa, y = Volume, fill = Etapa)) +
  geom_col(width = 0.6, show.legend = FALSE) +
  geom_text(aes(label = format(Volume, big.mark=".", scientific=FALSE)), vjust = -0.5, fontface = "bold") +
  scale_fill_manual(values = c("#118AB2", "#FFD166", "#06D6A0")) +
  scale_y_continuous(labels = label_number(scale_cut = cut_short_scale()), limits = c(0, max(df_funil$Volume) * 1.1)) +
  labs(
    title = "O Funil do MED: Dificuldade de Recuperação",
    subtitle = "De 53 Milhões de contestações, a minoria termina em devolução de fato",
    x = "Etapa do Processo MED",
    y = "Quantidade de Ocorrências",
    caption = "Fonte: Banco Central do Brasil (API Olinda)"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(face = "bold", size = 16),
    axis.text.x = element_text(face = "bold", size = 11)
  )

ggsave(file.path(pasta_charts, "fraudes_funil_med.png"), plot = g2, width = 9, height = 6, dpi = 300)

cat("Gráficos de Fraudes gerados com sucesso na pasta 'charts/'.\n")
