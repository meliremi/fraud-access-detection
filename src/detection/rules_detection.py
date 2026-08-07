"""
2.1 - Detection par regles simples (Melissa)

IMPORTANT : les seuils ci-dessous sont des valeurs de depart. A ajuster avec les
observations EDA de Selma (notebooks/exploration_initiale.ipynb) si besoin.

Regles :
- brute_force : >= 5 echecs en 10 minutes pour un meme user_id (fail_count_10min)
- unusual_hour : heure de connexion trop eloignee de la moyenne habituelle de l'utilisateur
- impossible_travel : deja calcule dans features.py (impossible_travel_score)
- unauthorized_access : acces a un endpoint sensible que l'utilisateur ne visite
  quasiment jamais habituellement (proxy sans info de role explicite)

Entree : data/processed/logs_features.csv
Sortie : data/processed/logs_rules.csv (ajoute anomaly_rule_based et anomaly_reason)
"""

import pandas as pd

INPUT_PATH = "data/processed/logs_features.csv"
OUTPUT_PATH = "data/processed/logs_rules.csv"

FAILED_ATTEMPTS_THRESHOLD = 5
SENSITIVE_ENDPOINTS = ["/admin", "/users/delete", "/config"]
MIN_NORMAL_SENSITIVE_ACCESSES = 3  # en dessous, l'acces est considere comme inhabituel


def detect_brute_force(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["flag_brute_force"] = df["fail_count_10min"] >= FAILED_ATTEMPTS_THRESHOLD
    return df


def detect_unusual_hour(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # seuil : au moins 2 ecarts-types de l'utilisateur, avec un minimum de 3h
    # (pour ne pas etre trop sensible chez les utilisateurs tres reguliers)
    threshold = df["usual_hour_std"].mul(2).clip(lower=3)
    df["flag_unusual_hour"] = df["hour_deviation"] > threshold
    return df


def detect_impossible_travel(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # deja calcule dans features.py (add_impossible_travel_score)
    df["flag_impossible_travel"] = df["impossible_travel_score"].astype(bool)
    return df


def detect_unauthorized_access(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    is_sensitive = df["endpoint"].isin(SENSITIVE_ENDPOINTS)

    access_counts = df.loc[is_sensitive].groupby("user_id").size()
    rare_users = access_counts[access_counts < MIN_NORMAL_SENSITIVE_ACCESSES].index

    df["flag_unauthorized_access"] = is_sensitive & df["user_id"].isin(rare_users)
    return df


def consolidate_rules(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    flag_cols = {
        "flag_brute_force": "brute_force",
        "flag_unusual_hour": "unusual_hour",
        "flag_impossible_travel": "impossible_travel",
        "flag_unauthorized_access": "unauthorized_access",
    }

    df["anomaly_rule_based"] = df[list(flag_cols.keys())].any(axis=1).astype(int)

    def build_reason(row):
        reasons = [label for col, label in flag_cols.items() if row[col]]
        return ",".join(reasons) if reasons else ""

    df["anomaly_reason"] = df.apply(build_reason, axis=1)
    return df


def main():
    df = pd.read_csv(INPUT_PATH, parse_dates=["timestamp"])

    df = detect_brute_force(df)
    df = detect_unusual_hour(df)
    df = detect_impossible_travel(df)
    df = detect_unauthorized_access(df)
    df = consolidate_rules(df)

    df.to_csv(OUTPUT_PATH, index=False)

    n_flagged = df["anomaly_rule_based"].sum()
    print(f"{len(df)} lignes analysees -> {OUTPUT_PATH}")
    print(f"{n_flagged} anomalies detectees par les regles ({n_flagged / len(df):.1%})")

    if "ground_truth_anomaly" in df.columns:
        true_positives = ((df["anomaly_rule_based"] == 1) & (df["ground_truth_anomaly"] == 1)).sum()
        total_true = (df["ground_truth_anomaly"] == 1).sum()
        print(f"Verite terrain retrouvee : {true_positives}/{total_true} anomalies injectees detectees")


if __name__ == "__main__":
    main()