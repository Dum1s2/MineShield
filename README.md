# MindShield

Детектор фишинга и социальной инженерии для корпоративных чатов и почты (Telegram / Slack / Email).

## Структура репозитория

```text
MindShield/
├── api/            # Общий FastAPI-сервис (точка входа)
├── ml/             # Код, ноутбуки, веса моделей, датасеты (зона DS)
├── sec/            # Проверки URL, WHOIS, SPF/DKIM, репутация (зона ИБ)
├── bot/            # Telegram / Slack бот
├── schemas.py      # Общий Pydantic-контракт (JSON между модулями)
├── tests/          # Тесты на примерах фишинга и легитимных сообщений
├── .env.example    # Шаблон переменных окружения (.env в .gitignore)
├── requirements.txt
└── README.md
```

## Быстрый старт (Windows PowerShell, Python 3.12)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest
uvicorn api.main:app --reload
```

## Правила работы в Git

1. Контракт между `ml/` и `sec/` зафиксирован в `schemas.py`.
2. Ветка `main` всегда рабочая — напрямую в `main` не пушить.
3. Новые задачи — в отдельных ветках (`feat/ml-text-classifier`, `feat/sec-url-checker`, `fix/bot-timeout`) через PR и взаимное ревью.
4. Датасеты (`data/`, `*.csv`, `*.parquet`, `*.pkl`) и секреты (`.env`) не коммитить.
