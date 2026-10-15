```mermaid
---
title: "Arquitetura de Dados — Ecossistema de Pagamentos Pix (Bronze → Prata → Ouro)"
---

flowchart TB

    subgraph FONTES["🌐 Fontes Externas (APIs BCB)"]
        direction LR
        API_PIX["Olinda API<br/>Pix_DadosAbertos"]
        API_SPI["Olinda API<br/>SPI Liquidação"]
    end

    subgraph BRONZE["🟤 Camada Bronze — Dados Brutos (CSV)"]
        direction TB
        
        subgraph BRONZE_PIX["Contexto: Pix"]
            B_CAD["PixUsuariosCadastradosDICT<br/>70 linhas | 4 colunas<br/>📋 Arquivo único"]
            B_TXN["EstatisticasTransacoesPix<br/>~13k linhas/mês | 12 colunas<br/>📁 Particionado YYYYMM"]
            B_FRD["EstatisticasFraudesPix<br/>~50 linhas/mês | 24 colunas<br/>📁 Particionado YYYYMM"]
            B_MUN["TransacoesPixPorMunicipio<br/>~5.572 linhas/mês | 19 colunas<br/>📁 Particionado YYYYMM"]
        end
    end

    subgraph LIMPEZA["⚙️ Transformações (Bronze → Prata)"]
        direction TB
        L1["1. Conversão Monetária<br/>Text → Float<br/>vírgula , → ponto ."]
        L2["2. Padronização de Datas<br/>AnoMes 202608 → 2026-08-01"]
        L3["3. Renomeação snake_case<br/>PAG_PFPJ → pag_pfpj"]
        L4["4. Tratamento de Nulos<br/>Municipio_Ibge NaN → 0"]
        L5["5. Filtro de Ruído<br/>Remove 'Nao disponivel'"]
    end

    subgraph PRATA["⚪ Camada Prata — Dados Limpos"]
        direction TB
        P_ADO["prata_adocao_pix.csv<br/>~70 linhas<br/>Série temporal de usuários"]
        P_TXN["prata_transacoes_pix.csv<br/>~900k linhas consolidadas<br/>Valor como float"]
        P_FRD["prata_fraudes_pix.csv<br/>~70 linhas<br/>11 campos monetários limpos"]
        P_MUN["prata_municipios_pix.csv<br/>~390k linhas consolidadas<br/>Nulos geográficos tratados"]
    end

    subgraph ANALISES["🔬 Eixos Analíticos (Perguntas do Projeto)"]
        direction TB
        A1["📈 Eixo 1: Explosão da Adoção<br/>Crescimento mensal PF vs PJ"]
        A2["💳 Eixo 2: Substituição de Cartões<br/>Evolução P2B vs P2P"]
        A3["👥 Eixo 3: Perfil Demográfico<br/>Heatmap Idade × Região"]
        A4["🗺️ Eixo 4: Democratização Financeira<br/>Ticket médio capital vs interior"]
        A5["🔒 Eixo 5: Segurança<br/>Fraudes / Total Transações"]
        A6["🔄 Eixo 6: Eficácia do MED<br/>Taxa de Recuperação de Golpes"]
    end

    subgraph OURO["🟡 Camada Ouro — Dashboard Final"]
        DASH["Dashboard Custo Brasil<br/>Visualizações Interativas"]
    end

    %% Fluxo: Fontes → Bronze
    API_PIX --> B_CAD
    API_PIX --> B_TXN
    API_PIX --> B_FRD
    API_PIX --> B_MUN

    %% Fluxo: Bronze → Limpeza
    B_CAD --> L1
    B_TXN --> L1
    B_FRD --> L1
    B_MUN --> L1
    L1 --> L2 --> L3 --> L4 --> L5

    %% Fluxo: Limpeza → Prata
    L5 --> P_ADO
    L5 --> P_TXN
    L5 --> P_FRD
    L5 --> P_MUN

    %% Fluxo: Prata → Análises
    P_ADO --> A1
    P_TXN --> A2
    P_TXN --> A3
    P_MUN --> A4
    P_FRD --> A5
    P_TXN -.->|"Cruzamento mensal"| A5
    P_FRD --> A6

    %% Fluxo: Análises → Ouro
    A1 --> DASH
    A2 --> DASH
    A3 --> DASH
    A4 --> DASH
    A5 --> DASH
    A6 --> DASH

    %% Estilos
    classDef fonte fill:#4A90D9,color:#fff,stroke:#2C5F8A
    classDef bronze fill:#CD7F32,color:#fff,stroke:#8B5A2B
    classDef limpeza fill:#FF9800,color:#fff,stroke:#E65100
    classDef prata fill:#C0C0C0,color:#333,stroke:#808080
    classDef analise fill:#7B1FA2,color:#fff,stroke:#4A148C
    classDef ouro fill:#FFD700,color:#333,stroke:#B8860B

    class API_PIX,API_SPI fonte
    class B_CAD,B_TXN,B_FRD,B_MUN bronze
    class L1,L2,L3,L4,L5 limpeza
    class P_ADO,P_TXN,P_FRD,P_MUN prata
    class A1,A2,A3,A4,A5,A6 analise
    class DASH ouro
```

---

## Diagrama de Relacionamento entre Tabelas (Modelo Lógico da Prata)

```mermaid
erDiagram
    PRATA_ADOCAO_PIX {
        date data_referencia PK
        int qtd_usuarios_pf
        int qtd_usuarios_pj
        int qtd_usuarios_total
    }

    PRATA_TRANSACOES_PIX {
        date data_referencia PK
        string pag_pfpj
        string rec_pfpj
        string pag_regiao
        string rec_regiao
        string pag_idade
        string rec_idade
        string forma_iniciacao
        string natureza
        string finalidade
        float valor
        int quantidade
    }

    PRATA_FRAUDES_PIX {
        date data_referencia PK
        int qtde_pix_contestados
        int qtde_contestacoes_aceitas
        int qtde_contestacoes_rejeitadas
        float taxa_contestacoes_100mil
        int qtde_usuarios_marcados_fraude
        int qtde_chaves_marcadas_fraude
        float valor_contestados_aceitos
        int qtde_devolvida_integral_med
        float valor_devolvidos_integralmente
        int qtde_devolvida_parcial_med
        float valor_devolvidos_parcialmente
        float valor_residual_nao_devolvido
        float percentual_devolucao
    }

    PRATA_MUNICIPIOS_PIX {
        date data_referencia PK
        int municipio_ibge PK
        string municipio
        int estado_ibge
        string estado
        string sigla_regiao
        string regiao
        float vl_pagador_pf
        int qt_pagador_pf
        float vl_pagador_pj
        int qt_pagador_pj
        float vl_recebedor_pf
        int qt_recebedor_pf
        float vl_recebedor_pj
        int qt_recebedor_pj
        int qt_pes_pagador_pf
        int qt_pes_pagador_pj
        int qt_pes_recebedor_pf
        int qt_pes_recebedor_pj
    }

    PRATA_ADOCAO_PIX ||--o{ PRATA_TRANSACOES_PIX : "data_referencia"
    PRATA_ADOCAO_PIX ||--o{ PRATA_FRAUDES_PIX : "data_referencia"
    PRATA_ADOCAO_PIX ||--o{ PRATA_MUNICIPIOS_PIX : "data_referencia"
    PRATA_TRANSACOES_PIX }o--|| PRATA_FRAUDES_PIX : "data_referencia"
