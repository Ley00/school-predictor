# Sequência Operacional

Este diagrama mostra, em ordem temporal, como uma execução completa do projeto acontece quando o usuário roda o workflow principal.

```mermaid
sequenceDiagram
    actor Usuario
    participant CLI as school_predictor.cli
    participant APP as application.py
    participant ORCH as orchestration.py
    participant DATA as data.py / dataset.py
    participant MODEL as modeling.py
    participant ART as artifacts/
    participant REPORT as reporting.py
    participant DASH as dashboard.py

    Usuario->>CLI: workflow --project-root .
    CLI->>APP: run_default_workflow(project_root)
    APP->>ORCH: run_full_reporting_pipeline(project_root)

    loop Para cada modo técnico
        ORCH->>DATA: load_source_tables()
        DATA-->>ORCH: tabelas CSV carregadas
        ORCH->>DATA: build_prediction_dataset()
        DATA-->>ORCH: dataset temporal
        ORCH->>DATA: select_model_columns()
        DATA-->>ORCH: colunas do modelo
        ORCH->>MODEL: train_and_evaluate()
        MODEL-->>ORCH: métricas e predictions
        ORCH->>ART: save_artifacts() e write_report()
    end

    ORCH->>REPORT: build_school_reports()
    REPORT->>ART: ler artifacts/pipeline/*
    REPORT->>ART: gravar artifacts/reports/*
    Usuario->>DASH: abrir dashboard
    DASH->>ART: ler artifacts/reports/*
    DASH-->>Usuario: consulta operacional
```

## Leitura rápida

- a execução principal sempre começa pela CLI.
- o workflow público usa os CSVs canônicos já existentes como entrada.
- os dois modos da pipeline são rodados separadamente dentro do mesmo workflow.
- cada modo produz seus próprios artefatos técnicos antes da consolidação final.
- a função `build_school_reports()` lê os artefatos dos dois modos e só então grava `artifacts/reports/`.
- o dashboard entra apenas depois, consumindo os relatórios finais já prontos.
- os relatórios finais surgem apenas depois que os dois modos terminam.
