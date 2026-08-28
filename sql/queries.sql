-- Top 10 utilisateurs avec le plus d'anomalies
SELECT l.user_id, COUNT(*) AS nb_anomalies
FROM anomalies a
JOIN logs l ON a.log_id = l.log_id
WHERE a.is_anomaly = 1
GROUP BY l.user_id
ORDER BY nb_anomalies DESC
LIMIT 10;
-- (ex: user_0161 -> 19 anomalies, user_0156 -> 19, user_0219 -> 18, ...)

-- Nombre d'anomalies par jour
SELECT DATE(l.timestamp) AS jour, COUNT(*) AS nb_anomalies
FROM anomalies a
JOIN logs l ON a.log_id = l.log_id
WHERE a.is_anomaly = 1
GROUP BY jour
ORDER BY jour;

-- Repartition des anomalies par type
SELECT anomaly_type, COUNT(*) AS nb
FROM anomalies
WHERE is_anomaly = 1
GROUP BY anomaly_type
ORDER BY nb DESC;
-- (ex: brute_force -> 596, ml_detected -> 424, unusual_hour -> 199, ...)

-- Repartition des anomalies par pays
SELECT l.country, COUNT(*) AS nb_anomalies
FROM anomalies a
JOIN logs l ON a.log_id = l.log_id
WHERE a.is_anomaly = 1
GROUP BY l.country
ORDER BY nb_anomalies DESC;

-- Taux d'anomalies par source (login / api / db)
SELECT l.source,
       COUNT(*) AS total,
       SUM(a.is_anomaly) AS nb_anomalies,
       ROUND(100.0 * SUM(a.is_anomaly) / COUNT(*), 2) AS taux_pct
FROM logs l
JOIN anomalies a ON l.log_id = a.log_id
GROUP BY l.source;
-- (ex: login -> 13.1% d'anomalies, api -> 6.23%, db -> 2.66%)