import pandas as pd
import duckdb

URL = "https://storage.dosm.gov.my/cpi/cpi_2d_state.parquet"

# EXTRACT
df = pd.read_parquet(URL)
print(df.shape)
print(df.dtypes)
print(df.head())

# TRANSFORM
df["date"] = pd.to_datetime(df["date"])
df["division"] = df["division"].astype(str)
df = df.rename(columns={"index": "cpi_index"})  # elak nama reserved dalam SQL
df = df.dropna(subset=["cpi_index"]).drop_duplicates()

# Lookup nama kategori (semak dengan jadual MCOICOP rasmi OpenDOSM)
names = {
    "overall": "Overall",
    "01": "Food & non-alcoholic beverages",
    "02": "Alcohol & tobacco",
    "03": "Clothing & footwear",
    "04": "Housing, water, electricity, gas",
    "05": "Furnishings & household equipment",
    "06": "Health",
    "07": "Transport",
    "08": "Information & communication",
    "09": "Recreation, sport & culture",
    "10": "Education",
    "11": "Restaurants & accommodation",
    "12": "Insurance & financial services",
    "13": "Personal care & other",
}
df["division_name"] = df["division"].map(names)

# LOAD
con = duckdb.connect("data/cpi.duckdb")
con.execute("CREATE OR REPLACE TABLE cpi AS SELECT * FROM df")
print(con.execute("SELECT COUNT(*) FROM cpi").fetchone())
con.execute(open("queries.sql", encoding="utf-8").read())
con.close()