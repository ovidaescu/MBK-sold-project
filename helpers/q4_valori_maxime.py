import streamlit as st
import plotly.express as px

def create_mix_pie_chart(row, title):
    #print("\n--- PIE CHART DEBUG ---")
    #print("APE:", row.get("ape", 0))
    #print("HIDRO:", row.get("hidro", 0))
    #print("All row data:")
    #print(row.to_dict())

    labels = ['Eolian', 'Foto', 'Ape (Hidro)', 'Nuclear', 'Cărbune', 'Hidrocarburi', 'Biomasă']
    values = [ # no negative values in the pie chart 
        max(0, row.get('eolian', 0)),
        max(0, row.get('foto', 0)),
        max(0, row.get('hidro', 0)),
        max(0, row.get('nuclear', 0)),
        max(0, row.get('carbune', 0)),
        max(0, row.get('hidrocarburi', 0)),
        max(0, row.get('biomasa', 0))
    ]
    
    fig = px.pie(
        names=labels, 
        values=values, 
        title=title,
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(margin=dict(t=40, b=0, l=0, r=0))
    return fig  

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

        # compute deviation for export row: consum_teoretic_e = productie + sold, then compare with consum to see the deviation
        consum_teoretic_e = row_exp['productie'] + row_exp['sold'] 
        deviatie_e = abs(row_exp['consum'] - consum_teoretic_e)
        
        with st.expander("Verificare de consistență a datelor"):
            st.write(f"Conform ecuației: `Producție + Sold ≈ Consum`")
            st.write(f"**Calcul:** {row_exp['productie']:.0f} + ({row_exp['sold']:.0f}) = {consum_teoretic_e:.0f} MW")
            st.caption(f"*Deviație de {deviatie_e:.0f} MW față de consumul măsurat ({row_exp['consum']:.0f} MW), cauzată de pierderile din rețea și marja senzorilor.*")

        st.markdown("---")
        fig_exp = create_mix_pie_chart(row_exp, "Proporții Mix Energetic")
        st.plotly_chart(fig_exp, use_container_width=True)

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

        # compute deviation for import row: consum_teoretic_i = productie + sold, then compare with consum to see the deviation
        consum_teoretic_i = row_imp['productie'] + row_imp['sold'] 
        deviatie_i = abs(row_imp['consum'] - consum_teoretic_i)
        
        with st.expander("Verificare de consistență a datelor"):
            st.write(f"Conform ecuației: `Producție + Sold ≈ Consum`")
            st.write(f"**Calcul:** {row_imp['productie']:.0f} + {row_imp['sold']:.0f} = {consum_teoretic_i:.0f} MW")
            st.caption(f"*Deviație de {deviatie_i:.0f} MW față de consumul măsurat ({row_imp['consum']:.0f} MW), justificată prin pierderile tehnologice.*")

        st.markdown("---")
        fig_imp = create_mix_pie_chart(row_imp, "Proporții Mix Energetic")
        st.plotly_chart(fig_imp, use_container_width=True)

    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

    st.info("""
        **Răspuns direct:** Extremele rețelei au fost un export maxim de 2900 MW și un import maxim de 2953 MW, ambele fiind dictate de o combinație clară între nivelul consumului și disponibilitatea surselor regenerabile.

        **Contextul extremelor:**
        * **Context Maxim Export (Surplus):** A apărut primăvara, la mijlocul zilei (23 martie, ora 12:54). Consumul național era la un nivel foarte redus (doar 4762 MW). În același timp, natura a oferit o producție uriașă: energia eoliană a reprezentat cea mai mare felie a mixului (34.2%), ajutată de fotovoltaic.
        * **Context Maxim Import (Deficit):** A apărut iarna, la vârful de seară (25 februarie, ora 18:44). Consumul a explodat la aproape 8500 MW. Din cauza întunericului și lipsei de vânt, producția eoliană și solară a fost practic zero (sub 1.25% din mix). Deficitul masiv a trebuit acoperit din import, în ciuda funcționării la capacitate a centralelor pe hidrocarburi, cărbune și hidro.
        """)