# Security Module (InfoSec Zone)

Зона ответственности ИБ:
- Безопасный анализатор URL (разворачивание редиректов с защитой от SSRF и таймаутами).
- Проверка возраста домена (WHOIS), SSL и репутационных баз (URLhaus / VirusTotal / Safe Browsing).
- Парсинг и валидация почтовых заголовков (`SPF`, `DKIM`, `DMARC`, `From` vs `Reply-To`).
- Контракт: принимает `AnalyzeRequest`, возвращает `SecResult` (`sec_score`, `reasons`).
