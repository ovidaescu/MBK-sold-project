import pandas as pd
import numpy as np
import streamlit as st

# custom csv reader pentru a gestiona multiple encodări și a evita erorile de citire
def load_any_file(file_source):
    if hasattr(file_source, "name"):
        name = file_source.name.lower()
    else:
        name = str(file_source).lower()

    if name.endswith(".xlsx") or name.endswith(".xls"):
        if hasattr(file_source, "seek"): # chech if the file-like object supports seek
            file_source.seek(0) # start reading from the beginning of the file
        return pd.read_excel(file_source)

    # Fallback CSV
    if hasattr(file_source, "seek"):
        file_source.seek(0)
    return pd.read_csv(file_source, sep=None, engine="python")





@st.cache_data
def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """Normalizează coloanele și calculează variabilele derivate."""
    # Normalizare nume coloane
    df.columns = (
        df.columns.str.strip() # removes leading and trailing whitespace
        .str.lower()
        .str.replace(r"\[.*\]", "", regex=True) # removes any text within square brackets
        .str.strip() # removes leading and trailing whitespace again after removing brackets
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
                # converts the column to numeric, replacing commas with dots for decimal conversion
                df[target] = pd.to_numeric(
                    df[col].astype(str).str.replace(",", "."), errors="coerce" # replace commas with dots for decimal conversion
                )
                # .astype(str) is used to ensure that the replacement works even if the column is not of string type initially and can t be converted to numerical values

    # Convenția Transelectrica: Sold = Productie - Consum
    if "sold" not in df.columns and "productie" in df and "consum" in df:
        df["sold"] = df["productie"] - df["consum"]

    # Status energetic
    # lambda function is used to apply a condition to each value in the "sold" column, returning "Export" if the value is greater than 0, "Import" if less than 0, and "Echilibru" if equal to 0
    df["status"] = df["sold"].apply(
        lambda v: "Import" if v > 0 else "Export" if v < 0 else "Echilibru"
    )

    # Surse variabile și sarcină reziduală
    eolian = df["eolian"].fillna(0) if "eolian" in df.columns else 0
    foto = df["foto"].fillna(0) if "foto" in df.columns else 0
    df["variabil"] = eolian + foto

    if "consum" in df.columns:
        df["sarcina_reziduala"] = df["consum"] - df["variabil"]

    return df