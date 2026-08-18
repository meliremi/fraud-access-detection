"""
2.3 - Clustering (Melissa)

- KMeans pour regrouper les comportements (methode du coude affichee, k choisi = 5)
- DBSCAN pour reperer les points isoles (label -1 = anomalie potentielle)
- A comparer avec les resultats des regles et d'Isolation Forest

Entree : data/processed/logs_features.csv
Sortie : data/processed/logs_clustering.csv (ajoute cluster_kmeans, anomaly_dbscan)
"""

import pandas as pd
from sklearn.cluster import DBSCAN, KMeans
from sklearn.preprocessing import StandardScaler

INPUT_PATH = "data/processed/logs_features.csv"
OUTPUT_PATH = "data/processed/logs_clustering.csv"

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

KMEANS_K = 5  # choisi apres avoir regarde la methode du coude (voir print_elbow)
DBSCAN_EPS = 1.5
DBSCAN_MIN_SAMPLES = 10


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["country_changed"] = df["country_changed"].astype(int)
    df["minutes_since_last_login"] = df["minutes_since_last_login"].fillna(
        df["minutes_since_last_login"].max()
    )
    return df


def print_elbow(X_scaled, k_range=range(2, 9)):
    """Affiche l'inertie pour differents k, pour choisir k a l'oeil (methode du coude)."""
    print("Methode du coude (inertie par k) :")
    for k in k_range:
        model = KMeans(n_clusters=k, random_state=42, n_init=10)
        model.fit(X_scaled)
        print(f"  k={k} -> inertie={model.inertia_:.0f}")


def run_kmeans(df: pd.DataFrame, X_scaled, k: int = KMEANS_K) -> pd.DataFrame:
    df = df.copy()
    model = KMeans(n_clusters=k, random_state=42, n_init=10)
    df["cluster_kmeans"] = model.fit_predict(X_scaled)
    return df


def run_dbscan(df: pd.DataFrame, X_scaled) -> pd.DataFrame:
    df = df.copy()
    model = DBSCAN(eps=DBSCAN_EPS, min_samples=DBSCAN_MIN_SAMPLES)
    labels = model.fit_predict(X_scaled)
    df["cluster_dbscan"] = labels
    df["anomaly_dbscan"] = (labels == -1).astype(int)  # -1 = bruit = anomalie potentielle
    return df


def main():
    df = pd.read_csv(INPUT_PATH, parse_dates=["timestamp"])
    df = prepare_features(df)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[FEATURES])

    print_elbow(X_scaled)

    df = run_kmeans(df, X_scaled)
    df = run_dbscan(df, X_scaled)

    df.to_csv(OUTPUT_PATH, index=False)

    print(f"\n{len(df)} lignes analysees -> {OUTPUT_PATH}")
    print("Repartition des clusters KMeans :")
    print(df["cluster_kmeans"].value_counts().sort_index())

    n_flagged = df["anomaly_dbscan"].sum()
    print(f"\n{n_flagged} anomalies detectees par DBSCAN ({n_flagged / len(df):.1%})")

    if "ground_truth_anomaly" in df.columns:
        true_positives = ((df["anomaly_dbscan"] == 1) & (df["ground_truth_anomaly"] == 1)).sum()
        total_true = (df["ground_truth_anomaly"] == 1).sum()
        print(f"Verite terrain retrouvee : {true_positives}/{total_true} anomalies injectees detectees")


if __name__ == "__main__":
    main()