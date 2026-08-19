import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import csv
import io
from datetime import datetime, timedelta

st.set_page_config(page_title="EDA SEN - Sold Import/Export", layout="wide")



# custom csv reader pentru a gestiona multiple encodări și a evita erorile de citire
def load_any_file(file_source):
    if hasattr(file_source, "name"):
        name = file_source.name.lower()
    else:
        name = str(file_source).lower()

    if name.endswith(".xlsx") or name.endswith(".xls"):
        if hasattr(file_source, "seek"):
            file_source.seek(0)
        return pd.read_excel(file_source)

    # Fallback CSV
    if hasattr(file_source, "seek"):
        file_source.seek(0)
    return pd.read_csv(file_source, sep=None, engine="python")

# ----------------------------------------------------
# 1. FUNCȚII DE ÎNCĂRCARE ȘI PROCESARE DATE
# ----------------------------------------------------
@st.cache_data
def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """Normalizează coloanele și calculează variabilele derivate."""
    # Normalizare nume coloane
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"\[.*\]", "", regex=True)
        .str.strip()
    )

    # Identificare coloană timestamp
    time_cols = [
        c
        for c in df.columns
        if any(k in c for k in ["data", "time", "date", "timp", "timestamp"])
    ]
    if time_cols:
        df["timestamp"] = pd.to_datetime(df[time_cols[0]], dayfirst=True)
        df = df.sort_values("timestamp")

    # Conversie coloane numerice
    mapping = {
        "consum": "consum",
        "productie": "productie",
        "eolian": "eolian",
        "foto": "foto",
        "solar": "foto",
        "hidro": "hidro",
        "ape": "hidro",
        "nuclear": "nuclear",
        "carbune": "carbune",
        "hidrocarburi": "hidrocarburi",
        "gaz": "hidrocarburi",
        "sold": "sold",
    }

    for col in df.columns:
        for key, target in mapping.items():
            if key in col:
                df[target] = pd.to_numeric(
                    df[col].astype(str).str.replace(",", "."), errors="coerce"
                )

    # Convenția Transelectrica: Sold = Productie - Consum
    if "sold" not in df.columns and "productie" in df and "consum" in df:
        df["sold"] = df["productie"] - df["consum"]

    # Status energetic
    df["status"] = df["sold"].apply(
        lambda v: "Export" if v > 0 else "Import" if v < 0 else "Echilibru"
    )

    # Surse variabile și sarcină reziduală
    eolian = df["eolian"].fillna(0) if "eolian" in df.columns else 0
    foto = df["foto"].fillna(0) if "foto" in df.columns else 0
    df["variabil"] = eolian + foto

    if "consum" in df.columns:
        df["sarcina_reziduala"] = df["consum"] - df["variabil"]

    return df


# function to generate synthetic data for demonstration purposes
@st.cache_data
def get_synthetic_data() -> pd.DataFrame:
    """Generează un set de date demonstrativ pe 1 an în absența unui fișier local."""
    dates = pd.date_range(end=pd.Timestamp.now(), periods=52560, freq="10min")
    n = len(dates)
    np.random.seed(42)

    hour_factor = np.sin(np.linspace(0, 2 * np.pi * 365, n))
    consum = 5500 + 1800 * np.sin(np.linspace(0, 2 * np.pi * 365 * 24, n))
    eolian = np.clip(1200 + 1000 * np.sin(np.linspace(0, 50 * np.pi, n)), 0, None)
    foto = np.clip(
        2200
        * np.sin(np.linspace(0, 2 * np.pi * 365 * 24, n))
        * (dates.hour >= 6)
        * (dates.hour <= 19),
        0,
        None,
    )
    hidro = 1800 + 400 * np.random.randn(n)
    nuclear = np.full(n, 1400)
    carbune = 1000 + 200 * np.random.randn(n)
    hidrocarburi = 800 + 200 * np.random.randn(n)

    prod = hidro + nuclear + carbune + hidrocarburi + eolian + foto
    sold = prod - consum

    return pd.DataFrame(
        {
            "timestamp": dates,
            "consum": consum,
            "productie": prod,
            "carbune": carbune,
            "hidrocarburi": hidrocarburi,
            "hidro": hidro,
            "nuclear": nuclear,
            "eolian": eolian,
            "foto": foto,
            "sold": sold,
        }
    )


# ----------------------------------------------------
# 2. SELECȚIE SURSĂ DATE (SIDEBAR)
# ----------------------------------------------------
st.sidebar.header("📁 Sursă Date")
uploaded_file = st.sidebar.file_uploader(
    "Încarcă fișier Transelectrica (Excel sau CSV)", type=["xlsx", "xls", "csv"]
)

DEFAULT_FILE = "Grafic_SEN_2025.csv"

df_all = None   

if uploaded_file is not None:
    raw_df = load_any_file(uploaded_file)
    df_all = process_data(raw_df)
    st.sidebar.success("Fișier încărcat manual!")
elif os.path.exists(DEFAULT_FILE):
    raw_df = load_any_file(DEFAULT_FILE)
    df_all = process_data(raw_df)
    st.sidebar.info(f"Se utilizează setul local: `{DEFAULT_FILE}`")
#else: mock data if no file is found in root or uploaded by the user
    #df_all = process_data(get_synthetic_data())
    #st.sidebar.warning("⚠️ Se utilizează date generate (pune fișierul în folder).")


if df_all is None or df_all.empty:
    st.warning("⚠️ Nu a fost găsit niciun set de date. Te rog să încarci un fișier din meniul lateral pentru a continua.")
    st.stop() # Această comandă oprește scriptul aici. Nu va mai rula nimic mai jos!

# ----------------------------------------------------
# 3. FILTRARE PE INTERVAL DE TIMP
# ----------------------------------------------------
min_timestamp = df_all["timestamp"].min()
max_timestamp = df_all["timestamp"].max()

min_date = min_timestamp.date()
max_date = max_timestamp.date()

st.sidebar.header("📅 Filtrare Perioadă")

# Creăm o cheie unică bazată pe limitele fișierului
# Dacă schimbi fișierul, cheia se schimbă, iar Streamlit resetează complet calendarul
calendar_key = f"date_picker_{min_date}_{max_date}"

date_range = st.sidebar.date_input(
    "Selectează intervalul",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    key=calendar_key
)


start_time = st.sidebar.time_input(
    "Ora de început",
    value=min_timestamp.time().replace(second=0, microsecond=0),
)

end_time = st.sidebar.time_input(
    "Ora de sfârșit",
    value=max_timestamp.time().replace(second=0, microsecond=0),
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range

    start_datetime = datetime.combine(start_date, start_time)
    end_datetime = datetime.combine(end_date, end_time)

    if start_datetime > end_datetime:
        st.error("Ora de început trebuie să fie înaintea orei de sfârșit.")
        st.stop()

    # Include the complete selected ending minute
    end_datetime_exclusive = end_datetime + timedelta(minutes=1)

    df = df_all[
        (df_all["timestamp"] >= start_datetime)
        & (df_all["timestamp"] < end_datetime_exclusive)
    ].copy()
else:
    st.info("Selectează o dată de început și una de sfârșit.")
    st.stop()

st.sidebar.info(
    f"Interval selectat:\n\n"
    f"**{start_datetime:%d-%m-%Y %H:%M}** - "
    f"**{end_datetime:%d-%m-%Y %H:%M}**"
)

# debugs for the dates inside the root file
# st.sidebar.write(f"🔍 **Debug Min Date:** {min_date}")
# st.sidebar.write(f"🔍 **Debug Max Date:** {max_date}")

st.title("⚡ SEN România: Analiza Soldului Energetic (Import / Export)")

# ----------------------------------------------------
# 4. RĂSPUNSURI LA ÎNTREBĂRILE EDA
# ----------------------------------------------------

# ÎNTREBAREA 1: Profilul orar
st.subheader("1. Profilul orar al soldului: Vârf vs. Gol de consum")
df["ora"] = df["timestamp"].dt.hour
hourly_agg = df.groupby("ora")[["sold", "consum", "productie"]].mean().reset_index()

fig_hourly = go.Figure()
fig_hourly.add_trace(
    go.Scatter(
        x=hourly_agg["ora"],
        y=hourly_agg["sold"],
        name="Sold Mediu (MW)",
        line=dict(color="#1f77b4", width=3),
    )
)
fig_hourly.add_trace(
    go.Scatter(
        x=hourly_agg["ora"],
        y=hourly_agg["consum"],
        name="Consum Mediu (MW)",
        line=dict(color="#d62728", dash="dot"),
        yaxis="y2",
    )
)
fig_hourly.update_layout(
    xaxis=dict(title="Ora zilei (0 - 23)", tickmode="linear"),
    yaxis=dict(
        title="Sold (MW) [>0 Export / <0 Import]",
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor="gray",
    ),
    yaxis2=dict(
        title="Consum (MW)", overlaying="y", side="right", showgrid=False
    ),
    hovermode="x unified",
)
st.plotly_chart(fig_hourly, use_container_width=True)

# ÎNTREBAREA 2: Relația cu sursele variabile
st.subheader("2. Legătura dintre sold și sursele variabile (Eolian & Solar)")
col_m1, col_m2, col_m3 = st.columns(3)
if "eolian" in df.columns:
    col_m1.metric("Corelație Sold – Eolian", round(df["sold"].corr(df["eolian"]), 3))
if "foto" in df.columns:
    col_m2.metric("Corelație Sold – Fotovoltaic", round(df["sold"].corr(df["foto"]), 3))
if "sarcina_reziduala" in df.columns:
    col_m3.metric(
        "Corelație Sold – Sarcină Reziduală",
        round(df["sold"].corr(df["sarcina_reziduala"]), 3),
    )

fig_scatter = px.scatter(
    df,
    x="variabil",
    y="sold",
    color="status",
    color_discrete_map={"Import": "#d62728", "Export": "#2ca02c", "Echilibru": "#7f7f7f"},
    labels={"variabil": "Producție Variabilă (Eolian + Foto) [MW]", "sold": "Sold (MW)"},
    title="Distribuția soldului în funcție de regenerabilele variabile",
)
fig_scatter.add_hline(y=0, line_dash="dash", line_color="black")
st.plotly_chart(fig_scatter, use_container_width=True)

# ÎNTREBAREA 3: Ore pe zi Import vs. Export
st.subheader("3. Număr de ore/zi: Net Importator vs. Net Exportator")
df_hourly = df.set_index("timestamp").resample("1h")[["sold"]].mean().reset_index()
df_hourly["data"] = df_hourly["timestamp"].dt.date
df_hourly["status"] = df_hourly["sold"].apply(
    lambda v: "Import" if v < 0 else "Export" if v > 0 else "Echilibru"
)

daily_hours = (
    df_hourly.groupby(["data", "status"])
    .size()
    .unstack(fill_value=0)
    .reset_index()
)
for col in ["Import", "Export"]:
    if col not in daily_hours.columns:
        daily_hours[col] = 0

fig_hours = px.bar(
    daily_hours,
    x="data",
    y=["Import", "Export"],
    labels={"data": "Data", "value": "Număr ore / zi", "variable": "Regim"},
    color_discrete_map={"Import": "#d62728", "Export": "#2ca02c"},
    title="Bilanțul zilnic al orelor de funcționare",
)
st.plotly_chart(fig_hours, use_container_width=True)

# ÎNTREBAREA 4: Valori maxime și context
st.subheader("4. Valori Maxime Înregistrate & Contextul Mixului Energetic")
idx_max_exp = df["sold"].idxmax()
idx_max_imp = df["sold"].idxmin()

row_exp = df.loc[idx_max_exp]
row_imp = df.loc[idx_max_imp]

col_e, col_i = st.columns(2)
with col_e:
    st.success(f"### 🟢 Maxim Export: {row_exp['sold']:.1f} MW")
    st.write(f"**Data / Ora:** {row_exp['timestamp']}")
    st.write(f"**Consum:** {row_exp.get('consum', 'N/A')} MW")
    st.write(f"**Producție totală:** {row_exp.get('productie', 'N/A')} MW")
    st.write(f"**Eolian:** {row_exp.get('eolian', 0):.1f} MW | **Foto:** {row_exp.get('foto', 0):.1f} MW")

with col_i:
    st.error(f"### 🔴 Maxim Import: {abs(row_imp['sold']):.1f} MW")
    st.write(f"**Data / Ora:** {row_imp['timestamp']}")
    st.write(f"**Consum:** {row_imp.get('consum', 'N/A')} MW")
    st.write(f"**Producție totală:** {row_imp.get('productie', 'N/A')} MW")