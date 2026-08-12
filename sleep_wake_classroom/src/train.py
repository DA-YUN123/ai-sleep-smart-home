from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    roc_auc_score,
)


def create_subject_split(subjects: list[str], seed: int = 42) -> dict[str, list[str]]:
    """참가자 목록을 고정된 시드로 Train 70%, Validation 15%, Test 15%로 분리합니다."""
    unique = np.array(sorted(set(subjects)))
    if len(unique) < 7:
        raise ValueError("신뢰할 수 있는 참가자 분할을 위해 최소 7명이 필요합니다.")
    rng = np.random.default_rng(seed)
    shuffled = unique[rng.permutation(len(unique))]
    train_end = max(1, int(len(shuffled) * 0.70))
    validation_end = max(train_end + 1, int(len(shuffled) * 0.85))
    return {
        "train": shuffled[:train_end].tolist(),
        "validation": shuffled[train_end:validation_end].tolist(),
        "test": shuffled[validation_end:].tolist(),
    }


def select_feature_columns(frame: pd.DataFrame, mode: str) -> list[str]:
    """센서 모드에 맞는 PPG 또는 ACC 특징 열 이름을 선택합니다."""
    if mode == "ppg":
        columns = [column for column in frame.columns if column.startswith("ppg_")]
    elif mode == "acc":
        columns = [column for column in frame.columns if column.startswith("acc_")]
    elif mode == "ppg_acc":
        columns = [
            column
            for column in frame.columns
            if column.startswith(("ppg_", "acc_"))
        ]
    else:
        raise ValueError(f"지원하지 않는 mode입니다: {mode}")
    if not columns:
        raise ValueError(f"{mode} 모드에 사용할 특징 열이 없습니다.")
    return columns


def load_feature_csv(data_file: Path) -> pd.DataFrame:
    """단일 특징 CSV를 읽고 필수 열과 라벨 값을 검사합니다."""
    if not data_file.is_file():
        raise FileNotFoundError(f"특징 CSV를 찾지 못했습니다: {data_file.resolve()}")
    frame = pd.read_csv(data_file)
    required = {"subject_group", "label"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"특징 CSV에 필수 열이 없습니다: {missing}")
    if frame.empty:
        raise ValueError("특징 CSV에 학습할 행이 없습니다.")
    if frame["subject_group"].isna().any():
        raise ValueError("subject_group에 비어 있는 값이 있습니다.")
    if frame["label"].isna().any():
        raise ValueError("label에 비어 있는 값이 있습니다.")
    labels = set(frame["label"].unique())
    if not labels.issubset({0, 1}) or not labels:
        raise ValueError(f"label은 숫자 0과 1만 사용할 수 있습니다: {sorted(labels)}")
    return frame


def evaluate_model(model: RandomForestClassifier, x: np.ndarray, y: np.ndarray) -> tuple[dict, np.ndarray, np.ndarray]:
    """Sleep/Wake 예측을 수행하고 불균형에 강한 평가지표를 계산합니다."""
    prediction = model.predict(x)
    probability = model.predict_proba(x)[:, 1]
    metrics = {
        "balanced_accuracy": float(balanced_accuracy_score(y, prediction)),
        "macro_f1": float(f1_score(y, prediction, average="macro", zero_division=0)),
        "wake_f1": float(f1_score(y, prediction, labels=[0], average="macro", zero_division=0)),
        "sleep_f1": float(f1_score(y, prediction, labels=[1], average="macro", zero_division=0)),
        "roc_auc": float(roc_auc_score(y, probability)) if np.unique(y).size == 2 else None,
        "epochs": int(len(y)),
    }
    return metrics, prediction, probability


def run_training(data_file: Path, output_dir: Path, mode: str, workers: int, seed: int = 42) -> dict:
    """단일 특징 CSV에서 참가자를 분할하고 모델 학습·평가·저장을 수행합니다."""
    frame = load_feature_csv(data_file)
    feature_columns = select_feature_columns(frame, mode)
    feature_values = frame[feature_columns].to_numpy(dtype=np.float32)
    if not np.isfinite(feature_values).all():
        raise ValueError(f"{mode} 특징 열에 NaN 또는 무한대 값이 있습니다.")
    split = create_subject_split(frame["subject_group"].astype(str).tolist(), seed=seed)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "split.json").write_text(json.dumps(split, ensure_ascii=False, indent=2), encoding="utf-8")

    loaded = {}
    for split_name, subject_ids in split.items():
        subset = frame[frame["subject_group"].astype(str).isin(subject_ids)]
        loaded[split_name] = (
            feature_values[subset.index.to_numpy()],
            subset["label"].to_numpy(dtype=np.int8),
            subset["subject_group"].astype(str).to_numpy(),
        )

    x_train, y_train, _ = loaded["train"]
    model = RandomForestClassifier(
        n_estimators=400,
        max_depth=None,
        min_samples_leaf=3,
        class_weight="balanced_subsample",
        random_state=seed,
        n_jobs=max(1, workers),
    )
    model.fit(x_train, y_train)

    all_metrics = {
        "mode": mode,
        "feature_count": len(feature_columns),
        "train_epochs": int(len(y_train)),
    }
    test_outputs = None
    for split_name in ["validation", "test"]:
        x, y, ids = loaded[split_name]
        metrics, prediction, probability = evaluate_model(model, x, y)
        all_metrics[split_name] = metrics
        if split_name == "test":
            test_outputs = (y, prediction, probability, ids)

    (output_dir / "metrics.json").write_text(
        json.dumps(all_metrics, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    joblib.dump(
        {
            "model": model,
            "mode": mode,
            "seed": seed,
            "feature_columns": feature_columns,
        },
        output_dir / "model.joblib",
    )

    y, prediction, probability, ids = test_outputs
    pd.DataFrame(
        {"subject_group": ids, "label": y, "prediction": prediction, "sleep_probability": probability}
    ).to_csv(output_dir / "predictions.csv", index=False)

    matrix = confusion_matrix(y, prediction, labels=[0, 1])
    fig, axis = plt.subplots(figsize=(5, 4))
    sns.heatmap(matrix, annot=True, fmt="d", cmap="Blues", xticklabels=["Wake", "Sleep"], yticklabels=["Wake", "Sleep"], ax=axis)
    axis.set_xlabel("Predicted")
    axis.set_ylabel("True")
    axis.set_title(f"Confusion Matrix ({mode})")
    fig.tight_layout()
    fig.savefig(output_dir / "confusion_matrix.png", dpi=160)
    plt.close(fig)
    return all_metrics


def main() -> None:
    """명령행 인자를 읽어 단일 센서 모드 실험을 실행합니다."""
    parser = argparse.ArgumentParser(description="Sleep/Wake 모델 학습")
    parser.add_argument("--data", type=Path, required=True, help="단일 특징 CSV 경로")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mode", choices=["ppg", "acc", "ppg_acc"], required=True)
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    metrics = run_training(args.data, args.output, args.mode, args.workers, args.seed)
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
