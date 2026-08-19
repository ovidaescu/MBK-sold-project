import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

# Endpoint-ul direct sau parsarea exportului CSV de la Transelectrica
DATA_URL = "https://www.transelectrica.ro/widget/web/tel/sen-grafic/-/SENGrafic_WAR_SENGraficportlet"


@st.cache_data(ttl=3600)
def load_data(start_date, end_date):
    """Exemplu de încărcare/parsare a datelor.

    Dacă folosești un CSV descărcat sau API intern, adaptează maparea
    coloanelor.
    """
    # Exemplu de descărcare date (sau încărcare din fișier local/repo)
    # df = pd.read_csv('date_sen.csv') # Alternativă locală
    try:
        response = requests.get(
            DATA_URL,
            params={"start": start_date, "end": end_date},
            timeout=30,
        )
        response.raise_for_status()
        df = pd.DataFrame(response.json())
    except Exception:
        # Fallback demonstrativ dacă API-ul extern nu răspunde direct
        st.warning("Se utilizează structura standard de coloane Transelectrica.")
        return pd.DataFrame()

    # Parsare timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    # Conversie numerică
    cols = [
        "consum",
        "productie",
        "eolian",
        "foto",
        "hidro",
        "nuclear",
        "carbune",
        "hidrocarburi",
        "sold",
    ]
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Conform Transelectrica: Sold = Productie - Consum
    # Sold > 0: Export | Sold < 0: Import
    df["status"] = df["sold"].apply(
        lambda v: "Export" if v > 0 else "Import" if v < 0 else "Echilibru"
    )

    # Calcul surse variabile și sarcină reziduală
    if "eolian" in df.columns and "foto" in df.columns:
        df["variabil"] = df["eolian"].fillna(0) + df["foto"].fillna(0)
        df["sarcina_reziduala"] = df["consum"] - df["variabil"]

    return df


st.set_page_config(page_title="Dashboard SEN - Sold Energetic", layout="wide")
st.title("⚡ SEN România: Analiza Exploratorie a Soldului (Import / Export)")

st.sidebar.header("Parametri analiză")
start_date = st.sidebar.date_input(
    "Data început", pd.to_datetime("today") - pd.Timedelta(days=7)
)
end_date = st.sidebar.date_input("Data sfârșit", pd.to_datetime("today"))

if start_date <= end_date:
    df = load_data(start_date.isoformat(), end_date.isoformat())

    if not df.empty:
        # ----------------------------------------------------
        # 1. PROFILUL ORAR: VÂRF VS. GOL
        # ----------------------------------------------------
        st.header("1. Profilul orar al soldului și consumului")
        df["ora"] = df["timestamp"].dt.hour
        hourly_agg = (
            df.groupby("ora")[["sold", "consum", "productie"]]
            .mean()
            .reset_index()
        )

        fig_hourly = go.Figure()
        fig_hourly.add_trace(
            go.Scatter(
                x=hourly_agg["ora"],
                y=hourly_agg["sold"],
                name="Sold Mediu (MW)",
                line=dict(color="royalblue", width=3),
            )
        )
        fig_hourly.add_trace(
            go.Scatter(
                x=hourly_agg["ora"],
                y=hourly_agg["consum"],
                name="Consum Mediu (MW)",
                line=dict(color="firebrick", dash="dot"),
                yaxis="y2",
            )
        )

        fig_hourly.update_layout(
            title="Soldul mediu orar vs. Profilul de consum",
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

        # ----------------------------------------------------
        # 2. LEGĂTURA CU SURSELE VARIABILE (EOLIAN + FOTO)
        # ----------------------------------------------------
        st.header("2. Relația Sold – Surse Variabile (Eolian & Solar)")
        c1, c2, c3 = st.columns(3)
        c1.metric(
            "Corelație Sold - Eolian",
            f"{df['sold'].corr(df['eolian']):.3f}"
            if "eolian" in df.columns
            else "N/A",
        )
        c2.metric(
            "Corelație Sold - Foto",
            f"{df['sold'].corr(df['foto']):.3f}"
            if "foto" in df.columns
            else "N/A",
        )
        c3.metric(
            "Corelație Sold - Sarcina Reziduală",
            f"{df['sold'].corr(df['sarcina_reziduala']):.3f}"
            if "sarcina_reziduala" in df.columns
            else "N/A",
        )

        fig_var = px.scatter(
            df,
            x="variabil",
            y="sold",
            color="status",
            color_discrete_map={
                "Import": "crimson",
                "Export": "forestgreen",
                "Echilibru": "gray",
            },
            hover_data=["timestamp", "consum", "productie"],
            labels={
                "variabil": "Producție Variabilă (Eolian + Foto) [MW]",
                "sold": "Sold (MW)",
            },
            title="Distribuția soldului în funcție de producția regenerabilă variabilă",
        )
        fig_var.add_hline(y=0, line_dash="dash", line_color="black")
        st.plotly_chart(fig_var, use_container_width=True)

        # ----------------------------------------------------
        # 3. ORE PE ZI: IMPORT VS. EXPORT
        # ----------------------------------------------------
        st.header("3. Durata zilnică: Net Importator vs. Net Exportator")

        # Agregare la nivel de oră pentru a calcula corect numărul de ore
        df["data"] = df["timestamp"].dt.date
        df_hourly = (
            df.set_index("timestamp")
            .resample("1h")[["sold"]]
            .mean()
            .reset_index()
        )
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

        st.dataframe(
            daily_hours.rename(
                columns={"Import": "Ore Import / zi", "Export": "Ore Export / zi"}
            ),
            use_container_width=True,
        )

        # ----------------------------------------------------
        # 4. VALORI MAXIME ȘI CONTEXT MIX ENERGETIC
        # ----------------------------------------------------
        st.header("4. Valori Maxime Înregistrate & Contextul Mixului")

        max_export_row = df.loc[df["sold"].idxmax()]
        max_import_row = df.loc[
            df["sold"].idxmin()
        ]  # Cel mai negativ = cel mai mare import

        col_exp, col_imp = st.columns(2)

        with col_exp:
            st.success(
                f"### 🟢 Maxim Export: {max_export_row['sold']:.1f} MW"
            )
            st.write(f"**Data/Ora:** {max_export_row['timestamp']}")
            st.write(f"**Consum:** {max_export_row.get('consum', 'N/A')} MW")
            st.write(
                f"**Producție totală:** {max_export_row.get('productie', 'N/A')} MW"
            )
            st.write(
                f"**Eolian + Foto:** {max_export_row.get('variabil', 'N/A')} MW"
            )

        with col_imp:
            st.error(
                f"### 🔴 Maxim Import: {abs(max_import_row['sold']):.1f} MW"
            )
            st.write(f"**Data/Ora:** {max_import_row['timestamp']}")
            st.write(f"**Consum:** {max_import_row.get('consum', 'N/A')} MW")
            st.write(
                f"**Producție totală:** {max_import_row.get('productie', 'N/A')} MW"
            )
            st.write(
                f"**Eolian + Foto:** {max_import_row.get('variabil', 'N/A')} MW"
            )

    else:
        st.info(
            "Nu s-au putut încărca date pentru intervalul selectat. Verifică sursa de date."
        )