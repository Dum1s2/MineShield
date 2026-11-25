from schemas import AnalyzeRequest, ReasonItem, SecResult


def analyze_sec(request: AnalyzeRequest) -> SecResult:
    """
    InfoSec module entrypoint.
    TODO (ИБ): безопасное разворачивание редиректов (с защитой от SSRF),
    проверка WHOIS/SSL/репутации URL и валидация заголовков SPF/DKIM/DMARC.
    """
    reasons: list[ReasonItem] = []

    if request.channel == "email" and request.headers:
        auth_results = request.headers.get("Authentication-Results", "").lower()
        if "spf=fail" in auth_results or "dkim=fail" in auth_results or "dmarc=fail" in auth_results:
            reasons.append(
                ReasonItem(
                    category="email_auth_fail",
                    description="Ошибка проверки подлинности отправителя (SPF/DKIM/DMARC)",
                    evidence=auth_results[:120],
                    weight=0.7,
                )
            )

    score = min(1.0, round(sum(r.weight for r in reasons), 4))
    return SecResult(sec_score=score, reasons=reasons, checked_urls=list(request.urls))
