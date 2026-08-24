import streamlit as st
import pandas as pd
import plotly.express as px

# ÎNTREBAREA 3: Ore pe zi Import vs. Export
def print_q3(df):
    st.subheader("3. Număr de ore/zi: Net Importator vs. Net Exportator")
    # create a new dataframe set the date as index for easier resampling, resample to hourly frequency and calculate the mean sold for each hour
    # resampling data in groups by hour ( 8:30,8:45 - > group 8)
    # compute the mean for each hour, reset the index to have a flat dataframe again
    df_hourly = df.set_index("timestamp").resample("1h")[["sold"]].mean().reset_index()
    # create a new column with only the date from the timpestamp withouth the hour
    df_hourly["data"] = df_hourly["timestamp"].dt.date
    # new column for status  
    df_hourly["status"] = df_hourly["sold"].apply(
        lambda v: "Import" if v > 0 else "Export" if v < 0 else "Echilibru"
    )

    daily_hours = (
        df_hourly.groupby(["data", "status"]) # group by date and status
        .size() # count the number of occurrences for each group
        .unstack(fill_value=0) # unstack - create a new dataframe with the status as columns and fill missing values with 0
        .reset_index() # reset the index to have a flat dataframe again
    )
    for col in ["Import", "Export", "Echilibru"]:
        if col not in daily_hours.columns:
            daily_hours[col] = 0

    fig_hours = px.bar(
        daily_hours,
        x="data",
        y=["Import", "Export", "Echilibru"],
        labels={"data": "Data", "value": "Număr ore / zi", "variable": "Regim"},
        color_discrete_map={"Import": "#d62728", "Export": "#2ca02c", "Echilibru": "#7f7f7f"},
        title="Bilanțul zilnic al orelor de funcționare",
    )

    first_month = pd.Timestamp(daily_hours["data"].min()).replace(day=1)
    last_month = pd.Timestamp(daily_hours["data"].max()).replace(day=1)
    if last_month != first_month:
        # first_month + pd.offsets.MonthBegin(1) - to skip the line for January, otherwise just first_month 
        for month_start in pd.date_range(first_month + pd.offsets.MonthBegin(1), last_month, freq="MS"): # MS = Month Start, so add a line for each month start
            fig_hours.add_vline(
                x=month_start,
                line_width=1,
                line_dash="dash",
                line_color="rgba(255, 255, 255, 0.45)",
            )

    # setting for the axis
    fig_hours.update_layout(

        yaxis=dict(
            range=[0, 24], 
            dtick=4, 
        ),
        xaxis=dict(
            dtick="M1",
            tickformat="%b %Y", 
            ticklabelmode="period",
            tickangle=0,
            hoverformat="%d %b %Y", 
        )
        
    )

    st.plotly_chart(fig_hours, use_container_width=True)