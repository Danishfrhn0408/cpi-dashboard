import duckdb

con = duckdb.connect("data/cpi.duckdb")
rows = con.execute("""
    SELECT division_name, ROUND(yoy_pct, 2) AS yoy
    FROM cpi_yoy
    WHERE state = 'Selangor' AND division <> 'overall'
      AND date = (SELECT MAX(date) FROM cpi)
    ORDER BY yoy DESC
    LIMIT 5
""").fetchall()
for r in rows:
    print(r)