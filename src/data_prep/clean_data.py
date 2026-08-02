"""
1.2 - Nettoyage des logs (Melissa)

- Valeurs manquantes (IP non resolue -> "unknown", endpoint/query_type non concernes -> "N/A")
- Suppression des doublons stricts
- Normalisation des timestamps (parsing datetime, tri chronologique)
- Typage correct des colonnes (categorielles vs datetime vs numeriques)

Entree : data/raw/logs.csv
Sortie : data/processed/logs_clean.csv
"""

import os

import pandas as pd

RAW_PATH = "data/raw/logs.csv"
OUTPUT_PATH = "data/processed/logs_clean.csv"


def clean_logs(input_path: str = RAW_PATH) -> pd.DataFrame:
    df = pd.read_csv(input_path)

    # 1) timestamps : parsing datetime, on vire les lignes dont la date est illisible
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    n_before = len(df)
    df = df.dropna(subset=["timestamp"])
    if len(df) < n_before:
        print(f"{n_before - len(df)} lignes avec timestamp invalide supprimees")

    # 2) doublons stricts (toutes les colonnes identiques)
    n_before = len(df)
    df = df.drop_duplicates()
    if len(df) < n_before:
        print(f"{n_before - len(df)} doublons stricts supprimes")

    # 3) valeurs manquantes
    df["ip_address"] = df["ip_address"].fillna("unknown")
    df["endpoint"] = df["endpoint"].fillna("N/A")
    df["query_type"] = df["query_type"].fillna("N/A")
    df["ground_truth_type"] = df["ground_truth_type"].fillna("none")

    # 4) typage des colonnes categorielles
    categorical_cols = ["source", "device", "status", "endpoint", "query_type", "country"]
    for col in categorical_cols:
        df[col] = df[col].astype("category")

    df["ground_truth_anomaly"] = df["ground_truth_anomaly"].astype(int)
    df["session_duration"] = df["session_duration"].astype(float)

    return df.sort_values("timestamp").reset_index(drop=True)


def main():
    os.makedirs("data/processed", exist_ok=True)
    df = clean_logs()
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"{len(df)} lignes nettoyees -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()