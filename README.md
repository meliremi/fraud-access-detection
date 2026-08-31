# Système de Détection d'Accès Frauduleux

Projet de fin d'études — Melissa Remila & Selma Benzouaoua

## Objectif

Détecter des accès suspects ou frauduleux à partir de logs utilisateurs (connexions, accès API, activité base de données), en combinant des règles simples et des méthodes de machine learning (Isolation Forest, clustering), avec un dashboard de visualisation interactif.

## Répartition des tâches

- **Melissa** : génération et préparation des données, détection (règles + ML), dashboard Streamlit.
- **Selma** : analyse exploratoire (EDA), base de données SQL, validation des résultats et tests unitaires.

## Structure du projet

```
fraud-access-detection/
├── data/
│   ├── raw/                  # logs générés (CSV/JSON)
│   └── processed/            # logs nettoyés + logs_scored.csv (résultat final)
├── src/
│   ├── data_prep/            # génération, nettoyage, feature engineering
│   ├── detection/            # règles, Isolation Forest, clustering, fusion
│   ├── dashboard/            # application Streamlit
│   ├── alerts/                # système d'alertes (bonus)
│   └── utils/
├── notebooks/
│   └── exploration_initiale.ipynb   # EDA
├── sql/                        # schéma, import, requêtes
├── tests/                      # tests unitaires + validation (precision/recall/F1)
├── reports/                    # rapport final
├── requirements.txt
└── README.md
```

## Installation

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

## Utilisation — pipeline complet

Exécuter dans l'ordre depuis la racine du projet :

```bash
python src/data_prep/generate_logs.py
python src/data_prep/clean_data.py
python src/data_prep/features.py
python src/detection/rules_detection.py
python src/detection/isolation_forest_model.py
python src/detection/clustering_model.py
python src/detection/merge_results.py
```

Cela produit `data/processed/logs_scored.csv`, le fichier final utilisé par le dashboard, la base SQL et les tests.

## Lancer le dashboard

```bash
streamlit run src/dashboard/app.py
```

Trois pages : **Overview** (indicateurs clés et tendances), **Anomalies** (exploration filtrable, heatmap heure/jour), **Utilisateur** (analyse individuelle vs comportement habituel).

## Base de données SQL

```bash
python sql/load_data.py
```

Charge les logs et les anomalies dans une base SQLite (`sql/fraud_detection.db`). Requêtes types dans `sql/queries.sql`.

## Tests

```bash
pytest tests/ -v
```

Comprend les tests de nettoyage/features, les tests de détection par règles (cas limites) et la validation de la détection (precision/recall/F1 comparés à la vérité terrain injectée dans les données).

## Système d'alertes (bonus)

```bash
python src/alerts/alert_system.py
```

Scanne les résultats et signale les anomalies critiques (brute force, accès non autorisé).

## Méthodes de détection

- **Règles simples** : seuils sur les échecs de connexion, les heures inhabituelles, les changements de pays rapprochés, les accès à des endpoints sensibles.
- **Isolation Forest** : détection non supervisée sur les features comportementales.
- **Clustering (KMeans + DBSCAN)** : regroupement des comportements et détection des points isolés.
- **Fusion** : les trois méthodes sont combinées dans `logs_scored.csv` (colonnes `is_anomaly`, `anomaly_score`, `detected_by`).

## Technologies

Python, Pandas, Scikit-learn, Streamlit, Plotly, SQLite, Faker, Pytest, Git/GitHub.

