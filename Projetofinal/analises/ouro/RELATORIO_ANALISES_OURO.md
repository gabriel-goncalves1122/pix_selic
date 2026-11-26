# Relatório Analítico da Camada Ouro — Teorias, Gráficos e Evidências

**Projeto:** Radiografia do Pix no Brasil (ECOX14 — UNIFEI)  
**Fonte:** Camada Ouro (`dados/ouro/projeto.duckdb`, modelada via dbt sobre APIs BCB Olinda & SGS)  
**Janela Analisada:** Novembro/2020 a Outubro/2026 (`72 meses`)

---

## 1. Síntese Executiva (Big Numbers da Camada Ouro)

| Indicador | Resultado Consolidado (`2020-11` a `2026-10`) |
| :--- | :--- |
| **Quantidade Total de Transações Pix** | **261,31 bilhões** |
| **Volume Financeiro Nominal** | **R$ 110,40 trilhões** |
| **Volume Real Deflacionado (IPCA base 2026-10)** | **R$ 120,43 trilhões** |
| **Ticket Médio Geral / Evolução** | **R$ 466,36** (caiu de R$ 876,20 em `2020-11` para R$ 445,15 em `2026-10`) |
| **Share do Pix vs. Cartões (`2026-T2`)** | **63,6%** das transações e **88,6%** do volume financeiro |
| **Participação PJ no Valor (`2020-11` → `2026-10`)** | **47,83% → 64,15%** |
| **Perda Líquida no MED (`2022-01` a `2026-09`)** | **R$ 24,99 bilhões** não devolvidos (de R$ 27,57 bi contestados e aceitos) |

---

## 2. Eixo 1 — Macroeconomia & Juro Real (Aba 1)

### Gráfico 1.1: Volume Pix Nominal vs. Real Deflacionado (IPCA)
- **Pergunta:** *Quanto do crescimento explosivo do Pix é expansão real de uso e quanto é apenas efeito inflacionário?*
- **Teoria / Hipótese:** Pela distinção clássica entre valores nominais e reais (*ilusão monetária*), comparar séries financeiras plurianuais sem deflação superestima o crescimento recente após choques inflacionários (como o pico do IPCA em 2021–2022). Deflacionar o volume pela série mensal do IPCA (SGS 433) traz toda a série para o poder de compra constante do último mês (`2026-10`).
- **O que os dados dizem:**
  - O volume mensal saltou de **R$ 25,87 bi** nominais (**R$ 36,34 bi** reais) em `2020-11` para **R$ 3,28 trilhões** em `2026-10` — uma multiplicação real de **~90 vezes** em 6 anos.
  - A área sombreada entre a curva nominal e a real evidencia a **erosão inflacionária acumulada** no acumulado histórico: a soma nominal é **R$ 110,40 tri**, que corrigida pelo IPCA equivale a **R$ 120,43 tri** a preços de `2026-10`.

### Gráfico 1.2: Política Monetária (Selic Meta, IPCA 12m e Juro Real Ex-Post)
- **Pergunta:** *Em quais regimes monetários (juro real negativo vs. restritivo) ocorreu a consolidação do Pix?*
- **Teoria / Hipótese:** Pela **Equação de Fisher** ($1 + r = \frac{1 + i}{1 + \pi}$), o juro real *ex-post* mede o aperto monetário efetivo descontando a inflação acumulada em 12 meses. Regimes de juro real negativo estimulam consumo e giro de curto prazo; regimes restritivos encarecem o crédito tradicional.
- **O que os dados dizem:**
  - A série atravessou dois regimes opostos: **15 meses com juro real negativo** (mínimo de **-4,35% a.a.**, quando a Selic partiu de **2,00%** e o IPCA 12m atingiu **12,13%**), seguidos por um longo ciclo restritivo até o pico da Selic em **15,00% a.a.** e juro real máximo de **10,78% a.a.** (média do período: **5,29% a.a.**).

### Gráfico 1.3: Dispersão Macro (Juro Real % × Volume Real do Pix)
- **Pergunta:** *O aperto monetário (juros altos) freou a adoção do Pix?*
- **Teoria / Hipótese:** Se o Pix dependesse apenas de aquecimento cíclico da economia, esperar-se-ia correlação negativa ou estagnação quando o juro real subisse acima de 6% a.a. Por outro lado, pela hipótese do **custo de oportunidade da liquidez e substituição do crédito caro**, juros altos tornam pagamentos à vista instantâneos mais atrativos que linhas rotativas.
- **O que os dados dizem:**
  - A correlação linear entre juro real e volume real é fortemente positiva (**$r = 0{,}81$**; Selic vs. volume real: **$r = 0{,}72$**). Isso não significa causalidade direta dos juros sobre o Pix, mas comprova que a **curva de adoção estrutural do Pix foi imune ao aperto monetário** e continuou ganhando escala mesmo com juro real acima de 8% a.a.

---

## 3. Eixo 2 — Substituição de Meios de Pagamento (Aba 2)

### Gráfico 2.1: Share de Quantidade Trimestral (Pix × Cartões — Área Empilhada 100%)
- **Pergunta:** *Qual meio de pagamento perdeu mais participação relativa com a ascensão do Pix?*
- **Teoria / Hipótese:** Pela teoria da **difusão de inovações e canibalização de substitutos próximos**, um meio instantâneo sem tarifa para PF substitui primeiro os instrumentos de débito imediato (Cartão de Débito e Pré-Pago) antes de atingir o Crédito (que oferece prazo/parcelamento).
- **O que os dados dizem:**
  - Entre `2021-T1` e `2026-T2`, o **Pix saltou de 10,8% para 63,6%** da quantidade total de transações (de 0,73 bi para 20,78 bi/trimestre).
  - Como previsto pela teoria, o **Cartão de Débito** sofreu a maior compressão: despencou de **44,8%** (líder em `2021-T1`) para **12,5%** em `2026-T2`. O **Crédito** caiu de **38,7%** para **18,0%** (preservado pela função de financiamento), e o **Pré-Pago** manteve nicho em **5,9%**.

### Gráfico 2.2: Volume Financeiro e Ticket Médio no Último Trimestre (`2026-T2`)
- **Pergunta:** *Os cartões ainda competem em volume financeiro ou apenas em nichos específicos?*
- **Teoria / Hipótese:** Instrumentos com custo zero por transação e liquidação instantânea atraem desde micro-pagamentos até liquidações B2B de alto valor, enquanto o cartão fica restrito ao varejo presencial/online parcelado.
- **O que os dados dizem (`2026-T2`):**
  - O **Pix responde por 88,6% de todo o volume financeiro** (**R$ 8,90 tri** no trimestre, ticket médio **R$ 428,16**).
  - O **Crédito** aparece em 2º com **8,3%** (**R$ 0,83 tri**, ticket **R$ 141,15**), seguido por **Débito** (**2,4%**, **R$ 0,24 tri**, ticket **R$ 57,82**) e **Pré-Pago** (**0,8%**, **R$ 0,08 tri**, ticket **R$ 41,10**).

### Gráfico 2.3: Meios Tradicionais Mensais (TED, Boleto, Cheque e DOC — Escala Logarítmica)
- **Pergunta:** *O Pix eliminou a TED, o Boleto, o Cheque e o DOC?*
- **Teoria / Hipótese:** Trilhos legados caros e lentos para o varejo (DOC e Cheque) tendem à extinção; já trilhos corporativos de altíssimo valor unitário (TED) ou com função de cobrança/faturamento (Boleto) tendem a coexistir por inércia contratual e limites operacionais.
- **O que os dados dizem (`2020-11` → `2026-10`):**
  - Na quantidade total (Pix + tradicionais), o Pix foi de **5,31% para 95,31%** (e no valor, de **0,96% para 44,06%**).
  - O **DOC foi a zero (`R$ 0,0`)** após sua descontinuação oficial; o **Cheque encolheu quase pela metade** (**R$ 52,5 bi → R$ 27,9 bi**).
  - Por outro lado, **TED** (**R$ 2,57 tri → R$ 4,34 tri**) e **Boleto** (**R$ 375,6 bi → R$ 568,2 bi**) continuam crescendo em termos nominais para grandes liquidações interbancárias e cobranças.

### Gráfico 2.4: Volume Pix por Natureza Econômica (P2P, P2B, B2B, B2P)
- **Pergunta:** *O Pix é majoritariamente usado para transferências entre pessoas ou para negócios?*
- **Teoria / Hipótese:** Embora a percepção popular associe o Pix ao P2P ("mandar um Pix para um amigo"), a **Lei de Pareto em fluxos financeiros** sugere que transações entre empresas (B2B) concentram a maior parte do valor mesmo sendo minoria em quantidade.
- **O que os dados dizem (acumulado histórico):**
  - **Em valor financeiro, o B2B domina com 44,9% (R$ 49,55 tri)** usando apenas **8,94 bi** de transações (ticket médio de **R$ 5.540,48**).
  - **Em quantidade de operações, o varejo e as pessoas dominam:** **P2P** soma **127,46 bi** transações (ticket **R$ 259,88**, 30,0% do valor) e **P2B** soma **101,41 bi** transações (ticket **R$ 125,77**, 11,6% do valor). A queda do ticket médio geral (R$ 876 → R$ 445) com alta do % PJ (47,8% → 64,2%) reflete exatamente essa dupla adoção: **varejo de baixo ticket + tesouraria B2B**.

---

## 4. Eixo 3 — Geografia & Demografia Geracional (Aba 3)

### Gráficos 3.1 e 3.2: Fluxo Regional (Pago vs. Recebido) e Saldo Líquido Interestadual
- **Pergunta:** *Como o dinheiro circula entre as regiões brasileiras via Pix e quem é recebedor líquido?*
- **Teoria / Hipótese:** Pela **geografia econômica**, espera-se que centros financeiros e polos comerciais/e-commerce (como Sudeste) concentrem o volume bruto, mas fluxos interestaduais líquidos revelam para onde a liquidez é drenada (serviços digitais, agronegócio, sedes fiscais ou apostas/plataformas).
- **O que os dados dizem (excluindo UFs não informadas):**
  - **Concentração:** O **Sudeste** responde por mais da metade do fluxo nacional (**R$ 59,00 tri** recebidos e **R$ 59,08 tri** pagos, saldo quase neutro de **-R$ 80,1 bi**).
  - **Única região superavitária:** O **Centro-Oeste** apresenta saldo líquido positivo expressivo de **+R$ 628,7 bilhões** (R$ 10,82 tri recebidos vs. R$ 10,19 tri pagos).
  - **Maiores pagadores líquidos:** **Nordeste** (**-R$ 306,7 bi**), **Sul** (**-R$ 146,3 bi**) e **Norte** (**-R$ 108,4 bi**) enviam mais recursos líquidos via Pix para outras regiões do que recebem.

### Gráfico 3.3: Mapa de Calor Etário (Adoção Geracional)
- **Pergunta:** *O Pix ainda é restrito aos jovens ou já convergiu entre as gerações?*
- **Teoria / Hipótese:** Curvas de adoção tecnológica seguem um gradiente etário na entrada (nativos digitais de 20–39 anos adotam primeiro), mas o **efeito de rede** (externalidade positiva de rede) puxa coortes mais velhas ao longo do tempo, que por sua vez operam com maior renda/ticket médio.
- **O que os dados dizem:**
  - **Volume:** `30 a 39 anos` lidera (**29,5%**, **67,62 bi** transações), seguida por `20 a 29 anos` (**27,1%**, **62,11 bi**) e `40 a 49 anos` (**22,2%**, **50,93 bi**). Juntas, as faixas de 20 a 49 anos concentram **78,8%** das operações.
  - **Ticket médio crescente com a idade:** sobe monotonicamente de **R$ 63,32** (`até 19 anos`) → **R$ 137,80** (`20–29`) → **R$ 198,73** (`30–39`) → **R$ 230,00** (`40–49`) → **R$ 261,32** (`50–59`) → **R$ 411,06** (`mais de 60 anos`), confirmando maior ticket unitário nas faixas sêniores.

---

## 5. Eixo 4 — Segurança & Efetividade do MED (Aba 4)

### Gráfico 4.1: Funil Financeiro MED Agregado (`2022-01` a `2026-09`)
- **Pergunta:** *Quando uma fraude é contestada e aceita no MED, quanto do dinheiro realmente volta para a vítima?*
- **Teoria / Hipótese:** O Mecanismo Especial de Devolução (MED) depende do bloqueio cautelar na conta recebedora. Como o Pix liquida em segundos, se o fraudador dispersar o saldo antes da notificação da vítima, o funil financeiro sofre uma perda severa entre o valor aceito e o devolvido.
- **O que os dados dizem:**
  - Em 57 meses de MED, houve **68,82 milhões** de contestações, com **15,50 milhões aceitas** somando **R$ 27,57 bilhões**.
  - Apenas **R$ 2,59 bilhões foram devolvidos** (**R$ 1,71 bi** integral + **R$ 0,88 bi** parcial — **~9,4% do valor**), deixando uma **perda não devolvida de R$ 24,99 bilhões (~90,6%)**.

### Gráfico 4.2: Efetividade do MED (%) × Razão Chaves/Usuário ("Contas Laranjas")
- **Pergunta:** *Por que a efetividade em quantidade difere da recuperação financeira e qual o papel das contas laranjas?*
- **Teoria / Hipótese:** Fraudadores operam contas de passagem ("laranjas") registrando múltiplas chaves por CPF/CNPJ ou descartando contas em sequência. O eixo duplo separa o percentual de casos com devolução da multiplicidade de chaves marcadas por usuário fraudador.
- **O que os dados dizem:**
  - A efetividade média mensal em número de ocorrências com alguma devolução é de **32,81%**, mas o contraste com os **9,4% em valor** mostra que **fraudes de ticket baixo têm maior chance de recuperação parcial, enquanto grandes golpes são pulverizados imediatamente**.
  - A razão média de chaves por usuário fraudador manteve-se estável em torno de **1,06x** (pico de **1,13x**), indicando que o combate no DICT tende a marcar a relação 1:1 conta/chave, enquanto a evasão ocorre na velocidade de saída do recurso.

### Gráfico 4.3: Causas de Não Devolução no MED (Saldo Insuficiente × Conta Encerrada)
- **Pergunta:** *O dinheiro não volta porque a conta foi encerrada ou porque já foi esvaziada?*
- **Teoria / Hipótese:** Se o gargalo fosse apenas encerramento cadastral após o golpe, predominaria `conta encerrada`; se o gargalo for a **assimetria de velocidade** entre o saque/transferência instantânea e a abertura do MED, predominará `saldo insuficiente`.
- **O que os dados dizem:**
  - Entre as causas discriminadas, **Saldo Insuficiente soma R$ 15,16 bilhões**, contra apenas **R$ 0,69 bilhão** por Conta Encerrada (**95,6% vs. 4,4%**). Os dados confirmam empiricamente que o principal desafio do MED é a **velocidade de dispersão em cascata** antes do bloqueio.

---

## 6. Limitações Metodológicas Registradas no Pipeline

1. **Janelas temporais assimétricas:** o Pix inicia em `2020-11`, os dados comparativos de Cartões (`MPV`) cobrem até `2026-T2` e o MED só possui registros a partir de `2022-01` (série encerrada em `2026-09` na última extração).
2. **Granularidade mista:** `fato_pix_macro_mensal` opera no grão mensal (`ano_mes`) enquanto `fato_cartoes_vs_pix_trimestral` opera no grão trimestral (`trimestre`), unificados via `dim_tempo`.
3. **Registros regionais não identificados:** transações sem UF/região declarada (`Nao informado`) são mantidas na carga bruta para consistência do total nacional (`consistencia_regional_total`), mas filtradas nas visões de fluxo interestadual.
