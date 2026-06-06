from pathlib import Path

from school_predictor.cli import main


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent
    main(["workflow", "--project-root", str(project_root)])
