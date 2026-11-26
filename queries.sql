CREATE OR REPLACE VIEW cpi_yoy AS
SELECT
  state, division, division_name, date, cpi_index,
  (cpi_index / LAG(cpi_index, 12) OVER (
      PARTITION BY state, division ORDER BY date
  ) - 1) * 100 AS yoy_pct
FROM cpi;