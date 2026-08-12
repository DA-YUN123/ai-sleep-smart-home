from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .train import run_training


def run_comparison(data_file: Path, output_dir: Path, workers: int, seed: int = 42) -> pd.DataFrame:
    """세 센서 모드를 동일한 참가자 분할로 학습하고 비교 결과를 저장합니다."""
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for mode in ["ppg", "acc", "ppg_acc"]:
        print(f"\n===== {mode} 학습 시작 =====")
        metrics = run_training(data_file, output_dir / mode, mode, workers, seed)
        row = {"mode": mode}
        row.update(metrics["test"])
        rows.append(row)

    comparison = pd.DataFrame(rows)
    comparison.to_csv(output_dir / "comparison.csv", index=False)
    plot_columns = ["balanced_accuracy", "macro_f1", "wake_f1", "sleep_f1", "roc_auc"]
    axis = comparison.set_index("mode")[plot_columns].plot(kind="bar", figsize=(10, 5), ylim=(0, 1))
    axis.set_ylabel("Score")
    axis.set_title("Sleep/Wake Sensor Comparison")
    axis.legend(loc="lower right")
    axis.figure.tight_layout()
    axis.figure.savefig(output_dir / "comparison.png", dpi=160)
    plt.close(axis.figure)
    return comparison


def main() -> None:
    """PPG, ACC, PPG+ACC를 동일한 참가자 분할로 순차 학습하고 결과를 비교합니다."""
    parser = argparse.ArgumentParser(description="Sleep/Wake 세 센서 입력 모드 비교")
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    comparison = run_comparison(
        data_file=args.data,
        output_dir=args.output,
        workers=args.workers,
        seed=args.seed,
    )
    print(comparison.to_string(index=False))


if __name__ == "__main__":
    main()
