-- Registered frame; WatchEvent action is always started. Do not scan its payload.
-- https://docs.github.com/en/rest/using-the-rest-api/github-event-types#watchevent
WITH creations AS (
  SELECT repo_id,
    ARRAY_AGG(STRUCT(repo_name, created_at)
      ORDER BY created_at, id LIMIT 1)[OFFSET(0)] AS creation
  FROM (
    -- Year prefixes exclude the non-table day.yesterday view.
    SELECT id, repo.id AS repo_id, repo.name AS repo_name, created_at
    FROM `githubarchive.day.2023*`
    WHERE _TABLE_SUFFIX BETWEEN '0101' AND '1231'
      AND type = 'CreateEvent' AND JSON_VALUE(payload, '$.ref_type') = 'repository'
    UNION ALL
    SELECT id, repo.id AS repo_id, repo.name AS repo_name, created_at
    FROM `githubarchive.day.2024*`
    WHERE _TABLE_SUFFIX BETWEEN '0101' AND '1231'
      AND type = 'CreateEvent' AND JSON_VALUE(payload, '$.ref_type') = 'repository'
    UNION ALL
    SELECT id, repo.id AS repo_id, repo.name AS repo_name, created_at
    FROM `githubarchive.day.2025*`
    WHERE _TABLE_SUFFIX BETWEEN '0101' AND '0221'
      AND type = 'CreateEvent' AND JSON_VALUE(payload, '$.ref_type') = 'repository'
  )
  WHERE DATE(created_at) BETWEEN DATE '2023-01-01' AND DATE '2025-02-21'
  GROUP BY repo_id
), stars AS (
  SELECT DISTINCT event_id, repo_id, event_date
  FROM (
    SELECT id AS event_id, repo.id AS repo_id, DATE(created_at) AS event_date
    FROM `githubarchive.day.2023*`
    WHERE _TABLE_SUFFIX BETWEEN '0101' AND '1231' AND type = 'WatchEvent'
    UNION ALL
    SELECT id AS event_id, repo.id AS repo_id, DATE(created_at) AS event_date
    FROM `githubarchive.day.2024*`
    WHERE _TABLE_SUFFIX BETWEEN '0101' AND '1231' AND type = 'WatchEvent'
    UNION ALL
    SELECT id AS event_id, repo.id AS repo_id, DATE(created_at) AS event_date
    FROM `githubarchive.day.2025*`
    WHERE _TABLE_SUFFIX BETWEEN '0101' AND '0521' AND type = 'WatchEvent'
  )
  WHERE event_date BETWEEN DATE '2023-01-01' AND DATE '2025-05-21'
), eligible AS (
  SELECT c.repo_id, c.creation.repo_name AS repo_name,
    DATE(c.creation.created_at) AS creation_date,
    COUNT(s.event_id) AS day90_stars
  FROM creations AS c
  LEFT JOIN stars AS s ON c.repo_id = s.repo_id
    AND s.event_date BETWEEN DATE(c.creation.created_at)
      AND DATE_ADD(DATE(c.creation.created_at), INTERVAL 89 DAY)
  GROUP BY c.repo_id, repo_name, creation_date
)
SELECT *, CASE WHEN day90_stars < 100 THEN '20-99'
  WHEN day90_stars < 1000 THEN '100-999' ELSE '1000+' END AS sampling_stratum
FROM eligible
WHERE day90_stars >= 20
ORDER BY sampling_stratum, repo_id
