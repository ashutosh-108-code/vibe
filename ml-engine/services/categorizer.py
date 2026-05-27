# ml-engine/services/categorizer.py
import pickle
import os
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from data.training_data import LABELED_TRANSACTIONS, KEYWORD_RULES

MODEL_PATH = Path(os.getenv("MODEL_PATH", "./models/categorizer.pkl"))

class ExpenseCategorizer:
    def __init__(self):
        self.rules = KEYWORD_RULES
        self.pipeline = None
        self._load_or_train()

    def _load_or_train(self):
        try:
            if MODEL_PATH.exists():
                with open(MODEL_PATH, "rb") as f:
                    self.pipeline = pickle.load(f)
                # Verify that the loaded pipeline is fully functional and fitted
                self.pipeline.predict_proba(["test description"])
            else:
                self._train()
        except Exception as e:
            print(f"Failed to load or validate model from {MODEL_PATH}: {e}. Retraining model...")
            self._train()

    def _train(self):
        texts = [t[0] for t in LABELED_TRANSACTIONS]
        labels = [t[1] for t in LABELED_TRANSACTIONS]
        self.pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4),
                                      min_df=1, sublinear_tf=True)),
            ("clf", MultinomialNB(alpha=0.1)),
        ])
        self.pipeline.fit(texts, labels)
        try:
            MODEL_PATH.parent.mkdir(exist_ok=True)
            with open(MODEL_PATH, "wb") as f:
                pickle.dump(self.pipeline, f)
        except Exception as e:
            print(f"Warning: Could not save trained model to {MODEL_PATH}: {e}")

    def categorize(self, description: str) -> tuple[str, float]:
        """Returns (category, confidence). Tries rules first, ML as fallback."""
        text_lower = description.lower()
        for category, keywords in self.rules.items():
            if any(kw in text_lower for kw in keywords):
                return category, 1.0  # Rule-based: full confidence

        # ML fallback
        proba = self.pipeline.predict_proba([description])[0]
        confidence = float(proba.max())
        category = self.pipeline.classes_[proba.argmax()]
        return category, confidence

    def categorize_batch(self, descriptions: list[str]) -> list[dict]:
        return [
            {"category": cat, "confidence": conf}
            for cat, conf in (self.categorize(d) for d in descriptions)
        ]

# Singleton - import this everywhere
categorizer = ExpenseCategorizer()
