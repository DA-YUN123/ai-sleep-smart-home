"""학생용 수면 지표 산식 및 리포트 실습입니다. TODO 1~8을 완성하세요."""

from __future__ import annotations

import html

SLEEP_STAGES = {"LS", "DS", "REM"}
WEIGHTS = {"TST": .20, "SE": .20, "SL": .10, "WASO": .15, "REM": .10, "NREM": .10, "SHIFT": .05, "WAKE": .10}


def total_times(stages: list[str], epoch_seconds: float) -> tuple[float, float]:
    """TODO 1: 총 기록 시간과 총 수면 시간을 분 단위로 계산합니다."""
    # TIB = 전체 epoch 수 × epoch 초 / 60
    # TST = 수면 단계 epoch 수 × epoch 초 / 60
    raise NotImplementedError("TODO 1을 완성하세요.")


def sleep_efficiency(tib_minutes: float, tst_minutes: float) -> float:
    """TODO 2: 수면 효율을 백분율로 계산합니다."""
    # SE = TST / TIB × 100
    raise NotImplementedError("TODO 2를 완성하세요.")


def latency_and_waso(stages: list[str], epoch_seconds: float) -> tuple[float, float]:
    """TODO 3: 수면 잠복기와 입면 후 각성 시간을 분 단위로 계산합니다."""
    # 최초 수면 인덱스 이전 시간은 잠복기입니다.
    # 최초 수면부터 마지막 수면 사이의 W 개수는 WASO입니다.
    raise NotImplementedError("TODO 3을 완성하세요.")


def stage_percentages(stages: list[str]) -> tuple[float, float]:
    """TODO 4: 총 수면 epoch 대비 REM과 NREM(LS+DS) 비율을 계산합니다."""
    raise NotImplementedError("TODO 4를 완성하세요.")


def transition_metrics(stages: list[str], epoch_seconds: float) -> tuple[int, int, float, float]:
    """TODO 5: 단계 변경과 각성 전환의 횟수 및 시간당 지수를 계산합니다."""
    # 단계 변경: 최초~마지막 수면 구간에서 인접 단계가 다른 횟수
    # 각성 전환: 직전 단계가 W가 아니고 다음 단계가 W인 횟수
    raise NotImplementedError("TODO 5를 완성하세요.")


def tst_score(hours: float) -> int:
    """TODO 6: 대표 예제로 총 수면 시간을 점수 구간으로 변환합니다."""
    # <4:20, <5:40, <6:65, <7:85, 7~9:100, <=10:90, 그 외:70
    raise NotImplementedError("TODO 6을 완성하세요.")


def weighted_total(scores: dict[str, float]) -> float:
    """TODO 7: 항목 점수와 WEIGHTS를 이용해 100점 종합점수를 계산합니다."""
    raise NotImplementedError("TODO 7을 완성하세요.")


def build_student_html(metrics: dict[str, object], source_name: str) -> str:
    """TODO 8: 제목, 입력 파일, 총점이 포함된 간단한 HTML 리포트를 만듭니다."""
    # source_name에는 html.escape를 적용하세요.
    raise NotImplementedError("TODO 8을 완성하세요.")


def run_checks() -> None:
    """작은 가상 수면 단계 배열로 학생이 구현한 산식을 자동 검사합니다."""
    stages = ["W", "W", "LS", "LS", "W", "REM", "REM", "W"]
    tib, tst = total_times(stages, 30)
    assert (tib, tst) == (4.0, 2.0), f"TODO 1 결과: {(tib, tst)}"
    assert sleep_efficiency(tib, tst) == 50.0, "TODO 2를 확인하세요."
    latency, waso = latency_and_waso(stages, 30)
    assert (latency, waso) == (1.0, 0.5), f"TODO 3 결과: {(latency, waso)}"
    rem, nrem = stage_percentages(stages)
    assert (rem, nrem) == (50.0, 50.0), f"TODO 4 결과: {(rem, nrem)}"
    shifts, wakes, shift_rate, wake_rate = transition_metrics(stages, 30)
    assert (shifts, wakes) == (2, 1), f"TODO 5 횟수: {(shifts, wakes)}"
    assert round(shift_rate, 3) == 48.0 and round(wake_rate, 3) == 24.0, "TODO 5 시간당 지수를 확인하세요."
    assert [tst_score(value) for value in [3.9, 4, 5, 6, 7, 9, 10, 10.1]] == [20, 40, 65, 85, 100, 100, 90, 70]
    scores = {name: 100.0 for name in WEIGHTS}
    assert weighted_total(scores) == 100.0, "TODO 7을 확인하세요."
    report = build_student_html({"Total_Sleep_Score": 88.5}, "<sample>.csv")
    assert "88.5" in report and "&lt;sample&gt;.csv" in report, "TODO 8을 확인하세요."
    print("모든 학생 실습 검사를 통과했습니다!")


if __name__ == "__main__":
    run_checks()
