"""학생 실습 검사와 완성형 수면 리포트 실행을 제공하는 통합 메뉴입니다."""

from __future__ import annotations

import json
import webbrowser
from pathlib import Path

from solution.report import generate_report

PROJECT_ROOT = Path(__file__).resolve().parent
SAMPLE_CSV = PROJECT_ROOT / "Data" / "sample_predictions.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "solution"
EPOCH_SECONDS = 30.0


def check_student_exercises() -> None:
    from student.exercises import run_checks
    run_checks()


def run_solution_report() -> Path:
    paths = generate_report(SAMPLE_CSV, OUTPUT_DIR, EPOCH_SECONDS)
    print("\n[완성형 리포트 생성 완료]")
    for name, path in paths.items():
        print(f"{name}: {path}")
    return paths["html"]


def show_solution_metrics() -> None:
    json_path = OUTPUT_DIR / "metrics.json"
    if not json_path.is_file():
        run_solution_report()
    metrics = json.loads(json_path.read_text(encoding="utf-8"))
    for key in ["TIB_minutes", "TST_minutes", "SE_percent", "SL_minutes", "WASO_minutes", "REM_percent", "NREM_percent", "StageShift_per_hour", "WakeTransition_per_hour", "Total_Sleep_Score"]:
        print(f"{key}: {metrics[key]}")


def open_solution_report() -> None:
    path = OUTPUT_DIR / "report.html"
    if not path.is_file():
        path = run_solution_report()
    webbrowser.open(path.resolve().as_uri(), new=2)


def main() -> None:
    actions = {"1": check_student_exercises, "2": run_solution_report, "3": show_solution_metrics, "4": open_solution_report}
    print("\n[수면 지표·리포트 수업]")
    print("1. 학생 TODO 자동검사")
    print("2. 완성형 계산·리포트 프로그램 실행")
    print("3. 완성형 주요 지표 확인")
    print("4. 완성형 HTML 리포트 열기")
    selected = input("선택 번호를 입력하세요 (1/2/3/4): ").strip()
    if selected not in actions:
        raise ValueError("1, 2, 3, 4 중 하나를 입력하세요.")
    actions[selected]()


if __name__ == "__main__":
    main()
