from fastapi import FastAPI

from ml.analyzer import analyze_ml
from schemas import AnalyzeRequest, RiskLevel, VerdictResponse
from sec.analyzer import analyze_sec

app = FastAPI(title="MindShield API", version="0.1.0")


def _compute_verdict(ml_score: float, sec_score: float) -> tuple[float, RiskLevel]:
    total = round(max(ml_score, sec_score, 0.6 * ml_score + 0.4 * sec_score), 4)
    total = min(1.0, total)
    if total >= 0.7:
        return total, "high"
    if total >= 0.35:
        return total, "medium"
    return total, "low"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze", response_model=VerdictResponse)
def analyze(request: AnalyzeRequest) -> VerdictResponse:
    ml_result = analyze_ml(request)
    sec_result = analyze_sec(request)
    total_score, risk_level = _compute_verdict(ml_result.ml_score, sec_result.sec_score)

    all_reasons = ml_result.reasons + sec_result.reasons
    if all_reasons:
        summary = "; ".join(r.description for r in all_reasons[:3])
    else:
        summary = "Признаки фишинга не обнаружены"

    return VerdictResponse(
        risk_level=risk_level,
        total_score=total_score,
        ml=ml_result,
        sec=sec_result,
        summary=summary,
    )
