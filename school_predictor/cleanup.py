from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path


LATEX_PATTERNS = (
    "*.aux",
    "*.bbl",
    "*.blg",
    "*.brf",
    "*.fdb_latexmk",
    "*.fls",
    "*.log",
    "*.out",
    "*.synctex.gz",
    "*.toc",
)

DEFAULT_TARGETS = ("latex", "pycache")
AVAILABLE_TARGETS = ("latex", "pycache", "results")


@dataclass(frozen=True)
class CleanupSummary:
    targets: tuple[str, ...]
    dry_run: bool
    removed: tuple[Path, ...]


def clean_workspace(project_root: str | Path = ".", targets: tuple[str, ...] = DEFAULT_TARGETS, dry_run: bool = False) -> CleanupSummary:
    """Remove local build artefacts while preserving project source files."""
    root = Path(project_root).resolve()
    normalized_targets = _normalize_targets(targets)
    removed: list[Path] = []

    if "latex" in normalized_targets:
        removed.extend(_remove_latex_artifacts(root, dry_run=dry_run))

    if "pycache" in normalized_targets:
        removed.extend(_remove_pycache_dirs(root, dry_run=dry_run))

    if "results" in normalized_targets:
        removed.extend(_remove_result_artifacts(root, dry_run=dry_run))

    return CleanupSummary(
        targets=normalized_targets,
        dry_run=dry_run,
        removed=tuple(sorted(removed)),
    )


def _normalize_targets(targets: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    normalized = tuple(dict.fromkeys(targets))
    invalid = [target for target in normalized if target not in AVAILABLE_TARGETS]
    if invalid:
        raise ValueError(f"Targets de limpeza inválidos: {', '.join(invalid)}")
    return normalized


def _remove_latex_artifacts(root: Path, dry_run: bool) -> list[Path]:
    tcc_root = root / "tcc"
    if not tcc_root.exists():
        return []

    removed: list[Path] = []
    for pattern in LATEX_PATTERNS:
        for file_path in tcc_root.glob(pattern):
            removed.append(file_path)
            if not dry_run:
                file_path.unlink(missing_ok=True)
    return removed


def _remove_pycache_dirs(root: Path, dry_run: bool) -> list[Path]:
    removed: list[Path] = []
    skip_names = {".git", ".venv", "venv"}

    for pycache_dir in root.rglob("__pycache__"):
        if any(part in skip_names for part in pycache_dir.parts):
            continue
        removed.append(pycache_dir)
        if not dry_run:
            shutil.rmtree(pycache_dir, ignore_errors=True)

    return removed


def _remove_result_artifacts(root: Path, dry_run: bool) -> list[Path]:
    result_dirs = (
        root / "artifacts" / "database",
        root / "artifacts" / "pipeline",
        root / "artifacts" / "reports",
    )
    removed: list[Path] = []

    for result_dir in result_dirs:
        if not result_dir.exists():
            continue

        for child in result_dir.iterdir():
            removed.append(child)
            if dry_run:
                continue
            if child.is_dir():
                shutil.rmtree(child, ignore_errors=True)
            else:
                child.unlink(missing_ok=True)

    return removed
