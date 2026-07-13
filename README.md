# School Predictor for Academic Risk Analysis

Projeto de TCC para análise preditiva de dados escolares, com foco em antecipar risco acadêmico e apoiar decisões de professor, coordenação e secretaria.

Hoje o repositório está organizado em torno de uma arquitetura principal chamada `school_predictor/`, que concentra:
- acesso ao banco
- preparação local dos insumos públicos
- extração de CSVs
- pipeline de modelagem
- geração de relatórios
- dashboard em Streamlit

## Objetivo

O projeto busca responder duas perguntas principais:
- qual tende a ser a próxima nota do aluno em uma disciplina
- se esse aluno está entrando em uma zona de atenção pedagógica

Esses sinais são consolidados em relatórios operacionais para uso escolar.

## Arquitetura atual

### Núcleo principal

- `school_predictor/`
  - pacote principal da aplicação
- `school_predictor/database/`
  - acesso ao banco, preparação local dos insumos e extração dos CSVs
- `school_predictor/pipeline/`
  - dataset, modelagem, avaliação e relatórios
- `school_predictor/app/`
  - dashboard Streamlit
- `artifacts/`
  - diretório canônico dos CSVs extraídos, artefatos da pipeline e relatórios operacionais

### Pontos de entrada

- `main.py`
  - ponto de entrada mínimo, hoje delegando para a CLI
- `dashboard_streamlit.py`
  - ponto de entrada do dashboard
- `school_predictor/cli.py`
  - CLI principal do projeto

### Pastas acadêmicas e de apoio

- `docs/`
  - documentação textual do TCC
- `diagrama/`
  - diagramas da arquitetura e do fluxo
- `crisp_dm/`
  - notebooks demonstrativos organizados pelas fases do CRISP-DM para apresentacao academica

### Itens locais fora do Git

- `tcc/`
  - monografia e pré-projeto em LaTeX mantidos apenas localmente
- `school_predictor/database/private_sql/`
  - consultas SQL reais de extração e preparação
- `school_predictor/database/private_runtime.py`
  - orquestração privada local do banco

### Escopo atual

- o repositório foi reduzido ao fluxo operacional atual do TCC
- o código histórico fora desse fluxo foi descartado
- o runtime atual não depende mais da pilha legada de grafos/PyTorch
- `artifacts/` concentra as entradas e saídas locais necessárias para operação

## Estrutura resumida

```text
.
├── school_predictor/
│   ├── app/
│   ├── database/
│   └── pipeline/
├── pyproject.toml
├── artifacts/
├── main.py
├── dashboard_streamlit.py
├── crisp_dm/
├── docs/
└── diagrama/
```

## Requisitos

- Python 3.12 a 3.14
- ambiente virtual `.venv`
- SQL Server local ou acessível pela rede
- ODBC Driver 18 for SQL Server

Para o dashboard:
- `streamlit`
- `plotly`

Para a monografia:
- `MacTeX`, `TeX Live` ou equivalente

## Configuração local segura

O repositório não versiona:
- credenciais do banco
- arquivos `.env`
- consultas SQL reais de extração
- artefatos locais de dados e resultados
- a monografia LaTeX em `tcc/`

Ignorados no Git:
- `.env`
- `school_predictor/database/private_sql/`
- `school_predictor/database/private_runtime.py`
- `artifacts/`
- `tcc/`

## Proteção das consultas SQL

As consultas reais de extração do banco nao ficam mais expostas no código versionado. O repositório público mantém apenas:
- o fluxo de extração
- o fluxo público de preparação do banco
- o contrato conceitual das entradas
- os CSVs esperados pela pipeline

As consultas SQL reais ficam em ambiente local, na pasta ignorada:
- `school_predictor/database/private_sql/`

A orquestração privada do banco e da extração também fica em um arquivo local ignorado:
- `school_predictor/database/private_runtime.py`

Se necessário, você também pode apontar outro diretório privado com:
- `SCHOOL_PREDICTOR_SQL_DIR`

Documentação pública da entrada dos dados:
- [docs/ENTRADA_DE_DADOS_E_CONTRATOS.md](/Users/warley/Desktop/Development/Personal/KnowledgeGraphModelSchoolEducation/docs/ENTRADA_DE_DADOS_E_CONTRATOS.md)

## Como replicar o repositório sem acesso ao banco institucional

Para entender ou reproduzir a arquitetura pública do projeto, o repositório precisa apenas do contrato dos CSVs em:
- `artifacts/database/csv/aluno.csv`
- `artifacts/database/csv/media_nota_aluno.csv`
- `artifacts/database/csv/faltas_aluno.csv`
- `artifacts/database/csv/pagamento_aluno.csv`
- `artifacts/database/csv/responsaveis_aluno.csv`
- `artifacts/database/csv/professor_disciplina.csv`

Esses arquivos são a interface de entrada da pipeline. Quem não tiver acesso ao banco institucional pode:
- gerar arquivos equivalentes com a mesma granularidade e significado
- ou montar um conjunto de dados sintéticos seguindo o contrato em `docs/ENTRADA_DE_DADOS_E_CONTRATOS.md`

Em outras palavras:
- dados sintéticos sao a forma recomendada de alimentar o projeto publicado
- os CSVs canônicos são a forma mínima de reproduzir a pipeline pública

Exemplos mínimos, apenas para entender o formato esperado de cada CSV:

`aluno.csv`
```csv
IDUnidade,NomeUnidade,IDPeriodo,NomePeriodo,IDCurso,NomeCurso,IDSerie,NomeSerie,IDTurma,ApelidoTurma,IDMatricula,SituacaoMatricula,IDAluno,NomeAluno
U1,Escola Exemplo,P2025,2025,C1,Ensino Médio,S1,1ª Série,T1,1ª Série A - Matutino,M1,Matriculado,A1,Aluno 00001
```

`media_nota_aluno.csv`
```csv
IDUnidade,NomeUnidade,IDPeriodo,NomePeriodo,IDCurso,NomeCurso,IDSerie,NomeSerie,IDTurma,ApelidoTurma,IDMatricula,SituacaoMatricula,IDAluno,NomeAluno,IDDisciplina,NomeDisciplina,IDEtapa,NomeEtapa,IDMedia,ValorMedia
U1,Escola Exemplo,P2025,2025,C1,Ensino Médio,S1,1ª Série,T1,1ª Série A - Matutino,M1,Matriculado,A1,Aluno 00001,D1,Matemática,E1,1º BIMESTRE,MED1,7.5
```

`faltas_aluno.csv`
```csv
IDUnidade,NomeUnidade,IDPeriodo,NomePeriodo,IDCurso,NomeCurso,IDSerie,NomeSerie,IDTurma,ApelidoTurma,IDMatricula,SituacaoMatricula,IDAluno,NomeAluno,IDDisciplinaxSerie,IDDisciplina,NomeDisciplina,IDEtapaxSerie,IDEtapa,NomeEtapa,IDFalta,DataFalta
U1,Escola Exemplo,P2025,2025,C1,Ensino Médio,S1,1ª Série,T1,1ª Série A - Matutino,M1,Matriculado,A1,Aluno 00001,DS1,D1,Matemática,ES1,E1,1º BIMESTRE,F1,2025-03-12
```

`pagamento_aluno.csv`
```csv
IDUnidade,NomeUnidade,IDPeriodo,NomePeriodo,IDCurso,NomeCurso,IDSerie,NomeSerie,IDTurma,ApelidoTurma,IDMatricula,SituacaoMatricula,IDAluno,NomeAluno,IDMovimento,IDMatriculaMovimento,ParcelaMovimento,DescricaoMovimento,DataAntecipadoMovimento,ValorAntecipadoMovimento,DataVencimentoMovimento,ValorMovimento,PagoMovimento,ValorPagoMovimento,EhMensalidadeMovimento,EhMatriculaMovimento
U1,Escola Exemplo,P2025,2025,C1,Ensino Médio,S1,1ª Série,T1,1ª Série A - Matutino,M1,Matriculado,A1,Aluno 00001,MOV1,MM1,1,Mensalidade Março,2025-03-05,850.0,2025-03-05,850.0,True,850.0,True,False
```

`responsaveis_aluno.csv`
```csv
IDUnidade,NomeUnidade,IDPeriodo,NomePeriodo,IDCurso,NomeCurso,IDSerie,NomeSerie,IDTurma,ApelidoTurma,IDMatricula,SituacaoMatricula,IDAluno,NomeAluno,IDResponsavel,NomeResponsavel,TipoResponsavel
U1,Escola Exemplo,P2025,2025,C1,Ensino Médio,S1,1ª Série,T1,1ª Série A - Matutino,M1,Matriculado,A1,Aluno 00001,R1,Responsável 00001,Mãe
```

`professor_disciplina.csv`
```csv
IDUnidade,NomeUnidade,IDPeriodo,NomePeriodo,IDCurso,NomeCurso,IDSerie,NomeSerie,IDTurma,ApelidoTurma,IDDisciplinaxFuncionario,IDFuncionario,NomeFuncionario,IDDisciplina,NomeDisciplina
U1,Escola Exemplo,P2025,2025,C1,Ensino Médio,S1,1ª Série,T1,1ª Série A - Matutino,DF1,F1,Professor 00001,D1,Matemática
```

### Significado das colunas dos CSVs

Colunas acadêmicas comuns, presentes em quase todos os arquivos:
- `IDUnidade`: identificador interno da unidade escolar.
- `NomeUnidade`: nome legível da unidade escolar.
- `IDPeriodo`: identificador interno do período letivo.
- `NomePeriodo`: ano ou nome do período letivo usado pela pipeline.
- `IDCurso`: identificador interno do curso.
- `NomeCurso`: nome do curso, como `Ensino Fundamental` ou `Ensino Médio`.
- `IDSerie`: identificador interno da série.
- `NomeSerie`: nome legível da série, como `6º Ano` ou `1ª Série`.
- `IDTurma`: identificador interno da turma.
- `ApelidoTurma`: nome ou apelido legível da turma.
- `IDMatricula`: identificador interno da matrícula do aluno.
- `SituacaoMatricula`: situação acadêmica da matrícula, como `Matriculado`.
- `IDAluno`: identificador interno do aluno.
- `NomeAluno`: nome do aluno em formato artificial compatível com o fluxo público.

Colunas específicas de `aluno.csv`:
- `IDUnidadexTipoCurso`: identificador da relação entre unidade e tipo de curso.
- `IDCursoxPeriodo`: identificador da relação entre curso e período letivo.
- `DataMatricula`: data da matrícula do aluno.
- `CodigoAluno`: código institucional do aluno.
- `SexoAluno`: sexo cadastrado do aluno.
- `DataNascimentoAluno`: data de nascimento do aluno.
- `QuadraResidenciaAluno`: quadra do endereço residencial.
- `LoteResidenciaAluno`: lote do endereço residencial.
- `NumeroResidenciaAluno`: número do imóvel residencial.
- `ComplementoResidenciaAluno`: complemento do endereço residencial.
- `BairroResidenciaAluno`: bairro do endereço residencial.
- `CEPResidenciaAluno`: CEP do endereço residencial.

Colunas específicas de `media_nota_aluno.csv`:
- `IDDisciplina`: identificador interno da disciplina.
- `NomeDisciplina`: nome legível da disciplina.
- `IDEtapa`: identificador interno da etapa avaliativa.
- `NomeEtapa`: nome da etapa, como `1º BIMESTRE`.
- `IDMedia`: identificador interno do registro de média.
- `ValorMedia`: nota ou média do aluno naquela disciplina e etapa.

Colunas específicas de `faltas_aluno.csv`:
- `IDDisciplinaxSerie`: identificador da relação entre disciplina e série.
- `IDEtapaxSerie`: identificador da relação entre etapa e série.
- `IDFalta`: identificador interno do evento de falta.
- `DataFalta`: data em que a falta ocorreu.

Colunas específicas de `pagamento_aluno.csv`:
- `IDMovimento`: identificador interno do movimento financeiro.
- `IDMatriculaMovimento`: identificador da matrícula associada ao movimento.
- `ParcelaMovimento`: número ou referência da parcela.
- `DescricaoMovimento`: descrição legível da cobrança ou item financeiro.
- `DataAntecipadoMovimento`: data em que o pagamento ocorreu ou foi antecipado.
- `ValorAntecipadoMovimento`: valor antecipado pago, quando existir.
- `DataVencimentoMovimento`: data de vencimento da cobrança.
- `ValorMovimento`: valor original da cobrança.
- `PagoMovimento`: indica se a cobrança foi paga.
- `ValorPagoMovimento`: valor efetivamente pago.
- `EhMensalidadeMovimento`: indica se o movimento é mensalidade.
- `EhMatriculaMovimento`: indica se o movimento é taxa de matrícula.

Colunas específicas de `responsaveis_aluno.csv`:
- `IDResponsavel`: identificador interno do responsável.
- `TipoResponsavel`: tipo do vínculo, como `Mãe`, `Pai` ou outro responsável.
- `NomeResponsavel`: nome do responsável em formato artificial compatível com o fluxo público.
- `SexoResponsavel`: sexo cadastrado do responsável.
- `DataNascimentoResponsavel`: data de nascimento do responsável.
- `LogradouroResidenciaResponsavel`: logradouro do endereço residencial do responsável.
- `QuadraResidenciaResponsavel`: quadra do endereço residencial do responsável.
- `LoteResidenciaResponsavel`: lote do endereço residencial do responsável.
- `NumeroResidenciaResponsavel`: número do imóvel residencial do responsável.
- `ComplementoResidenciaResponsavel`: complemento do endereço residencial do responsável.
- `BairroResidenciaResponsavel`: bairro do endereço residencial do responsável.
- `CEPResidenciaResponsavel`: CEP do endereço residencial do responsável.

Colunas específicas de `professor_disciplina.csv`:
- `IDDisciplinaxFuncionario`: identificador interno do vínculo entre disciplina e professor.
- `IDFuncionario`: identificador interno do professor ou funcionário.
- `NomeFuncionario`: nome do professor ou funcionário em formato artificial compatível com o fluxo público.
- `IDDisciplina`: identificador interno da disciplina vinculada ao professor.
- `NomeDisciplina`: nome da disciplina vinculada ao professor.

### 1. Criar o `.env`

```bash
cp .env.example .env
```

Preencha com os dados locais:

```env
DB_DRIVER=ODBC Driver 18 for SQL Server
DB_NAME=COLEGIO_TESTE
DB_HOST=127.0.0.1
DB_PORT=1433
DB_USER=seu_usuario
DB_PASS=sua_senha
```

### 2. Criar a camada privada local de operação com banco

```bash
cp school_predictor/database/private_runtime.example.py school_predictor/database/private_runtime.py
```

Esse arquivo local deve concentrar duas funções:
- `prepare_private_database(...)`
- `extract_private_school_data(...)`

Ele permanece fora do Git e é a camada onde ficam:
- a preparação local dos insumos públicos
- a extração e geração dos dados sintéticos ainda necessários

## Instalação

O repositório usa `pyproject.toml` como fonte principal de metadados e dependências.

Instalação recomendada:

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -e .
```

Arquivo usado nessa instalação:
- `pyproject.toml`
  - metadados do projeto, faixa validada de Python e dependências da aplicação

Observações:
- a faixa validada de Python para o projeto é `3.12` a `3.14`
- a instalação Python não instala dependências de sistema como ODBC Driver 18 ou MacTeX
- o driver ODBC e o SQL Server continuam sendo pré-requisitos externos
- se você preferir, ainda pode usar seu próprio gerenciamento de ambiente local

## CLI principal

O projeto agora possui uma CLI única:

```bash
./.venv/bin/python -m school_predictor --help
```

Comandos disponíveis:
- `workflow`
- `prepare-db`
- `extract`
- `pipeline`
- `reports`
- `compare-history`
- `compare-runs`
- `clean`

## Fluxos principais

## 1. Preparar novos insumos locais

Quando for necessário atualizar os insumos locais, o fluxo é:
- renomear para `COLEGIO_TESTE`
- remover tabelas desnecessárias
- gerar uma base sintética compatível com o contrato público
- reorganizar índices e atualizar estatísticas

O código principal fica em:
- `school_predictor/database/maintenance.py`

Na arquitetura atual, a implementação real dessa etapa deve ficar no arquivo local:
- `school_predictor/database/private_runtime.py`

No fluxo atual, essa etapa pode ser chamada por:

```bash
./.venv/bin/python -m school_predictor prepare-db
```

## 2. Extrair CSVs do banco

Depois da preparação do banco, a extração principal é feita por:
- `school_predictor/database/extraction.py`
- `school_predictor/database/queries.py`

Exemplo:

```bash
./.venv/bin/python -m school_predictor extract --project-root .
```

Esse fluxo gera os CSVs-base usados pela modelagem, como:
- `aluno.csv`
- `media_nota_aluno.csv`
- `faltas_aluno.csv`
- `pagamento_aluno.csv`
- `responsaveis_aluno.csv`
- `professor_disciplina.csv`

Eles passam a ser gravados de forma canônica em:
- `artifacts/database/csv/`

As consultas SQL que alimentam essa etapa sao carregadas localmente de:
- `school_predictor/database/private_sql/`

Na arquitetura atual, a implementação real dessa etapa também fica no arquivo local:
- `school_predictor/database/private_runtime.py`

O GitHub deve mostrar apenas o contrato conceitual da entrada de dados, nao o SQL real nem o desenho completo do banco.

O mesmo princípio vale para qualquer rotina local de preparação dos insumos: a aplicação publica o fluxo, o contrato e o objetivo da etapa, mas mantém fora do Git detalhes locais que não fazem parte da versão pública baseada em dados sintéticos.

Se o banco já tiver sido previamente tratado, você pode testar o projeto começando diretamente pela extração:

```bash
./.venv/bin/python -m school_predictor extract --project-root .
```

## 3. Rodar a pipeline preditiva

O núcleo atual está em:
- `school_predictor/pipeline/`

Execução completa:

```bash
./.venv/bin/python -m school_predictor workflow --project-root .
```

Execuções por modo:

```bash
./.venv/bin/python -m school_predictor pipeline --mode previsao_nota --project-root .
./.venv/bin/python -m school_predictor pipeline --mode alerta_risco --project-root .
```

O `main.py` já aponta para o fluxo principal:

```python
from school_predictor.cli import main

main(["workflow", "--project-root", "."])
```

No VS Code, o `F5` foi configurado em `.vscode/launch.json` para executar esse mesmo fluxo p\'ublico (`workflow --project-root ${workspaceFolder}`). Esse caminho roda a pipeline anal\'itica completa e gera os relat\'orios finais a partir dos CSVs can\^onicos j\'a existentes, sem acionar `prepare-db`, `extract` ou rotinas locais de gera\c{c}\~ao e prepara\c{c}\~ao dos dados sintéticos publicados.

Comparação de histórico mínimo:

```bash
./.venv/bin/python -m school_predictor compare-history --mode previsao_nota --history-values 1 2 3
```

Validação de estabilidade entre rodadas da mesma pipeline:

```bash
./.venv/bin/python -m school_predictor compare-runs --project-root . --mode previsao_nota --runs 5
./.venv/bin/python -m school_predictor compare-runs --project-root . --mode alerta_risco --runs 5
```

Esse comando executa o mesmo modo várias vezes e gera:
- `artifacts/pipeline/<modo>/run_stability_comparison.csv`
- `artifacts/pipeline/<modo>/run_stability_summary.txt`

O objetivo é verificar se métricas, candidatos selecionados e predições permanecem estáveis entre rodadas, mantendo a comparação com os baselines de última nota, média das duas últimas, média das três últimas e baseline híbrido.

## 5. Limpar artefatos locais

Para remover caches Python e auxiliares de compilação da monografia:

```bash
./.venv/bin/python -m school_predictor clean --project-root .
```

Para apenas simular a limpeza:

```bash
./.venv/bin/python -m school_predictor clean --project-root . --dry-run
```

Se você quiser limpar também os resultados locais da pipeline e das extrações:

```bash
./.venv/bin/python -m school_predictor clean --project-root . --targets latex pycache results
```

O alvo `results` é opcional justamente para evitar apagar saídas analíticas do TCC sem intenção.

## 4. Rodar o dashboard

Com o ambiente virtual ativo:

```bash
./.venv/bin/streamlit run dashboard_streamlit.py
```

Se os artefatos ainda não tiverem sido gerados nesta máquina, execute antes a pipeline principal:

```bash
./.venv/bin/python -m school_predictor workflow --project-root .
```

O dashboard real está em:
- `school_predictor/app/dashboard.py`

## Saídas geradas localmente

Os artefatos canônicos da pipeline passam a ser gravados em:
- `artifacts/pipeline/previsao_nota/`
- `artifacts/pipeline/alerta_risco/`
- `artifacts/reports/`

Essas pastas guardam:
- datasets finais
- previsões
- análises de erro
- relatórios técnicos
- relatórios escolares
- ranking executivo

Esses arquivos não devem ser enviados ao GitHub.

## Modelagem atual

O projeto trabalha com dois objetivos:
- regressão da próxima nota
- classificação de risco pedagógico

Os principais candidatos comparados hoje são:
- `HistGradientBoosting`
- `RandomForest`
- baselines temporais baseados nas últimas notas

As métricas principais são:
- `MAE` para regressão
- `F1` para classificação

## Monografia e pré-projeto

A pasta local `tcc/`, mantida fora do Git, contém o projeto LaTeX do IFG para:
- monografia final
- pré-projeto

Arquivos principais:
- `tcc/modelo-ifg.tex`
- `tcc/preprojeto-ifg.tex`

Compilar a monografia:

```bash
cd tcc
latexmk -pdf -interaction=nonstopmode modelo-ifg.tex
```

Observa\c{c}\~ao: os diagramas originais permanecem versionados em `diagrama/*.svg` como fonte can\^onica. Para a monografia local, o Cap\'itulo 4 consome as vers\~oes vetoriais exportadas em `tcc/fig/diagrama-export/*.pdf`, geradas a partir desses SVGs. Quando algum diagrama for alterado, regenere tamb\'em o PDF correspondente com o Inkscape antes de recompilar a monografia. Exemplo:

```bash
inkscape diagrama/arquitetural.svg --export-filename=tcc/fig/diagrama-export/arquitetural.pdf
inkscape diagrama/fluxo.svg --export-filename=tcc/fig/diagrama-export/fluxo.pdf
```

Compilar o pré-projeto:

```bash
cd tcc
latexmk -pdf -interaction=nonstopmode preprojeto-ifg.tex
```

## Consolidação da refatoração

Após a limpeza final:
- `school_predictor/` ficou como única base de código da aplicação
- `main.py` e `dashboard_streamlit.py` permanecem como pontos de entrada mínimos
- `artifacts/` concentra as entradas e saídas locais do fluxo operacional
- o código histórico fora do fluxo atual foi removido para reduzir ruído arquitetural

## Privacidade e sensibilidade

Este projeto documenta um dom\'inio escolar sens\'ivel. Por isso:
- nunca versionar credenciais
- nunca versionar SQL real de extração ou preparação do banco
- nunca subir datasets e resultados locais
- nunca subir a monografia local em `tcc/`
- manter a vers\~ao p\'ublica baseada em dados sintéticos

## Documentação complementar

- `docs/PERGUNTAS_E_RESPOSTAS_TCC.txt`
- `docs/REGRA_MINIMA_HISTORICO_AVALIACAO.txt`
- `diagrama/fluxo.md`
- `diagrama/arquitetural.md`
- `diagrama/casos_de_uso.md`
- `diagrama/sequencia_operacional.md`

## Licença

Ver [LICENSE](LICENSE).
