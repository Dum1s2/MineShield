from fastapi.testclient import TestClient

from api.main import app
from schemas import AnalyzeRequest

client = TestClient(app)


def test_health() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_phishing_message_high_risk() -> None:
    payload = AnalyzeRequest(
        text="Срочно! Ваш аккаунт заблокирован, перейдите по ссылке и введите пароль.",
        urls=["https://paypa1-security.com/login"],
        channel="telegram",
    )
    resp = client.post("/analyze", json=payload.model_dump())
    assert resp.status_code == 200
    data = resp.json()
    assert data["risk_level"] == "high"
    assert data["ml"]["ml_score"] >= 0.7
    categories = {r["category"] for r in data["ml"]["reasons"]}
    assert "urgency" in categories
    assert "typosquatting" in categories


def test_legit_message_low_risk() -> None:
    payload = AnalyzeRequest(
        text="Привет! Напоминаю про созвон в 15:00 по итогам спринта.",
        urls=["https://google.com"],
        channel="slack",
    )
    resp = client.post("/analyze", json=payload.model_dump())
    assert resp.status_code == 200
    data = resp.json()
    assert data["risk_level"] == "low"
    assert data["total_score"] == 0.0
    assert data["ml"]["reasons"] == []


def test_email_auth_fail_sec_signal() -> None:
    payload = AnalyzeRequest(
        text="Проверьте вложение.",
        urls=[],
        channel="email",
        headers={"Authentication-Results": "mx.example.com; spf=fail; dmarc=fail"},
    )
    resp = client.post("/analyze", json=payload.model_dump())
    assert resp.status_code == 200
    data = resp.json()
    assert data["sec"]["sec_score"] >= 0.7
    assert data["risk_level"] == "high"
