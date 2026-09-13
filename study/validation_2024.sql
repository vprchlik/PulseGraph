-- Exact fixed validation names are supplied as a query parameter; no target frame overlap.
-- Count by type, never payload.action. Duplicate event IDs count once per repository.
WITH names AS (
  SELECT DISTINCT repo.id AS repo_id
  FROM `githubarchive.day.2024*`
  WHERE _TABLE_SUFFIX BETWEEN '0101' AND '1231'
    AND repo.name IN UNNEST(@validation_repositories)
), events AS (
  SELECT DISTINCT id AS event_id, repo.id AS repo_id,
    TIMESTAMP_TRUNC(created_at, HOUR, 'UTC') AS hour_start
  FROM `githubarchive.day.2024*`
  WHERE _TABLE_SUFFIX BETWEEN '0101' AND '1231'
    AND type = 'WatchEvent'
    AND DATE(created_at) BETWEEN DATE '2024-01-01' AND DATE '2024-12-31'
), counts AS (
  SELECT e.repo_id, e.hour_start, COUNT(*) AS watch_events
  FROM events e JOIN names n USING (repo_id)
  GROUP BY e.repo_id, e.hour_start
), calendar AS (
  SELECT n.repo_id, hour_start
  FROM names n CROSS JOIN
    UNNEST(GENERATE_TIMESTAMP_ARRAY(TIMESTAMP '2024-01-01 00:00:00+00',
      TIMESTAMP '2024-12-31 23:00:00+00', INTERVAL 1 HOUR)) AS hour_start
)
SELECT c.repo_id, c.hour_start, COALESCE(n.watch_events, 0) AS watch_events
FROM calendar c LEFT JOIN counts n USING (repo_id, hour_start)
ORDER BY repo_id, hour_start
