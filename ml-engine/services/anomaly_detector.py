# ml-engine/services/anomaly_detector.py
import numpy as np
from sklearn.ensemble import IsolationForest
from collections import defaultdict

def detect_anomalies(transactions: list[dict]) -> list[dict]:
    """
    Flag transactions with unusual amounts per category.
    Returns transactions list with is_anomaly and anomaly_reason fields added.
    """
    if len(transactions) < 5:
        return transactions  # Not enough data to detect anomalies

    # Group by category and detect per-category anomalies
    by_category = defaultdict(list)
    for i, t in enumerate(transactions):
        by_category[t["category"]].append((i, t["amount"]))

    anomaly_indices = set()
    reasons = {}

    for category, items in by_category.items():
        if len(items) < 3:
            continue  # Need at least 3 data points
        amounts = np.array([a for _, a in items]).reshape(-1, 1)
        detector = IsolationForest(contamination=0.1, random_state=42)
        preds = detector.fit_predict(amounts)
        median_amount = float(np.median(amounts))

        for (idx, amount), pred in zip(items, preds):
            if pred == -1:
                multiple = round(amount / median_amount, 1) if median_amount > 0 else 0
                anomaly_indices.add(idx)
                reasons[idx] = (
                    f"Amount ₹{amount:,.0f} is {multiple}x above your "
                    f"usual {category} spending (₹{median_amount:,.0f})"
                )

    for i, t in enumerate(transactions):
        t["is_anomaly"] = i in anomaly_indices
        t["anomaly_reason"] = reasons.get(i)

    return transactions
