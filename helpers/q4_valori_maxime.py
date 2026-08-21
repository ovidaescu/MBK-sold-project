import streamlit as st

# ÎNTREBAREA 4: Valori maxime și context
def print_q4(df):
    st.subheader("4. Valori Maxime Înregistrate & Contextul Mixului Energetic")
    #idx_max_exp = df["sold"].idxmax()
    #idx_max_imp = df["sold"].idxmin()

    idx_max_exp = df["sold"].idxmin() # Exportul e negativ, deci căutăm minimul
    idx_max_imp = df["sold"].idxmax() # Importul e pozitiv, deci căutăm maximul

    row_exp = df.loc[idx_max_exp]
    row_imp = df.loc[idx_max_imp]

    col_e, col_i = st.columns(2)
    with col_e:
        st.success(f"### 🟢 Maxim Export: {abs(row_exp['sold']):.1f} MW")
        st.write(f"**Data / Ora:** {row_exp['timestamp']}")
        st.write(f"**Consum:** {row_exp.get('consum', 'N/A')} MW")
        st.write(f"**Producție totală:** {row_exp.get('productie', 'N/A')} MW")
        st.write(f"**Eolian:** {row_exp.get('eolian', 0):.1f} MW | **Foto:** {row_exp.get('foto', 0):.1f} MW")

    with col_i:
        st.error(f"### 🔴 Maxim Import: {row_imp['sold']:.1f} MW")
        st.write(f"**Data / Ora:** {row_imp['timestamp']}")
        st.write(f"**Consum:** {row_imp.get('consum', 'N/A')} MW")
        st.write(f"**Producție totală:** {row_imp.get('productie', 'N/A')} MW")