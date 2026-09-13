-- Exact fixed validation names are supplied as a query parameter; no target frame overlap.
-- Count by type, never payload.action. Duplicate event IDs count once per repository.
WITH names AS (
  SELECT DISTINCT repo.id AS repo_id
  FROM `githubarchive.day.*`
  WHERE _TABLE_SUFFIX BETWEEN '20240101' AND '20241231'
    AND repo.name IN UNNEST(@validation_repositories)
), events AS (
  SELECT DISTINCT id AS event_id, repo.id AS repo_id, DATE(created_at) AS event_date
  FROM `githubarchive.day.*`
  WHERE _TABLE_SUFFIX BETWEEN '20240101' AND '20241231'
    AND type = 'WatchEvent'
    AND DATE(created_at) BETWEEN DATE '2024-01-01' AND DATE '2024-12-31'
), counts AS (
  SELECT e.repo_id, e.event_date, COUNT(*) AS watch_events
  FROM events e JOIN names n USING (repo_id)
  GROUP BY e.repo_id, e.event_date
), calendar AS (
  SELECT n.repo_id, day AS event_date
  FROM names n CROSS JOIN
    UNNEST(GENERATE_DATE_ARRAY(DATE '2024-01-01', DATE '2024-12-31')) AS day
)
SELECT c.repo_id, c.event_date, COALESCE(n.watch_events, 0) AS watch_events
FROM calendar c LEFT JOIN counts n USING (repo_id, event_date)
ORDER BY repo_id, event_date
