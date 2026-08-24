import streamlit as st

# ÎNTREBAREA 4: Valori maxime și context
def print_q4(df):
    st.subheader("4. Valori Maxime Înregistrate & Contextul Mixului Energetic")
    #idx_max_exp = df["sold"].idxmax()
    #idx_max_imp = df["sold"].idxmin()

    # find the index of the maximum export and import values for the "sold" column in the dataframe
    idx_max_exp = df["sold"].idxmin() # Exportul e negativ, deci căutăm minimul
    idx_max_imp = df["sold"].idxmax() # Importul e pozitiv, deci căutăm maximul

    # get the rows corresponding to the maximum export and import values
    row_exp = df.loc[idx_max_exp]
    row_imp = df.loc[idx_max_imp]

    col_e, col_i = st.columns(2)
    with col_e:
        st.success(f"### 🟢 Maxim Export: {abs(row_exp['sold']):.1f} MW")
        st.write(f"**Data / Ora:** {row_exp['timestamp']}")
        st.write(f"**Consum:** {row_exp.get('consum', 'N/A')} MW")
        st.write(f"**Producție totală:** {row_exp.get('productie', 'N/A')} MW")
        st.markdown("---")
        st.write("**Din care (Mix):**")
        st.write(f" **Eolian:** {row_exp.get('eolian', 0):.1f} MW | **Foto:** {row_exp.get('foto', 0):.1f} MW")
        st.write(f" **Hidro:** {row_exp.get('hidro', 0):.0f} MW | **Nuclear:** {row_exp.get('nuclear', 0):.0f} MW")
        st.write(f" **Cărbune:** {row_exp.get('carbune', 0):.0f} MW |  **Hidrocarburi:** {row_exp.get('hidrocarburi', 0):.0f} MW")
        st.write(f" **Biomasă:** {row_exp.get('biomasa', 0):.0f} MW")

    with col_i:
        st.error(f"### 🔴 Maxim Import: {row_imp['sold']:.1f} MW")
        st.write(f"**Data / Ora:** {row_imp['timestamp']}")
        st.write(f"**Consum:** {row_imp.get('consum', 'N/A')} MW")
        st.write(f"**Producție totală:** {row_imp.get('productie', 'N/A')} MW")
        st.markdown("---")
        st.write("**Din care (Mix):**") 
        st.write(f" **Eolian:** {row_imp.get('eolian', 0):.1f} MW | **Foto:** {row_imp.get('foto', 0):.1f} MW")
        st.write(f" **Hidro:** {row_imp.get('hidro', 0):.0f} MW |  **Nuclear:** {row_imp.get('nuclear', 0):.0f} MW")
        st.write(f" **Cărbune:** {row_imp.get('carbune', 0):.0f} MW |  **Hidrocarburi:** {row_imp.get('hidrocarburi', 0):.0f} MW")
        st.write(f" **Biomasă:** {row_imp.get('biomasa', 0):.0f} MW")