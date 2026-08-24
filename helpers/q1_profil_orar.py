import streamlit as st
import plotly.graph_objects as go

# ÎNTREBAREA 1: Profilul orar
def print_q1(df):
    st.subheader("1. Profilul orar al soldului: Vârf vs. Gol de consum")
    df["ora"] = df["timestamp"].dt.hour
    # group by hour and calculate the mean of sold, consum, and productie columns, then reset the index to get a clean DataFrame
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
            title="Sold (MW) [>0 Import / <0 Export]",
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor="gray",
        ),
        yaxis2=dict(
            title="Consum (MW)", overlaying="y", side="right", showgrid=False
        ),
        hovermode="x unified", # this ensures that when you hover over the graph, it shows the values for all traces at that x-coordinate
    )
    st.plotly_chart(fig_hourly, use_container_width=True)

    st.info("""
            **Răspuns direct:** Da, importăm masiv la vârfurile de consum, iar exportul se realizează exclusiv pe un gol de cerere (dar un gol atipic, de prânz).

            **Concluzia analizei:**
            * **La vârf de consum (08:00-09:00 și 19:00-21:00):** România este **net importatoare**. Curba soldului o urmărește fidel pe cea a consumului, atingând un deficit mediu de peste 1000 MW seara.
            * **În golul de consum (11:00-14:00):** Sistemul devine **net exportator**. Este interesant de observat că exportul nu are loc noaptea (când consumul e minim - orele 01:00-05:00), ci la mijlocul zilei, fiind susținut puternic de vârful de producție fotovoltaică.
            """)