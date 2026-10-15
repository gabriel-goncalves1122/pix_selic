# Case de Engenharia: O Problema da Duplicação em Escada (Staircase Duplication)

> **Documentação de Arquitetura e Decisões de Refatoração**
> Esta documentação detalha um achado crítico durante a fase de Data Profiling da Camada Bronze e a subsequente refatoração do pipeline para a Camada Prata.

## 1. A Ingestão Inicial (V1)
No início do projeto, assumiu-se um comportamento de particionamento mensal padrão para a API Olinda do Banco Central do Brasil (BCB). Como a documentação OData do Bacen nem sempre é explícita sobre o comportamento de parâmetros customizados (como o parâmetro `Database`), construímos o orquestrador iterando cronologicamente, mês a mês, de `202011` a `202609`. 

O orquestrador executou perfeitamente, gerando resiliência, proveniência e checkpoints para dezenas de arquivos. O resultado aparente foi um sucesso: **2.5 GB de dados brutos** particionados baixados no disco.

## 2. A Descoberta via Data Profiling
Durante a etapa de Análise Exploratória (EDA), ao rodar o script de Analytics (que cruza metadados e estrutura com `data-profiling`), fizemos uma descoberta contraintuitiva.

Identificamos o **efeito cascata (Staircase Duplication)**. Descobrimos na prática que o parâmetro `Database` da API não filtra um mês exato, mas sim age como um ponto de partida temporal. Ele traz toda a série histórica subsequente à data solicitada.

Ou seja:
- O request de `Database=202011` retornou 5 anos inteiros de dados (100% da base).
- O request de `Database=202012` retornou 4 anos e 11 meses de dados (98% da base, quase tudo repetido).
- E assim sucessivamente.

Isso significa que os 2.5 GB armazenados na Camada Bronze eram, na verdade, uma gigantesca sobreposição dos mesmos registros da base de dados do BCB.

## 3. A Correção de Rota (Engenharia Eficiente)
Em vez de construir um processamento massivo (e caro) na Camada Prata para limpar um erro de premissa e deduplicar os 2.5 GB de lixo, adotamos uma abordagem inteligente de **Engenharia Eficiente**.

Como os dados brutos (Camada Bronze) nunca devem ser deletados ou mascarados — afinal, eles refletem exatamente o comportamento da fonte, por mais anômalo que seja —, mantivemos a rastreabilidade intacta. 

No entanto, como descobrimos matematicamente que o primeiro arquivo baixado (`_202011.csv`) já contém **a série histórica inteira de 2020 a 2026**, a nossa Camada Prata operará de forma extremamente cirúrgica e otimizada: 
Ela foi reescrita para ler **apenas o arquivo raiz** mais antigo, ignorando completamente o resto do ruído duplicado gerado pela extração iterativa.

### Conclusão e Lições Aprendidas
Este case demonstra a importância da maturidade técnica no ciclo de vida de dados:
1. **Medição e Teste:** Sem a fase de Data Profiling, este ruído passaria despercebido.
2. **Identificação de Falhas de Premissa:** Encontramos uma falha na nossa própria arquitetura de extração (assunção de comportamento da API).
3. **Refatoração Inteligente:** Corrigimos o pipeline na etapa seguinte do ETL, reduzindo a necessidade de processamento da Camada Prata de 2.5 GB para cerca de 50 MB (apenas os dados únicos reais), sem desperdiçar memória RAM, CPU ou perder a rastreabilidade da origem.
