# Instrucoes para agentes e colaboradores automatizados

Leia este arquivo antes de qualquer analise, teste, alteracao de codigo ou refatoracao neste repositorio.

## Sobre o projeto

Este projeto faz parte de um TCC voltado para analise de dados escolares com o objetivo de antecipar riscos academicos. O foco principal e prever proximas notas dos alunos e identificar sinais de alerta para apoiar o professor antes que o aluno chegue a uma situacao de reprovacao bimestral, trimestral, semestral ou anual.

As fontes de dados do projeto incluem, entre outras:
- notas
- faltas
- pagamentos
- dados cadastrais e escolares

O projeto teve uma fase inicial orientada a grafo e evoluiu para uma abordagem mais tabular com Random Forest. Hoje, a arquitetura principal do projeto esta concentrada em `school_predictor/`.
Os artefatos canônicos gerados localmente devem ser tratados como pertencentes a `artifacts/`.

## Registro das alteracoes

Nao ha mais um arquivo unico e obrigatorio de registro neste repositorio.

Quando uma alteracao relevante for feita, a documentacao deve ser atualizada no artefato mais adequado ao contexto, por exemplo:
- `README.md` quando a mudanca afetar instalacao, configuracao local, estrutura do repositorio, fluxo de uso, comandos de execucao, artefatos gerados ou comportamento visivel do projeto
- pacote principal em `school_predictor/` quando a mudanca afetar a arquitetura atual da aplicacao
- `docs/ENTRADA_DE_DADOS_E_CONTRATOS.md` quando a mudanca afetar o fluxo de entrada dos dados, o contrato conceitual das extrações ou a forma segura de documentar o banco sem expor o SQL real
- `school_predictor/cli.py` quando a mudanca afetar a operacao principal do projeto por linha de comando
- arquivos em `docs/`
- notebooks em `crisp_dm/` quando a mudanca afetar as etapas CRISP-DM usadas para demonstrar o TCC
- projeto LaTeX da monografia em `tcc/`
- monografia do TCC
- arquivo de perguntas e respostas
- diagramas em `diagrama/` quando a mudanca afetar fluxo, arquitetura ou treinamento
- arquivos `.svg` dos diagramas quando houver versoes Mermaid em `.md`
- comentarios e docstrings do codigo quando isso melhorar a rastreabilidade tecnica
- `.gitignore` quando a mudanca criar novos artefatos gerados localmente, arquivos sensiveis ou saídas que nao devam subir para o Git

## Regras de trabalho

1. Nao alterar codigo sem antes entender em que etapa historica do projeto a mudanca se encaixa.
2. Preservar o contexto academico do TCC e registrar a motivacao tecnica de cada mudanca no artefato de documentacao mais adequado.
3. Priorizar explicacoes claras e rastreaveis, para que o orientador e o autor consigam entender o caminho seguido.
4. Evitar mudancas destrutivas ou reescritas amplas sem registrar:
   - problema identificado
   - decisao tomada
   - impacto esperado
5. Sempre considerar que os dados escolares possuem natureza temporal e sensivel.
6. Ao criar novos experimentos, registrar em documentacao adequada:
   - data
   - objetivo
   - arquivos afetados
   - resumo do resultado
   - proximo passo sugerido
7. Sempre que uma alteracao de codigo mudar fluxo, arquitetura, etapas da pipeline, criterios de treinamento, integracao de dados ou artefatos gerados, revisar e atualizar os diagramas da pasta `diagrama/`.
8. Sempre que um diagrama Mermaid da pasta `diagrama/` for criado ou alterado, regenerar tambem sua versao `.svg` correspondente para manter uma alternativa estavel de visualizacao.
9. Sempre que uma alteracao impactar setup, configuracao, comandos de uso, fluxo principal, estrutura documentada do repositorio ou saidas esperadas do projeto, atualizar tambem o `README.md`.
10. Sempre que uma alteracao mudar bootstrap, dependencias ou arquivos gerados localmente, revisar tambem o `.gitignore` e os arquivos de requisitos aplicaveis.
11. As consultas SQL reais de extração e a rotina SQL detalhada de preparação do banco devem permanecer fora do Git, carregadas localmente a partir de `school_predictor/database/private_sql/` e da camada privada `school_predictor/database/private_runtime.py`, ou de um diretório privado equivalente definido por ambiente.
12. Quando a entrada de dados mudar, documentar publicamente o contrato da extração, o significado dos CSVs e o objetivo de preparação do banco, mas nao expor o SQL bruto nem o desenho completo do banco institucional.
13. Sempre que qualquer alteracao de codigo mudar entrada de dados, preparacao, engenharia de atributos, escolha de modelos, metricas, validacao, relatorios, dashboard, artefatos gerados ou fluxo operacional, verificar os notebooks em `crisp_dm/` e atualizar os itens afetados quando necessario.
14. Os notebooks em `crisp_dm/` devem permanecer como material demonstrativo seguro: nao salvar outputs com dados reais sensiveis, nao expor SQL privado, credenciais, estrutura completa do banco institucional ou dados pessoais identificaveis.

## Objetivo das proximas iteracoes

As proximas iteracoes devem caminhar para:
- consolidacao da narrativa do TCC
- refatoracao da arquitetura atual
- criacao de uma pipeline reproduzivel
- uniao correta entre notas, faltas e pagamentos
- validacao de modelos com criterio temporal
- geracao de alertas pedagogicos com interpretabilidade
