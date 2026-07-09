from pathlib import Path

import pandas

from school_predictor.pipeline.config import PipelinePaths
from school_predictor.pipeline.modeling import (
    build_classification_baselines,
    build_regression_baselines,
    evaluate_classification,
    evaluate_regression,
)
from school_predictor.pipeline.orchestration import run_real_pipeline
from school_predictor.project import ensure_parent_dir


PREDICTION_KEY_COLUMNS = [
    "IDAluno",
    "NomePeriodo",
    "NomeSerie",
    "NomeDisciplina",
    "NomeEtapa",
]


def compare_pipeline_runs(
    project_root: str | Path = ".",
    mode: str = "previsao_nota",
    runs: int = 5,
    min_history: int | None = None,
) -> pandas.DataFrame:
    """Executa a mesma pipeline varias vezes e mede estabilidade dos resultados."""
    if runs < 2:
        raise ValueError("A comparacao de estabilidade exige pelo menos duas rodadas.")

    run_rows = []
    normalized_predictions = []
    resolved_paths = None

    for run_index in range(1, runs + 1):
        result = run_real_pipeline(project_root=project_root, min_history=min_history, mode=mode)
        resolved_paths = result["paths"]
        run_rows.append(_build_run_row(run_index, result))
        normalized_predictions.append(_normalize_predictions(result["predictions"]))

    comparison = pandas.DataFrame(run_rows)
    comparison = _add_prediction_comparison_columns(comparison, normalized_predictions)

    if resolved_paths is None:
        resolved_paths = PipelinePaths.from_project_root(project_root, mode=mode)

    comparison_csv = resolved_paths.output_dir / "run_stability_comparison.csv"
    summary_txt = resolved_paths.output_dir / "run_stability_summary.txt"
    ensure_parent_dir(comparison_csv)
    comparison.to_csv(comparison_csv, index=False, encoding="utf-8")
    summary_txt.write_text(_build_summary(comparison, mode, resolved_paths.min_history, comparison_csv), encoding="utf-8")
    return comparison


def _build_run_row(run_index: int, result: dict) -> dict:
    metrics = result["metrics"]
    split = metrics["split"]
    test_df = _select_test_frame(result["dataset"], split["test_years"])

    row = {
        "run": run_index,
        "mode": result["mode"],
        "min_history": result["paths"].min_history,
        "selected_regression": _format_candidate(metrics["selected_regression_candidate"]),
        "selected_classification": _format_candidate(metrics["selected_classification_candidate"]),
        "train_rows": split["train_rows"],
        "validation_rows": split["validation_rows"],
        "test_rows": split["test_rows"],
        "regression_mae": metrics["regression_model"]["mae"],
        "regression_rmse": metrics["regression_model"]["rmse"],
        "regression_acc_half": metrics["regression_model"]["accuracy_within_half_point"],
        "classification_precision": metrics["classification_model"]["precision"],
        "classification_recall": metrics["classification_model"]["recall"],
        "classification_f1": metrics["classification_model"]["f1"],
    }

    row.update(_build_baseline_metrics(test_df))
    return row


def _format_candidate(candidate: dict) -> str:
    return f"{candidate['source']}::{candidate['name']}"


def _select_test_frame(dataset: pandas.DataFrame, test_years: list[int]) -> pandas.DataFrame:
    years = {int(year) for year in test_years}
    return dataset[dataset["NomePeriodo"].astype(int).isin(years)].copy()


def _build_baseline_metrics(test_df: pandas.DataFrame) -> dict[str, float]:
    baseline_metrics = {}
    y_regression = test_df["target_nota_proxima"]
    y_classification = test_df["target_risco_proxima"]

    for name, predictions in build_regression_baselines(test_df).items():
        label = _baseline_label(name)
        metrics = evaluate_regression(y_regression, predictions)
        baseline_metrics[f"baseline_{label}_mae"] = metrics["mae"]
        baseline_metrics[f"baseline_{label}_rmse"] = metrics["rmse"]
        baseline_metrics[f"baseline_{label}_acc_half"] = metrics["accuracy_within_half_point"]

    for name, predictions in build_classification_baselines(test_df).items():
        label = _baseline_label(name)
        metrics = evaluate_classification(y_classification, predictions)
        baseline_metrics[f"baseline_{label}_precision"] = metrics["precision"]
        baseline_metrics[f"baseline_{label}_recall"] = metrics["recall"]
        baseline_metrics[f"baseline_{label}_f1"] = metrics["f1"]

    return baseline_metrics


def _baseline_label(name: str) -> str:
    return name.removeprefix("baseline_")


def _normalize_predictions(predictions: pandas.DataFrame) -> pandas.DataFrame:
    sort_columns = PREDICTION_KEY_COLUMNS + ["ValorMedia", "target_nota_proxima", "target_risco_proxima"]
    normalized = predictions.sort_values(sort_columns, kind="stable").reset_index(drop=True).copy()
    normalized["duplicate_index"] = normalized.groupby(PREDICTION_KEY_COLUMNS, dropna=False).cumcount()
    return normalized[
        PREDICTION_KEY_COLUMNS
        + [
            "duplicate_index",
            "predicted_next_grade",
            "predicted_risk_flag",
        ]
    ]


def _add_prediction_comparison_columns(
    comparison: pandas.DataFrame,
    normalized_predictions: list[pandas.DataFrame],
) -> pandas.DataFrame:
    reference = normalized_predictions[0]
    key_columns = PREDICTION_KEY_COLUMNS + ["duplicate_index"]

    max_grade_diffs = [0.0]
    risk_flag_changes = [0]
    missing_or_extra_rows = [0]

    for current in normalized_predictions[1:]:
        merged = reference.merge(
            current,
            on=key_columns,
            how="outer",
            suffixes=("_reference", "_current"),
            indicator=True,
        )
        matched = merged[merged["_merge"] == "both"].copy()
        if matched.empty:
            max_grade_diffs.append(float("nan"))
            risk_flag_changes.append(0)
        else:
            max_grade_diffs.append(
                float((matched["predicted_next_grade_reference"] - matched["predicted_next_grade_current"]).abs().max())
            )
            risk_flag_changes.append(
                int((matched["predicted_risk_flag_reference"] != matched["predicted_risk_flag_current"]).sum())
            )
        missing_or_extra_rows.append(int((merged["_merge"] != "both").sum()))

    comparison = comparison.copy()
    comparison["max_predicted_grade_diff_vs_run_1"] = max_grade_diffs
    comparison["risk_flag_changes_vs_run_1"] = risk_flag_changes
    comparison["missing_or_extra_prediction_rows_vs_run_1"] = missing_or_extra_rows
    comparison["regression_candidate_changed_vs_run_1"] = (
        comparison["selected_regression"] != comparison.loc[0, "selected_regression"]
    ).astype(int)
    comparison["classification_candidate_changed_vs_run_1"] = (
        comparison["selected_classification"] != comparison.loc[0, "selected_classification"]
    ).astype(int)
    return comparison


def _build_summary(comparison: pandas.DataFrame, mode: str, min_history: int, comparison_csv: Path) -> str:
    numeric_columns = comparison.select_dtypes(include="number").columns.difference(
        [
            "run",
            "min_history",
            "train_rows",
            "validation_rows",
            "test_rows",
        ]
    )
    metric_std = comparison[numeric_columns].std(numeric_only=True).fillna(0)
    metric_variations = metric_std[metric_std > 1e-12]

    prediction_changed = (
        comparison["max_predicted_grade_diff_vs_run_1"].fillna(0).max() > 1e-12
        or comparison["risk_flag_changes_vs_run_1"].max() > 0
        or comparison["missing_or_extra_prediction_rows_vs_run_1"].max() > 0
    )
    candidate_changed = (
        comparison["regression_candidate_changed_vs_run_1"].max() > 0
        or comparison["classification_candidate_changed_vs_run_1"].max() > 0
    )
    stable = not prediction_changed and not candidate_changed and metric_variations.empty

    lines = [
        "Validacao de estabilidade das rodadas da pipeline",
        "",
        f"- modo: {mode}",
        f"- rodadas executadas: {len(comparison)}",
        f"- historico minimo: {min_history}",
        f"- comparacao CSV: {comparison_csv}",
        f"- candidato de regressao: {comparison.loc[0, 'selected_regression']}",
        f"- candidato de classificacao: {comparison.loc[0, 'selected_classification']}",
        f"- linhas de treino/validacao/teste: {int(comparison.loc[0, 'train_rows'])}/{int(comparison.loc[0, 'validation_rows'])}/{int(comparison.loc[0, 'test_rows'])}",
        "",
    ]

    if stable:
        lines.append("Resultado: as rodadas nao alteraram metricas, candidatos selecionados ou predicoes.")
    else:
        lines.append("Resultado: foram encontradas variacoes entre as rodadas.")
        if not metric_variations.empty:
            lines.append("- metricas com desvio padrao observado:")
            for name, value in metric_variations.items():
                lines.append(f"  - {name}: {value:.12f}")
        if candidate_changed:
            lines.append("- houve mudanca em candidato selecionado.")
        if prediction_changed:
            lines.append("- houve mudanca em predicoes ou na quantidade de linhas comparadas.")

    lines.extend(
        [
            "",
            "Leitura para o TCC:",
            "- esta validacao verifica estabilidade das execucoes com a configuracao atual;",
            "- estabilidade entre rodadas nao equivale a validacao externa em outra escola ou periodo;",
            "- os baselines de ultima nota, media das duas ultimas, media das tres ultimas e baseline hibrido permanecem registrados para comparacao.",
        ]
    )
    return "\n".join(lines)
