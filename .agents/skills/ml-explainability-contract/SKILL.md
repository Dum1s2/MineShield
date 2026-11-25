---
name: ml-explainability-contract
description: >-
  Define and validate the Pydantic I/O contract (`schemas.py`) and
  human-readable explainability outputs (`ml_score` + `reasons`) between `ml/`,
  `sec/`, and `bot/`. Use when designing `schemas.py`, extracting trigger
  phrases/features from the classifier, or testing `ml/` integration.
---

# ML Explainability & Pydantic Contract

Keep `ml/` and `sec/` decoupled via strict Pydantic schemas and produce concise, human-readable reasons for every risk score.

## Contract Guidelines (`schemas.py`)

- **Input to `ml/`:** `text: str`, `urls: list[str]`, optional `channel: Literal["telegram", "slack", "email"]`.
- **Output from `ml/`:**
  - `ml_score: float` — calibrated probability in `[0.0, 1.0]`.
  - `reasons: list[ReasonItem]` (or structured tags + short human-readable explanations, e.g., category `urgency` / `authority_pressure` / `credential_request` / `typosquatting`, matched snippet or feature, and contribution weight).
  - `model_version: str` — for traceability across experiments.

## Explainability Rules

1. **Actionable, not raw weights:** Translate top positive features (e.g., TF-IDF n-grams, SHAP values, or domain-similarity flags) into 1–3 short user-facing reasons (e.g., *"Искусственная срочность («срочно переведите», «в течение 15 минут»)"*).
2. **Safe text handling:** Never log full raw corporate messages or extracted credentials/tokens in production logs; truncate or mask sensitive snippets in `reasons` if needed.
3. **Graceful degradation:** If `text` is empty or only contains a URL, `ml/` must still return a valid schema (`ml_score` from domain/lexical features or `0.0` with empty `reasons`), never raise an unhandled exception.

## Verification

- Validate `ml/` output against `schemas.py` with `pytest` on edge cases: empty text, RU+EN mixed text, URL-only message, and high-confidence phishing.
