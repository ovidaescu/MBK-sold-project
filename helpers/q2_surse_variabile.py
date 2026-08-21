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

    st.markdown("---") # delimitation line

    # selectbox to choose which variable to plot on the X-axis
    optiune_grafic = st.selectbox(
        "Alege ce dorești să analizezi pe axa orizontală (X):",
        options=["Cumulat (Eolian + Fotovoltaic)", "Doar Eolian", "Doar Fotovoltaic", "Sarcină Reziduală"],
    )

    # logic for changing the X-axis variable based on the selected option
    if optiune_grafic == "Cumulat (Eolian + Fotovoltaic)":
        coloana_x = "variabil"
        eticheta_x = "Producție Variabilă (Eolian + Foto) [MW]"
    elif optiune_grafic == "Doar Eolian":
        coloana_x = "eolian"
        eticheta_x = "Producție Eoliană [MW]"
    elif optiune_grafic == "Doar Fotovoltaic":
        coloana_x = "foto"
        eticheta_x = "Producție Fotovoltaică [MW]"
    else :
        coloana_x = "sarcina_reziduala"
        eticheta_x = "Sarcină Reziduală [MW]"

    fig_scatter = px.scatter(
        df,
        x = coloana_x, #x="variabil",
        y="sold",
        color="status", # color the points based on the "status" column, which indicates whether the sold is Import, Export, or Echilibru
        color_discrete_map={"Import": "#d62728", "Export": "#2ca02c", "Echilibru": "#7f7f7f"},
        #labels={"variabil": "Producție Variabilă (Eolian + Foto) [MW]", "sold": "Sold (MW)"},
        labels={coloana_x: eticheta_x, "sold": "Sold (MW)"},
        title="Distribuția soldului în funcție de regenerabilele variabile",
    )

    # delete this line if you want to keep the default legend title
    fig_scatter.update_traces(
        marker=dict(
            size=6,             # Mărimea punctului (o poți crește dacă vrei să fie mai vizibile)
            opacity=1.0,        # Eliminăm transparența (puncte solide)
            line=dict(
                width=0.8,      # Grosimea conturului (0.8 sau 1 este ideal pentru multe puncte)
                color='black'   # Culoarea conturului (negru ajută culorile roșu/verde să iasă în evidență)
            )
        )
    )

    fig_scatter.add_hline(y=0, line_dash="dash", line_color="black")
    st.plotly_chart(fig_scatter, use_container_width=True)