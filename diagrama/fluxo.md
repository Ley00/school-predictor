# Fluxo da Pipeline

Este diagrama representa o fluxo operacional principal do projeto, desde a preparação opcional dos insumos locais até a geração dos relatórios e o consumo pelo dashboard.

```mermaid
flowchart TD
    A["Início da execução"] --> B["CLI: school_predictor"]
    B --> C{"Qual comando foi acionado?"}

    C -->|prepare-db| D["Preparar insumos locais"]
    D --> D1["Gerar dados falsos e ajustar estrutura"]
    D1 --> Z["Fim"]

    C -->|extract| E["Conectar ao banco"]
    E --> F["Executar extração privada"]
    F --> G["Gerar CSVs em artifacts/database/csv"]
    G --> Z

    C -->|workflow| H["Rodar workflow completo"]
    H --> I["Executar modo previsao_nota"]
    H --> J["Executar modo alerta_risco"]
    I --> K["Carregar CSVs e montar dataset temporal do modo"]
    J --> L["Carregar CSVs e montar dataset temporal do modo"]
    K --> M["Treinar, validar e testar regressão"]
    L --> N["Treinar, validar e testar classificação"]
    M --> P["Salvar artifacts/pipeline/previsao_nota"]
    N --> Q["Salvar artifacts/pipeline/alerta_risco"]
    P --> R["Consolidar relatórios escolares"]
    Q --> R

    C -->|pipeline| W["Rodar um modo isolado da pipeline"]
    W --> X["Escolher previsao_nota ou alerta_risco"]
    X --> Y["Carregar CSVs e montar dataset temporal do modo"]
    Y --> AA["Treinar, validar, testar e salvar artifacts/pipeline"]
    R --> S["Gerar artifacts/reports"]
    S --> T["Dashboard e leitura operacional"]
    T --> Z

    C -->|reports| R
    C -->|compare-history| U["Comparar min_history entre cenários"]
    U --> Z
    C -->|clean| V["Limpar caches e artefatos locais"]
    V --> Z
```

## Leitura rápida

- `prepare-db` atua nos insumos locais e é opcional, usado quando a base pública precisa ser atualizada.
- `extract` transforma os insumos preparados em CSVs canônicos.
- `workflow` é o fluxo principal do TCC: roda os dois modos técnicos, salva os artefatos de cada um e consolida os relatórios finais.
- `pipeline` executa apenas um modo isolado, útil para depuração e análises específicas.
- `previsao_nota` e `alerta_risco` partem dos mesmos CSVs canônicos, mas cada modo reconstrói seu próprio dataset temporal com corte de histórico diferente.
- o dashboard consome apenas os relatórios finais, não treina modelos.
