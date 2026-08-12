"""학생용 수면 지표 산식 실습의 쉬운 정답 코드입니다.

각 함수는 계산 과정을 따라가기 쉽도록 중간 변수를 사용합니다.
학생 실습을 먼저 완료한 뒤 자신의 코드와 비교하세요.
"""

from __future__ import annotations

import html

SLEEP_STAGES = {"LS", "DS", "REM"}
WEIGHTS = {"TST": 0.20, "SE": 0.20, "SL": 0.10, "WASO": 0.15, "REM": 0.10, "NREM": 0.10, "SHIFT": 0.05, "WAKE": 0.10}


def total_times(stages: list[str], epoch_seconds: float) -> tuple[float, float]:
    total_epoch_count = len(stages)
    sleep_epoch_count = 0
    for stage in stages:
        if stage in SLEEP_STAGES:
            sleep_epoch_count += 1
    tib_minutes = total_epoch_count * epoch_seconds / 60
    tst_minutes = sleep_epoch_count * epoch_seconds / 60
    return tib_minutes, tst_minutes


def sleep_efficiency(tib_minutes: float, tst_minutes: float) -> float:
    if tib_minutes == 0:
        return 0.0
    return tst_minutes / tib_minutes * 100


def latency_and_waso(stages: list[str], epoch_seconds: float) -> tuple[float, float]:
    sleep_indices = []
    for index, stage in enumerate(stages):
        if stage in SLEEP_STAGES:
            sleep_indices.append(index)
    if not sleep_indices:
        total_minutes = len(stages) * epoch_seconds / 60
        return total_minutes, 0.0
    first_sleep_index = sleep_indices[0]
    last_sleep_index = sleep_indices[-1]
    latency_minutes = first_sleep_index * epoch_seconds / 60
    sleep_window = stages[first_sleep_index:last_sleep_index + 1]
    wake_count = sleep_window.count("W")
    waso_minutes = wake_count * epoch_seconds / 60
    return latency_minutes, waso_minutes


def stage_percentages(stages: list[str]) -> tuple[float, float]:
    sleep_count = 0
    rem_count = 0
    nrem_count = 0
    for stage in stages:
        if stage in SLEEP_STAGES:
            sleep_count += 1
        if stage == "REM":
            rem_count += 1
        if stage in {"LS", "DS"}:
            nrem_count += 1
    if sleep_count == 0:
        return 0.0, 0.0
    return rem_count / sleep_count * 100, nrem_count / sleep_count * 100


def transition_metrics(stages: list[str], epoch_seconds: float) -> tuple[int, int, float, float]:
    sleep_indices = []
    for index, stage in enumerate(stages):
        if stage in SLEEP_STAGES:
            sleep_indices.append(index)
    if not sleep_indices:
        return 0, 0, 0.0, 0.0
    first_sleep_index = sleep_indices[0]
    last_sleep_index = sleep_indices[-1]
    sleep_window = stages[first_sleep_index:last_sleep_index + 1]
    stage_shift_count = 0
    wake_transition_count = 0
    for current_stage, next_stage in zip(sleep_window, sleep_window[1:]):
        if current_stage != next_stage:
            stage_shift_count += 1
        if current_stage != "W" and next_stage == "W":
            wake_transition_count += 1
    sleep_window_hours = len(sleep_window) * epoch_seconds / 3600
    stage_shift_per_hour = stage_shift_count / sleep_window_hours
    wake_transition_per_hour = wake_transition_count / sleep_window_hours
    return stage_shift_count, wake_transition_count, stage_shift_per_hour, wake_transition_per_hour


def tst_score(hours: float) -> int:
    if hours < 4:
        return 20
    if hours < 5:
        return 40
    if hours < 6:
        return 65
    if hours < 7:
        return 85
    if hours <= 9:
        return 100
    if hours <= 10:
        return 90
    return 70


def weighted_total(scores: dict[str, float]) -> float:
    total = 0.0
    for metric_name, weight in WEIGHTS.items():
        total += scores[metric_name] * weight
    return round(total, 2)


def build_student_html(metrics: dict[str, object], source_name: str) -> str:
    safe_source_name = html.escape(source_name)
    total_score = metrics["Total_Sleep_Score"]
    return f"""<!doctype html>
<html lang="ko">
<head><meta charset="utf-8"><title>학생 수면 리포트</title></head>
<body><h1>수면 지표 리포트</h1><p>입력 파일: {safe_source_name}</p><strong>종합점수: {total_score}</strong></body>
</html>
"""
