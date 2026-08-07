"""
1.3 - Feature engineering (Melissa)

Ajoute :
- hour_of_day, day_of_week, is_weekend
- fail_count_10min, fail_count_1h : compteur glissant des echecs par utilisateur
- minutes_since_last_login, country_changed, impossible_travel_score
- usual_hour_mean/std, usual_country, hour_deviation, is_new_country (baseline utilisateur)
- source_code, device_code : encodage numerique pour le ML

Entree : data/processed/logs_clean.csv
Sortie : data/processed/logs_features.csv
"""

import os

import pandas as pd

INPUT_PATH = "data/processed/logs_clean.csv"
OUTPUT_PATH = "data/processed/logs_features.csv"


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["hour_of_day"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek  # 0 = lundi ... 6 = dimanche
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
    return df


def add_rolling_failure_counts(df: pd.DataFrame) -> pd.DataFrame:
    """Compte, pour chaque connexion, le nombre d'echecs du meme utilisateur
    dans les 10 dernieres minutes et dans la derniere heure (fenetres glissantes)."""
    df = df.sort_values(["user_id", "timestamp"]).copy()
    df["is_fail"] = (df["status"] == "fail").astype(int)

    df = df.set_index("timestamp")
    df["fail_count_10min"] = (
        df.groupby("user_id")["is_fail"].rolling("10min").sum().reset_index(level=0, drop=True)
    )
    df["fail_count_1h"] = (
        df.groupby("user_id")["is_fail"].rolling("1h").sum().reset_index(level=0, drop=True)
    )
    df = df.reset_index()
    df = df.drop(columns=["is_fail"])
    return df.reset_index(drop=True)


def add_impossible_travel_score(df: pd.DataFrame, threshold_minutes: int = 60) -> pd.DataFrame:
    """Repere les changements de pays trop rapides entre deux connexions du meme utilisateur."""
    df = df.sort_values(["user_id", "timestamp"]).copy()
    df["prev_country"] = df.groupby("user_id")["country"].shift(1)
    df["prev_timestamp"] = df.groupby("user_id")["timestamp"].shift(1)
    df["minutes_since_last_login"] = (
        (df["timestamp"] - df["prev_timestamp"]).dt.total_seconds() / 60
    )
    df["country_changed"] = (df["country"] != df["prev_country"]) & df["prev_country"].notna()
    df["impossible_travel_score"] = (
        df["country_changed"] & (df["minutes_since_last_login"] < threshold_minutes)
    ).astype(int)
    df = df.drop(columns=["prev_country", "prev_timestamp"])
    return df


def add_user_baseline(df: pd.DataFrame) -> pd.DataFrame:
    """Calcule le comportement habituel de chaque utilisateur (heure moyenne, pays le plus frequent)
    puis mesure l'ecart de chaque connexion par rapport a cette baseline."""
    df = df.copy()

    baseline_hour = (
        df.groupby("user_id")["hour_of_day"]
        .agg(usual_hour_mean="mean", usual_hour_std="std")
        .reset_index()
    )
    baseline_hour["usual_hour_std"] = baseline_hour["usual_hour_std"].fillna(0)

    usual_country = (
        df.groupby("user_id")["country"]
        .agg(lambda x: x.mode().iloc[0])
        .reset_index()
        .rename(columns={"country": "usual_country"})
    )

    df = df.merge(baseline_hour, on="user_id", how="left")
    df = df.merge(usual_country, on="user_id", how="left")

    df["hour_deviation"] = (df["hour_of_day"] - df["usual_hour_mean"]).abs()
    df["is_new_country"] = (df["country"] != df["usual_country"]).astype(int)
    return df


def encode_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    """Encodage numerique simple des variables categorielles pour les modeles ML."""
    df = df.copy()
    for col in ["source", "device"]:
        df[f"{col}_code"] = df[col].astype("category").cat.codes
    return df


def main():
    os.makedirs("data/processed", exist_ok=True)
    df = pd.read_csv(INPUT_PATH, parse_dates=["timestamp"])

    df = add_time_features(df)
    df = add_rolling_failure_counts(df)
    df = add_impossible_travel_score(df)
    df = add_user_baseline(df)
    df = encode_categoricals(df)

    df.to_csv(OUTPUT_PATH, index=False)
    print(f"{len(df)} lignes avec features -> {OUTPUT_PATH}")
    print(f"Colonnes ajoutees : {[c for c in df.columns if c not in ['user_id','timestamp','source','ip_address','country','city','device','status','endpoint','query_type','session_duration','ground_truth_anomaly','ground_truth_type']]}")


if __name__ == "__main__":
    main()