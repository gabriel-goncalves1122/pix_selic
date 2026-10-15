# Roteiro do Apresentador & Guia Técnico do Projeto
## Pix × "Custo Brasil": Dinâmica dos Meios de Pagamento e Variáveis Macroeconômicas
**Disciplina:** Engenharia de Dados (ECOX14) — UNIFEI  
**Arquitetura:** Pipeline Medalhão (Bronze ➔ Prata ➔ Ouro)  
**Fontes:** Banco Central do Brasil (APIs Olinda e Sistema SGS)  

---

## SUMÁRIO
1. [PARTE 1: Glossário & Fundamentos Técnicos (Domínio dos Conceitos)](#parte-1-glossário--fundamentos-técnicos)
   - [1.1 O que é a API Olinda (BCB Dados Abertos / OData)?](#11-o-que-é-a-api-olinda-bcb-dados-abertos--odata)
   - [1.2 O que é o Sistema SGS do Banco Central?](#12-o-que-é-o-sistema-sgs-do-banco-central)
   - [1.3 Selic Meta vs. Selic Realizada (Over) & Convenção de 252 Dias Úteis](#13-selic-meta-vs-selic-realizada-over--convenção-de-252-dias-úteis)
   - [1.4 O que são as Operações de Mercado Aberto (Selic Operações)?](#14-o-que-são-as-operações-de-mercado-aberto-selic-operações)
   - [1.5 Por que a Arquitetura Medalhão (Bronze, Prata, Ouro)?](#15-por-que-a-arquitetura-medalhão-bronze-prata-ouro)
   - [1.6 Por que Apache Parquet (Snappy) e não CSV?](#16-por-que-apache-parquet-snappy-e-não-csv)
   - [1.7 O Mecanismo Especial de Devolução (MED) e as Contas Laranjas](#17-o-mecanismo-especial-de-devolução-med-e-as-contas-laranjas)
2. [PARTE 2: Roteiro Slide a Slide (Bastidores, Metodologia e O Que Falar)](#parte-2-roteiro-slide-a-slide)
   - [Slide 1: Capa Institucional](#slide-1-capa-institucional)
   - [Slide 2: Conceito & Pergunta Norteadora](#slide-2-conceito--pergunta-norteadora)
   - [Slide 3: Arquitetura Medalhão: Resiliência e Linhagem](#slide-3-arquitetura-medalhão-resiliência-e-linhagem)
   - [Slide 4: Diagnóstico da Bronze & O Case Real do Pix](#slide-4-diagnóstico-da-bronze--o-case-real-do-pix)
   - [Slide 5: Matriz De / Para: Higienização de Títulos e Tipagem](#slide-5-matriz-de--para-higienização-de-títulos-e-tipagem)
   - [Slide 6: Antes × Depois em Números & Compressão Parquet](#slide-6-antes--depois-em-números--compressão-parquet)
   - [Slide 7: Resultados Analíticos: Evolução do Pix & Funil do MED](#slide-7-resultados-analíticos-evolução-do-pix--funil-do-med)
   - [Slide 8: Resultados Macroeconômicos: Taxa Selic & Mercado Aberto](#slide-8-resultados-macroeconômicos-taxa-selic--mercado-aberto)
   - [Slide 9: Roadmap da Camada Ouro: Star Schema Integrado](#slide-9-roadmap-da-camada-ouro-star-schema-integrado)
3. [PARTE 3: Guia de Respostas para a Banca Avaliadora](#parte-3-guia-de-respostas-para-a-banca-avaliadora)

---

# PARTE 1: Glossário & Fundamentos Técnicos

Antes de subir ao palco ou abrir o microfone, você precisa ter clareza absoluta sobre o ecossistema do Banco Central e os termos de engenharia de dados. Aqui está tudo mastigado:

### 1.1 O que é a API Olinda (BCB Dados Abertos / OData)?
* **O que significa:** Olinda é a plataforma corporativa de distribuição de dados abertos do Banco Central do Brasil.
* **O protocolo OData (Open Data Protocol):** Criado originalmente pela Microsoft e padronizado pela OASIS, o OData transforma um endpoint HTTP em uma interface de consulta avançada. Em vez de uma API REST comum que só entrega um JSON fixo, o OData permite parâmetros na URL como `$select` (escolher colunas), `$filter` (filtrar linhas como no `WHERE` do SQL), `$top` (paginação) e `$format` (pedir em JSON ou CSV).
* **Quais serviços Olinda nós usamos:**
  1. `Pix_DadosAbertos`: Traz as transações mensais agregadas por finalidade, modalidade e perfil pagador/recebedor (PF e PJ), além das estatísticas de fraudes e contestações MED.
  2. `selic_operacoes`: Registra todas as operações financeiras consolidadas no mercado interbancário pelo Sistema Especial de Liquidação e de Custódia (Selic).

### 1.2 O que é o Sistema SGS do Banco Central?
* **O que significa:** SGS é a sigla para **Sistema Gerenciador de Séries Temporais**. É um sistema legado do Banco Central, criado há décadas para catalogar e fornecer indicadores macroeconômicos contínuos.
* **Características dos dados do SGS:**
  - O SGS é estritamente **univariado e bidimensional**: qualquer chamada retorna apenas duas colunas: `[Data, Valor]`.
  - O formato bruto do SGS é regionalizado para o Brasil: delimitador de ponto-e-vírgula (`;`), datas como texto `"DD/MM/YYYY"` e números com vírgula decimal (`"2,00"`).
* **Quais séries extraímos do SGS:**
  - **Série 432:** *Taxa de juros - Selic fixada pelo Copom (% a.a.)*. É a meta oficial de juros do país.
  - **Série 11:** *Taxa de juros - Selic acumulada no mês (% a.d. e % a.m.)*. É a taxa real efetivamente praticada no mercado dia a dia.
  - **Série 433:** *Índice Nacional de Preços ao Consumidor Amplo (IPCA)* mensal para medir inflação.

### 1.3 Selic Meta vs. Selic Realizada (Over) & Convenção de 252 Dias Úteis
* **Selic Meta:** É a taxa decidida a cada 45 dias pelo Comitê de Política Monetária (COPOM). Ela expressa a vontade de política monetária do Banco Central para conter a inflação ou estimular a economia. Exemplo: 10,75% ao ano.
* **Selic Realizada (Over):** É a taxa efetiva apurada diariamente com base no custo real dos empréstimos interbancários garantidos por títulos públicos federais. Ela oscila diariamente ligeiramente abaixo ou em torno da Meta.
* **A Matemática da Anualização (Base 252):** No mercado financeiro brasileiro, os juros de títulos públicos só rendem em dias úteis. Por convenção padrão do Bacen e da B3, considera-se que um ano útil possui **252 dias úteis**.
  - A série 11 diária do SGS entrega a taxa diária $t_d$ em percentual (% a.d.).
  - Para calcular a taxa anualizada correspondente na Camada Prata, aplicamos a capitalização composta:
    $$\text{Taxa Anualizada (\% a.a.)} = \left[ \left(1 + \frac{t_d}{100}\right)^{252} - 1 \right] \times 100$$
  - Esse tratamento transformou uma série bruta imprópria para comparações em uma métrica diretamente comparável com a Selic Meta anual do Copom.

### 1.4 O que são as Operações de Mercado Aberto (Selic Operações)?
O mercado aberto (*Open Market*) é onde o Banco Central e os bancos comerciais compram e vendem títulos públicos para controlar a quantidade de dinheiro em circulação:
* **Operações Compromissadas (Recompra/Revenda):** Uma instituição vende um título hoje para outra assumindo o compromisso formal de recomprá-lo amanhã (ou em data futura) a um preço pré-definido. É o motor do giro diário de liquidez entre os bancos — movimentou impressionantes **R$ 4,72 quatrilhões** na nossa base histórica.
* **Redesconto do Banco Central:** Linha de assistência temporária de liquidez que o Bacen estende a instituições financeiras com necessidade momentânea de caixa (movimentou R$ 495 trilhões).
* **Compra e Venda Definitiva:** Negociações definitivas de títulos da dívida pública sem cláusula de recompra (movimentou R$ 163 trilhões).

### 1.5 Por que a Arquitetura Medalhão (Bronze, Prata, Ouro)?
A arquitetura medalhão (criada pela Databricks e padrão em Data Lakehouses modernos) organiza os dados em camadas com responsabilidades claras:
* **Bronze (Raw / Cru):** O dado é salvo exatamente como a API entregou. Sem filtros, sem alteração de nomes, imutável. Salva-se também a linhagem (`proveniencia.json` contendo URL de extração, timestamp, tamanho e hash). Se houver qualquer dúvida ou bug futuro de transformação, a fonte bruta está preservada no disco.
* **Prata (Curated / Higienizado):** O dado é limpo, tipado nativamente (`float64`, `int64`, `date`), estruturado em colunas semânticas (`snake_case`), e salvo em formato analítico colunar (Parquet). É a camada que os cientistas de dados e analistas de BI consultam.
* **Ouro (Business / Consolidado):** Modelagem dimensional voltada para o negócio (Star Schema / Tabelas Fato). No nosso caso, é o merge temporal que junta as transações do Pix com a taxa de juros e a inflação por mês.

### 1.6 Por que Apache Parquet (Snappy) e não CSV?
* **Compressão:** O CSV armazena caracteres ASCII linha por linha. O número `"182470.50"` em CSV gasta 9 bytes. No Parquet, ele é armazenado binariamente de forma colunar e comprimido via algoritmo Snappy, ocupando até **85% menos espaço**.
* **Preservação de Esquema e Tipagem:** O CSV não sabe o que é uma data ou um número; tudo é texto quando você reabre o arquivo. No Parquet, o metadado embutido (*footer metadata*) armazena explicitamente o tipo de dado de cada coluna. Uma coluna `date` abre como data nativa instantaneamente no Python, R ou DuckDB.
* **Desempenho de Leitura (Predicate Pushdown e I/O Colunar):** Se você quer fazer uma query apenas para calcular a média da coluna `valor`, o DuckDB ou o Pandas lê apenas a coluna solicitada em disco, ignorando as outras dezenas de colunas. No CSV, o motor precisa ler e fazer parse de todo o arquivo do início ao fim.

### 1.7 O Mecanismo Especial de Devolução (MED) e as Contas Laranjas
* **O que é o MED:** É uma funcionalidade regulamentada pelo Banco Central (Resolução BCB nº 103/2021) específica para o Pix, desenhada para viabilizar a devolução de recursos em casos de fundada suspeita de fraude ou golpe (ex: falso parente, invasão, engenharia social) ou falha operacional.
* **O funil da dor (por que só 33% do dinheiro confirmado é recuperado?):**
  - A vítima demora minutos ou horas para perceber o golpe e acionar o banco.
  - Os fraudadores utilizam automações bancárias para pulverizar o dinheiro em segundos através de cadeias de **contas laranjas** (*money mules* abertas com CPFs falsos ou laranjas cooptados).
  - Quando a notificação do MED atinge o banco de destino para executar o bloqueio cautelar, a conta receptora já está com saldo zero.

---

# PARTE 2: Roteiro Slide a Slide

---

## Slide 1: Capa Institucional
* **Visual na Tela:** Título institucional grande (*Pix × "Custo Brasil"*), subtítulo sobre evolução de meios de pagamento e correlação com IPCA e Selic, e badges institucionais (Banco Central do Brasil, Pix Dados Abertos, SGS & Olinda).
* **O que aconteceu na Engenharia:** Os cards de metadados acadêmicos foram limpos para dar um aspecto corporativo de alto nível.
* **Metodologia:** Abertura limpa e institucional alinhada ao Banco Central.

### 🎙️ O que falar (Script do Apresentador):
> "Bom dia a todos e ao professor avaliador.  
> O objetivo do meu projeto final de Engenharia de Dados é investigar a relação entre a revolução dos meios de pagamento no país e as variáveis macroeconômicas que compõem o chamado 'Custo Brasil'.  
> Especificamente, analisamos o comportamento exponencial da adoção do Pix frente aos ciclos de inflação medida pelo IPCA e a taxa básica de juros, a Selic, a partir de dados públicos extraídos diretamente dos sistemas oficiais do Banco Central do Brasil."
*(Duração: 30 a 45 segundos)*

---

## Slide 2: Conceito & Pergunta Norteadora
* **Visual na Tela:** Card com a Pergunta Norteadora em destaque, ladeada por dois eixos analíticos: *Eixo 1 (Dinâmica dos Meios de Pagamento - Volume, Segmentação e Segurança/MED)* e *Eixo 2 (Variáveis Macroeconômicas - Custo de Oportunidade, Poder de Compra e Inelasticidade)*.
* **O que aconteceu na Engenharia:** As frases longas foram sintetizadas em palavras-chave para ancorar o raciocínio visualmente.
* **Metodologia:** Divisão em dois pilares: de um lado, microdados transacionais de pagamento; do outro lado, séries de política monetária e inflação.

### 🎙️ O que falar (Script do Apresentador):
> "Nossa pergunta norteadora é: *Como a adoção em massa do Pix impactou os volumes transacionais no país e qual é a correlação dessa dinâmica com a inflação e a taxa Selic?*  
> Para responder a isso com rigor técnico, dividimos a engenharia em dois eixos complementares:  
> No **Eixo 1**, olhamos para a microdinâmica do Pix: crescimento de transações entre Pessoas Físicas e Jurídicas, finalidades de uso e as estatísticas do sistema antifraude com o Mecanismo Especial de Devolução (MED).  
> No **Eixo 2**, trazemos o contexto macroeconômico: a taxa Selic Meta e a taxa diária praticada no mercado aberto, e o índice de preços IPCA. A hipótese central que levantamos é que o Pix funcionou como uma tecnologia inelástica, ou seja, continuou acelerando sua adoção de forma independente dos ciclos severos de aperto monetário."
*(Duração: 45 a 60 segundos)*

---

## Slide 3: Arquitetura Medalhão: Resiliência e Linhagem
* **Visual na Tela:** Diagrama de blocos horizontais interligados por setas de processamento: *Fontes Externas (APIs Bacen)* ➔ *Camada Bronze (Estoque Bruto + Proveniência)* ➔ *Camada Prata (Dados Higienizados Parquet)* ➔ *Camada Ouro (Data Mart Star Schema)*, com rodapé destacando a integração com análises em R.
* **O que aconteceu na Engenharia:** Construímos um orquestrador com lógica de *checkpoint*, salvaguardas de retries HTTP e persistência de metadados em JSON para cada extração bruta.
* **Metodologia:** Adoção do padrão Medalhão (*Lakehouse*), garantindo imutabilidade e auditabilidade desde a origem até a entrega analítica.

### 🎙️ O que falar (Script do Apresentador):
> "Para processar e estruturar esses dados, implementamos um pipeline na **Arquitetura Medalhão**.  
> Na camada de **Fontes**, consumimos dois barramentos do Bacen: o barramento moderno OData da API Olinda e as séries do sistema SGS.  
> Na **Camada Bronze**, nossa prioridade foi a resiliência e a linhagem: os dados foram extraídos via scripts Python com controle de checkpoint e tentativas automáticas (retries), salvando os CSVs brutos exatamente como vieram, acompanhados de arquivos `proveniencia.json` com metadados de auditoria.  
> Na **Camada Prata**, realizamos o trabalho pesado de engenharia: parsing de formatos regionais brasileiros, padronização semântica de colunas e conversão para o formato colunar Apache Parquet.  
> Por fim, a **Camada Ouro** foi modelada em Star Schema para agregar os dados em uma visão mensal integrada, permitindo tanto cruzamentos analíticos em R quanto consultas de alto desempenho."
*(Duração: 50 a 60 segundos)*

---

## Slide 4: Diagnóstico da Bronze & O Case Real do Pix
* **Visual na Tela:** Dois cards comparativos lado a lado:
  - *Esquerda:* Lista de 3 erros estruturais da Bronze (Numéricos como String com vírgula, Chaves Temporais sem tipagem nativa, Conflito de delimitadores `,` vs `;`).
  - *Direita:* O case real de ingestão do Pix: o erro de premissa do loop mensal (70 CSVs / 2,8 GB) versus a descoberta no profiling de que o 1º CSV já continha toda a base (68,7 MB), gerando uma economia de 97,5% e protegendo a máquina local.
* **O que aconteceu na Engenharia:** Você escreveu um orquestrador que desceu mês a mês, mas no profiling com Pandas percebeu que a API do Bacen já acumulava todo o histórico desde novembro de 2020 a cada chamada. Você otimizou a leitura para o arquivo raiz.
* **Metodologia:** *Data Profiling* antes do processamento analítico para evitar custos computacionais inúteis e desperdício de memória RAM.

### 🎙️ O que falar (Script do Apresentador):
> "Ao inspecionar os dados brutos na Camada Bronze, nos deparamos com desafios clássicos de qualidade de dados públicos:  
> Primeiro, campos financeiros e taxas vieram como texto com vírgula e pontos de milhar, impossibilitando qualquer operação matemática. Segundo, as datas não possuíam padrão temporal: algumas eram números inteiros, outras strings no padrão brasileiro, e outras no padrão ISO. Terceiro, tínhamos conflito de delimitadores entre vírgula na Olinda e ponto-e-vírgula no SGS.  
> Mas o aprendizado mais rico de engenharia deste projeto foi o **Case da Ingestão do Pix**:  
> Eu desenhei inicialmente um orquestrador com laços de repetição mês a mês e salvaguardas HTTP robustas para baixar as safras. O script baixou 70 arquivos totalizando 2,8 GB. Porém, ao executar a etapa de **Data Profiling**, descobri que a API do Bacen não estava particionando os dados; cada chamada já entregava o histórico cumulativo completo desde 2020.  
> Ou seja: apenas o primeiro CSV de 68.7 MB já continha 100% das informações! Identificar isso foi crucial para o meu ambiente: em vez de travar a memória RAM e a CPU do meu computador tentando ler e concatenar 2,8 GB de dados redundantes, o pipeline Prata lê diretamente o arquivo consolidado, economizando 2,7 GB de disco e eliminando 97,5% de I/O desnecessário."
*(Duração: 70 a 90 segundos — este é o slide mais importante da sua narrativa pessoal)*

---

## Slide 5: Matriz De / Para: Higienização de Títulos e Tipagem
* **Visual na Tela:** Tabela limpa de 6 colunas comparando o Dado Bruto (Bronze) com o Dado Limpo (Prata), destacando a padronização das colunas originais para `snake_case` com prefixos (`qtd_*`, `vl_*`) e a conversão de tipos para `float64`, `int64` e `date`.
* **O que aconteceu na Engenharia:** Construção de funções modulares em Python (`tratar_valor_financeiro`, `limpar_estatisticas_fraudes`, `limpeza_taxa_selic`, `limpeza_operacoes_selic`) para transformar as anomalias detectadas.
* **Metodologia:** Tratamento determinístico com tipagem estrita, conversão canônica de datas (`YYYY-MM-01`) e eliminação completa do tipo `object` genérico do Pandas.

### 🎙️ O que falar (Script do Apresentador):
> "Aqui no Slide 5 apresentamos a nossa **Matriz De / Para**, que documenta as transformações aplicadas entre a Camada Bronze e a Prata.  
> Não se tratou apenas de limpar valores, mas também de redesenhar o esquema: padronizamos títulos heterogêneos para a convenção analítica `snake_case` com prefixos semânticos claros: tudo o que é contagem recebeu o prefixo `qtd_`, e tudo o que é monetário recebeu `vl_`.  
> Do ponto de vista dos tipos, convertemos valores monetários em texto para `float64`, chaves inteiras ou textuais de ano-mês para o tipo nativo `date` ancorado no primeiro dia do mês, e eliminamos pontos de milhar das estatísticas de fraudes.  
> Com isso, 100% das colunas quantitativas da Camada Prata tornaram-se nativamente numéricas e prontas para agregação."
*(Duração: 45 a 60 segundos)*

---

## Slide 6: Antes × Depois em Números & Compressão Parquet
* **Visual na Tela:** Dois gráficos compactos lado a lado:
  - *Esquerda:* Ecossistema Pix (Transações e Fraudes) — 21 colunas de texto reduzidas para apenas 9 categóricas legítimas, e colunas numéricas subindo de 15 para 27.
  - *Direita:* Ecossistema Macro (SGS e Selic Operações) — 8 textos caindo para apenas 1 categórico e 11 numéricas nativas.
  - *Abaixo:* 3 KPIs em caixas claras: *154 CSVs ➔ 4 Parquets*, *-85% I/O & Espaço*, e *100% Tipagem Nativa*.
* **O que aconteceu na Engenharia:** Consolidação dos 154 arquivos em 4 datasets Parquet (`pix_transacoes`, `pix_fraudes`, `taxa_selic_diaria_mensal` e `selic_operacoes_mercado`).
* **Metodologia:** Armazenamento colunar com algoritmo Snappy para viabilizar consultas analíticas sub-segundo em R e DuckDB.

### 🎙️ O que falar (Script do Apresentador):
> "Neste slide vemos o impacto quantitativo da higienização e da conversão para o formato Apache Parquet com compressão Snappy.  
> No gráfico da esquerda, referente ao **Ecossistema Pix**, reduzimos colunas de texto que eram falso-positivo de 21 para apenas 9 variáveis categóricas legítimas, elevando as variáveis numéricas de 15 para 27.  
> No gráfico da direita, no **Ecossistema Macroeconômico**, o efeito foi ainda mais drástico: 8 colunas de texto viraram apenas 1 categórica, e as numéricas subiram para 11 campos tipados.  
> Consolidamos 154 arquivos CSV dispersos em apenas **4 datasets Parquet unificados**, obtendo uma redução de **85% no espaço em disco e no custo de I/O**, garantindo 100% de integridade de tipagem nativa."
*(Duração: 45 a 60 segundos)*

---

## Slide 7: Resultados Analíticos: Evolução do Pix & Funil do MED
* **Visual na Tela:** Dois blocos visuais de alto impacto:
  - *Esquerda:* Gráfico de área em SVG nativo mostrando a curva exponencial de transações do Pix, subindo de 29,5 milhões de operações em nov/2020 para **7,37 bilhões** em ago/2026.
  - *Direita:* Funil do MED em CSS demonstrando a perda de eficácia: 53,1 milhões de contestações ➔ 14,1 milhões aceitas (fraude comprovada) ➔ apenas 4,69 milhões devolvidas financeiramente (33,2% de taxa de recuperação sobre as fraudes aceitas).
* **O que aconteceu na Engenharia:** Os dados limpos da Prata foram agregados por safra mensal para alimentar diretamente as coordenadas vetoriais do SVG e a árvore do funil.
* **Metodologia:** Engenharia analítica gerando visualizações vetoriais sem depender de imagens pesadas ou estáticas.

### 🎙️ O que falar (Script do Apresentador):
> "Com a Camada Prata estruturada, extraímos os primeiros resultados analíticos.  
> À esquerda, a curva temporal revela a maior disrupção da história do sistema de pagamentos brasileiro: o Pix saltou de 29,5 milhões de operações no seu lançamento em novembro de 2020 para incríveis **7,37 bilhões de transações mensais** em 2026.  
> Porém, à direita, revelamos a face crítica da velocidade das transações através do nosso **Funil do Mecanismo Especial de Devolução (MED)**:  
> Ao longo da série, foram registradas mais de 53 milhões de contestações. Destas, 14,1 milhões foram comprovadas como fraude pela autoridade bancária. No entanto, apenas 4,69 milhões conseguiram devolução financeira efetiva.  
> Isso significa que **em 66,8% dos golpes confirmados, a vítima não recupera um único centavo**. O dado reflete um gargalo estrutural: a velocidade instantânea do Pix permite aos criminosos pulverizar o dinheiro em contas laranjas antes que o bloqueio cautelar seja acionado."
*(Duração: 60 a 75 segundos)*

---

## Slide 8: Resultados Macroeconômicos: Taxa Selic & Mercado Aberto
* **Visual na Tela:**
  - *Esquerda:* Curva de juros da Selic (SGS Série 432 / 11) mostrando o ciclo de política monetária desde o piso histórico de 2,00% até o ciclo de alta de 14,25%.
  - *Direita:* Painel de liquidez das Operações de Mercado Aberto (API Olinda), unificando 82 arquivos mensais em 2.978 registros, com os volumes monumentais: **R$ 4,72 Quatrilhões** em Compromissadas, R$ 495 Trilhões em Redesconto e R$ 163 Trilhões em Compra/Venda Definitiva.
* **O que aconteceu na Engenharia:** Processamento e unificação das 82 safras de operações de mercado aberto e pareamento com a Selic diária anualizada.
* **Metodologia:** Contextualização macroeconômica do ambiente de juros sob o qual o Pix floresceu.

### 🎙️ O que falar (Script do Apresentador):
> "No Slide 8, conectamos o Pix ao cenário macroeconômico brasileiro.  
> Na curva à esquerda, temos o ciclo da Taxa Selic: o Pix nasceu em plena pandemia com juros na mínima histórica de 2,00% ao ano, e atravessou um dos ciclos de aperto monetário mais agressivos do mundo, subindo até patamares de 14%.  
> À direita, trouxemos um dado raramente explorado em projetos acadêmicos: as **Operações no Selic extraídas da API Olinda**. Concatenamos 82 arquivos mensais independentes em um único painel histórico.  
> Esse painel revela a colossal magnitude do mercado aberto brasileiro: as operações de recompra e revenda compromissadas movimentaram mais de **R$ 4,7 quatrilhões**. São essas operações diárias de liquidez entre os bancos que dão o lastro real para que qualquer sistema de pagamentos funcione no Brasil."
*(Duração: 60 segundos)*

---

## Slide 9: Roadmap da Camada Ouro: Star Schema Integrado
* **Visual na Tela:** Modelagem conceitual do Star Schema mostrando as tabelas dimensionais da Prata convergindo para a tabela fato central `ouro_pix_macro_mensal`, contendo chave temporal `ano_mes`, volume transacional, ticket médio, Selic Meta e IPCA 12m. Checklist com etapas concluídas e próximos passos.
* **O que aconteceu na Engenharia:** Especificação do schema de unificação 1:1 via chave `ano_mes` para análises econométricas e econometria em R.
* **Metodologia:** Modelagem dimensional (*Kimball*) para suporte à tomada de decisão e testes de elasticidade.

### 🎙️ O que falar (Script do Apresentador):
> "Para finalizar, o Slide 9 apresenta o nosso roadmap para a **Camada Ouro**.  
> Já consolidamos com sucesso a Prata do Pix e a Prata Macroeconômica. A próxima etapa é materializar a tabela fato central `ouro_pix_macro_mensal` através de um Star Schema.  
> Essa tabela agregará o volume total do Pix, ticket médio e percentual de transações PJ, conectando-os diretamente à taxa Selic e à inflação acumulada daquele mesmo mês.  
> A meta final desse Data Mart é rodar modelos de regressão e séries temporais em R para testar a nossa hipótese inicial: demonstrar estatisticamente que a utilidade marginal e o ganho de eficiência do Pix superaram qualquer desestímulo trazido pelo ciclo de juros altos, reduzindo de forma tangível o 'Custo Brasil'.  
> Muito obrigado, e fico à disposição da banca para responder às perguntas."
*(Duração: 45 a 60 segundos)*

---

# PARTE 3: Guia de Respostas para a Banca Avaliadora

Aqui estão as perguntas mais difíceis que professores e avaliadores de Engenharia de Dados costumam fazer, com as respostas técnicas exatas para você gabaritar:

### Pergunta 1: *"Por que você usou Python e Pandas puro em vez de ferramentas de Big Data como Apache Spark ou PySpark?"*
* **Sua Resposta:**  
  *"Excelente pergunta, professor. O princípio fundamental de engenharia de software é aplicar a ferramenta correta para o volume de dados do problema, evitando o chamado 'over-engineering'. O dataset consolidado do Pix após o profiling possui cerca de 740 mil linhas e a base de fraudes possui 52 meses. Isso cabe confortavelmente na memória RAM de uma única máquina (menos de 200 MB em memória). Usar um cluster Spark para essa ordem de grandeza geraria um overhead massivo de coordenação de nós, serialização JVM e latência de rede sem ganho real de throughput. O Pandas, aliado ao motor colunar do Apache Parquet (Snappy) e DuckDB, nos entrega tempo de resposta sub-segundo em uma única máquina, com consumo mínimo de recursos."*

### Pergunta 2: *"Como você lidou com a consistência de tipos na ingestão se o formato do Banco Central mudar no futuro?"*
* **Sua Resposta:**  
  *"Adotamos duas salvaguardas: primeiro, na Camada Bronze, mantemos o dado raw intacto e salvamos o arquivo `proveniencia.json` com a linhagem e timestamp. Segundo, no pipeline de transformação para a Prata, encapsulamos as transformações em funções defensivas com blocos de tratamento de exceção e conversão forçada via esquemas explícitos (com tipos declarados em dicionários do Pandas e coerção via `pd.to_datetime` e `errors='coerce'`). Se uma coluna nova for inserida ou o nome mudar, o schema levanta um aviso ou erro controlado sem corromper a base histórica existente."*

### Pergunta 3: *"Por que converter as taxas diárias do SGS com base em 252 dias úteis e não 360 ou 365 dias corridos?"*
* **Sua Resposta:**  
  *"Porque essa é a convenção regulatória oficial do mercado financeiro nacional fixada pelo Banco Central do Brasil e pela B3 para títulos da dívida pública federal negociados no Selic. Títulos públicos só pagam remuneração em dias úteis. Aplicar base de 360 ou 365 dias corridos subestimaria ou distorceria a taxa de juros efetiva praticada no mercado interbancário ao compará-la com a Selic Meta anual do Copom."*

### Pergunta 4: *"O que você destacaria como o maior diferencial técnico da entrega?"*
* **Sua Resposta:**  
  *"O maior diferencial técnico foi o senso crítico de Data Profiling que demonstramos no Slide 4. Muitas vezes o engenheiro de dados se apaixona pelo código de ingestão complexo (loops, retries, dezenas de arquivos) e não examina o conteúdo dos dados. Ao perfilar o dado bruto, identificamos que a API do Bacen acumulava o histórico em um único CSV raiz, o que nos permitiu eliminar 2,7 GB de dados redundantes e otimizar em 97,5% o I/O em disco. Além disso, trouxemos dados inéditos de quatrilhões de reais em operações de mercado aberto da API Olinda, conectando engenharia de dados à realidade macroeconômica brasileira."*
