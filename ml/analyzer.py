import re
from urllib.parse import urlparse

from schemas import AnalyzeRequest, MLResult, ReasonItem

# Minimal MVP social-engineering & lookalike domain baseline.
# Replace/augment with calibrated TF-IDF + LogReg/LightGBM pipeline in ml/.

URGENCY_PATTERNS = [
    r"\bсрочно\b",
    r"\bнемедленно\b",
    r"\bв течение \d+ минут\b",
    r"\bаккаунт.{0,20}заблокир",
    r"\burgent\b",
    r"\bimmediately\b",
    r"\baccount.{0,20}suspend",
    r"\bverify.{0,15}now\b",
]

AUTHORITY_OR_PAYMENT_PATTERNS = [
    r"\bот (ceo|директор|руководител)",
    r"\bперевед(и|ите) (деньги|средства)\b",
    r"\bкод из (смс|sms)\b",
    r"\bпароль\b",
    r"\bwire transfer\b",
    r"\breset.{0,15}password\b",
]

PROTECTED_BRANDS = ("paypal", "google", "microsoft", "telegram", "yandex", "sberbank", "tinkoff")


def _extract_host(url: str) -> str:
    parsed = urlparse(url if "://" in url else f"https://{url}")
    return (parsed.hostname or "").lower()


def _has_cyrillic_latin_mix(host: str) -> bool:
    has_cyr = bool(re.search(r"[а-яё]", host))
    has_lat = bool(re.search(r"[a-z]", host))
    return has_cyr and has_lat


def _check_domain_lookalike(host: str) -> ReasonItem | None:
    if not host:
        return None
    if host.startswith("xn--") or ".xn--" in host:
        return ReasonItem(
            category="homoglyph",
            description="Обнаружен IDN/punycode-домен (возможная подмена символов)",
            evidence=host,
            weight=0.7,
        )
    if _has_cyrillic_latin_mix(host):
        return ReasonItem(
            category="homoglyph",
            description="Смешение кириллицы и латиницы в домене",
            evidence=host,
            weight=0.85,
        )
    normalized = host.replace("0", "o").replace("1", "l").replace("rn", "m")
    for brand in PROTECTED_BRANDS:
        if brand in normalized and f"{brand}." not in host and not host.endswith(f".{brand}.com"):
            return ReasonItem(
                category="typosquatting",
                description=f"Домен визуально имитирует бренд «{brand}»",
                evidence=host,
                weight=0.75,
            )
    return None


def analyze_ml(request: AnalyzeRequest) -> MLResult:
    """Analyze message text and URLs for social engineering and lookalike domains."""
    reasons: list[ReasonItem] = []
    text_lower = request.text.lower()

    for pattern in URGENCY_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            reasons.append(
                ReasonItem(
                    category="urgency",
                    description="Искусственная срочность или угроза блокировки",
                    evidence=match.group(0),
                    weight=0.45,
                )
            )
            break

    for pattern in AUTHORITY_OR_PAYMENT_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            reasons.append(
                ReasonItem(
                    category="social_engineering",
                    description="Давление авторитетом или запрос чувствительных данных/перевода",
                    evidence=match.group(0),
                    weight=0.5,
                )
            )
            break

    for url in request.urls:
        host = _extract_host(url)
        domain_reason = _check_domain_lookalike(host)
        if domain_reason:
            reasons.append(domain_reason)

    score = min(1.0, round(sum(r.weight for r in reasons), 4))
    return MLResult(ml_score=score, reasons=reasons, model_version="0.1.0-mvp-heuristic")
