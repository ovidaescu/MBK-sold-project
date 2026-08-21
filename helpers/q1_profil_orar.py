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