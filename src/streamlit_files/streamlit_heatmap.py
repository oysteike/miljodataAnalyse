import streamlit as st
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'src')))
from processing.heatmap_utils import load_data, filter_data, interpolate_data, make_map, plot_legend

def show():
    st.title("Interpolert heatmap for nedbør i januar 2025")
    st.markdown("""
    **Visualiserer interpolerte værdata for nedbør i januar 2025.**
    Med data fra hele Norge lages et interaktivt heatmap.
    Velg værtype og dato for å se dataene i kartet.  
    Noen av områdene vil være hvite på grunn av manglende data – denne oversikten er altså mindre fullstendig.

     *Vær oppmerksom på at interpolering ikke gir nøyaktige resultater.*
    """)  
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, '..', '..', 'data', 'Jan_2025')

    try:
        df = load_data(data_dir)
    except Exception as e:
        st.error(f"Kunne ikke laste opp data: {e}. Vennligst sjekk datakildene og prøv igjen.")
        return
    available_types = sorted(df['datatype'].unique())
    datatype = st.selectbox("Velg værtype", available_types)

    max_value = df[df['datatype'] == datatype]["value"].max()
    dates = sorted(df['referenceTimestamp'].unique())
    selected_index = st.number_input("Velg dag", min_value=0, max_value=len(dates)-1, value=0, step=1)
    selected_date = dates[selected_index]
    st.write(f"Valgt dato: {selected_date}")

    radius = 80
    intensity = 0.7
    threshold = 0.05
    cutoff = 75
    if datatype == "temperatur":
        cutoff = 750

    filtered_df = filter_data(df, datatype, selected_date, max_value)

    interp_df = interpolate_data(filtered_df, cutoff)
    if interp_df.empty:
        st.warning("Datasettet inneholder ikke nødvendig data for interpolering. Minst 3 datapunkter og posisjon er nødvendig.")
        return

    deck = make_map(interp_df, radius, intensity, threshold)
    st.pydeck_chart(deck)

    min_val = filtered_df["value"].min()
    st.subheader("Fargeskala")
    unit = "m/s" if datatype.lower() == "vind" else "mm"
    st.write(f"Verdier: {min_val:.1f} {unit} – {max_value:.1f} {unit}")
    legend = plot_legend(min_val, max_value, datatype)
    st.image(legend)

    with st.expander("📊 Rådata og statistikk"):
        st.write("Antall opprinnelige punkter:", len(filtered_df))
        st.dataframe(filtered_df[["lat", "lon", "value"]].head())
        st.write(filtered_df["value"].describe())
        st.write("Antall interpolerte punkter:", len(interp_df))


