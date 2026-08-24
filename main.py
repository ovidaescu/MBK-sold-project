import os
import streamlit as st
from datetime import datetime, timedelta

# Importăm modulele noastre
from helpers.data_processing import load_any_file, process_data
from helpers.q1_profil_orar import print_q1
from helpers.q2_surse_variabile import print_q2
from helpers.q3_bilant_zilnic import print_q3
from helpers.q4_valori_maxime import print_q4


st.set_page_config(page_title="EDA SEN - Sold Import/Export", layout="wide")


# --- SIDEBAR & DATE ---
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
elif os.path.exists(DEFAULT_FILE): # check if the default file exists in the root directory
    raw_df = load_any_file(DEFAULT_FILE)
    df_all = process_data(raw_df)
    st.sidebar.info(f"Se utilizează setul local: `{DEFAULT_FILE}`")

if df_all is None or df_all.empty:
    st.warning("⚠️ Nu a fost găsit niciun set de date. Te rog să încarci un fișier din meniul lateral pentru a continua.")
    st.stop() # Această comandă oprește scriptul aici. Nu va mai rula nimic mai jos!



# --- FILTRARE PE INTERVAL DE TIMP ---

#d timestamp = date + time
min_timestamp = df_all["timestamp"].min() 
max_timestamp = df_all["timestamp"].max()

# only dates
min_date = min_timestamp.date()
max_date = max_timestamp.date()

st.sidebar.header("📅 Filtrare Perioadă")

# Creăm o cheie unică bazată pe limitele fișierului
# Dacă schimbi fișierul, cheia se schimbă, iar Streamlit resetează complet calendarul
calendar_key = f"date_picker_{min_date}_{max_date}"

date_range = st.sidebar.date_input(
    "Selectează intervalul",
    value=(min_date, max_date),
    min_value=min_date, # set the minimum selectable date to the earliest date in the dataset
    max_value=max_date, # set the maximum selectable date to the latest date in the dataset
    key=calendar_key # unique key to reset the date picker when the file changes
)

# get the start and end times from the sidebar, defaulting to the min and max timestamps of the dataset
start_time = st.sidebar.time_input(
    "Ora de început",
    value=min_timestamp.time().replace(second=0, microsecond=0),
)

end_time = st.sidebar.time_input(
    "Ora de sfârșit",
    value=max_timestamp.time().replace(second=0, microsecond=0),
)

if isinstance(date_range, tuple) and len(date_range) == 2: # check if the date_range is a tuple of length 2
    start_date, end_date = date_range

    start_datetime = datetime.combine(start_date, start_time)
    end_datetime = datetime.combine(end_date, end_time)

    if start_datetime > end_datetime:
        st.error("Ora de început trebuie să fie înaintea orei de sfârșit.")
        st.stop()

    # Include the complete selected ending minute by adding one minute to the end_datetime for filtering
    end_datetime_exclusive = end_datetime + timedelta(minutes=1)

    # new dataframe filtered by the selected date and time range
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


# --- DASHBOARD PRINCIPAL ---
st.title("⚡ SEN România: Analiza Soldului Energetic (Import / Export)")

print_q1(df)
st.divider()
print_q2(df)
st.divider()
print_q3(df)
st.divider()
print_q4(df)

#print(df)
#print(df.columns.tolist())