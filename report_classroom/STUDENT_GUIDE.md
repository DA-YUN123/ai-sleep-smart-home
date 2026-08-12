# 수면 지표 계산·리포트 생성 학생 실습 설명서

## 1단계: Python 3.12 설치

Windows 64비트 Python 3.12를 권장합니다. Python이 설치되어 있지 않다면 공식 다운로드 페이지에서 Python Install Manager를 먼저 설치합니다.

```text
https://www.python.org/downloads/
```

설치가 끝나면 열려 있던 PowerShell을 모두 닫고 새 PowerShell을 엽니다. 다음 한 줄로 Python 3.12를 설치합니다.

```powershell
py install 3.12
```

설치된 Python 목록을 확인합니다.

```powershell
py list
```

Python 3.12 버전을 확인합니다.

```powershell
py -3.12 --version
```

`Python 3.12.x`가 표시되면 다음 단계로 넘어갑니다. `py` 명령을 찾지 못하면 Python Install Manager 설치 후 PowerShell을 새로 열었는지 확인합니다.

## 2단계: 프로젝트 폴더로 이동

PowerShell에서 프로젝트 폴더로 이동합니다.

```powershell
Set-Location -LiteralPath '<report_classroom 폴더 경로>'
```

현재 위치와 파일을 확인합니다.

```powershell
Get-Location
```

```powershell
Get-ChildItem -Force
```

`Data`, `student`, `solution`, `requirements.txt`, `run_classroom.py`가 보이면 정상입니다.

## 3단계: 프로젝트 가상환경 생성

프로젝트 안에 `.venv` 가상환경을 만듭니다.

```powershell
py -3.12 -m venv .venv
```

```powershell
.\.venv\Scripts\Activate.ps1
```

PowerShell 앞에 `(.venv)`가 표시되면 활성화된 것입니다.

`Activate.ps1` 실행이 차단되면 현재 사용자에게 로컬 스크립트 실행을 허용합니다.

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

새 PowerShell에서 프로젝트 폴더로 이동한 뒤 활성화 명령을 다시 실행합니다.

## 4단계: pip와 프로젝트 환경 확인

현재 사용 중인 Python 위치를 확인합니다.

```powershell
python -c "import sys; print(sys.executable)"
```

출력 경로에 `.venv\Scripts\python.exe`가 포함되어야 합니다. pip도 업그레이드합니다.

```powershell
python -m pip install --upgrade pip
```

이 프로젝트는 표준 라이브러리만 사용하지만 환경 확인을 위해 다음 명령을 실행합니다.

```powershell
python -m pip install -r requirements.txt
```

Python이 정상적으로 실행되는지 확인합니다.

```powershell
python -c "import csv,json,html,pathlib; print('Python 환경 준비 완료')"
```

## 5단계: 입력 CSV 이해

예제 파일은 다음 위치에 있습니다.

```text
Data/sample_predictions.csv
```

각 행은 기본 30초 구간 하나이며 `Prediction_3class` 열에 다음 값이 있습니다.

- `W`: Wake
- `NREM`: 비렘수면, 계산할 때 LS로 변환
- `REM`: 렘수면

완성형 프로그램은 `Predicted_Stage`, `Prediction_3class`, `Stage` 열을 지원하며 `WAKE`, `LIGHT`, `DEEP`, `NREM` 별칭도 표준 단계로 변환합니다.

## 학생이 작성할 함수 전체 목록

학생은 `student/exercises.py`에서 다음 함수들을 작성합니다.

| 함수 | 입력 | 반환값 | 학습 내용 |
|---|---|---|---|
| `total_times` | 단계 목록, epoch 초 | TIB분, TST분 | 전체 기록·수면 시간 |
| `sleep_efficiency` | TIB분, TST분 | SE 백분율 | 비율과 0 나누기 처리 |
| `latency_and_waso` | 단계 목록, epoch 초 | SL분, WASO분 | 최초·마지막 수면 구간 |
| `stage_percentages` | 단계 목록 | REM%, NREM% | 수면 단계 구성비 |
| `transition_metrics` | 단계 목록, epoch 초 | 변경 횟수·각성 횟수·시간당 지수 | 인접 단계 비교 |
| `tst_score` | TST 시간 | 점수 | 대표 점수 조건문 연습 |
| `weighted_total` | 항목별 점수 딕셔너리 | 종합점수 | 가중합 |
| `build_student_html` | 지표 딕셔너리, 파일명 | HTML 문자열 | 리포트 구성과 escape |

### `total_times(stages, epoch_seconds)`

입력 예시:

```python
stages = ["W", "W", "LS", "REM"]
epoch_seconds = 30
```

전체 4개 구간이므로 TIB는 `4 × 30 / 60 = 2분`입니다. LS와 REM 두 구간이 수면이므로 TST는 `2 × 30 / 60 = 1분`입니다. 반환값은 `(2.0, 1.0)`입니다.

### `sleep_efficiency(tib_minutes, tst_minutes)`

TIB가 2분이고 TST가 1분이면 `1 / 2 × 100 = 50%`입니다. TIB가 0인 경우에는 ZeroDivisionError가 발생하지 않도록 0을 반환해야 합니다.

### `latency_and_waso(stages, epoch_seconds)`

예제 `[W, W, LS, LS, W, REM, W]`에서 최초 수면은 인덱스 2입니다. 따라서 잠복기는 `2 × 30 / 60 = 1분`입니다. 최초 LS부터 마지막 REM 사이의 W는 한 개이므로 WASO는 `1 × 30 / 60 = 0.5분`입니다. 마지막 REM 뒤의 W는 WASO에 포함하지 않습니다.

수면 단계가 하나도 없다면 잠복기는 전체 기록 시간이고 WASO는 0입니다.

### `stage_percentages(stages)`

분모는 전체 행이 아니라 수면 단계 `LS+DS+REM`의 개수입니다. 수면 구성이 `[LS, LS, DS, REM]`이면 REM은 25%, NREM은 75%입니다. 수면이 없으면 두 값 모두 0을 반환합니다.

### `transition_metrics(stages, epoch_seconds)`

먼저 최초 수면부터 마지막 수면까지의 `sleep_window`를 만듭니다. `zip(window, window[1:])`로 인접한 두 단계를 비교합니다.

- `LS → REM`: 단계 변경 1회, 각성 전환 0회
- `REM → W`: 단계 변경 1회, 각성 전환 1회
- `W → LS`: 단계 변경 1회, 각성 전환 0회
- `LS → LS`: 변경 없음

시간당 지수의 분모는 `sleep_window 길이 × epoch_seconds / 3600`입니다. 함수는 `(단계 변경 횟수, 각성 전환 횟수, 시간당 단계 변경, 시간당 각성 전환)` 네 값을 반환합니다.

### `tst_score(hours)`

학생은 여러 점수 함수 중 TST 점수 하나만 직접 작성합니다. `if` 문을 낮은 시간부터 순서대로 작성합니다. 나머지 점수표는 학생 TODO를 마친 뒤 `solution/metrics.py`에서 읽고 비교합니다.

### `weighted_total(scores)`

`scores`의 키는 `WEIGHTS`의 키와 같아야 합니다. 각 점수에 가중치를 곱한 뒤 모두 더하고 소수 둘째 자리까지 반올림합니다. 모든 항목이 100점이면 종합점수도 100점이어야 합니다.

### `build_student_html(metrics, source_name)`

반환값은 파일이 아니라 HTML 문자열입니다. 최소한 문서 제목, 입력 파일명, `Total_Sleep_Score`가 포함되어야 합니다. `source_name`에 `<`, `>`, `&`가 들어올 수 있으므로 `html.escape(source_name)`을 사용합니다.

## 6단계: 기본 시간 지표 작성

`student/exercises.py`를 열고 TODO 1을 완성합니다.

```text
TIB(분) = 전체 epoch 수 × epoch 초 / 60
TST(분) = LS·DS·REM epoch 수 × epoch 초 / 60
```

TODO 2에서 수면 효율을 계산합니다.

```text
SE(%) = TST / TIB × 100
```

## 7단계: 잠복기와 WASO 작성

TODO 3을 완성합니다.

```text
SL = 최초 수면 epoch 이전 구간의 시간
WASO = 최초 수면부터 마지막 수면 사이에 있는 W의 총시간
```

기록 마지막의 Wake는 마지막 수면 이후이므로 WASO에 포함하지 않습니다.

## 8단계: 수면 단계 비율 작성

TODO 4를 완성합니다.

```text
REM(%) = REM epoch 수 / 전체 수면 epoch 수 × 100
NREM(%) = (LS + DS) epoch 수 / 전체 수면 epoch 수 × 100
```

수면 epoch가 하나도 없으면 두 비율은 0으로 처리합니다.

## 9단계: 단계 전환 지표 작성

TODO 5를 완성합니다.

```text
단계 변경 횟수 = 최초~마지막 수면 구간에서 인접 단계가 달라진 횟수
각성 전환 횟수 = 직전 단계가 W가 아니고 현재 단계가 W인 횟수
시간당 지수 = 횟수 / 수면 구간 시간
```

## 10단계: 대표 점수와 종합점수 작성

TODO 6에서 총 수면 시간 점수표 하나를 조건문으로 작성합니다. 모든 점수표를 한꺼번에 작성하지 않아도 됩니다. TODO 7에서는 이미 준비된 항목 점수에 다음 가중치를 적용합니다.

| 항목 | 가중치 |
|---|---:|
| TST | 20% |
| 수면 효율 | 20% |
| 잠복기 | 10% |
| WASO | 15% |
| REM | 10% |
| NREM | 10% |
| 단계 변경 | 5% |
| 각성 전환 | 10% |

```text
종합점수 = Σ(항목별 점수 × 가중치)
```

## 11단계: 학생 HTML 리포트 작성

TODO 8에서 제목, 입력 파일명, 총점이 들어간 HTML 문자열을 작성합니다. 파일명에는 `html.escape()`를 적용해 HTML 특수문자를 안전하게 처리합니다.

## 12단계: 학생 코드 자동검사

다음 한 줄을 실행합니다.

```powershell
python student/exercises.py
```

또는 통합 메뉴에서 1번을 선택합니다.

```powershell
python run_classroom.py
```

완료 메시지:

```text
모든 학생 실습 검사를 통과했습니다!
```

## 13단계: 완성형 프로그램 실행

통합 메뉴를 실행하고 2번을 선택합니다.

```powershell
python run_classroom.py
```

완성형 프로그램은 다음 파일을 생성합니다.

```text
outputs/solution/metrics.json
outputs/solution/metrics.csv
outputs/solution/report.html
```

메뉴 3번에서는 주요 지표를 터미널에서 보고, 4번에서는 HTML 리포트를 브라우저로 엽니다.

## 14단계: 학생 코드와 완성형 코드 비교

학생 코드가 모두 통과한 뒤 다음 파일을 비교합니다.

- 학생 산식: `student/exercises.py`
- 정답 산식: `student/exercises_answer.py`
- 완성형 전체 지표: `solution/metrics.py`
- 완성형 리포트: `solution/report.py`

단순히 답을 복사하지 말고 다음을 확인합니다.

정답 파일은 짧은 한 줄 코드보다 다음 순서가 보이도록 작성되어 있습니다.

```text
입력 확인 → 필요한 개수 세기 → 시간·비율 계산 → 결과 반환
```

1. 분과 초 단위가 정확히 변환됐는가?
2. 최초 수면과 마지막 수면의 인덱스를 올바르게 찾았는가?
3. 수면이 전혀 없는 경우 0으로 나누지 않는가?
4. 각성 전환과 모든 단계 변경을 구분했는가?
5. 가중치 합이 100%인가?
6. HTML에 입력값을 그대로 넣지 않고 escape했는가?

## 15단계: 결과 보고서 작성

다음 내용을 포함합니다.

1. TIB, TST, SE, SL, WASO의 정의와 산식
2. REM/NREM 비율 산식
3. 단계 변경과 각성 전환의 차이
4. 항목별 점수 구간
5. 가중 종합점수 산식
6. 예제 CSV에서 계산된 주요 지표
7. 완성형 HTML 리포트 화면
8. 구현 중 발생한 오류와 해결 방법
9. 현재 점수 기준의 한계
10. 의료 진단용으로 사용할 수 없는 이유

## 참고: NREM 점수 기준

완성형 프로그램은 기존 프로젝트의 결과를 재현하기 위해 `NREM=LS+DS`로 계산하면서 제공된 NREM 점수 구간을 그대로 사용합니다. 해당 구간은 일반적인 전체 NREM 비율과 맞지 않을 가능성이 있으므로 교육용 산식 비교 대상으로만 사용합니다.

## 전체 실행 명령 요약

```powershell
py -3.12 -m venv .venv
```

```powershell
.\.venv\Scripts\Activate.ps1
```

```powershell
python student/exercises.py
```

```powershell
python run_classroom.py
```
