import duckdb
import plotly.express as px
import streamlit as st
import os
import subprocess
import sys

if not os.path.exists("data/cpi.duckdb"):
    os.makedirs("data", exist_ok=True)
    subprocess.run([sys.executable, "etl.py"], check=True)
st.set_page_config(page_title="Malaysia Inflation (CPI)", layout="wide")
st.title("Malaysia Inflation (CPI)")
st.caption("Source: OpenDOSM. Index base 2010 = 100")


@st.cache_data
def load():
    con = duckdb.connect("data/cpi.duckdb", read_only=True)
    df = con.execute("SELECT * FROM cpi_yoy").df()
    con.close()
    return df


df = load()

# Penapis di sisi
states = st.sidebar.multiselect(
    "State", sorted(df["state"].unique()), default=["Selangor"]
)
cats = sorted(df["division_name"].dropna().unique())
cat = st.sidebar.selectbox(
    "Category", cats, index=cats.index("Overall") if "Overall" in cats else 0
)

sel = df[df["state"].isin(states) & (df["division_name"] == cat)]
latest = df["date"].max()

# Angka ringkas
if states:
    cur = sel[sel["date"] == latest].dropna(subset=["yoy_pct"])
    if not cur.empty:
        cols = st.columns(len(cur))
        for c, (_, r) in zip(cols, cur.iterrows()):
            c.metric(f"{r['state']} (annual inflation)", f"{r['yoy_pct']:.2f}%")

# Carta 1: indeks
st.subheader("Price index trend")
st.plotly_chart(
    px.line(sel, x="date", y="cpi_index", color="state"),
    width="stretch",
)

# Carta 2: inflasi tahunan
st.subheader("Annual inflation (%)")
st.plotly_chart(
    px.line(sel.dropna(subset=["yoy_pct"]), x="date", y="yoy_pct", color="state"),
    width="stretch",
)

# Carta 3: perbandingan negeri
st.subheader(f"State comparison: {cat} (latest month)")
comp = (
    df[(df["division_name"] == cat) & (df["date"] == latest)]
    .dropna(subset=["yoy_pct"])
    .sort_values("yoy_pct")
)
st.plotly_chart(
    px.bar(comp, x="yoy_pct", y="state", orientation="h"),
    width="stretch",
)