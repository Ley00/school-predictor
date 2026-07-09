# Arquitetura da Solucao

Este diagrama resume a arquitetura final em blocos maiores, priorizando a leitura do caminho dos dados e das responsabilidades principais da solucao.

```mermaid
flowchart LR
    subgraph Operacao["Operacao e Interface"]
        CLI["CLI e execucao<br/>main.py e school_predictor.cli"]
        DASH["Dashboard<br/>app/dashboard.py"]
    end

    subgraph Privada["Camada privada local"]
        DB["Insumos locais e rotinas privadas<br/>prepare-db, access, maintenance"]
        EXT["Extracao privada<br/>extraction e private_runtime/private_sql"]
    end

    subgraph Publica["Camada publica reproduzivel"]
        CSV["CSVs canonicos<br/>artifacts/database/csv"]
        PIPE["Pipeline analitica<br/>data, dataset, orchestration, modeling, reporting"]
        TECH["Artefatos tecnicos<br/>artifacts/pipeline"]
        REPORTS["Relatorios finais<br/>artifacts/reports"]
    end

    subgraph Consumo["Uso institucional"]
        SCHOOL["Professor, coordenacao,<br/>secretaria e dashboard"]
    end

    CLI --> DB
    DB --> EXT
    EXT --> CSV
    CLI --> PIPE
    CSV --> PIPE
    PIPE --> TECH
    PIPE --> REPORTS
    REPORTS --> DASH
    REPORTS --> SCHOOL
```

## Leitura rapida

- a camada privada local prepara os insumos e gera os CSVs canonicos fora do Git;
- os CSVs canonicos sao a interface publica de entrada da pipeline;
- a pipeline analitica produz artefatos tecnicos e relatorios finais;
- a escola e o dashboard consomem apenas os relatorios finais.
