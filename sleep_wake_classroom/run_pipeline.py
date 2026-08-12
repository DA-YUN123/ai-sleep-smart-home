"""단일 특징 CSV를 사용하는 Sleep/Wake 모델 학습 통합 실행 파일입니다.

학생은 아래의 '경로 및 실행 설정'만 자신의 환경에 맞게 수정하면 됩니다.
모든 기본 경로는 이 프로젝트 폴더 내부를 기준으로 자동 생성됩니다.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.compare import run_comparison
from src.train import run_training


# =============================================================================
# 경로 및 실행 설정: 학생은 필요한 경우 이 영역만 수정하세요.
# =============================================================================

# 이 파일이 있는 폴더를 프로젝트 최상위 경로로 자동 설정합니다.
PROJECT_ROOT = Path(__file__).resolve().parent

# 모든 입출력 폴더는 프로젝트 폴더 내부 경로로 설정합니다.
DATASET_CSV = PROJECT_ROOT / "Data" / "distribution" / "sleep_wake_features.csv"
RESULTS_DIR = PROJECT_ROOT / "results"

# CPU 병렬 작업 수와 재현용 난수 시드를 설정합니다.
WORKERS = 16
SEED = 42


def choose_training_mode() -> str:
    """학생에게 센서 입력 구성을 보여주고 선택한 학습 모드를 반환합니다."""
    choices = {
        "1": "ppg",
        "2": "acc",
        "3": "ppg_acc",
    }
    print("\n[학습할 센서 데이터를 선택하세요]")
    print("1. PPG만 사용")
    print("2. ACC만 사용")
    print("3. PPG와 ACC 둘 다 사용")

    while True:
        selected = input("선택 번호를 입력하세요 (1/2/3): ").strip()
        if selected in choices:
            mode = choices[selected]
            print(f"선택한 학습 모드: {mode}\n")
            return mode
        print("1, 2, 3 중 하나를 입력하세요.")


def validate_project_path(path: Path, name: str) -> Path:
    """설정한 경로가 프로젝트 내부인지 검사하고 정규화된 경로를 반환합니다."""
    resolved_root = PROJECT_ROOT.resolve()
    resolved_path = path.resolve()
    if not resolved_path.is_relative_to(resolved_root):
        raise ValueError(
            f"{name}은 프로젝트 폴더 내부여야 합니다: {resolved_path}"
        )
    return resolved_path


def print_settings() -> None:
    """실행 전에 현재 경로와 주요 설정을 학생이 확인할 수 있도록 출력합니다."""
    print("\n[현재 실행 설정]")
    print(f"프로젝트: {PROJECT_ROOT}")
    print(f"특징 데이터: {DATASET_CSV}")
    print(f"학습 결과: {RESULTS_DIR}")
    print(f"병렬 작업 수: {WORKERS}")
    print(f"난수 시드: {SEED}")
    print()


def train_one_mode(mode: str) -> None:
    """선택한 센서 모드 하나를 학습하고 프로젝트 내부 results에 저장합니다."""
    data_file = validate_project_path(DATASET_CSV, "DATASET_CSV")
    results_dir = validate_project_path(RESULTS_DIR, "RESULTS_DIR")
    metrics = run_training(
        data_file=data_file,
        output_dir=results_dir / mode,
        mode=mode,
        workers=WORKERS,
        seed=SEED,
    )
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


def compare_all_modes() -> None:
    """PPG, ACC, PPG+ACC를 학습하고 프로젝트 내부 results에서 비교합니다."""
    data_file = validate_project_path(DATASET_CSV, "DATASET_CSV")
    results_dir = validate_project_path(RESULTS_DIR, "RESULTS_DIR")
    comparison = run_comparison(
        data_file=data_file,
        output_dir=results_dir,
        workers=WORKERS,
        seed=SEED,
    )
    print(comparison.to_string(index=False))


def main() -> None:
    """명령행에서 선택한 단일 센서 또는 비교 학습을 실행합니다."""
    parser = argparse.ArgumentParser(
        description="단일 특징 CSV 기반 Sleep/Wake 프로젝트 통합 실행"
    )
    parser.add_argument(
        "step",
        nargs="?",
        choices=["ppg", "acc", "ppg_acc", "compare", "all"],
        help="생략하면 센서 선택 메뉴를 표시합니다.",
    )
    args = parser.parse_args()

    print_settings()
    step = args.step if args.step is not None else choose_training_mode()

    if step in {"ppg", "acc", "ppg_acc"}:
        train_one_mode(step)
    if step in {"compare", "all"}:
        compare_all_modes()


if __name__ == "__main__":
    main()
