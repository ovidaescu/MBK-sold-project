import streamlit as st
import plotly.express as px

# ÎNTREBAREA 3: Ore pe zi Import vs. Export
def print_q3(df):
    st.subheader("3. Număr de ore/zi: Net Importator vs. Net Exportator")
    df_hourly = df.set_index("timestamp").resample("1h")[["sold"]].mean().reset_index()
    df_hourly["data"] = df_hourly["timestamp"].dt.date
    df_hourly["status"] = df_hourly["sold"].apply(
        lambda v: "Import" if v > 0 else "Export" if v < 0 else "Echilibru"
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