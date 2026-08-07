"""
2.2 - Detection Isolation Forest (Melissa)

- Selection des features numeriques pertinentes
- Normalisation (StandardScaler)
- IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
- Sauvegarde du modele entraine (joblib) pour reutilisation dans le dashboard

Entree : data/processed/logs_features.csv
Sortie : data/processed/logs_if.csv (ajoute anomaly_score_if, anomaly_if)
"""

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

INPUT_PATH = "data/processed/logs_features.csv"
OUTPUT_PATH = "data/processed/logs_if.csv"
MODEL_PATH = "src/detection/isolation_forest.joblib"
SCALER_PATH = "src/detection/scaler.joblib"

FEATURES = [
    "hour_of_day",
    "day_of_week",
    "is_weekend",
    "fail_count_10min",
    "fail_count_1h",
    "minutes_since_last_login",
    "country_changed",
    "impossible_travel_score",
    "hour_deviation",
    "is_new_country",
    "source_code",
    "device_code",
    "session_duration",
]


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    """Complete les valeurs manquantes propres au ML (ex: pas de connexion precedente)
    et force les types numeriques."""
    df = df.copy()
    df["country_changed"] = df["country_changed"].astype(int)
    # premiere connexion d'un utilisateur -> pas d'ecart connu, on met une valeur haute
    # (= "aucune connexion recente", donc pas suspect de ce point de vue)
    df["minutes_since_last_login"] = df["minutes_since_last_login"].fillna(
        df["minutes_since_last_login"].max()
    )
    return df


def train_isolation_forest(df: pd.DataFrame):
    X = df[FEATURES]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    model.fit(X_scaled)

    df["anomaly_score_if"] = model.decision_function(X_scaled)
    df["anomaly_if"] = (model.predict(X_scaled) == -1).astype(int)

    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    return df


def main():
    df = pd.read_csv(INPUT_PATH, parse_dates=["timestamp"])
    df = prepare_features(df)
    df = train_isolation_forest(df)
    df.to_csv(OUTPUT_PATH, index=False)

    n_flagged = df["anomaly_if"].sum()
    print(f"{len(df)} lignes analysees -> {OUTPUT_PATH}")
    print(f"{n_flagged} anomalies detectees par Isolation Forest ({n_flagged / len(df):.1%})")

    if "ground_truth_anomaly" in df.columns:
        true_positives = ((df["anomaly_if"] == 1) & (df["ground_truth_anomaly"] == 1)).sum()
        total_true = (df["ground_truth_anomaly"] == 1).sum()
        print(f"Verite terrain retrouvee : {true_positives}/{total_true} anomalies injectees detectees")


if __name__ == "__main__":
    main()