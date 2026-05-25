import numpy
import pandas

from school_predictor.pipeline.data import prepare_absences, prepare_grades, prepare_payments, prepare_teachers


GROUP_KEYS = ["IDAluno", "NomePeriodo", "NomeDisciplina"]


def _build_absence_features(absences: pandas.DataFrame) -> pandas.DataFrame:
    """Agrega faltas por aluno, ano, disciplina e etapa."""
    if absences.empty:
        return pandas.DataFrame(columns=GROUP_KEYS + ["stage_order", "faltas_etapa", "faltas_acumuladas"])

    grouped = (
        absences.groupby(GROUP_KEYS + ["stage_order"], dropna=False)
        .size()
        .reset_index(name="faltas_etapa")
        .sort_values(GROUP_KEYS + ["stage_order"], kind="stable")
    )
    grouped["faltas_acumuladas"] = grouped.groupby(GROUP_KEYS)["faltas_etapa"].cumsum()
    return grouped


def _build_payment_features(payments: pandas.DataFrame) -> pandas.DataFrame:
    """Resume a situação financeira do aluno por ano letivo."""
    if payments.empty:
        return pandas.DataFrame(
            columns=[
                "IDAluno",
                "NomePeriodo",
                "pagamentos_registrados_ano",
                "pagamentos_pendentes_ano",
                "proporcao_mensalidades_ano",
                "media_valor_pagamento_ano",
                "media_dias_ate_pagamento_ano",
            ]
        )

    enriched = payments.copy()
    enriched["pagamento_pendente"] = (~enriched["PagoMovimento"].fillna(False)).astype(int)
    enriched["mensalidade_flag"] = enriched["EhMensalidadeMovimento"].fillna(False).astype(int)

    return (
        enriched.groupby(["IDAluno", "NomePeriodo"], dropna=False)
        .agg(
            pagamentos_registrados_ano=("IDMovimento", "count"),
            pagamentos_pendentes_ano=("pagamento_pendente", "sum"),
            proporcao_mensalidades_ano=("mensalidade_flag", "mean"),
            media_valor_pagamento_ano=("ValorMovimento", "mean"),
            media_dias_ate_pagamento_ano=("dias_ate_pagamento", "mean"),
        )
        .reset_index()
    )


def build_prediction_dataset(source_tables: dict[str, pandas.DataFrame], min_history: int = 2) -> pandas.DataFrame:
    """Monta o dataset longitudinal final da pipeline.

    Etapas principais:
    1. prepara notas, faltas, pagamentos e professores
    2. une tudo em uma única base por observação temporal
    3. cria atributos históricos e contextuais
    4. cria o alvo de próxima nota e risco
    5. aplica o corte de histórico mínimo por disciplina
    6. cria baselines de comparação
    """
    grades = prepare_grades(source_tables["grades"])
    absences = prepare_absences(source_tables["absences"])
    payments = prepare_payments(source_tables["payments"])
    teachers = prepare_teachers(source_tables["teachers"])

    absence_features = _build_absence_features(absences)
    payment_features = _build_payment_features(payments)

    dataset = grades.copy()
    dataset = dataset.merge(
        absence_features,
        on=GROUP_KEYS + ["stage_order"],
        how="left",
    )
    dataset = dataset.merge(
        payment_features,
        on=["IDAluno", "NomePeriodo"],
        how="left",
    )
    dataset = dataset.merge(
        teachers,
        on=["IDUnidade", "IDPeriodo", "IDCurso", "IDSerie", "IDTurma", "IDDisciplina"],
        how="left",
    )

    dataset["faltas_etapa"] = dataset["faltas_etapa"].fillna(0)
    dataset["faltas_acumuladas"] = dataset["faltas_acumuladas"].fillna(0)
    dataset["professor_disponivel"] = dataset["NomeFuncionario"].notna().astype(int)
    dataset["quantidade_professores_disciplina"] = dataset["quantidade_professores_disciplina"].fillna(0)
    dataset["NomeFuncionario"] = dataset["NomeFuncionario"].fillna("Professor não identificado ou não vinculado")

    # A partir daqui começa a engenharia temporal do histórico da disciplina.
    grouped_grade = dataset.groupby(GROUP_KEYS)["ValorMedia"]
    dataset["historico_disciplina_count"] = grouped_grade.cumcount()
    dataset["nota_anterior_1"] = grouped_grade.shift(1)
    dataset["nota_anterior_2"] = grouped_grade.shift(2)
    dataset["nota_anterior_3"] = grouped_grade.shift(3)
    dataset["media_duas_ultimas_notas"] = dataset[["nota_anterior_1", "nota_anterior_2"]].mean(axis=1)
    dataset["media_tres_ultimas_notas"] = dataset[["nota_anterior_1", "nota_anterior_2", "nota_anterior_3"]].mean(axis=1)
    dataset["delta_nota_1_2"] = dataset["nota_anterior_1"] - dataset["nota_anterior_2"]
    dataset["delta_nota_2_3"] = dataset["nota_anterior_2"] - dataset["nota_anterior_3"]

    disciplina_cumsum = grouped_grade.cumsum() - dataset["ValorMedia"]
    disciplina_cumcount = grouped_grade.cumcount()
    dataset["media_historica_disciplina"] = disciplina_cumsum / disciplina_cumcount.replace(0, numpy.nan)
    dataset["desvio_historico_disciplina"] = dataset[
        ["nota_anterior_1", "nota_anterior_2", "nota_anterior_3"]
    ].std(axis=1)
    dataset["tendencia_ultima_nota"] = dataset["ValorMedia"] - dataset["nota_anterior_1"]

    # Resumos do aluno dentro do próprio ano letivo.
    student_year_group = dataset.groupby(["IDAluno", "NomePeriodo"])["ValorMedia"]
    aluno_ano_cumsum = student_year_group.cumsum() - dataset["ValorMedia"]
    aluno_ano_cumcount = student_year_group.cumcount()
    dataset["media_historica_aluno_ano"] = aluno_ano_cumsum / aluno_ano_cumcount.replace(0, numpy.nan)

    student_year_summary = (
        grades.groupby(["IDAluno", "NomePeriodo"], dropna=False)["ValorMedia"]
        .mean()
        .reset_index(name="media_aluno_ano")
        .sort_values(["IDAluno", "NomePeriodo"], kind="stable")
    )
    student_year_summary["media_aluno_ano_anterior"] = student_year_summary.groupby("IDAluno")["media_aluno_ano"].shift(1)
    dataset = dataset.merge(
        student_year_summary[["IDAluno", "NomePeriodo", "media_aluno_ano_anterior"]],
        on=["IDAluno", "NomePeriodo"],
        how="left",
    )

    # Resumo do histórico da disciplina em anos anteriores.
    subject_year_summary = (
        grades.groupby(["IDAluno", "NomeDisciplina", "NomePeriodo"], dropna=False)["ValorMedia"]
        .mean()
        .reset_index(name="media_disciplina_ano")
        .sort_values(["IDAluno", "NomeDisciplina", "NomePeriodo"], kind="stable")
    )
    subject_year_summary["media_disciplina_ano_anterior"] = (
        subject_year_summary.groupby(["IDAluno", "NomeDisciplina"])["media_disciplina_ano"].shift(1)
    )
    dataset = dataset.merge(
        subject_year_summary[["IDAluno", "NomeDisciplina", "NomePeriodo", "media_disciplina_ano_anterior"]],
        on=["IDAluno", "NomeDisciplina", "NomePeriodo"],
        how="left",
    )

    # Referência média da corte para comparar o aluno com seus pares.
    cohort_stage_reference = (
        grades.groupby(["NomePeriodo", "NomeSerie", "NomeDisciplina", "stage_order"], dropna=False)["ValorMedia"]
        .mean()
        .reset_index(name="media_coorte_etapa")
    )
    dataset = dataset.merge(
        cohort_stage_reference,
        on=["NomePeriodo", "NomeSerie", "NomeDisciplina", "stage_order"],
        how="left",
    )
    dataset["desvio_em_relacao_coorte"] = dataset["ValorMedia"] - dataset["media_coorte_etapa"]

    # O alvo sempre usa a próxima observação disponível da sequência.
    dataset["target_nota_proxima"] = grouped_grade.shift(-1)
    dataset["target_risco_proxima"] = (dataset["target_nota_proxima"] < 6.0).astype("Int64")

    dataset["etapas_restantes"] = dataset.groupby(GROUP_KEYS)["stage_order"].transform("max") - dataset["stage_order"]

    dataset = dataset[dataset["target_nota_proxima"].notna()].copy()
    dataset = dataset[dataset["historico_disciplina_count"] >= min_history].copy()
    dataset["target_risco_proxima"] = dataset["target_risco_proxima"].astype(int)

    # Baselines simples continuam no dataset para comparação honesta com os modelos.
    dataset["baseline_ultima_nota"] = dataset["ValorMedia"]
    dataset["baseline_media_duas_ultimas"] = dataset["media_duas_ultimas_notas"].fillna(dataset["baseline_ultima_nota"])
    dataset["baseline_media_tres_ultimas"] = dataset["media_tres_ultimas_notas"].fillna(dataset["baseline_media_duas_ultimas"])
    dataset["baseline_hibrido"] = dataset[
        ["baseline_ultima_nota", "media_historica_disciplina", "media_historica_aluno_ano"]
    ].mean(axis=1)
    dataset["baseline_hibrido"] = dataset["baseline_hibrido"].fillna(dataset["baseline_ultima_nota"])

    numeric_fill_columns = [
        "nota_anterior_1",
        "nota_anterior_2",
        "nota_anterior_3",
        "media_duas_ultimas_notas",
        "media_tres_ultimas_notas",
        "delta_nota_1_2",
        "delta_nota_2_3",
        "media_historica_disciplina",
        "desvio_historico_disciplina",
        "tendencia_ultima_nota",
        "media_historica_aluno_ano",
        "media_aluno_ano_anterior",
        "media_disciplina_ano_anterior",
        "media_coorte_etapa",
        "desvio_em_relacao_coorte",
        "pagamentos_registrados_ano",
        "pagamentos_pendentes_ano",
        "proporcao_mensalidades_ano",
        "media_valor_pagamento_ano",
        "media_dias_ate_pagamento_ano",
    ]

    for column in numeric_fill_columns:
        if column in dataset.columns:
            dataset[column] = dataset[column].replace([numpy.inf, -numpy.inf], numpy.nan)

    dataset["possui_historico_disciplina"] = dataset["nota_anterior_1"].notna().astype(int)

    return dataset.reset_index(drop=True)


def select_model_columns(dataset: pandas.DataFrame) -> tuple[list[str], list[str]]:
    """Define quais colunas entram no modelo e quais são categóricas."""
    feature_columns = [
        "NomePeriodo",
        "NomeSerie",
        "NomeDisciplina",
        "NomeEtapa",
        "stage_order",
        "etapas_restantes",
        "ValorMedia",
        "nota_anterior_1",
        "nota_anterior_2",
        "nota_anterior_3",
        "media_duas_ultimas_notas",
        "media_tres_ultimas_notas",
        "delta_nota_1_2",
        "delta_nota_2_3",
        "media_historica_disciplina",
        "desvio_historico_disciplina",
        "tendencia_ultima_nota",
        "media_historica_aluno_ano",
        "media_aluno_ano_anterior",
        "media_disciplina_ano_anterior",
        "media_coorte_etapa",
        "desvio_em_relacao_coorte",
        "faltas_etapa",
        "faltas_acumuladas",
        "NomeFuncionario",
        "quantidade_professores_disciplina",
        "professor_disponivel",
        "pagamentos_registrados_ano",
        "pagamentos_pendentes_ano",
        "proporcao_mensalidades_ano",
        "media_valor_pagamento_ano",
        "media_dias_ate_pagamento_ano",
        "possui_historico_disciplina",
    ]
    categorical_columns = ["NomeSerie", "NomeDisciplina", "NomeEtapa"]
    if "NomeFuncionario" in feature_columns:
        categorical_columns.append("NomeFuncionario")
    return feature_columns, categorical_columns
