# ML Module (Data Science Zone)

Зона ответственности DS:
- Датасеты и эксперименты (`random_state=42`, без утечек данных).
- NLP-классификатор (`TF-IDF + LogReg/LightGBM`, калибровка вероятностей).
- Детектор typosquatting и гомоглифов (`analyzer.py`).
- Контракт: принимает `AnalyzeRequest`, возвращает `MLResult` (`ml_score`, `reasons`).
