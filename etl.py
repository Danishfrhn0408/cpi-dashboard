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
    "overall": "Keseluruhan",
    "01": "Makanan & minuman tidak beralkohol",
    "02": "Alkohol & tembakau",
    "03": "Pakaian & kasut",
    "04": "Perumahan, air, elektrik, gas",
    "05": "Perabot & peralatan rumah",
    "06": "Kesihatan",
    "07": "Pengangkutan",
    "08": "Maklumat & komunikasi",
    "09": "Rekreasi, sukan & budaya",
    "10": "Pendidikan",
    "11": "Restoran & penginapan",
    "12": "Insurans & kewangan",
    "13": "Penjagaan peribadi & lain-lain",
}
df["division_name"] = df["division"].map(names)

# LOAD
con = duckdb.connect("data/cpi.duckdb")
con.execute("CREATE OR REPLACE TABLE cpi AS SELECT * FROM df")
print(con.execute("SELECT COUNT(*) FROM cpi").fetchone())
con.close()