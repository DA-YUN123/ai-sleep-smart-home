"""완성된 지표 계산 결과를 JSON, CSV, HTML 리포트로 저장합니다."""

from __future__ import annotations

import csv
import html
import json
from pathlib import Path

from .metrics import WEIGHTS, calculate_metrics, read_stages


def build_html(metrics: dict[str, object], source_name: str) -> str:
    """계산 결과를 브라우저에서 열 수 있는 독립 HTML 문서로 구성합니다."""
    score_rows = "".join(f"<tr><td>{key}</td><td>{metrics[key]}</td><td>{weight * 100:.0f}%</td></tr>" for key, weight in WEIGHTS.items())
    cards = "".join(f"<div class='card'><span>{label}</span><b>{metrics[key]}</b><small>{unit}</small></div>" for label, key, unit in [
        ("총 기록", "TIB_minutes", "분"), ("총 수면", "TST_minutes", "분"), ("수면 효율", "SE_percent", "%"),
        ("잠복기", "SL_minutes", "분"), ("입면 후 각성", "WASO_minutes", "분"), ("REM", "REM_minutes", "분")])
    return f"""<!doctype html><html lang='ko'><head><meta charset='utf-8'><title>수면 지표 리포트</title><style>
body{{background:#eef2f8;font-family:'Malgun Gothic',sans-serif;color:#17233c}}main{{max-width:960px;margin:30px auto;background:white;padding:30px;border-radius:20px}}header{{display:flex;justify-content:space-between}}.score{{background:#536dfe;color:white;padding:20px;border-radius:16px;font-size:28px}}.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:24px 0}}.card{{border:1px solid #dde3ee;padding:16px;border-radius:12px;display:flex;flex-direction:column}}.card b{{font-size:24px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:10px;border-bottom:1px solid #ddd;text-align:left}}</style></head><body><main>
<header><div><h1>수면 지표 리포트</h1><p>입력: {html.escape(source_name)}</p></div><div class='score'>{metrics['Total_Sleep_Score']} / 100</div></header>
<section class='grid'>{cards}</section><h2>항목 점수와 가중치</h2><table><tr><th>항목</th><th>점수</th><th>가중치</th></tr>{score_rows}</table>
<p>이 결과는 교육용 계산 결과이며 의료 진단을 대신하지 않습니다.</p></main></body></html>"""


def generate_report(input_csv: Path, output_dir: Path, epoch_seconds: float = 30.0) -> dict[str, Path]:
    """입력 CSV를 계산해 JSON, CSV, HTML 파일 세 개를 생성합니다."""
    metrics = calculate_metrics(read_stages(input_csv), epoch_seconds)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path, csv_path, html_path = output_dir / "metrics.json", output_dir / "metrics.csv", output_dir / "report.html"
    json_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    with csv_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(metrics)); writer.writeheader(); writer.writerow(metrics)
    html_path.write_text(build_html(metrics, input_csv.name), encoding="utf-8")
    return {"json": json_path, "csv": csv_path, "html": html_path}
