"""수면 단계 배열에서 교육용 수면 지표와 점수를 계산하는 완성 코드입니다."""

from __future__ import annotations

import csv
from pathlib import Path

SLEEP_STAGES = {"LS", "DS", "REM"}
VALID_STAGES = SLEEP_STAGES | {"W"}
ALIASES = {"WAKE": "W", "NREM": "LS", "LIGHT": "LS", "DEEP": "DS"}
WEIGHTS = {"TST_score": .20, "SE_score": .20, "SL_score": .10, "WASO_score": .15,
           "REM_score": .10, "NREM_score": .10, "StageShift_score": .05,
           "WakeTransition_score": .10}


def normalize_stage(value: str) -> str:
    stage = ALIASES.get(value.strip().upper(), value.strip().upper())
    if stage not in VALID_STAGES:
        raise ValueError(f"사용할 수 없는 수면 단계입니다: {value}")
    return stage


def read_stages(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        fields = reader.fieldnames or []
        column = next((name for name in ("Predicted_Stage", "Prediction_3class", "Stage") if name in fields), None)
        if column is None:
            raise ValueError("수면 단계 열이 없습니다.")
        stages = [normalize_stage(row.get(column, "")) for row in reader]
    if not stages:
        raise ValueError("CSV에 수면 단계가 없습니다.")
    return stages


def score_tst(hours: float) -> int:
    return 20 if hours < 4 else 40 if hours < 5 else 65 if hours < 6 else 85 if hours < 7 else 100 if hours <= 9 else 90 if hours <= 10 else 70


def score_se(value: float) -> int:
    return 100 if value >= 90 else 90 if value >= 85 else 75 if value >= 80 else 60 if value >= 75 else 40 if value >= 70 else 20


def score_sl(minutes: float) -> int:
    return 100 if minutes <= 20 else 90 if minutes <= 30 else 70 if minutes <= 45 else 50 if minutes <= 60 else 20


def score_waso(minutes: float) -> int:
    return 100 if minutes <= 20 else 80 if minutes <= 40 else 60 if minutes <= 60 else 40 if minutes <= 90 else 20


def score_rem(percent: float) -> int:
    return 100 if 20 <= percent <= 25 else 90 if 18 <= percent < 20 or 25 < percent <= 28 else 75 if 15 <= percent < 18 or 28 < percent <= 30 else 50 if 10 <= percent < 15 or 30 < percent <= 35 else 20


def score_nrem(percent: float) -> int:
    return 100 if 15 <= percent <= 23 else 90 if 12 <= percent < 15 or 23 < percent <= 25 else 70 if 10 <= percent < 12 or 25 < percent <= 30 else 50 if 5 <= percent < 10 or 30 < percent <= 35 else 20


def score_shift(per_hour: float) -> int:
    return 100 if per_hour <= 10 else 85 if per_hour <= 15 else 70 if per_hour <= 20 else 50 if per_hour <= 30 else 20


def score_wake_transition(per_hour: float) -> int:
    return 100 if per_hour <= 5 else 90 if per_hour <= 10 else 70 if per_hour <= 15 else 45 if per_hour <= 30 else 20


def calculate_metrics(stages: list[str], epoch_seconds: float = 30.0) -> dict[str, float | int]:
    if epoch_seconds <= 0 or not stages:
        raise ValueError("단계 목록이 필요하고 epoch 시간은 0보다 커야 합니다.")
    stages = [normalize_stage(stage) for stage in stages]
    tib = len(stages) * epoch_seconds
    sleep_indices = [index for index, stage in enumerate(stages) if stage in SLEEP_STAGES]
    tst = len(sleep_indices) * epoch_seconds
    if sleep_indices:
        first, last = sleep_indices[0], sleep_indices[-1]
        window = stages[first:last + 1]
        sl = first * epoch_seconds
        waso = window.count("W") * epoch_seconds
        window_hours = len(window) * epoch_seconds / 3600
        shifts = sum(a != b for a, b in zip(window, window[1:]))
        wakes = sum(a != "W" and b == "W" for a, b in zip(window, window[1:]))
        shift_rate, wake_rate = shifts / window_hours, wakes / window_hours
    else:
        sl, waso, shifts, wakes, shift_rate, wake_rate = tib, 0, 0, 0, 0.0, 0.0
    se = tst / tib * 100
    rem_minutes = stages.count("REM") * epoch_seconds / 60
    nrem_minutes = (stages.count("LS") + stages.count("DS")) * epoch_seconds / 60
    rem_percent = rem_minutes * 60 / tst * 100 if tst else 0.0
    nrem_percent = nrem_minutes * 60 / tst * 100 if tst else 0.0
    scores = {"TST_score": score_tst(tst / 3600), "SE_score": score_se(se), "SL_score": score_sl(sl / 60),
              "WASO_score": score_waso(waso / 60), "REM_score": score_rem(rem_percent),
              "NREM_score": score_nrem(nrem_percent), "StageShift_score": score_shift(shift_rate),
              "WakeTransition_score": score_wake_transition(wake_rate)}
    total = sum(scores[name] * weight for name, weight in WEIGHTS.items())
    return {"epoch_seconds": epoch_seconds, "epoch_count": len(stages), "TIB_minutes": round(tib / 60, 3),
            "TST_minutes": round(tst / 60, 3), "SE_percent": round(se, 3), "SL_minutes": round(sl / 60, 3),
            "WASO_minutes": round(waso / 60, 3), "REM_minutes": round(rem_minutes, 3),
            "REM_percent": round(rem_percent, 3), "NREM_minutes": round(nrem_minutes, 3),
            "NREM_percent": round(nrem_percent, 3), "StageShift_count": shifts,
            "StageShift_per_hour": round(shift_rate, 3), "Wake_transition_count": wakes,
            "WakeTransition_per_hour": round(wake_rate, 3), **scores, "Total_Sleep_Score": round(total, 2)}
