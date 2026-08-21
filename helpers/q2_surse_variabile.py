import streamlit as st
import plotly.express as px


# ÎNTREBAREA 2: Relația cu sursele variabile
def print_q2(df):
    st.subheader("2. Legătura dintre sold și sursele variabile (Eolian & Solar)")
    col_m1, col_m2, col_m3 = st.columns(3)
    if "eolian" in df.columns:
        # calculate the correlation between the "sold" and "eolian" columns, round it to 3 decimal places, and display it in the first metric column
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
        color="status", # color the points based on the "status" column, which indicates whether the sold is Import, Export, or Echilibru
        color_discrete_map={"Import": "#d62728", "Export": "#2ca02c", "Echilibru": "#7f7f7f"},
        labels={"variabil": "Producție Variabilă (Eolian + Foto) [MW]", "sold": "Sold (MW)"},
        title="Distribuția soldului în funcție de regenerabilele variabile",
    )
    fig_scatter.add_hline(y=0, line_dash="dash", line_color="black")
    st.plotly_chart(fig_scatter, use_container_width=True)