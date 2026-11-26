import duckdb
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Inflasi Malaysia (CPI)", layout="wide")
st.title("Inflasi Malaysia (CPI)")
st.caption("Sumber: OpenDOSM. Indeks asas 2010 = 100")


@st.cache_data
def load():
    con = duckdb.connect("data/cpi.duckdb", read_only=True)
    df = con.execute("SELECT * FROM cpi_yoy").df()
    con.close()
    return df


df = load()

# Penapis di sisi
states = st.sidebar.multiselect(
    "Negeri", sorted(df["state"].unique()), default=["Selangor"]
)
cats = sorted(df["division_name"].dropna().unique())
cat = st.sidebar.selectbox(
    "Kategori", cats, index=cats.index("Keseluruhan") if "Keseluruhan" in cats else 0
)

sel = df[df["state"].isin(states) & (df["division_name"] == cat)]
latest = df["date"].max()

# Angka ringkas
if states:
    cur = sel[sel["date"] == latest].dropna(subset=["yoy_pct"])
    if not cur.empty:
        cols = st.columns(len(cur))
        for c, (_, r) in zip(cols, cur.iterrows()):
            c.metric(f"{r['state']} (inflasi tahunan)", f"{r['yoy_pct']:.2f}%")

# Carta 1: indeks
st.subheader("Trend indeks harga")
st.plotly_chart(
    px.line(sel, x="date", y="cpi_index", color="state"),
    use_container_width=True,
)

# Carta 2: inflasi tahunan
st.subheader("Inflasi tahunan (%)")
st.plotly_chart(
    px.line(sel.dropna(subset=["yoy_pct"]), x="date", y="yoy_pct", color="state"),
    use_container_width=True,
)

# Carta 3: perbandingan negeri
st.subheader(f"Perbandingan negeri: {cat} (bulan terkini)")
comp = (
    df[(df["division_name"] == cat) & (df["date"] == latest)]
    .dropna(subset=["yoy_pct"])
    .sort_values("yoy_pct")
)
st.plotly_chart(
    px.bar(comp, x="yoy_pct", y="state", orientation="h"),
    use_container_width=True,
)