import argparse
from pathlib import Path

from school_predictor.application import (
    extract_school_data_from_database,
    prepare_updated_database,
    run_default_workflow,
    run_full_reporting_pipeline,
    run_real_pipeline,
)
from school_predictor.cleanup import AVAILABLE_TARGETS, DEFAULT_TARGETS, clean_workspace
from school_predictor.pipeline.history import write_history_comparison
from school_predictor.pipeline.reporting import build_school_reports
from school_predictor.pipeline.stability import compare_pipeline_runs


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="school-predictor",
        description="CLI principal do projeto de predicao escolar.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    workflow_parser = subparsers.add_parser("workflow", help="Roda a pipeline completa com relatórios finais.")
    workflow_parser.add_argument("--project-root", default=".")

    prepare_parser = subparsers.add_parser("prepare-db", help="Prepara um banco restaurado localmente.")
    prepare_parser.add_argument("--user", default="default")
    prepare_parser.add_argument("--source-database")

    extract_parser = subparsers.add_parser("extract", help="Extrai os CSVs base a partir do banco.")
    extract_parser.add_argument("--user", default="default")
    extract_parser.add_argument("--project-root", default=".")
    extract_parser.add_argument("--student-name")
    extract_parser.add_argument("--academic-period")
    extract_parser.add_argument("--specific", action="store_true")

    pipeline_parser = subparsers.add_parser("pipeline", help="Roda um modo isolado da pipeline.")
    pipeline_parser.add_argument("--project-root", default=".")
    pipeline_parser.add_argument("--mode", choices=("previsao_nota", "alerta_risco"), required=True)
    pipeline_parser.add_argument("--min-history", type=int)

    reports_parser = subparsers.add_parser("reports", help="Gera apenas os relatórios escolares finais.")
    reports_parser.add_argument("--project-root", default=".")

    history_parser = subparsers.add_parser("compare-history", help="Compara cortes de histórico mínimo.")
    history_parser.add_argument("--project-root", default=".")
    history_parser.add_argument("--mode", choices=("previsao_nota", "alerta_risco"), default="previsao_nota")
    history_parser.add_argument("--history-values", nargs="+", type=int, default=[1, 2, 3])

    runs_parser = subparsers.add_parser("compare-runs", help="Compara estabilidade entre múltiplas rodadas da pipeline.")
    runs_parser.add_argument("--project-root", default=".")
    runs_parser.add_argument("--mode", choices=("previsao_nota", "alerta_risco"), required=True)
    runs_parser.add_argument("--runs", type=int, default=5)
    runs_parser.add_argument("--min-history", type=int)

    clean_parser = subparsers.add_parser("clean", help="Remove artefatos locais de build e cache.")
    clean_parser.add_argument("--project-root", default=".")
    clean_parser.add_argument(
        "--targets",
        nargs="+",
        choices=AVAILABLE_TARGETS,
        default=list(DEFAULT_TARGETS),
        help="Tipos de artefatos locais a remover.",
    )
    clean_parser.add_argument("--dry-run", action="store_true", help="Lista o que seria removido sem apagar arquivos.")

    return parser


def main(argv: list[str] | None = None):
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "workflow":
        return run_default_workflow(project_root=args.project_root)

    if args.command == "prepare-db":
        return prepare_updated_database(user=args.user, source_database=args.source_database)

    if args.command == "extract":
        return extract_school_data_from_database(
            user=args.user,
            project_root=args.project_root,
            student_name=args.student_name,
            academic_period=args.academic_period,
            specific=args.specific,
        )

    if args.command == "pipeline":
        return run_real_pipeline(
            project_root=args.project_root,
            min_history=args.min_history,
            mode=args.mode,
        )

    if args.command == "reports":
        return build_school_reports(project_root=args.project_root)

    if args.command == "compare-history":
        return write_history_comparison(
            project_root=Path(args.project_root),
            history_values=tuple(args.history_values),
            mode=args.mode,
        )

    if args.command == "compare-runs":
        return compare_pipeline_runs(
            project_root=Path(args.project_root),
            mode=args.mode,
            runs=args.runs,
            min_history=args.min_history,
        )

    if args.command == "clean":
        summary = clean_workspace(
            project_root=args.project_root,
            targets=tuple(args.targets),
            dry_run=args.dry_run,
        )
        action = "seriam removidos" if summary.dry_run else "removidos"
        print(f"{len(summary.removed)} artefatos {action} para os alvos: {', '.join(summary.targets)}")
        for item in summary.removed:
            print(item)
        return summary

    parser.error(f"Comando desconhecido: {args.command}")
