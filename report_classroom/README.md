# 수면 지표 계산 및 리포트 생성 수업 프로젝트

학생이 수면 단계 결과에서 지표 산식을 직접 구현하고 간단한 HTML 리포트를 만든 뒤, 제공된 완성형 계산·리포트 프로그램을 실행해 결과를 비교하는 프로젝트입니다.

Python이 설치되지 않은 학생도 [STUDENT_GUIDE.md](STUDENT_GUIDE.md)의 1단계부터 순서대로 진행하면 됩니다.

![수면 지표 계산 및 리포트 생성 실습 흐름](assets/report_classroom_workflow.png)

## 수업 순서

1. `student/exercises.py`의 쉬운 TODO 1~8을 순서대로 작성합니다.
2. 작은 가상 데이터로 산식을 자동검사합니다.
3. 제공된 예제 `Data/sample_predictions.csv`의 구조를 확인합니다.
4. 완성형 계산 프로그램으로 지표를 생성합니다.
5. JSON, CSV, HTML 결과를 확인합니다.
6. 학생 산식과 완성형 산식을 비교하고 보고서를 작성합니다.

## 폴더 구조

```text
report_classroom/
├── Data/
│   └── sample_predictions.csv
├── student/
│   ├── exercises.py
│   └── exercises_answer.py
├── solution/
│   ├── metrics.py
│   └── report.py
├── outputs/                    # 실행 후 자동 생성
├── run_classroom.py
├── requirements.txt
└── STUDENT_GUIDE.md
```

## 실행

프로젝트 폴더에서 다음 한 줄을 실행합니다.

```powershell
python run_classroom.py
```

메뉴:

```text
1. 학생 TODO 자동검사
2. 완성형 계산·리포트 프로그램 실행
3. 완성형 주요 지표 확인
4. 완성형 HTML 리포트 열기
```

상세한 실습 방법은 `STUDENT_GUIDE.md`를 1단계부터 따라가면 됩니다.

## 주요 산식

```text
TIB = 전체 epoch 수 × epoch 시간
TST = 수면 epoch 수 × epoch 시간
SE = TST / TIB × 100
SL = 기록 시작부터 최초 수면까지의 시간
WASO = 최초 수면부터 마지막 수면 사이의 Wake 시간
REM 비율 = REM 시간 / TST × 100
NREM 비율 = (LS + DS) 시간 / TST × 100
종합점수 = Σ(항목 점수 × 가중치)
```

NREM 점수 구간은 기존 계산 프로그램에서 제공된 교육용 기준을 그대로 사용합니다. 일반적인 임상 해석과 다를 수 있으며 결과는 의료 진단을 대신하지 않습니다.
