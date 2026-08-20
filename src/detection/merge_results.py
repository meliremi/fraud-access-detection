"""
2.4 - Consolidation des resultats de detection (Melissa)

Fusionne les 3 methodes (regles, Isolation Forest, clustering) en un seul fichier final.
Les 3 fichiers d'entree viennent tous de logs_features.csv, traites independamment sans
reordonner les lignes -> on peut les recoller par position (meme ordre, meme longueur).

Colonnes finales ajoutees :
- is_anomaly (0/1) : au moins une des 3 methodes a detecte une anomalie (OR logique)
- anomaly_score : proportion des methodes qui ont flague la ligne (0, 0.33, 0.67, 1)
- anomaly_type : type d'anomalie si connu via les regles, sinon "ml_detected"
- detected_by : quelles methodes ont declenche (rule / isolation_forest / clustering)

Sortie finale : data/processed/logs_scored.csv
"""

import pandas as pd

RULES_PATH = "data/processed/logs_rules.csv"
IF_PATH = "data/processed/logs_if.csv"
CLUSTERING_PATH = "data/processed/logs_clustering.csv"
OUTPUT_PATH = "data/processed/logs_scored.csv"


def merge_all(rules_path: str = RULES_PATH, if_path: str = IF_PATH, clustering_path: str = CLUSTERING_PATH) -> pd.DataFrame:
    df_rules = pd.read_csv(rules_path, parse_dates=["timestamp"])
    df_if = pd.read_csv(if_path)
    df_clustering = pd.read_csv(clustering_path)

    assert len(df_rules) == len(df_if) == len(df_clustering), (
        "Les 3 fichiers n'ont pas le meme nombre de lignes, "
        "verifie que rules/isolation_forest/clustering ont bien tourne sur le meme logs_features.csv"
    )

    df = df_rules.copy()
    df["anomaly_score_if"] = df_if["anomaly_score_if"]
    df["anomaly_if"] = df_if["anomaly_if"]
    df["cluster_kmeans"] = df_clustering["cluster_kmeans"]
    df["anomaly_dbscan"] = df_clustering["anomaly_dbscan"]

    # is_anomaly : OR logique entre les 3 methodes
    df["is_anomaly"] = (
        (df["anomaly_rule_based"] == 1) | (df["anomaly_if"] == 1) | (df["anomaly_dbscan"] == 1)
    ).astype(int)

    # detected_by : liste des methodes qui ont declenche, separees par des virgules
    def detected_by(row):
        methods = []
        if row["anomaly_rule_based"] == 1:
            methods.append("rule")
        if row["anomaly_if"] == 1:
            methods.append("isolation_forest")
        if row["anomaly_dbscan"] == 1:
            methods.append("clustering")
        return ",".join(methods)

    df["detected_by"] = df.apply(detected_by, axis=1)

    # anomaly_type : garde le motif des regles s'il existe, sinon "ml_detected" si detecte par IF/clustering seuls
    df["anomaly_type"] = df["anomaly_reason"].replace("", pd.NA)
    df.loc[df["anomaly_type"].isna() & (df["is_anomaly"] == 1), "anomaly_type"] = "ml_detected"

    # anomaly_score : proportion des 3 methodes qui ont flague (facile a lire, 0 a 1)
    df["anomaly_score"] = (
        df[["anomaly_rule_based", "anomaly_if", "anomaly_dbscan"]].sum(axis=1) / 3
    )

    return df


def main():
    df = merge_all()
    df.to_csv(OUTPUT_PATH, index=False)

    n_anomalies = df["is_anomaly"].sum()
    print(f"{len(df)} lignes -> {OUTPUT_PATH}")
    print(f"{n_anomalies} anomalies au total ({n_anomalies / len(df):.1%}), toutes methodes confondues")
    print("\nRepartition par nombre de methodes ayant detecte :")
    print(df.loc[df["is_anomaly"] == 1, "detected_by"].value_counts())

    if "ground_truth_anomaly" in df.columns:
        tp = ((df["is_anomaly"] == 1) & (df["ground_truth_anomaly"] == 1)).sum()
        total_true = (df["ground_truth_anomaly"] == 1).sum()
        fp = ((df["is_anomaly"] == 1) & (df["ground_truth_anomaly"] == 0)).sum()
        print(f"\nVerite terrain : {tp}/{total_true} anomalies injectees retrouvees, {fp} faux positifs")


if __name__ == "__main__":
    main()