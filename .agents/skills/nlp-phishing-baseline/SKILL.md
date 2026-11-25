---
name: nlp-phishing-baseline
description: >-
  Build, train, calibrate, and evaluate fast CPU-friendly NLP baselines for
  phishing and social engineering detection in corporate chats and emails. Use
  when working in `ml/` on datasets, text classification (TF-IDF +
  LogReg/LightGBM or compact models), probability calibration, or Recall/FPR
  evaluation.
---

# NLP Phishing & Social Engineering Baseline

Workflow for developing the `ml/` text classifier in MindShield without data leakage or heavy GPU dependencies.

## Principles

- **CPU-first speed:** Start with `TF-IDF` (word + char n-grams) + `LogisticRegression` / `LightGBM`. Only consider compact transformers if baseline Recall at target FPR is insufficient and latency stays under ~50 ms on CPU.
- **Reproducibility:** Fix `random_state=42` everywhere (splits, vectorizers, models) and pin versions in `pyproject.toml` / `uv.lock`.
- **No leakage:** Deduplicate near-identical phishing templates and split by **group/sender/campaign** or **time** (`GroupShuffleSplit` / `TimeSeriesSplit`), never random row split across repeated templates.

## Steps

1. **Audit datasets first:** Combine phishing corpora (e.g., PhishTank, Nazario, public phishing/spam datasets) with legitimate business communication (e.g., Enron, corporate chat/support text). Check class balance, language mix (RU/EN), and template duplicates.
2. **Build minimal pipeline:**
   - Normalize text (strip zero-width chars, normalize whitespace, preserve urgency/punctuation cues and URLs as tokens rather than dropping them blindly).
   - Fit `sklearn.pipeline.Pipeline` inside CV/train split only — never fit `TfidfVectorizer` on full data.
3. **Evaluate for B2B anti-phishing:**
   - Primary metric: **Recall at fixed low False Positive Rate** (e.g., FPR ≤ 1%–2%) and **PR-AUC** (not raw Accuracy).
   - Calibrate output probabilities (`CalibratedClassifierCV` with isotonic/sigmoid on validation fold) so `ml_score` in `[0.0, 1.0]` is meaningful for `sec/` Rule Engine.
4. **Error analysis:** Inspect top False Positives (legitimate urgent emails) and False Negatives (subtle social engineering) before tuning hyperparameters.

## Verification

- Run end-to-end training & evaluation script from a clean state and confirm identical metrics with `random_state=42`.
- Verify single-message inference latency on CPU and confirm serialized artifact loads cleanly without network calls.
