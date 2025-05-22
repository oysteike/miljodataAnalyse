import streamlit as st
import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'src')))
from processing.correlation_utils import load_data, plot_weather_dashboard, calculate_correlation

def show():
    st.title("Sammenligning av værdata")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, '..', '..', 'data', 'oslo_2015-2025')
    data_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]

    selected_file1 = st.selectbox("Velg første datakilde", sorted(data_files))
    selected_file2 = st.selectbox("Velg andre datakilde", data_files)

    # Sørger for at de to valgene ikke er det samme
    while selected_file1 == selected_file2:
        st.warning("Kan ikke velge samme fil to ganger. Velg en annen fil for andre datakilde.")
        selected_file2 = st.selectbox("Velg andre datakilde (CSV)", sorted(data_files))

    file_path1 = os.path.join(data_dir, selected_file1)
    file_path2 = os.path.join(data_dir, selected_file2)

    df = load_data(file_path1, file_path2)
    st.write(f"Antall datapunkter: {len(df)}")

    start_date = st.date_input("Velg start-dato", min_value=pd.to_datetime("2015-01-01"), max_value=pd.to_datetime("2025-01-01"), value=pd.to_datetime("2015-01-01"))
    end_date = st.date_input("Velg slutt-dato", min_value=start_date, max_value=pd.to_datetime("2025-01-01"), value=pd.to_datetime("2025-01-01"))
    start_date_ts = pd.Timestamp(start_date)
    end_date_ts = pd.Timestamp(end_date)

    # Filtrer datasettet basert på start- og slutt-dato
    df_filtered = df[(pd.to_datetime(df['referenceTimestamp']) >= start_date_ts) & (pd.to_datetime(df['referenceTimestamp']) <= end_date_ts)]

    st.write(f"Antall datapunkter vist: {len(df_filtered)}")

    corr = calculate_correlation(df) # Bruker fortsatt hele datasettet til korrelasjon
    if abs(corr) < 0.3:
        st.warning(f"Korrelasjonen er svak; {corr}. Det er ingen klar sammenheng i datasettene")
    elif abs(corr) > 0.7:
        st.success("Det er sterk sammenheng mellom datasettene! Du kan betrakte de som avhengige")
    if corr > 0:
        st.info(f"Det er en positiv sammenheng i datasettene. Korrelasjone har verdi: {corr}") 
    else:
        st.info(f"Det er en negativ sammenheng i datasettene. Korrelasjone har verdi: {corr}")


    fig1, fig2 = plot_weather_dashboard(df_filtered) # Bruker bare de filtrerte datapunktene til å plotte
    st.plotly_chart(fig1)
    st.plotly_chart(fig2)

    st.dataframe(df_filtered)