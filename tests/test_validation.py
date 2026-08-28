"""
3.1 - Validation de la detection (Selma)

Le dataset etant synthetique avec anomalies injectees (ground_truth_anomaly,
genere par Melissa dans generate_logs.py), on peut calculer precision/rappel/F1
entre cette verite terrain et la detection finale (is_anomaly).
"""
import pandas as pd
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score

DATA_PATH = "data/processed/logs_scored.csv"


def load_scored_data(path: str = DATA_PATH) -> pd.DataFrame:
    return pd.read_csv(path)


def compute_metrics(df: pd.DataFrame) -> dict:
    y_true = df["ground_truth_anomaly"]
    y_pred = df["is_anomaly"]
    return {
        "precision": precision_score(y_true, y_pred),
        "recall": recall_score(y_true, y_pred),
        "f1": f1_score(y_true, y_pred),
    }


def test_detection_recall_above_baseline():
    """Le systeme doit detecter au moins 50% des anomalies injectees."""
    df = load_scored_data()
    metrics = compute_metrics(df)
    assert metrics["recall"] > 0.5


def test_detection_precision_reasonable():
    """Les anomalies detectees ne doivent pas etre noyees sous les faux positifs."""
    df = load_scored_data()
    metrics = compute_metrics(df)
    assert metrics["precision"] > 0.5


def main():
    df = load_scored_data()
    metrics = compute_metrics(df)
    print(f"Precision : {metrics['precision']:.2%}")
    print(f"Recall : {metrics['recall']:.2%}")
    print(f"F1-score : {metrics['f1']:.2%}")
    cm = confusion_matrix(df["ground_truth_anomaly"], df["is_anomaly"])
    print(f"Matrice de confusion (lignes=verite, colonnes=predit) :\n{cm}")


if __name__ == "__main__":
    main()