"""Execute the credit-risk notebooks in dependency order."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
NOTEBOOK_DIR = PROJECT_DIR / "notebooks"
STAGES = (
    "01_eda.ipynb",
    "02_preprocessing.ipynb",
    "03_feature_engineering.ipynb",
    "04_modeling.ipynb",
    "05_explainability.ipynb",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--from-stage",
        choices=STAGES,
        default=STAGES[0],
        help="First notebook to execute (default: %(default)s).",
    )
    parser.add_argument(
        "--to-stage",
        choices=STAGES,
        default=STAGES[-1],
        help="Last notebook to execute (default: %(default)s).",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=1200,
        help="Per-cell timeout in seconds; use -1 for no timeout (default: %(default)s).",
    )
    parser.add_argument(
        "--no-inplace",
        action="store_true",
        help="Execute notebooks without replacing their saved outputs.",
    )
    return parser.parse_args()


def selected_stages(first: str, last: str) -> tuple[str, ...]:
    start = STAGES.index(first)
    stop = STAGES.index(last)
    if start > stop:
        raise ValueError("--from-stage must not come after --to-stage")
    return STAGES[start : stop + 1]


def validate_inputs(stages: tuple[str, ...]) -> None:
    missing_notebooks = [name for name in stages if not (NOTEBOOK_DIR / name).is_file()]
    if missing_notebooks:
        raise FileNotFoundError(f"Missing notebooks: {', '.join(missing_notebooks)}")

    data_dir = PROJECT_DIR / "data"
    model_dir = PROJECT_DIR / "models"
    first_stage_inputs = {
        "01_eda.ipynb": [data_dir / "application_train.csv", data_dir / "bureau.csv"],
        "02_preprocessing.ipynb": [data_dir / "application_train.csv"],
        "03_feature_engineering.ipynb": [
            data_dir / "application_train_clean.parquet",
            data_dir / "split_assignments.parquet",
            data_dir / "bureau.csv",
        ],
        "04_modeling.ipynb": [
            data_dir / "application_features.parquet",
            data_dir / "split_assignments.parquet",
            data_dir / "feature_dictionary.json",
        ],
        "05_explainability.ipynb": [
            data_dir / "application_features.parquet",
            data_dir / "split_assignments.parquet",
            model_dir / "credit_scoring_feature_pipeline.pkl",
            model_dir / "model_metadata.json",
        ],
    }
    required_inputs = first_stage_inputs[stages[0]]
    if "03_feature_engineering.ipynb" in stages:
        required_inputs = [*required_inputs, data_dir / "bureau.csv"]
    missing_inputs = sorted(
        {str(path.relative_to(PROJECT_DIR)) for path in required_inputs if not path.is_file()}
    )
    if missing_inputs:
        raise FileNotFoundError(f"Missing stage inputs: {', '.join(missing_inputs)}")


def execute_notebook(notebook: str, timeout: int, inplace: bool) -> None:
    command = [
        sys.executable,
        "-m",
        "jupyter",
        "nbconvert",
        "--to",
        "notebook",
        "--execute",
        f"--ExecutePreprocessor.timeout={timeout}",
    ]
    if inplace:
        command.append("--inplace")
    else:
        command.extend(["--stdout", "--log-level=ERROR"])
    command.append(notebook)

    print(f"\n=== Running {notebook} ===", flush=True)
    stdout = subprocess.DEVNULL if not inplace else None
    subprocess.run(command, cwd=NOTEBOOK_DIR, check=True, stdout=stdout)


def main() -> int:
    args = parse_args()
    try:
        stages = selected_stages(args.from_stage, args.to_stage)
        validate_inputs(stages)
        for notebook in stages:
            execute_notebook(notebook, args.timeout, inplace=not args.no_inplace)
    except (FileNotFoundError, ValueError) as error:
        print(f"Pipeline configuration error: {error}", file=sys.stderr)
        return 2
    except subprocess.CalledProcessError as error:
        print(f"Pipeline stopped after a notebook failed (exit {error.returncode}).", file=sys.stderr)
        return error.returncode or 1

    print("\nPipeline completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
